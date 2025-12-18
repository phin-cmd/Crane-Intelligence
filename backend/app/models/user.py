"""
Crane Intelligence Platform - User Models
Implements user authentication and user management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import enum
from ..core.database import Base


class UserRole(enum.Enum):
    """User roles based on target customers from roadmap"""
    CRANE_RENTAL_COMPANY = "crane_rental_company"  # Fleet valuation and optimization
    EQUIPMENT_DEALER = "equipment_dealer"          # Inventory pricing and services
    FINANCIAL_INSTITUTION = "financial_institution" # Collateral assessment
    OTHERS = "others"                               # Public users (general public)


class User(Base):
    """User model for authentication and user management"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    user_role = Column(Enum(UserRole, values_callable=lambda x: [e.value for e in x]), nullable=False)
    
    # Payment tracking for payment history
    total_payments = Column(Float, default=0.0)  # Total amount paid by user
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    
    # Company relationship
    company_id = Column(Integer, nullable=True)
    
    # Notification preferences (JSON field for flexible preference management)
    notification_preferences = Column(String, nullable=True)  # JSON string of notification preferences
    
    # Relationships (lazy loading to avoid circular imports)
    # Note: These are defined here but relationships are set up in equipment.py
    # to avoid circular import issues
    # UserNotification relationship - using string reference to avoid circular import
    notifications = relationship("UserNotification", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.user_role.value}')>"


class UserSession(Base):
    """User session management for authentication"""
    
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    session_token = Column(String, unique=True, index=True, nullable=False)
    refresh_token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, expires_at='{self.expires_at}')>"
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at


class UsageLog(Base):
    """Usage logging for subscription management and analytics"""
    
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    action_type = Column(String, nullable=False)  # 'valuation', 'api_call', 'portfolio_analysis'
    endpoint = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    ip_address = Column(String)
    user_agent = Column(String)
    success = Column(Boolean, default=True)
    error_message = Column(String)
    
    # Additional context
    crane_manufacturer = Column(String)
    crane_model = Column(String)
    crane_capacity = Column(Float)
    
    def __repr__(self):
        return f"<UsageLog(id={self.id}, user_id={self.user_id}, action='{self.action_type}')>"


class PasswordResetToken(Base):
    """Password reset token model for forgot password functionality"""
    
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    def is_expired(self):
        """Check if the token has expired"""
        return datetime.utcnow() > self.expires_at


class EmailVerificationToken(Base):
    """Email verification token model for email verification functionality"""
    
    __tablename__ = "email_verification_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    def is_expired(self):
        """Check if the token has expired"""
        return datetime.utcnow() > self.expires_at


