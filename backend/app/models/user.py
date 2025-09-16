"""
Crane Intelligence Platform - User Models
Implements user authentication and subscription management for the MVP
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Float
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import enum
from .base import Base


class SubscriptionTier(enum.Enum):
    """Subscription tiers according to the roadmap"""
    BASIC = "basic"      # $999/month - Valuation engine + market comparables
    PRO = "pro"          # $2499/month - Deal Score + portfolio analysis + API access
    ENTERPRISE = "enterprise"  # Custom pricing - Large organizations


class UserRole(enum.Enum):
    """User roles based on target customers from roadmap"""
    CRANE_RENTAL_COMPANY = "crane_rental_company"  # Fleet valuation and optimization
    EQUIPMENT_DEALER = "equipment_dealer"          # Inventory pricing and services
    FINANCIAL_INSTITUTION = "financial_institution" # Collateral assessment
    ADMIN = "admin"                                 # Platform administration


class User(Base):
    """User model for authentication and subscription management"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    user_role = Column(Enum(UserRole), nullable=False)
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.BASIC)
    
    # Subscription management
    subscription_start_date = Column(DateTime, default=func.now())
    subscription_end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Usage tracking for subscription limits
    monthly_valuations_used = Column(Integer, default=0)
    monthly_api_calls_used = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', tier='{self.subscription_tier.value}')>"
    
    @property
    def subscription_is_active(self) -> bool:
        """Check if subscription is currently active"""
        if not self.subscription_end_date:
            return False
        return datetime.utcnow() < self.subscription_end_date
    
    @property
    def days_until_expiry(self) -> int:
        """Calculate days until subscription expires"""
        if not self.subscription_end_date:
            return 0
        delta = self.subscription_end_date - datetime.utcnow()
        return max(0, delta.days)
    
    def can_perform_valuation(self) -> bool:
        """Check if user can perform a valuation based on subscription tier"""
        if not self.subscription_is_active:
            return False
        
        # Basic tier: 50 valuations/month
        # Pro tier: 200 valuations/month  
        # Enterprise: Unlimited
        limits = {
            SubscriptionTier.BASIC: 50,
            SubscriptionTier.PRO: 200,
            SubscriptionTier.ENTERPRISE: float('inf')
        }
        
        limit = limits.get(self.subscription_tier, 0)
        return self.monthly_valuations_used < limit
    
    def can_access_api(self) -> bool:
        """Check if user can access API based on subscription tier"""
        if not self.subscription_is_active:
            return False
        
        # Only Pro and Enterprise tiers have API access
        return self.subscription_tier in [SubscriptionTier.PRO, SubscriptionTier.ENTERPRISE]
    
    def can_access_portfolio_analysis(self) -> bool:
        """Check if user can access portfolio analysis based on subscription tier"""
        if not self.subscription_is_active:
            return False
        
        # Only Pro and Enterprise tiers have portfolio analysis
        return self.subscription_tier in [SubscriptionTier.PRO, SubscriptionTier.ENTERPRISE]
    
    def increment_usage(self, valuation: bool = False, api_call: bool = False):
        """Increment usage counters"""
        if valuation:
            self.monthly_valuations_used += 1
        if api_call:
            self.monthly_api_calls_used += 1


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


class SubscriptionPlan(Base):
    """Subscription plan definitions according to the roadmap"""
    
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    tier = Column(Enum(SubscriptionTier), unique=True, nullable=False)
    name = Column(String, nullable=False)
    monthly_price = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    
    # Feature limits
    monthly_valuations_limit = Column(Integer, nullable=False)
    monthly_api_calls_limit = Column(Integer, nullable=False)
    has_deal_score = Column(Boolean, default=False)
    has_portfolio_analysis = Column(Boolean, default=False)
    has_api_access = Column(Boolean, default=False)
    has_priority_support = Column(Boolean, default=False)
    
    # Additional features
    features = Column(String)  # JSON string of additional features
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SubscriptionPlan(tier='{self.tier.value}', price=${self.monthly_price})>"


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


# Default subscription plans based on the roadmap
DEFAULT_SUBSCRIPTION_PLANS = [
    {
        "tier": SubscriptionTier.BASIC,
        "name": "Basic Plan",
        "monthly_price": 999.00,
        "description": "Access to valuation engine and market comparables",
        "monthly_valuations_limit": 50,
        "monthly_api_calls_limit": 0,
        "has_deal_score": False,
        "has_portfolio_analysis": False,
        "has_api_access": False,
        "has_priority_support": False,
        "features": "Basic valuation, Market comparables, Email support"
    },
    {
        "tier": SubscriptionTier.PRO,
        "name": "Pro Plan", 
        "monthly_price": 2499.00,
        "description": "Advanced features including Deal Score, portfolio analysis, and API access",
        "monthly_valuations_limit": 200,
        "monthly_api_calls_limit": 1000,
        "has_deal_score": True,
        "has_portfolio_analysis": True,
        "has_api_access": True,
        "has_priority_support": False,
        "features": "Pro valuation, Deal scoring, Portfolio analysis, API access, Phone support"
    },
    {
        "tier": SubscriptionTier.ENTERPRISE,
        "name": "Enterprise Plan",
        "monthly_price": 0.00,  # Custom pricing
        "description": "Custom solutions for large organizations with specific needs",
        "monthly_valuations_limit": -1,  # Unlimited
        "monthly_api_calls_limit": -1,   # Unlimited
        "has_deal_score": True,
        "has_portfolio_analysis": True,
        "has_api_access": True,
        "has_priority_support": True,
        "features": "Enterprise features, Custom integrations, Dedicated support, SLA guarantees"
    }
]
