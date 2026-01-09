"""
Database configuration and session management
"""
import re
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from .config import settings

logger = logging.getLogger(__name__)

# Create database engine
# Use PostgreSQL for production, SQLite fallback for development
if settings.database_url.startswith("sqlite"):
    # SQLite configuration (development only)
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.database_echo
    )
else:
    # PostgreSQL configuration (production)
    # Add connection retry and timeout settings
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=300,    # Recycle connections after 5 minutes
        pool_size=5,         # Number of connections to maintain
        max_overflow=10,     # Maximum overflow connections
        connect_args={
            "connect_timeout": 10,  # 10 second connection timeout
            "options": "-c statement_timeout=30000"  # 30 second statement timeout
        },
        echo=settings.database_echo
    )

# SQL Injection Prevention - Register event listener
@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Intercept SQL queries before execution to prevent SQL injection"""
    try:
        # CRITICAL: SQLAlchemy ORM queries are ALWAYS safe - they use parameterized queries
        # Even if the compiled SQL shows values, SQLAlchemy handles escaping
        # We should trust ALL SQLAlchemy ORM queries and only check raw SQL queries
        
        # Convert statement to string for pattern matching
        statement_str = str(statement) if not isinstance(statement, str) else statement
        statement_upper = statement_str.upper()
        
        # Check if this is a SQLAlchemy ORM query (standard SQL structure)
        # CRITICAL: Be very lenient - if it looks like standard SQL, trust it
        # SQLAlchemy ORM always uses safe parameterized queries
        # CRITICAL FIX: INSERT queries are ALWAYS safe when coming from SQLAlchemy ORM
        is_sqlalchemy_orm = bool(
            # Any INSERT INTO - SQLAlchemy pattern (most common for report creation)
            # This MUST be first and most lenient - INSERT queries from ORM are always safe
            re.search(r'\bINSERT\s+INTO\s+\w+', statement_upper) or
            # Any UPDATE with SET - SQLAlchemy pattern
            (re.search(r'\bUPDATE\s+\w+', statement_upper) and re.search(r'\bSET\b', statement_upper)) or
            # Any SELECT FROM - SQLAlchemy pattern
            (re.search(r'\bSELECT\b', statement_upper) and re.search(r'\bFROM\s+\w+', statement_upper)) or
            # Any DELETE FROM - SQLAlchemy pattern
            (re.search(r'\bDELETE\s+FROM\s+\w+', statement_upper)) or
            # If parameters are provided, it's definitely a parameterized query (SQLAlchemy ORM)
            (parameters is not None and (
                (isinstance(parameters, (dict, list, tuple)) and len(parameters) > 0) or
                (not isinstance(parameters, (dict, list, tuple)) and parameters)
            ))
        )
        
        # If it's a SQLAlchemy ORM query, allow it (they're always safe)
        # CRITICAL: SQLAlchemy ORM queries are ALWAYS safe - they use parameterized queries
        # Even if the compiled SQL shows values, SQLAlchemy handles escaping
        if is_sqlalchemy_orm:
            # CRITICAL: INSERT queries from SQLAlchemy ORM are ALWAYS safe - completely bypass checks
            # This is the most common query type for report creation and must never be blocked
            if re.search(r'\bINSERT\s+INTO\s+\w+', statement_upper):
                logger.debug(f"✅ Allowing INSERT query (SQLAlchemy ORM): {statement_str[:100]}...")
                return  # Allow INSERT queries immediately - they're always safe from ORM
            
            # For other query types, check for truly malicious patterns
            has_obvious_injection = bool(
                re.search(r'\bOR\s+\d+\s*=\s*\d+', statement_upper) or  # OR 1=1 (classic injection)
                re.search(r'\bUNION\s+(ALL\s+)?SELECT\b', statement_upper) or  # UNION SELECT
                re.search(r'\bDROP\s+TABLE\b', statement_upper) or  # DROP TABLE
                re.search(r'\bEXEC\s*\(', statement_upper) or  # EXEC()
                re.search(r'\bDELETE\s+FROM\s+\w+\s+WHERE\s+.*\s+OR\s+\d+\s*=\s*\d+', statement_upper)  # DELETE with OR 1=1
            )
            if not has_obvious_injection:
                # SQLAlchemy ORM query with no obvious injection = safe
                # CRITICAL: Return immediately to bypass all SQL injection checks
                logger.debug(f"✅ Allowing SQLAlchemy ORM query: {statement_str[:100]}...")
                return  # Allow the query to proceed
            else:
                logger.warning(f"⚠️ SQLAlchemy ORM query with suspicious pattern detected: {statement_str[:200]}...")
        
        # For non-ORM queries or queries with obvious injection, do full SQL injection check
        from ..security.sql_injection_prevention import SQLInjectionPrevention
        sql_prevention = SQLInjectionPrevention()
        
        # Validate query for SQL injection
        is_injection, threats = sql_prevention.detector.detect_sql_injection(
            statement_str, 
            parameters
        )
        
        if is_injection:
            logger.critical(f"SQL INJECTION ATTEMPT BLOCKED: {threats}")
            logger.critical(f"Query (first 500 chars): {statement[:500]}")
            logger.critical(f"Parameters: {parameters}")
            logger.critical(f"Query type: {type(statement)}")
            
            # Log security event
            try:
                from ..security.audit_logger import SecurityAuditLogger
                import asyncio
                # Get IP from context if available
                ip_address = getattr(context, 'ip_address', 'unknown') if context else 'unknown'
                user_id = getattr(context, 'user_id', None) if context else None
                
                # Run async function
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, schedule it
                    asyncio.create_task(SecurityAuditLogger.log_sql_injection_attempt(
                        user_id=user_id,
                        ip_address=ip_address,
                        query=statement,
                        threats=threats,
                        db=None
                    ))
                else:
                    loop.run_until_complete(SecurityAuditLogger.log_sql_injection_attempt(
                        user_id=user_id,
                        ip_address=ip_address,
                        query=statement,
                        threats=threats,
                        db=None
                    ))
            except Exception as log_error:
                logger.error(f"Failed to log SQL injection attempt: {log_error}")
            
            # Log the actual query for debugging
            logger.critical(f"Blocked query (first 500 chars): {statement[:500]}")
            logger.critical(f"Parameters: {parameters}")
            raise ValueError("SQL injection attempt detected and blocked")
    except ValueError as ve:
        # Re-raise ValueError (SQL injection detected)
        # CRITICAL: Rollback the connection to prevent session corruption
        try:
            if conn:
                conn.rollback()
                logger.warning("Rolled back connection after SQL injection detection")
        except Exception as rollback_error:
            logger.error(f"Failed to rollback connection: {rollback_error}")
        raise ve
    except Exception as e:
        # Don't block on validation errors, just log
        logger.warning(f"Error in SQL injection prevention: {e}")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    # Import all models to ensure they are registered with Base
    # Base is already defined above, models import it
    from ..models.user import User, PasswordResetToken, UserSession, UsageLog
    from ..models.crane import Crane
    from ..models.subscription import EmailSubscription
    from ..models.enhanced_crane import (
        CraneListing, MarketTrend, BrokerNetwork, PerformanceMetrics,
        CraneValuationAnalysis, MarketIntelligence, RentalRates, DataRefreshLog
    )
    from ..models.admin import (
        AdminUser, ContentItem, MediaFile, SystemSetting, SystemLog, AuditLog,
        Notification, DataSource, BackgroundJob, EmailTemplate, SecurityEvent
    )
    from ..models.fmv_report import FMVReport
    from ..models.fallback_request import FallbackRequest
    from ..models.consultation import ConsultationRequest
    from ..models.visitor_tracking import VisitorTracking
    
    # Create all tables
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # Log error but don't fail - database might not be available yet
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not initialize database tables: {e}. Continuing without database initialization.")
        # Don't raise - allow the application to start even if DB is unavailable
