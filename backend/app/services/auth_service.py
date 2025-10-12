"""
Authentication and Subscription Service
Provides user authentication and subscription management
"""

from typing import Dict, Optional
from fastapi import Depends, HTTPException, Header
import logging

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Subscription management service"""
    
    def __init__(self):
        self.subscription_plans = {
            "basic": {
                "name": "Basic",
                "monthly_valuations_limit": 50,
                "monthly_api_calls_limit": 1000,
                "features": ["basic_valuation"]
            },
            "pro": {
                "name": "Professional",
                "monthly_valuations_limit": 200,
                "monthly_api_calls_limit": 5000,
                "features": ["basic_valuation", "deal_score", "portfolio_analysis", "api_access"]
            },
            "enterprise": {
                "name": "Enterprise",
                "monthly_valuations_limit": -1,  # Unlimited
                "monthly_api_calls_limit": -1,   # Unlimited
                "features": ["basic_valuation", "deal_score", "portfolio_analysis", "api_access", "custom_reports"]
            }
        }
    
    def get_subscription_plan(self, tier: str) -> Optional[Dict]:
        """Get subscription plan details"""
        return self.subscription_plans.get(tier.lower())
    
    def get_all_plans(self) -> Dict:
        """Get all subscription plans"""
        return self.subscription_plans
    
    def can_access_feature(self, tier: str, feature: str) -> bool:
        """Check if tier can access feature"""
        plan = self.get_subscription_plan(tier)
        if not plan:
            return False
        return feature in plan.get("features", [])


class AuthService:
    """Authentication service"""
    
    def __init__(self):
        self.subscription_service = SubscriptionService()
    
    def get_current_user_from_token(self, token: str) -> Optional[Dict]:
        """Get current user from token"""
        # Simplified for demo
        return {
            "user_id": "demo_user",
            "email": "demo@craneintelligence.com",
            "subscription_tier": "pro"
        }


# Singleton instances
subscription_service = SubscriptionService()
auth_service = AuthService()


# Dependency functions for FastAPI
async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict:
    """Get current user from authorization header"""
    # Simplified authentication for demo
    return {
        "user_id": "demo_user",
        "email": "demo@craneintelligence.com",
        "subscription_tier": "pro"
    }


async def require_api_access(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Require API access feature"""
    tier = current_user.get("subscription_tier", "basic")
    if not subscription_service.can_access_feature(tier, "api_access"):
        raise HTTPException(status_code=403, detail="API access requires Pro or Enterprise subscription")
    return current_user


async def require_portfolio_analysis(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Require portfolio analysis feature"""
    tier = current_user.get("subscription_tier", "basic")
    if not subscription_service.can_access_feature(tier, "portfolio_analysis"):
        raise HTTPException(status_code=403, detail="Portfolio analysis requires Pro or Enterprise subscription")
    return current_user

