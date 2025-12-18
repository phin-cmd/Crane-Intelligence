"""
Crane Intelligence Platform - Simplified Authentication API
This is a simplified version to get login/signup working immediately
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta

from ...services.auth_service import auth_service
from ...services.brevo_email_service import BrevoEmailService
from ...models.user import User, UserRole, EmailVerificationToken
from ...core.database import get_db
from ...core.config import settings
import secrets
import logging

logger = logging.getLogger(__name__)

# Function to get fresh Brevo email service instance
# This ensures we always read the latest API key from environment
def get_brevo_email_service():
    """Get a fresh BrevoEmailService instance to ensure it reads the latest API key"""
    try:
        service = BrevoEmailService()
        if not service.api_key:
            logger.warning("⚠️ WARNING: Brevo API key not configured! Email sending will fail.")
            logger.warning("⚠️ Set BREVO_API_KEY environment variable or add to .env file and restart the server.")
        return service
    except Exception as e:
        logger.error(f"Failed to initialize Brevo email service: {e}", exc_info=True)
        return None

# Initialize for module-level checks (but use get_brevo_email_service() in endpoints)
brevo_email_service = get_brevo_email_service()
if brevo_email_service and brevo_email_service.api_key:
    logger.info("✓ Brevo email service initialized successfully")
    print("✓ Brevo email service initialized")
else:
    logger.warning("⚠️ WARNING: Brevo API key not configured! Email sending will fail.")
    print("⚠️ WARNING: BREVO_API_KEY environment variable is not set. Email verification emails will not be sent.")

router = APIRouter()

class AuthRequest(BaseModel):
    email: EmailStr
    password: str
    user_role: str = "others"  # Default to "others" if not provided
    full_name: str = None
    username: str = None
    company_name: str = None

class AuthResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any] = None
    error: str = None

@router.post("/login", response_model=AuthResponse)
async def login(request: AuthRequest, db: Session = Depends(get_db)):
    """User login endpoint"""
    try:
        print(f"Login attempt for: {request.email}")
        
        # Find user
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            print(f"User not found: {request.email}")
            return AuthResponse(
                success=False,
                message="Login failed",
                error="Invalid email or password"
            )
        
        print(f"User found: {user.email}, verified: {user.is_verified}, active: {user.is_active}")
        
        # Verify password
        if not auth_service.verify_password(request.password, user.hashed_password):
            print("Password verification failed")
            return AuthResponse(
                success=False,
                message="Login failed",
                error="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            print("User account is inactive")
            return AuthResponse(
                success=False,
                message="Login failed",
                error="Account is deactivated"
            )
        
        # CRITICAL: Check if account is verified - STRICT ENFORCEMENT
        if not user.is_verified:
            print(f"Login attempt blocked for unverified user: {user.email} (ID: {user.id})")
            return AuthResponse(
                success=False,
                message="Email verification required",
                error="Please verify your email address before logging in. Check your inbox for verification instructions. If you didn't receive the email, you can request a new verification email."
            )
        
        # Create notification for successful login (if first login after verification)
        try:
            from ...models.notification import UserNotification
            # Check if user has any notifications - if not, create a welcome notification
            existing_notifications = db.query(UserNotification).filter(
                UserNotification.user_id == user.id
            ).count()
            
            if existing_notifications == 0:
                # User has no notifications, create welcome notification
                welcome_notification = UserNotification(
                    user_id=user.id,
                    title="Welcome to Crane Intelligence! 🎉",
                    message=f"Welcome {user.full_name or user.username}! Your account is ready. Start by exploring our FMV report generation tools.",
                    type="welcome",
                    read=False
                )
                db.add(welcome_notification)
                db.commit()
                logger.info(f"✅ Created welcome notification for user {user.id} on first login")
        except Exception as notif_error:
            logger.warning(f"⚠️ Failed to create login notification: {notif_error}", exc_info=True)
            db.rollback()
        
        # Create session tokens
        tokens = auth_service.create_session_tokens(
            user_id=user.id,
            email=user.email,
            user_role=user.user_role.value
        )
        
        print(f"Tokens created successfully")
        
        return AuthResponse(
            success=True,
            message="Welcome back! You've successfully logged in.",
            data={
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "user_role": user.user_role.value if user.user_role else "user",
                    "total_payments": float(user.total_payments) if hasattr(user, 'total_payments') else 0.0
                },
                "tokens": tokens
            }
        )
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return AuthResponse(
            success=False,
            message="Login failed",
            error="An error occurred during login"
        )

@router.post("/signup", response_model=AuthResponse)
async def signup(request: AuthRequest, db: Session = Depends(get_db)):
    """User signup endpoint"""
    try:
        print(f"Signup attempt for: {request.email}")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            print(f"User already exists: {request.email}")
            return AuthResponse(
                success=False,
                message="Signup failed",
                error="Email already registered"
            )
        
        # Map user_role string to UserRole enum
        role_mapping = {
            "crane_rental_company": UserRole.CRANE_RENTAL_COMPANY,
            "equipment_dealer": UserRole.EQUIPMENT_DEALER,
            "financial_institution": UserRole.FINANCIAL_INSTITUTION,
            "others": UserRole.OTHERS
        }
        selected_role = role_mapping.get(request.user_role.lower() if request.user_role else "others", UserRole.OTHERS)
        
        # Create new user with all required fields
        new_user = User(
            email=request.email,
            hashed_password=auth_service.get_password_hash(request.password),
            full_name=request.full_name if hasattr(request, 'full_name') and request.full_name else request.email.split('@')[0],
            username=request.username if hasattr(request, 'username') and request.username else request.email.split('@')[0],
            company_name=request.company_name if hasattr(request, 'company_name') and request.company_name else "",
            user_role=selected_role,  # Use role from request or default to OTHERS
            is_active=True,
            is_verified=False,  # Requires email verification - DO NOT BYPASS
            total_payments=0.0  # Start with no payments
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"User created successfully: {new_user.email}")
        
        # Generate email verification token
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
        if not email_service:
            logger.error(f"CRITICAL: Brevo email service not initialized! Cannot send verification email to {new_user.email}")
            print(f"✗ CRITICAL: Brevo email service not initialized")
            email_error_details = "Email service not configured"
        elif not email_service.api_key:
            logger.error(f"CRITICAL: BREVO_API_KEY not configured. Cannot send verification email to {new_user.email}")
            logger.error(f"Please set BREVO_API_KEY environment variable or add to .env file and restart the server.")
            print(f"✗ CRITICAL: Brevo API key not configured")
            email_error_details = "Brevo API key not configured"
        else:
            email_sent = False
            email_error_details = None
            try:
                logger.info(f"Attempting to send verification email to {new_user.email} using Brevo API")
                print(f"📧 Attempting to send verification email to {new_user.email}")
                print(f"📧 Brevo API key configured: {bool(email_service.api_key)}")
                print(f"📧 From email: {email_service.from_email}")
                
                verification_email_result = email_service.send_template_email(
                    to_emails=[new_user.email],
                    template_name="email_verification.html",
                    template_context=verification_email_context,
                    subject=f"Verify Your Email Address - {settings.app_name}",
                    tags=["email-verification", "registration", "signup"]
                )
                
                logger.info(f"Brevo API response for {new_user.email}: {verification_email_result}")
                print(f"Brevo API response: {verification_email_result}")
                
                if verification_email_result.get("success"):
                    email_sent = True
                    logger.info(f"✓ Email verification email sent successfully to {new_user.email} (User ID: {new_user.id})")
                    print(f"✓ Verification email sent to {new_user.email}")
                else:
                    error_msg = verification_email_result.get('message', 'Unknown error')
                    status_code = verification_email_result.get('status_code', 'N/A')
                    logger.error(f"CRITICAL: Failed to send email verification email to {new_user.email}: {error_msg} (Status: {status_code})")
                    logger.error(f"User {new_user.id} ({new_user.email}) registered but verification email failed. Token: {verification_token}")
                    logger.error(f"Full Brevo response: {verification_email_result}")
                    print(f"✗ Failed to send verification email: {error_msg} (Status: {status_code})")
                    email_error_details = f"{error_msg} (Status: {status_code})"
            except Exception as email_error:
                logger.error(f"CRITICAL: Exception while sending verification email to {new_user.email}: {email_error}", exc_info=True)
                logger.error(f"User {new_user.id} ({new_user.email}) registered but verification email exception. Token: {verification_token}")
                print(f"✗ Exception sending verification email: {email_error}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                email_error_details = str(email_error)
        
        # Set email_sent and email_error_details if service was not available
        if not email_service or not email_service.api_key:
            email_sent = False
        
        # Welcome email will be sent AFTER email verification (in verify-email endpoint)
        # Do NOT send welcome email here - wait for email verification
        
        # Send admin notification about new user signup (email + in-app notification)
        admin_email_service = get_brevo_email_service()
        if admin_email_service and admin_email_service.api_key:
            try:
                from ...models.admin import Notification
                from sqlalchemy import text
                
                # Use raw SQL to avoid schema mismatch issues with AdminUser model
                try:
                    admin_users_result = db.execute(text("""
                        SELECT id, email, full_name, username 
                        FROM admin_users 
                        WHERE is_active = true AND is_verified = true
                    """))
                    admin_users_data = admin_users_result.fetchall()
                    admin_users = []
                    for row in admin_users_data:
                        # Create a simple object with the needed attributes
                        admin_obj = type('AdminUser', (), {
                            'id': row[0],
                            'email': row[1],
                            'full_name': row[2] if len(row) > 2 and row[2] else None,
                            'username': row[3] if len(row) > 3 and row[3] else None
                        })()
                        admin_users.append(admin_obj)
                except Exception as sql_error:
                    logger.warning(f"Failed to query admin users with raw SQL, trying ORM: {sql_error}")
                    # Fallback to ORM query
                    from ...models.admin import AdminUser
                    admin_users = db.query(AdminUser).filter(
                        AdminUser.is_active == True,
                        AdminUser.is_verified == True
                    ).all()
                
                if admin_users:
                    admin_emails = [admin.email for admin in admin_users]
                    admin_notification_context = {
                        "new_user_name": new_user.full_name,
                        "new_user_email": new_user.email,
                        "new_user_role": new_user.user_role.value if new_user.user_role else "user",
                        "signup_date": datetime.utcnow().strftime('%B %d, %Y at %I:%M %p'),
                        "platform_name": settings.app_name,
                        "admin_dashboard_url": f"{settings.admin_url or settings.frontend_url}/admin/users.html"
                    }
                    admin_email_result = admin_email_service.send_template_email(
                        to_emails=admin_emails,
                        template_name="admin_new_user_alert.html",
                        template_context=admin_notification_context,
                        subject=f"New User Registration - {new_user.email}",
                        tags=["admin-notification", "new-user", "signup"]
                    )
                    if admin_email_result.get("success"):
                        logger.info(f"✓ Admin notification email sent to {len(admin_emails)} admin(s) for new user {new_user.email}")
                    else:
                        logger.error(f"✗ Failed to send admin notification email: {admin_email_result.get('message', 'Unknown error')}")
                    
                    # Create in-app admin notifications for all active admins
                    try:
                        for admin in admin_users:
                            admin_notification = Notification(
                                admin_user_id=admin.id,
                                notification_type="new_user_signup",
                                title="New User Registration",
                                message=f"New user {new_user.full_name or new_user.email} ({new_user.user_role.value if new_user.user_role else 'user'}) has registered.",
                                action_url=f"{settings.admin_url or settings.frontend_url}/admin/users.html",
                                action_text="View User",
                                is_read=False
                            )
                            db.add(admin_notification)
                        db.commit()
                        logger.info(f"✅ Created in-app admin notifications for {len(admin_users)} admin(s) for new user {new_user.email}")
                    except Exception as notif_error:
                        logger.warning(f"Failed to create in-app admin notifications: {notif_error}", exc_info=True)
                        db.rollback()
            except Exception as admin_notif_error:
                logger.warning(f"Failed to send admin notification: {admin_notif_error}", exc_info=True)
        
        # Create user notification record
        try:
            from ...models.notification import UserNotification
            notification = UserNotification(
                user_id=new_user.id,
                title="Welcome to Crane Intelligence! 🎉",
                message="Thank you for joining us. Please verify your email to get started. Check your inbox for the verification email.",
                type="welcome",  # Use 'type' not 'notification_type'
                read=False  # Use 'read' not 'is_read'
            )
            db.add(notification)
            db.commit()
            logger.info(f"✅ Created welcome notification for new user {new_user.id} ({new_user.email})")
        except Exception as notif_error:
            logger.error(f"❌ Failed to create welcome notification for user {new_user.id}: {notif_error}", exc_info=True)
            db.rollback()
        
        # Build response message based on email sending status
        if email_sent:
            response_message = "Account created successfully! Please check your email inbox for verification instructions. You must verify your email before you can log in."
        else:
            # Provide helpful error message
            if email_error_details:
                response_message = f"Account created, but we couldn't send the verification email ({email_error_details}). Please contact support at {settings.mail_from_email} or use the resend verification feature."
            else:
                response_message = f"Account created, but we couldn't send the verification email. Please contact support at {settings.mail_from_email} or use the resend verification feature."
            logger.warning(f"User {new_user.id} ({new_user.email}) registered but email not sent. Error: {email_error_details}. Token: {verification_token}")
            # Also log the verification link for admin debugging
            logger.warning(f"Verification link for {new_user.email}: {verification_link}")
            print(f"⚠️ WARNING: Verification email not sent to {new_user.email}. Link: {verification_link}")
        
        return AuthResponse(
            success=True,
            message=response_message,
            data={
                "user": {
                    "id": new_user.id,
                    "email": new_user.email,
                    "username": new_user.username,
                    "full_name": new_user.full_name,
                    "user_role": new_user.user_role.value if new_user.user_role else "user",
                    "total_payments": float(new_user.total_payments) if hasattr(new_user, 'total_payments') else 0.0
                },
                "email_verification_required": True,
                "email_sent": email_sent
            }
        )
        
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return AuthResponse(
            success=False,
            message="Signup failed",
            error=f"An error occurred during signup: {str(e)}"
        )

# Add the missing get_current_user function
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return {
            "id": int(user_id),
            "email": email,
            "role": payload.get("role")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

class EmailVerificationRequest(BaseModel):
    token: str

@router.get("/test-email-config", response_model=Dict[str, Any])
async def test_email_config():
    """Test endpoint to check email configuration (for debugging)"""
    try:
        config_status = {
            "brevo_service_initialized": brevo_email_service is not None,
            "brevo_api_key_configured": bool(settings.brevo_api_key),
            "brevo_api_key_length": len(settings.brevo_api_key) if settings.brevo_api_key else 0,
            "from_email": settings.mail_from_email,
            "from_name": settings.mail_from_name,
            "template_dir": settings.email_templates_dir,
            "template_exists": False,
            "service_api_key_set": False
        }
        
        if brevo_email_service:
            config_status["service_api_key_set"] = bool(get_brevo_email_service().api_key)
            config_status["service_from_email"] = get_brevo_email_service().from_email
        
        # Check if template exists
        from pathlib import Path
        template_path = Path(settings.email_templates_dir) / "email_verification.html"
        config_status["template_exists"] = template_path.exists()
        config_status["template_path"] = str(template_path)
        
        return {
            "success": True,
            "config": config_status,
            "message": "Email configuration check completed"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to check email configuration"
        }


@router.get("/test-email-config")
async def test_email_config():
    """Test endpoint to check email configuration (for debugging)"""
    try:
        from pathlib import Path
        
        config_status = {
            "brevo_service_initialized": brevo_email_service is not None,
            "brevo_api_key_configured": bool(settings.brevo_api_key),
            "brevo_api_key_length": len(settings.brevo_api_key) if settings.brevo_api_key else 0,
            "from_email": settings.mail_from_email,
            "from_name": settings.mail_from_name,
            "template_dir": settings.email_templates_dir,
            "template_exists": False,
            "service_api_key_set": False
        }
        
        if brevo_email_service:
            config_status["service_api_key_set"] = bool(get_brevo_email_service().api_key)
            config_status["service_from_email"] = get_brevo_email_service().from_email
        
        # Check if template exists
        template_path = Path(settings.email_templates_dir) / "email_verification.html"
        config_status["template_exists"] = template_path.exists()
        config_status["template_path"] = str(template_path)
        
        return {
            "success": True,
            "config": config_status,
            "message": "Email configuration check completed"
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "message": "Failed to check email configuration"
        }


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
        db.refresh(user)
        
        logger.info(f"✓ Email verified successfully for user {user.email} (User ID: {user.id})")
        print(f"✓ Email verified for {user.email}")
        
        # Create notification for email verification success
        try:
            from ...models.notification import UserNotification
            verification_notification = UserNotification(
                user_id=user.id,
                title="Email Verified Successfully! ✅",
                message="Your email has been verified. You can now access all features of Crane Intelligence.",
                type="email_verification",
                read=False
            )
            db.add(verification_notification)
            db.commit()
            logger.info(f"✅ Created email verification notification for user {user.id}")
        except Exception as notif_error:
            logger.error(f"❌ Failed to create email verification notification: {notif_error}", exc_info=True)
            db.rollback()
        
        # Send welcome email AFTER email verification
        # brevo_email_service is available at module level
        if brevo_email_service and get_brevo_email_service().api_key:
            try:
                first_name = user.full_name.split()[0] if user.full_name else user.username
                welcome_email_context = {
                    "username": user.username,
                    "user_name": user.full_name,
                    "first_name": first_name,
                    "user_email": user.email,
                    "platform_name": settings.app_name,
                    "support_email": settings.mail_from_email,
                    "dashboard_url": f"{settings.frontend_url}/dashboard.html",
                    "report_generation_url": f"{settings.frontend_url}/report-generation.html",
                    "action_text": "Get Professional FMV Report",
                    "action_url": f"{settings.frontend_url}/report-generation.html"
                }
                get_brevo_email_service().send_template_email(
                    to_emails=[user.email],
                    template_name="welcome_email.html",
                    template_context=welcome_email_context,
                    subject=f"Welcome to {settings.app_name}!",
                    tags=["welcome", "registration", "email-verified"]
                )
                logger.info(f"✓ Welcome email sent to {user.email} after email verification")
            except Exception as welcome_error:
                logger.warning(f"Failed to send welcome email: {welcome_error}")
        
        # Send admin notification about email verification (user is now verified)
        if brevo_email_service and get_brevo_email_service().api_key:
            try:
                from ...models.admin import AdminUser
                admin_users = db.query(AdminUser).filter(
                    AdminUser.is_active == True,
                    AdminUser.is_verified == True
                ).all()
                
                if admin_users:
                    admin_emails = [admin.email for admin in admin_users]
                    first_name = user.full_name.split()[0] if user.full_name else user.username
                    admin_welcome_context = {
                        "new_user_name": user.full_name,
                        "new_user_email": user.email,
                        "new_user_role": user.user_role.value if user.user_role else "user",
                        "verification_date": datetime.utcnow().strftime('%B %d, %Y at %I:%M %p'),
                        "platform_name": settings.app_name,
                        "admin_dashboard_url": f"{settings.admin_url or settings.frontend_url}/admin/users.html"
                    }
                    admin_welcome_result = get_brevo_email_service().send_template_email(
                        to_emails=admin_emails,
                        template_name="admin_new_user_alert.html",
                        template_context=admin_welcome_context,
                        subject=f"User Email Verified - {user.email}",
                        tags=["admin-notification", "email-verified", "welcome"]
                    )
                    if admin_welcome_result.get("success"):
                        logger.info(f"✓ Admin welcome notification sent to {len(admin_emails)} admin(s) for verified user {user.email}")
                    else:
                        logger.error(f"✗ Failed to send admin welcome notification: {admin_welcome_result.get('message', 'Unknown error')}")
            except Exception as admin_welcome_error:
                logger.error(f"Failed to send admin welcome notification: {admin_welcome_error}", exc_info=True)
        
        return AuthResponse(
            success=True,
            message="Email verified successfully! You can now log in to your account.",
            data={
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "user_role": user.user_role.value if user.user_role else "others",
                    "is_verified": user.is_verified
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error verifying email: {str(e)}", exc_info=True)
        print(f"Verify email error: {str(e)}")
        return AuthResponse(
            success=False,
            message="Email verification failed",
            error=f"An error occurred during email verification: {str(e)}"
        )

@router.post("/resend-verification", response_model=AuthResponse)
async def resend_verification_email(request: AuthRequest, db: Session = Depends(get_db)):
    """Resend email verification email to user"""
    try:
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            return AuthResponse(
                success=False,
                message="User not found",
                error="No account found with this email address"
            )
        
        # Check if already verified
        if user.is_verified:
            return AuthResponse(
                success=True,
                message="Email already verified",
                data={"user": {"id": user.id, "email": user.email, "is_verified": True}}
            )
        
        # Generate new verification token
        verification_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        # Invalidate old tokens
        old_tokens = db.query(EmailVerificationToken).filter(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.used == False
        ).all()
        for old_token in old_tokens:
            old_token.used = True
        db.commit()
        
        # Create new verification token record
        verification_token_record = EmailVerificationToken(
            user_id=user.id,
            token=verification_token,
            expires_at=expires_at
        )
        db.add(verification_token_record)
        db.commit()
        
        # Send verification email
        verification_link = f"{settings.frontend_url}/verify-email.html?token={verification_token}"
        first_name = user.full_name.split()[0] if user.full_name else user.username
        
        verification_email_context = {
            "username": user.username,
            "user_name": user.full_name,
            "first_name": first_name,
            "user_email": user.email,
            "verification_link": verification_link,
            "verification_token": verification_token,
            "expiry_days": 1,
            "platform_name": settings.app_name,
            "support_email": settings.mail_from_email
        }
        
        email_sent = False
        if brevo_email_service and get_brevo_email_service().api_key:
            try:
                verification_email_result = get_brevo_email_service().send_template_email(
                    to_emails=[user.email],
                    template_name="email_verification.html",
                    template_context=verification_email_context,
                    subject=f"Verify Your Email Address - {settings.app_name}",
                    tags=["email-verification", "resend"]
                )
                
                if verification_email_result.get("success"):
                    email_sent = True
                    logger.info(f"✓ Verification email resent successfully to {user.email} (User ID: {user.id})")
                    print(f"✓ Verification email resent to {user.email}")
                else:
                    error_msg = verification_email_result.get('message', 'Unknown error')
                    logger.error(f"Failed to resend verification email to {user.email}: {error_msg}")
                    print(f"✗ Failed to resend verification email: {error_msg}")
            except Exception as email_error:
                logger.error(f"Exception while resending verification email to {user.email}: {email_error}", exc_info=True)
                print(f"✗ Exception resending verification email: {email_error}")
        
        if email_sent:
            return AuthResponse(
                success=True,
                message="Verification email sent successfully. Please check your inbox (and spam folder).",
                data={
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "is_verified": False
                    }
                }
            )
        else:
            return AuthResponse(
                success=False,
                message="Failed to send verification email",
                error="Please try again later or contact support"
            )
            
    except Exception as e:
        logger.error(f"Error resending verification email: {e}", exc_info=True)
        return AuthResponse(
            success=False,
            message="Failed to resend verification email",
            error=str(e)
        )


@router.get("/profile", response_model=AuthResponse)
async def get_profile(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    try:
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user from database
        user = db.query(User).filter(User.id == int(user_id)).first()
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
                    "user_role": user.user_role.value if user.user_role else "others",
                    "total_payments": float(user.total_payments) if hasattr(user, 'total_payments') else 0.0,
                    "company_name": user.company_name if hasattr(user, 'company_name') else ""
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        return AuthResponse(
            success=False,
            message="Failed to retrieve profile",
            error=str(e)
        )
