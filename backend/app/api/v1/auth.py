"""
Crane Intelligence Platform - Authentication API Endpoints
Implements user authentication and subscription management for the MVP
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr
import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ...services.auth_service import auth_service, subscription_service, get_current_user
from ...models.user import User, UserRole, SubscriptionTier, UserSession, PasswordResetToken
from ...core.database import get_db, init_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme
security = HTTPBearer()


class UserRegistrationRequest(BaseModel):
    """User registration request model"""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    full_name: str = Field(..., description="Full name")
    company_name: str = Field(..., description="Company name")
    user_role: UserRole = Field(..., description="User role based on target customers")
    subscription_tier: SubscriptionTier = Field(default=SubscriptionTier.BASIC, description="Initial subscription tier")


class UserLoginRequest(BaseModel):
    """User login request model"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class PasswordResetRequest(BaseModel):
    """Password reset request model"""
    email: EmailStr = Field(..., description="User email address")


class TokenRefreshRequest(BaseModel):
    """Token refresh request model"""
    refresh_token: str = Field(..., description="Refresh token")


class ForgotPasswordRequest(BaseModel):
    """Forgot password request model"""
    email: EmailStr = Field(..., description="User email address")


class ResetPasswordRequest(BaseModel):
    """Reset password request model"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")


class PasswordResetConfirmRequest(BaseModel):
    """Password reset confirmation request model"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")


class AuthResponse(BaseModel):
    """Authentication response model"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SubscriptionUpgradeRequest(BaseModel):
    """Subscription upgrade request model"""
    new_tier: SubscriptionTier = Field(..., description="New subscription tier")


# Initialize database on startup
init_db()

def create_demo_users(db: Session):
    """Create demo users for testing"""
    try:
        # Check if demo user already exists
        demo_user = db.query(User).filter(User.email == "demo@craneintelligence.com").first()
        if not demo_user:
            demo_user = User(
                email="demo@craneintelligence.com",
                username="demo_user",
                hashed_password=auth_service.get_password_hash("DemoOnly123"),
                full_name="Demo User",
                company_name="Crane Intelligence Demo",
                user_role=UserRole.CRANE_RENTAL_COMPANY,
                subscription_tier=SubscriptionTier.PRO,
                is_active=True,
                is_verified=True,
                monthly_valuations_used=25,
                monthly_api_calls_used=150,
                subscription_start_date=datetime.utcnow(),
                subscription_end_date=datetime.utcnow() + timedelta(days=365)
            )
            db.add(demo_user)
        
        # Check if test user already exists
        test_user = db.query(User).filter(User.email == "kankanamitra01@gmail.com").first()
        if not test_user:
            test_user = User(
                email="kankanamitra01@gmail.com",
                username="kankanamitra",
                hashed_password=auth_service.get_password_hash("password123"),
                full_name="Kankana Mitra",
                company_name="Mitra Construction",
                user_role=UserRole.CRANE_RENTAL_COMPANY,
                subscription_tier=SubscriptionTier.BASIC,
                is_active=True,
                is_verified=True,
                monthly_valuations_used=5,
                monthly_api_calls_used=25,
                subscription_start_date=datetime.utcnow(),
                subscription_end_date=datetime.utcnow() + timedelta(days=30)
            )
            db.add(test_user)
        
        db.commit()
        print("✅ Demo users created successfully")
    except Exception as e:
        db.rollback()
        print(f"⚠️  Demo users creation failed: {e}")

# Create demo users on startup
try:
    from ...core.database import SessionLocal
    db = SessionLocal()
    create_demo_users(db)
    db.close()
except Exception as e:
    print(f"⚠️  Demo users creation failed: {e}")


@router.post("/register", response_model=AuthResponse)
async def register_user(request: UserRegistrationRequest, db: Session = Depends(get_db)):
    """
    Register a new user account
    
    This endpoint creates a new user account with the specified subscription tier.
    Target customers from the roadmap:
    - Crane Rental Companies
    - Equipment Dealers  
    - Financial Institutions
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            return AuthResponse(
                success=False,
                message="Registration failed",
                error="An account with this email address already exists. Please try logging in or use a different email."
            )
        
        # Check if username already exists
        existing_username = db.query(User).filter(User.username == request.username).first()
        if existing_username:
            return AuthResponse(
                success=False,
                message="Registration failed",
                error="This username is already taken. Please choose a different username."
            )
        
        # Create new user
        new_user = User(
            email=request.email,
            username=request.username,
            hashed_password=auth_service.get_password_hash(request.password),
            full_name=request.full_name,
            company_name=request.company_name,
            user_role=request.user_role,
            subscription_tier=request.subscription_tier,
            is_active=True,
            is_verified=False,  # Requires email verification
            monthly_valuations_used=0,
            monthly_api_calls_used=0,
            subscription_start_date=datetime.utcnow(),
            subscription_end_date=datetime.utcnow() + timedelta(days=30)  # 30-day trial
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate verification code (in production, send via email)
        verification_code = auth_service.generate_verification_code()
        
        return AuthResponse(
            success=True,
            message="Account created successfully! Welcome to Crane Intelligence. Please check your email for verification instructions.",
            data={
                "user_id": new_user.id,
                "email": new_user.email,
                "username": new_user.username,
                "subscription_tier": new_user.subscription_tier.value,
                "verification_code": verification_code,  # In production, this would be sent via email
                "message": "Your account has been created. Please verify your email address to activate your account and start using the platform."
            }
        )
        
    except Exception as e:
        db.rollback()
        return AuthResponse(
            success=False,
            message="Registration failed",
            error="Unable to create account. Please try again or contact support if the problem persists."
        )


@router.post("/login", response_model=AuthResponse)
async def login_user(request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and provide access tokens
    
    Returns JWT access and refresh tokens for authenticated users.
    Access is granted based on subscription tier and account status.
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user:
            return AuthResponse(
                success=False,
                message="Login failed",
                error="No account found with this email address. Please check your email or create a new account."
            )
        
        # Verify password
        if not auth_service.verify_password(request.password, user.hashed_password):
            return AuthResponse(
                success=False,
                message="Login failed",
                error="Incorrect password. Please try again or reset your password if you've forgotten it."
            )
        
        # Check if account is active
        if not user.is_active:
            return AuthResponse(
                success=False,
                message="Account suspended",
                error="Your account has been suspended. Please contact support for assistance."
            )
        
        # Check if account is verified
        if not user.is_verified:
            return AuthResponse(
                success=False,
                message="Email verification required",
                error="Please verify your email address before logging in. Check your inbox for verification instructions."
            )
        
        # Check subscription status
        if not user.subscription_is_active:
            return AuthResponse(
                success=False,
                message="Subscription expired",
                error="Your subscription has expired. Please renew your subscription to continue using the platform."
            )
        
        # Create session tokens
        tokens = auth_service.create_session_tokens(
            user_id=user.id,
            email=user.email,
            subscription_tier=user.subscription_tier.value
        )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Get subscription plan details
        subscription_plan = subscription_service.get_subscription_plan(user.subscription_tier.value)
        
        return AuthResponse(
            success=True,
            message="Welcome back! You've successfully logged in.",
            data={
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "company_name": user.company_name,
                    "user_role": user.user_role.value,
                    "subscription_tier": user.subscription_tier.value,
                    "subscription_plan": subscription_plan
                },
                "tokens": tokens,
                "usage": {
                    "monthly_valuations_used": user.monthly_valuations_used,
                    "monthly_api_calls_used": user.monthly_api_calls_used
                }
            }
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message="Login failed",
            error="An unexpected error occurred. Please try again or contact support if the problem persists."
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(request: TokenRefreshRequest):
    """
    Refresh access token using refresh token
    
    This endpoint allows users to get a new access token without re-authenticating.
    """
    try:
        # Refresh the access token
        new_tokens = auth_service.refresh_access_token(request.refresh_token)
        
        return AuthResponse(
            success=True,
            message="Token refreshed successfully",
            data=new_tokens
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message="Token refresh failed",
            error=str(e)
        )


@router.post("/logout", response_model=AuthResponse)
async def logout_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Logout user and invalidate session
    
    In production, this would invalidate the refresh token.
    """
    try:
        # In production, you would invalidate the refresh token in the database
        # For now, we'll just return success
        
        return AuthResponse(
            success=True,
            message="Logout successful"
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message="Logout failed",
            error=str(e)
        )


@router.post("/forgot-password", response_model=AuthResponse)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Send password reset email to user
    
    This endpoint generates a password reset token and sends it via email.
    In production, this would send an actual email.
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user:
            # Don't reveal if email exists or not for security
            return AuthResponse(
                success=True,
                message="If an account with that email exists, a password reset link has been sent."
            )
        
        # Generate reset token
        import secrets
        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
        
        # Invalidate any existing tokens for this user
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used == False
        ).update({"used": True})
        
        # Create new reset token
        reset_token_record = PasswordResetToken(
            user_id=user.id,
            token=reset_token,
            expires_at=expires_at
        )
        db.add(reset_token_record)
        db.commit()
        
        # In production, send email with reset link
        # For now, we'll return the token in the response for testing
        reset_link = f"http://localhost:3000/reset-password.html?token={reset_token}"
        
        return AuthResponse(
            success=True,
            message="Password reset link sent to your email address.",
            data={
                "reset_link": reset_link,  # Remove this in production
                "expires_at": expires_at.isoformat()
            }
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message="Failed to process password reset request",
            error="An unexpected error occurred. Please try again later."
        )


@router.post("/reset-password", response_model=AuthResponse)
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset user password using reset token
    
    This endpoint validates the reset token and updates the user's password.
    """
    try:
        # Find the reset token
        reset_token_record = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == request.token,
            PasswordResetToken.used == False
        ).first()
        
        if not reset_token_record:
            return AuthResponse(
                success=False,
                message="Invalid or expired reset token",
                error="The password reset link is invalid or has expired. Please request a new one."
            )
        
        # Check if token is expired
        if reset_token_record.is_expired():
            # Mark token as used
            reset_token_record.used = True
            db.commit()
            
            return AuthResponse(
                success=False,
                message="Reset token has expired",
                error="The password reset link has expired. Please request a new one."
            )
        
        # Get the user
        user = db.query(User).filter(User.id == reset_token_record.user_id).first()
        if not user:
            return AuthResponse(
                success=False,
                message="User not found",
                error="The user associated with this reset token no longer exists."
            )
        
        # Update password
        user.hashed_password = auth_service.get_password_hash(request.new_password)
        
        # Mark token as used
        reset_token_record.used = True
        
        db.commit()
        
        return AuthResponse(
            success=True,
            message="Password has been reset successfully. You can now log in with your new password."
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message="Failed to reset password",
            error="An unexpected error occurred. Please try again later."
        )


@router.post("/password-reset", response_model=AuthResponse)
async def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Request password reset
    
    Generates a password reset token and sends it via email.
    """
    try:
        # Check if user exists
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user:
            # Don't reveal if user exists or not for security
            return AuthResponse(
                success=True,
                message="If an account with this email address exists, you will receive password reset instructions shortly.",
                data={
                    "message": "Please check your email inbox and spam folder for password reset instructions. The link will expire in 24 hours."
                }
            )
        
        # Check if account is active
        if not user.is_active:
            return AuthResponse(
                success=False,
                message="Account suspended",
                error="Password reset is not available for suspended accounts. Please contact support for assistance."
            )
        
        # Generate password reset token
        reset_token = auth_service.generate_password_reset_token(request.email)
        
        # In production, send this token via email
        # For demo purposes, we'll return it in the response
        
        return AuthResponse(
            success=True,
            message="Password reset instructions sent to your email",
            data={
                "reset_token": reset_token,  # In production, this would be sent via email
                "message": "Please check your email inbox and spam folder for password reset instructions. The link will expire in 24 hours. If you don't receive the email, please contact support."
            }
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message="Password reset request failed",
            error="Unable to process password reset request. Please try again or contact support if the problem persists."
        )


@router.post("/password-reset/confirm", response_model=AuthResponse)
async def confirm_password_reset(request: PasswordResetConfirmRequest, db: Session = Depends(get_db)):
    """
    Confirm password reset with token
    
    Allows users to set a new password using the reset token.
    """
    try:
        # Verify the reset token
        email = auth_service.verify_password_reset_token(request.token)
        if not email:
            return AuthResponse(
                success=False,
                message="Password reset failed",
                error="Invalid or expired reset token. Please request a new password reset link."
            )
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return AuthResponse(
                success=False,
                message="Password reset failed",
                error="User account not found. Please contact support for assistance."
            )
        
        # Check if account is active
        if not user.is_active:
            return AuthResponse(
                success=False,
                message="Account suspended",
                error="Password reset is not available for suspended accounts. Please contact support for assistance."
            )
        
        # Update password
        user.hashed_password = auth_service.get_password_hash(request.new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        
        return AuthResponse(
            success=True,
            message="Password updated successfully! You can now log in with your new password.",
            data={
                "message": "Your password has been successfully updated. Please log in with your new password to access your account."
            }
        )
        
    except Exception as e:
        db.rollback()
        return AuthResponse(
            success=False,
            message="Password reset failed",
            error="Unable to update password. Please try again or contact support if the problem persists."
        )


@router.get("/profile", response_model=AuthResponse)
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get current user profile and subscription information
    
    Returns user details, subscription status, and usage information.
    """
    try:
        # Get user from database
        user_email = current_user.get("email")
        user = db.query(User).filter(User.email == user_email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        subscription_plan = subscription_service.get_subscription_plan(user.subscription_tier.value)
        
        return AuthResponse(
            success=True,
            message="Profile retrieved successfully",
            data={
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "company_name": user.company_name,
                    "user_role": user.user_role.value,
                    "subscription_tier": user.subscription_tier.value,
                    "subscription_plan": subscription_plan,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "subscription_start_date": user.subscription_start_date.isoformat() if user.subscription_start_date else None,
                    "subscription_end_date": user.subscription_end_date.isoformat() if user.subscription_end_date else None
                },
                "usage": {
                    "monthly_valuations_used": user.monthly_valuations_used,
                    "monthly_api_calls_used": user.monthly_api_calls_used
                }
            }
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message="Profile retrieval failed",
            error="Unable to retrieve profile information. Please try again or contact support if the problem persists."
        )


@router.get("/subscription/plans", response_model=AuthResponse)
async def get_subscription_plans():
    """
    Get available subscription plans
    
    Returns all subscription plans according to the roadmap:
    - Basic Plan: $999/month
    - Pro Plan: $2499/month  
    - Enterprise Plan: Custom pricing
    """
    try:
        plans = subscription_service.get_all_plans()
        
        return AuthResponse(
            success=True,
            message="Subscription plans retrieved successfully",
            data={"plans": plans}
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message="Failed to retrieve subscription plans",
            error=str(e)
        )


@router.post("/subscription/upgrade", response_model=AuthResponse)
async def upgrade_subscription(
    request: SubscriptionUpgradeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade user subscription tier
    
    Allows users to upgrade their subscription to access more features.
    """
    try:
        user_email = current_user.get("email")
        user = db.query(User).filter(User.email == user_email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        current_tier = user.subscription_tier
        new_tier = request.new_tier
        
        # Check if upgrade is valid
        tier_hierarchy = {SubscriptionTier.BASIC: 1, SubscriptionTier.PRO: 2, SubscriptionTier.ENTERPRISE: 3}
        
        if tier_hierarchy.get(new_tier, 0) <= tier_hierarchy.get(current_tier, 0):
            return AuthResponse(
                success=False,
                message="Subscription upgrade failed",
                error="You can only upgrade to a higher subscription tier. Please select a tier above your current plan."
            )
        
        # Update subscription tier
        user.subscription_tier = new_tier
        user.updated_at = datetime.utcnow()
        
        # Extend subscription end date
        if user.subscription_end_date:
            user.subscription_end_date = user.subscription_end_date + timedelta(days=30)
        else:
            user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
        
        db.commit()
        
        # Get new subscription plan details
        subscription_plan = subscription_service.get_subscription_plan(new_tier.value)
        
        return AuthResponse(
            success=True,
            message="Subscription upgraded successfully!",
            data={
                "old_tier": current_tier.value,
                "new_tier": new_tier.value,
                "subscription_plan": subscription_plan,
                "message": f"Congratulations! Your subscription has been upgraded to {new_tier.value.title()} tier. You now have access to additional features and higher usage limits."
            }
        )
        
    except Exception as e:
        db.rollback()
        return AuthResponse(
            success=False,
            message="Subscription upgrade failed",
            error="Unable to upgrade subscription. Please try again or contact support if the problem persists."
        )


@router.get("/health", response_model=AuthResponse)
async def auth_health_check():
    """
    Health check for authentication service
    
    Verifies that the authentication service is working properly.
    """
    try:
        # Test JWT token creation
        test_token = auth_service.create_access_token({"test": "data"})
        test_payload = auth_service.verify_token(test_token)
        
        return AuthResponse(
            success=True,
            message="Authentication service is healthy",
            data={
                "status": "healthy",
                "jwt_test": "passed",
                "subscription_plans": len(subscription_service.get_all_plans())
            }
        )
        
    except Exception as e:
        return AuthResponse(
            success=False,
            message="Authentication service health check failed",
            error=str(e)
        )


# Import datetime for the login endpoint
from datetime import datetime
