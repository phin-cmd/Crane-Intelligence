"""
Crane Intelligence Platform - Authentication Service
Implements JWT-based authentication and subscription management for the MVP
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import json

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = "your-secret-key-here-change-in-production"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security scheme
security = HTTPBearer()


class AuthService:
    """Authentication and authorization service"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            # Use bcrypt directly to avoid passlib's password length check issues
            import bcrypt
            
            # Bcrypt has a 72-byte limit, so truncate if necessary
            password_bytes = plain_password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            
            # Verify using bcrypt directly
            result = bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
            print(f"Bcrypt direct verification result: {result}")
            return result
        except Exception as e:
            print(f"Bcrypt direct verification error: {str(e)}")
            # Fallback to passlib if bcrypt direct verification fails
            try:
                password_bytes = plain_password.encode('utf-8')
                if len(password_bytes) > 72:
                    password_bytes = password_bytes[:72]
                    plain_password = password_bytes.decode('utf-8', errors='ignore')
                result = pwd_context.verify(plain_password, hashed_password)
                print(f"Passlib fallback verification result: {result}")
                return result
            except Exception as fallback_error:
                print(f"Passlib fallback also failed: {str(fallback_error)}")
                return False
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password with bcrypt (72-byte limit handling)"""
        try:
            # Bcrypt has a 72-byte limit, so truncate if necessary
            # Use bcrypt directly to have better control over truncation
            import bcrypt
            
            # Encode to bytes to check length
            password_bytes = password.encode('utf-8')
            
            # Truncate to 72 bytes if necessary (bcrypt's limit)
            if len(password_bytes) > 72:
                # Truncate to 72 bytes, ensuring we don't break UTF-8 sequences
                truncated_bytes = password_bytes[:72]
                # Remove any incomplete UTF-8 sequences at the end
                while truncated_bytes and truncated_bytes[-1] & 0x80 and not (truncated_bytes[-1] & 0x40):
                    truncated_bytes = truncated_bytes[:-1]
                # Use truncated password for hashing
                password_bytes = truncated_bytes
            
            # Hash using bcrypt directly (more reliable than passlib for long passwords)
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt)
            return hashed.decode('utf-8')
        except Exception as e:
            # Fallback to passlib if bcrypt direct hashing fails
            try:
                # Ensure password is within 72 bytes for passlib
                password_bytes = password.encode('utf-8')
                if len(password_bytes) > 72:
                    truncated_bytes = password_bytes[:72]
                    while truncated_bytes and truncated_bytes[-1] & 0x80 and not (truncated_bytes[-1] & 0x40):
                        truncated_bytes = truncated_bytes[:-1]
                    password = truncated_bytes.decode('utf-8', errors='ignore')
                return pwd_context.hash(password)
            except Exception as fallback_error:
                print(f"Password hashing error (both bcrypt and passlib failed): {str(e)}, fallback: {str(fallback_error)}")
                raise ValueError(f"Password is too long. Maximum length is 72 bytes. Please use a shorter password.")
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def create_session_tokens(self, user_id: int, email: str, user_role: str = None) -> Dict[str, str]:
        """Create both access and refresh tokens for a user session"""
        data = {"sub": str(user_id), "email": email}
        if user_role:
            data["role"] = user_role
        
        access_token = self.create_access_token(data)
        refresh_token = self.create_refresh_token(data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """Create a new access token using a refresh token"""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            user_id = payload.get("sub")
            email = payload.get("email")
            user_role = payload.get("role")
            
            if not all([user_id, email]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            # Create new access token
            token_data = {"sub": user_id, "email": email}
            if user_role:
                token_data["role"] = user_role
            new_access_token = self.create_access_token(token_data)
            
            return {
                "access_token": new_access_token,
                "token_type": "bearer"
            }
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    def generate_verification_code(self) -> str:
        """Generate a verification code for email verification"""
        return secrets.token_urlsafe(6).upper()[:6]
    
    def generate_password_reset_token(self, email: str) -> str:
        """Generate a password reset token"""
        data = {"email": email, "type": "password_reset"}
        expire = datetime.utcnow() + timedelta(hours=24)
        data.update({"exp": expire})
        return jwt.encode(data, self.secret_key, algorithm=self.algorithm)
    
    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """Verify a password reset token and return the email"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "password_reset":
                return None
            return payload.get("email")
        except JWTError:
            return None


class SubscriptionService:
    """Subscription management service according to the roadmap"""
    
    def __init__(self):
        self.subscription_plans = {
            "basic": {
                "name": "Basic Plan",
                "monthly_price": 999.00,
                "description": "Access to valuation engine and market comparables",
                "monthly_valuations_limit": 50,
                "monthly_api_calls_limit": 0,
                "has_deal_score": False,
                "has_portfolio_analysis": False,
                "has_api_access": False,
                "features": ["Basic valuation", "Market comparables", "Email support"]
            },
            "pro": {
                "name": "Pro Plan",
                "monthly_price": 2499.00,
                "description": "Advanced features including Deal Score, portfolio analysis, and API access",
                "monthly_valuations_limit": 200,
                "monthly_api_calls_limit": 1000,
                "has_deal_score": True,
                "has_portfolio_analysis": True,
                "has_api_access": True,
                "features": ["Pro valuation", "Deal scoring", "Portfolio analysis", "API access", "Phone support"]
            },
        }
    
    def get_subscription_plan(self, tier: str) -> Optional[Dict[str, Any]]:
        """Get subscription plan details by tier"""
        return self.subscription_plans.get(tier.lower())
    
    def get_all_plans(self) -> Dict[str, Any]:
        """Get all available subscription plans"""
        return self.subscription_plans
    
    def can_access_feature(self, user_tier: str, feature: str) -> bool:
        """Check if a user can access a specific feature based on their subscription tier"""
        plan = self.get_subscription_plan(user_tier)
        if not plan:
            return False
        
        feature_access = {
            "deal_score": plan.get("has_deal_score", False),
            "portfolio_analysis": plan.get("has_portfolio_analysis", False),
            "api_access": plan.get("has_api_access", False),
            "priority_support": plan.get("has_priority_support", False)
        }
        
        return feature_access.get(feature, False)
    
    def get_usage_limits(self, user_tier: str) -> Dict[str, Any]:
        """Get usage limits for a subscription tier"""
        plan = self.get_subscription_plan(user_tier)
        if not plan:
            return {}
        
        return {
            "monthly_valuations_limit": plan.get("monthly_valuations_limit"),
            "monthly_api_calls_limit": plan.get("monthly_api_calls_limit")
        }


# Dependency functions for FastAPI
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token"""
    auth_service = AuthService()
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    
    # In a real implementation, you would fetch user from database here
    # For now, we'll return the payload
    return payload


async def require_subscription_tier(required_tier: str, current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require a specific subscription tier to access an endpoint"""
    user_tier = current_user.get("subscription_tier", "basic")
    
    # Define tier hierarchy
    tier_hierarchy = {"free": 1, "spot_check": 2, "professional": 3, "fleet_valuation": 4}
    
    if tier_hierarchy.get(user_tier, 0) < tier_hierarchy.get(required_tier, 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This feature requires {required_tier.title()} subscription or higher"
        )
    
    return current_user


async def require_api_access(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require API access (not available in current tiers)"""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="API access is not available in current subscription tiers"
    )


async def require_portfolio_analysis(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require portfolio analysis access (Fleet Valuation tier)"""
    return await require_subscription_tier("fleet_valuation", current_user)


# Global instances
auth_service = AuthService()
# SubscriptionService removed - subscription logic removed from platform
# subscription_service = SubscriptionService()  # DEPRECATED
