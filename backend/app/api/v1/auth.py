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
import logging
from datetime import datetime, timedelta

# Add the app directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ...services.auth_service import auth_service, get_current_user
from ...services.brevo_email_service import BrevoEmailService
from ...models.user import User, UserRole, UserSession, PasswordResetToken, EmailVerificationToken
from ...core.database import get_db, init_db
from ...core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme
security = HTTPBearer()

# Logger
logger = logging.getLogger(__name__)

# Initialize Brevo email service
# Note: This will read BREVO_API_KEY from environment or .env file
# We create a function to get a fresh instance to ensure it reads the latest API key
def get_brevo_email_service():
    """Get a fresh BrevoEmailService instance to ensure it reads the latest API key"""
    return BrevoEmailService()

brevo_email_service = get_brevo_email_service()
if not brevo_email_service.api_key:
    logger.warning("⚠️ BREVO_API_KEY not configured. Email sending will fail. Set BREVO_API_KEY environment variable or add to .env file.")


class UserRegistrationRequest(BaseModel):
    """User registration request model"""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password (min 8 characters, max 72 bytes)")
    full_name: str = Field(..., description="Full name")
    company_name: str = Field(..., description="Company name")
    user_role: UserRole = Field(..., description="User role based on target customers")


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


class EmailVerificationRequest(BaseModel):
    """Email verification request model"""
    token: str = Field(..., description="Email verification token")


class AuthResponse(BaseModel):
    """Authentication response model"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SubscriptionUpgradeRequest(BaseModel):
    """Subscription upgrade request model"""
    new_tier: str = Field(..., description="DEPRECATED - Subscription upgrade removed")


# Initialize database on startup (with error handling)
try:
    init_db()
except Exception as e:
    # Log but don't fail - database might not be available during import
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Could not initialize database during import: {e}. Database will be initialized on first use.")

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
                is_active=True,
                is_verified=True
            )
            db.add(demo_user)
        
        # REMOVED: Test user auto-creation with is_verified=True
        # This was causing users to bypass email verification requirements
        # All users must now go through the proper email verification flow
        # If you need test users, create them through the registration endpoint
        # which will properly send verification emails
        # test_user = db.query(User).filter(User.email == "kankanamitra01@gmail.com").first()
        # if not test_user:
        #     test_user = User(...)
        
        db.commit()
        print("SUCCESS: Demo users created successfully")
    except Exception as e:
        db.rollback()
        print(f"WARNING: Demo users creation failed: {e}")

# Create demo users on startup
try:
    from ...core.database import SessionLocal
    db = SessionLocal()
    create_demo_users(db)
    db.close()
except Exception as e:
    print(f"WARNING: Demo users creation failed: {e}")


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
        
        # Validate password length in bytes (bcrypt limit is 72 bytes)
        password_bytes = request.password.encode('utf-8')
        if len(password_bytes) > 72:
            return AuthResponse(
                success=False,
                message="Registration failed",
                error="Password is too long. Maximum length is 72 bytes. Please use a shorter password (approximately 72 characters for ASCII, fewer for Unicode characters)."
            )
        
        # Hash password with proper error handling
        try:
            hashed_password = auth_service.get_password_hash(request.password)
        except ValueError as e:
            # Handle password hashing errors with user-friendly message
            return AuthResponse(
                success=False,
                message="Registration failed",
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Password hashing error: {e}")
            return AuthResponse(
                success=False,
                message="Registration failed",
                error="An error occurred while processing your password. Please try again with a different password."
            )
        
        # Create new user
        new_user = User(
            email=request.email,
            username=request.username,
            hashed_password=hashed_password,
            full_name=request.full_name,
            company_name=request.company_name,
            user_role=request.user_role,
            is_active=True,
            is_verified=False  # Requires email verification
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create welcome notification for new user
        try:
            from ...models.notification import UserNotification
            welcome_notification = UserNotification(
                user_id=new_user.id,
                title="Welcome to Crane Intelligence! 🎉",
                message=f"Welcome {new_user.full_name or new_user.username}! Your account has been created successfully. Start by exploring our FMV report generation tools.",
                type="welcome",
                read=False
            )
            db.add(welcome_notification)
            db.commit()
            logger.info(f"✅ Created welcome notification for new user {new_user.id}")
        except Exception as notif_error:
            logger.warning(f"⚠️ Failed to create welcome notification for new user: {notif_error}", exc_info=True)
            db.rollback()
        
        # Generate email verification token
        import secrets
        verification_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
        
        # Create verification token record
        verification_token_record = EmailVerificationToken(
            user_id=new_user.id,
            token=verification_token,
            expires_at=expires_at
        )
        db.add(verification_token_record)
        db.commit()
        
        # Send email verification email via Brevo
        verification_link = f"{settings.frontend_url}/verify-email.html?token={verification_token}"
        # Extract first name from full_name
        first_name = new_user.full_name.split()[0] if new_user.full_name else new_user.username
        verification_email_context = {
            "username": new_user.username,
            "user_name": new_user.full_name,
            "first_name": first_name,
            "user_email": new_user.email,
            "verification_link": verification_link,
            "verification_token": verification_token,
            "expiry_days": 1,  # 24 hours = 1 day
            "platform_name": settings.app_name,
            "support_email": settings.mail_from_email
        }
        
        # Send email verification email - CRITICAL: This must succeed
        # Get fresh Brevo service instance to ensure API key is loaded
        email_service = get_brevo_email_service()
        if not email_service.api_key:
            logger.error(f"CRITICAL: BREVO_API_KEY not configured. Cannot send verification email to {new_user.email}")
            logger.error(f"Please set BREVO_API_KEY environment variable or add to .env file and restart the server.")
        
        email_sent = False
        try:
            verification_email_result = email_service.send_template_email(
                to_emails=[new_user.email],
                template_name="email_verification.html",
                template_context=verification_email_context,
                subject=f"Verify Your Email Address - {settings.app_name}",
                tags=["email-verification", "registration"]
            )
            
            if verification_email_result.get("success"):
                email_sent = True
                logger.info(f"✓ Email verification email sent successfully to {new_user.email} (User ID: {new_user.id})")
            else:
                error_msg = verification_email_result.get('message', 'Unknown error')
                logger.error(f"CRITICAL: Failed to send email verification email to {new_user.email}: {error_msg}")
                logger.error(f"User {new_user.id} ({new_user.email}) registered but verification email failed. Token: {verification_token}")
                logger.error(f"Verification link: {verification_link}")
        except Exception as email_error:
            logger.error(f"CRITICAL: Exception while sending verification email to {new_user.email}: {email_error}", exc_info=True)
            logger.error(f"User {new_user.id} ({new_user.email}) registered but verification email exception. Token: {verification_token}")
            logger.error(f"Verification link: {verification_link}")
        
        # Log verification token for debugging (only in development)
        if settings.debug:
            logger.info(f"DEBUG: Verification token for {new_user.email}: {verification_token}")
            logger.info(f"DEBUG: Verification link: {verification_link}")
        
        # Send welcome email via Brevo
        # Extract first name from full_name
        first_name = new_user.full_name.split()[0] if new_user.full_name else new_user.username
        email_context = {
            "username": new_user.username,
            "user_name": new_user.full_name,
            "first_name": first_name,
            "user_email": new_user.email,
            "account_type": new_user.user_role.value.replace("_", " ").title(),
            "registration_date": datetime.utcnow().strftime("%B %d, %Y"),
            "dashboard_url": f"{settings.frontend_url}/dashboard.html",
            "login_url": f"{settings.frontend_url}/login.html",
            "platform_name": settings.app_name,
            "support_email": settings.mail_from_email
        }
        
        welcome_email_result = brevo_email_service.send_template_email(
            to_emails=[new_user.email],
            template_name="user_registration.html",
            template_context=email_context,
            subject=f"Welcome to {settings.app_name}!",
            tags=["user-registration", "welcome"]
        )
        
        if not welcome_email_result.get("success"):
            logger.error(f"Failed to send welcome email: {welcome_email_result.get('message')}")
        
        # Send admin notification for new user registration
        try:
            from ...models.admin import AdminUser
            admin_users = db.query(AdminUser).filter(
                AdminUser.is_active == True,
                AdminUser.is_verified == True
            ).all()
            
            if admin_users:
                admin_emails = [admin.email for admin in admin_users]
                admin_notification_context = {
                    "user_name": new_user.full_name,
                    "user_email": new_user.email,
                    "username": new_user.username,
                    "company_name": new_user.company_name,
                    "registration_date": datetime.utcnow().strftime("%B %d, %Y at %I:%M %p"),
                    "account_type": new_user.user_role.value.replace("_", " ").title(),
                    "user_role": new_user.user_role.value.replace("_", " ").title(),
                    "admin_user_management_url": f"{settings.admin_url}/admin/users.html",
                    "platform_name": settings.app_name
                }
                
                admin_notification_result = brevo_email_service.send_template_email(
                    to_emails=admin_emails,
                    template_name="admin_user_registration.html",
                    template_context=admin_notification_context,
                    subject=f"New User Registration: {new_user.full_name}",
                    tags=["admin-notification", "user-registration"]
                )
                
                # Create admin notifications in bell for each admin user
                try:
                    from ...models.admin import Notification
                    for admin in admin_users:
                        admin_notification = Notification(
                            admin_user_id=admin.id,
                            notification_type="user_registration",
                            title=f"👤 New User Registration: {new_user.full_name}",
                            message=f"New user {new_user.full_name} ({new_user.email}) has registered on {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p')}.",
                            data={
                                "user_id": new_user.id,
                                "user_email": new_user.email,
                                "user_name": new_user.full_name,
                                "username": new_user.username,
                                "company_name": new_user.company_name,
                                "user_role": new_user.user_role.value if hasattr(new_user.user_role, 'value') else str(new_user.user_role),
                                "registration_date": datetime.utcnow().isoformat(),
                                "account_type": new_user.user_role.value.replace("_", " ").title() if hasattr(new_user.user_role, 'value') else str(new_user.user_role)
                            },
                            is_read=False
                        )
                        db.add(admin_notification)
                    db.commit()
                    logger.info(f"✅ Created admin notifications for new user registration: {new_user.email}")
                except Exception as admin_notif_error:
                    logger.warning(f"⚠️ Failed to create admin notifications in bell: {admin_notif_error}", exc_info=True)
                    db.rollback()
                
                if not admin_notification_result.get("success"):
                    logger.error(f"Failed to send admin notification: {admin_notification_result.get('message')}")
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}")
        
        # Build response message based on email sending status
        if email_sent:
            response_message = "Account created successfully! Please check your email inbox for verification instructions. You must verify your email before you can log in."
        else:
            response_message = f"Account created, but we couldn't send the verification email. Please contact support or use the resend verification feature. Your verification token is: {verification_token}"
            logger.warning(f"User {new_user.id} registered but email not sent - providing token in response for manual verification")
        
        return AuthResponse(
            success=True,
            message=response_message,
            data={
                "user_id": new_user.id,
                "email": new_user.email,
                "username": new_user.username,
                "email_verification_required": True,
                "email_sent": email_sent,
                "message": "Your account has been created. Please verify your email address to activate your account and start using the platform."
            }
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Registration exception for email {request.email}: {e}", exc_info=True)
        return AuthResponse(
            success=False,
            message="Registration failed",
            error="Unable to create account. Please try again or contact support if the problem persists."
        )


@router.post("/verify-email", response_model=AuthResponse)
async def verify_email(request: EmailVerificationRequest, db: Session = Depends(get_db)):
    """
    Verify user email address using verification token
    
    This endpoint verifies the user's email address and activates their account.
    """
    try:
        # Find the verification token
        verification_token_record = db.query(EmailVerificationToken).filter(
            EmailVerificationToken.token == request.token,
            EmailVerificationToken.used == False
        ).first()
        
        if not verification_token_record:
            return AuthResponse(
                success=False,
                message="Invalid verification token",
                error="The email verification link is invalid or has already been used. Please request a new verification email."
            )
        
        # Check if token is expired
        if verification_token_record.is_expired():
            # Mark token as used
            verification_token_record.used = True
            db.commit()
            
            return AuthResponse(
                success=False,
                message="Verification token has expired",
                error="The email verification link has expired. Please request a new verification email."
            )
        
        # Get the user
        user = db.query(User).filter(User.id == verification_token_record.user_id).first()
        if not user:
            return AuthResponse(
                success=False,
                message="User not found",
                error="The user associated with this verification token no longer exists."
            )
        
        # Verify the user's email
        user.is_verified = True
        
        # Mark token as used
        verification_token_record.used = True
        
        db.commit()
        
        # Send email verification success notification
        email_context = {
            "username": user.username or user.full_name,
            "user_email": user.email,
            "verification_date": datetime.utcnow().strftime("%B %d, %Y at %I:%M %p"),
            "login_url": f"{settings.frontend_url}/login.html",
            "dashboard_url": f"{settings.frontend_url}/dashboard.html",
            "platform_name": settings.app_name,
            "support_email": settings.mail_from_email
        }
        
        email_result = brevo_email_service.send_template_email(
            to_emails=[user.email],
            template_name="email_verification_success.html",
            template_context=email_context,
            subject="Email Verified Successfully - Crane Intelligence",
            tags=["email-verification", "success"]
        )
        
        if not email_result.get("success"):
            logger.error(f"Failed to send email verification success email: {email_result.get('message')}")
        
        return AuthResponse(
            success=True,
            message="Email address verified successfully! Your account is now active. You can now log in.",
            data={
                "user_id": user.id,
                "email": user.email,
                "is_verified": True,
                "login_url": f"{settings.frontend_url}/login.html"
            }
        )
        
    except Exception as e:
        logger.error(f"Error verifying email: {e}")
        return AuthResponse(
            success=False,
            message="Failed to verify email",
            error="An unexpected error occurred. Please try again later."
        )


@router.post("/resend-verification", response_model=AuthResponse)
async def resend_verification_email(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Resend email verification email
    
    This endpoint resends the email verification email to the user.
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user:
            # Don't reveal if email exists or not for security
            return AuthResponse(
                success=True,
                message="If an account with that email exists, a verification email has been sent."
            )
        
        # Check if already verified
        if user.is_verified:
            return AuthResponse(
                success=False,
                message="Email already verified",
                error="This email address has already been verified. You can log in to your account."
            )
        
        # Invalidate any existing unused verification tokens for this user
        db.query(EmailVerificationToken).filter(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.used == False
        ).update({"used": True})
        
        # Generate new verification token
        import secrets
        verification_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
        
        # Create new verification token record
        verification_token_record = EmailVerificationToken(
            user_id=user.id,
            token=verification_token,
            expires_at=expires_at
        )
        db.add(verification_token_record)
        db.commit()
        
        # Send email verification email via Brevo
        verification_link = f"{settings.frontend_url}/verify-email.html?token={verification_token}"
        # Extract first name from full_name
        first_name = user.full_name.split()[0] if user.full_name else user.username
        verification_email_context = {
            "username": user.username,
            "user_name": user.full_name,
            "first_name": first_name,
            "user_email": user.email,
            "verification_link": verification_link,
            "verification_token": verification_token,
            "expiry_days": 1,  # 24 hours = 1 day
            "platform_name": settings.app_name,
            "support_email": settings.mail_from_email
        }
        
        try:
            verification_email_result = brevo_email_service.send_template_email(
                to_emails=[user.email],
                template_name="email_verification.html",
                template_context=verification_email_context,
                subject=f"Verify Your Email Address - {settings.app_name}",
                tags=["email-verification", "resend"]
            )
            
            if not verification_email_result.get("success"):
                error_msg = verification_email_result.get('message', 'Unknown error')
                logger.error(f"CRITICAL: Failed to resend verification email to {user.email}: {error_msg}")
                return AuthResponse(
                    success=False,
                    message="Failed to send verification email",
                    error=f"Unable to send verification email. Please contact support at {settings.mail_from_email} for assistance."
                )
        except Exception as email_error:
            logger.error(f"CRITICAL: Exception while resending verification email to {user.email}: {email_error}", exc_info=True)
            return AuthResponse(
                success=False,
                message="Failed to send verification email",
                error=f"An error occurred while sending the verification email. Please contact support at {settings.mail_from_email} for assistance."
            )
        
        return AuthResponse(
            success=True,
            message="If an account with that email exists, a verification email has been sent."
        )
        
    except Exception as e:
        logger.error(f"Error resending verification email: {e}")
        return AuthResponse(
            success=False,
            message="Failed to resend verification email",
            error="An unexpected error occurred. Please try again later."
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
        
        # CRITICAL: Check if account is verified - STRICT ENFORCEMENT
        if not user.is_verified:
            logger.warning(f"Login attempt blocked for unverified user: {user.email} (ID: {user.id})")
            return AuthResponse(
                success=False,
                message="Email verification required",
                error="Please verify your email address before logging in. Check your inbox for verification instructions. If you didn't receive the email, you can request a new verification email."
            )
        
        # Create session tokens
        tokens = auth_service.create_session_tokens(
            user_id=user.id,
            email=user.email,
            user_role=user.user_role.value
        )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
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
                    "user_role": user.user_role.value
                },
                "tokens": tokens
            }
        )
        
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        return AuthResponse(
            success=False,
            message="Login failed",
            error="An error occurred during login"
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
    Send password reset email to user via Brevo
    
    This endpoint generates a password reset token and sends it via email.
    Includes rate limiting to prevent abuse.
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
        
        # Rate limiting: Check for recent password reset requests (last hour)
        recent_requests = db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.created_at >= datetime.utcnow() - timedelta(hours=1),
            PasswordResetToken.used == False
        ).count()
        
        if recent_requests >= 3:
            return AuthResponse(
                success=False,
                message="Too many password reset requests",
                error="Please wait before requesting another password reset. Check your email for the reset link."
            )
        
        # Generate reset token
        import secrets
        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
        
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
        
        # Send password reset email via Brevo
        reset_link = f"{settings.frontend_url}/reset-password.html?token={reset_token}"
        # Extract first name from full_name
        first_name = user.full_name.split()[0] if user.full_name else (user.username or "User")
        email_context = {
            "username": user.username or user.full_name,
            "user_name": user.full_name,
            "first_name": first_name,
            "user_email": user.email,
            "reset_link": reset_link,
            "expiry_hours": 24,
            "platform_name": settings.app_name,
            "support_email": settings.mail_from_email
        }
        
        email_result = brevo_email_service.send_template_email(
            to_emails=[user.email],
            template_name="password_reset.html",
            template_context=email_context,
            subject="Password Reset Request - Crane Intelligence",
            tags=["password-reset", "security"]
        )
        
        if not email_result.get("success"):
            logger.error(f"Failed to send password reset email: {email_result.get('message')}")
            # Still return success to user for security (don't reveal email issues)
        
        return AuthResponse(
            success=True,
            message="If an account with that email exists, a password reset link has been sent."
        )
        
    except Exception as e:
        logger.error(f"Error in forgot password: {e}")
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
        
        # Send password reset confirmation email via Brevo
        email_context = {
            "username": user.username or user.full_name,
            "user_email": user.email,
            "reset_timestamp": datetime.utcnow().strftime("%B %d, %Y at %I:%M %p"),
            "login_url": f"{settings.frontend_url}/login.html",
            "platform_name": settings.app_name,
            "support_email": settings.mail_from_email
        }
        
        email_result = brevo_email_service.send_template_email(
            to_emails=[user.email],
            template_name="password_reset_success.html",
            template_context=email_context,
            subject="Password Reset Successful - Crane Intelligence",
            tags=["password-reset", "security", "confirmation"]
        )
        
        if not email_result.get("success"):
            logger.error(f"Failed to send password reset confirmation email: {email_result.get('message')}")
        
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
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "total_payments": user.total_payments or 0
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
    """
    try:
        return AuthResponse(
            success=False,
            message="Subscription plans are no longer available",
            error="The platform now uses a pay-per-use model. Report types (Spot Check, Professional, Fleet Valuation) are available for purchase."
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
        
        # Subscription upgrade removed - pay-per-use model only
        return AuthResponse(
            success=False,
            message="Subscription upgrade is no longer available",
            error="The platform now uses a pay-per-use model. You can purchase reports (Spot Check, Professional, Fleet Valuation) as needed."
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
                "subscription_plans": 0  # Subscription plans removed
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
