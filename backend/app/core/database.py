"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from .config import settings

# Create database engine
# Use SQLite for development and demo
engine = create_engine(
    "sqlite:///./crane_intelligence.db",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
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
    from ..models.base import Base
    from ..models.user import User, PasswordResetToken, UserSession, UsageLog
    from ..models.crane import Crane
    from ..models.subscription import EmailSubscription
    from ..models.enhanced_crane import (
        CraneListing, MarketTrend, BrokerNetwork, PerformanceMetrics,
        CraneValuationAnalysis, MarketIntelligence, RentalRates, DataRefreshLog
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
