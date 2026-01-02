"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from .config import settings

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
