"""
Admin Authentication API endpoints
Separate from regular user authentication
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from ...core.database import get_db
from ...models.admin import AdminUser, AdminRole
from ...core.admin_auth import (
    get_current_admin_user,
    create_access_token,
    create_refresh_token,
    verify_token
)
from datetime import timedelta
from ...services.auth_service import auth_service
from ...services.brevo_email_service import BrevoEmailService
from ...core.config import settings
from ...core.admin_permissions import get_permissions_for_role, Permission

# Avoid importing User model here to prevent relationship initialization issues
# Only import AdminUser which doesn't have problematic relationships

router = APIRouter(prefix="/admin/auth", tags=["admin-auth"])

# Initialize Brevo email service
brevo_email_service = BrevoEmailService()

security = HTTPBearer()


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str
    two_factor_token: Optional[str] = None


class AdminLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes
    user: Dict[str, Any]


class AdminRefreshRequest(BaseModel):
    refresh_token: str


class AdminProfileResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    admin_role: str
    permissions: list
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    created_at: datetime


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    login_data: AdminLoginRequest,
    db: Session = Depends(get_db)
):
    """Admin login endpoint with 2FA support"""
    try:
        # Try to import TwoFactorService, but handle if pyotp is not available
        try:
            from ...services.two_factor_service import TwoFactorService
            two_factor_available = True
        except ImportError:
            logger.warning("TwoFactorService not available (pyotp not installed), proceeding without 2FA")
            two_factor_available = False
        
        # Find admin user
        # Handle case where database schema might be missing columns (e.g., two_factor_enabled)
        # Use a custom query that only selects columns that definitely exist
        from sqlalchemy import text
        try:
            # Try normal query first
            admin_user = db.query(AdminUser).filter(AdminUser.email == login_data.email).first()
        except Exception as db_error:
            # If query fails due to missing columns, rollback and use raw SQL
            logger.warning(f"AdminUser query failed (possible schema mismatch), using raw SQL: {db_error}")
            db.rollback()  # Rollback the failed transaction
            try:
                # Try querying with only essential columns first
                result = db.execute(
                    text("SELECT id, email, hashed_password, is_active, admin_role FROM admin_users WHERE email = :email"),
                    {"email": login_data.email}
                ).first()
                if not result:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid email or password"
                    )
                # Create a minimal admin user object
                class SimpleAdminUser:
                    def __init__(self, row):
                        self.id = row[0]
                        self.email = row[1]
                        self.hashed_password = row[2]
                        self.is_active = row[3]
                        self.admin_role = row[4]
                        # Set defaults for missing attributes
                        self.full_name = ''
                        self.username = self.email
                        self.two_factor_enabled = False  # Default since column doesn't exist
                        self.permissions = []  # Default empty permissions list
                        self.is_verified = True  # Default to verified
                        self.last_login = None
                        self.created_at = None
                        self.updated_at = None
                
                admin_user = SimpleAdminUser(result)
            except HTTPException:
                raise
            except Exception as sql_error:
                logger.error(f"Raw SQL query failed: {sql_error}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database error"
                )
        
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check account lockout (only if 2FA service is available)
        if two_factor_available:
            try:
                is_unlocked, lockout_message = TwoFactorService.check_account_lockout(admin_user)
            except Exception:
                # If 2FA check fails (e.g., missing columns), allow login
                is_unlocked, lockout_message = True, None
        else:
            is_unlocked, lockout_message = True, None
        if not is_unlocked:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=lockout_message
            )
        
        # Verify password
        if not auth_service.verify_password(login_data.password, admin_user.hashed_password):
            if two_factor_available:
                try:
                    TwoFactorService.record_failed_login(db, admin_user)
                except Exception:
                    pass  # Ignore if 2FA service fails
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not admin_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Check if 2FA is enabled (only if 2FA service is available)
        # Handle case where two_factor_enabled column might not exist in database
        two_factor_enabled = False
        try:
            if hasattr(admin_user, 'two_factor_enabled'):
                two_factor_enabled = bool(admin_user.two_factor_enabled)
        except Exception:
            two_factor_enabled = False
        
        if two_factor_enabled and two_factor_available:
            if not login_data.two_factor_token:
                # Return response indicating 2FA is required
                raise HTTPException(
                    status_code=status.HTTP_200_OK,
                    detail="2FA token required",
                    headers={"X-Requires-2FA": "true"}
                )
            
            # Verify 2FA token
            is_valid, error_message = TwoFactorService.verify_2fa_login(
                db,
                admin_user,
                login_data.two_factor_token
            )
            
            if not is_valid:
                TwoFactorService.record_failed_login(db, admin_user)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=error_message or "Invalid 2FA code"
                )
        elif two_factor_enabled and not two_factor_available:
            # If 2FA is enabled but service is not available, log warning and allow login
            logger.warning(f"Admin user {admin_user.email} has 2FA enabled but pyotp is not available, allowing login without 2FA")
        
        # Reset failed attempts on successful login (only if 2FA service is available)
        if two_factor_available:
            TwoFactorService.reset_failed_attempts(db, admin_user)
        
        # Get role-based permissions (before any db operations that might trigger relationships)
        try:
            user_role = AdminRole(admin_user.admin_role)
            role_permissions = get_permissions_for_role(user_role)
            # Combine with custom permissions if any
            custom_permissions = admin_user.permissions or []
            all_permissions = [p.value if hasattr(p, 'value') else str(p) for p in role_permissions] + [p for p in custom_permissions if p not in [str(p) for p in role_permissions]]
        except (ValueError, Exception) as e:
            logger.warning(f"Could not get role permissions: {e}")
            all_permissions = admin_user.permissions or []
        
        # Create tokens
        token_data = {
            "sub": str(admin_user.id),
            "email": admin_user.email,
            "admin_role": admin_user.admin_role,
            "type": "admin"
        }
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)
        
        # Update last login (skip if it causes issues)
        try:
            from sqlalchemy import update
            stmt = update(AdminUser).where(AdminUser.id == admin_user.id).values(last_login=datetime.utcnow())
            db.execute(stmt)
            db.commit()
        except Exception as e:
            # Log but don't fail login if last_login update fails
            logger.warning(f"Could not update last_login: {e}")
            db.rollback()
        
        return AdminLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": admin_user.id,
                "email": admin_user.email,
                "username": admin_user.username,
                "full_name": admin_user.full_name,
                "admin_role": admin_user.admin_role,
                "permissions": all_permissions
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during admin login: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=AdminLoginResponse)
async def admin_refresh(
    refresh_data: AdminRefreshRequest,
    db: Session = Depends(get_db)
):
    """Admin token refresh endpoint"""
    try:
        # Verify refresh token
        payload = verify_token(refresh_data.refresh_token)
        
        # Check token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Get user ID
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get admin user - handle missing columns gracefully
        admin_user = None
        try:
            admin_user = db.query(AdminUser).filter(AdminUser.id == int(user_id)).first()
        except Exception as db_error:
            # If query fails due to missing columns, rollback and use raw SQL
            logger.warning(f"AdminUser query failed in refresh (possible schema mismatch), using raw SQL: {db_error}")
            db.rollback()
            try:
                from sqlalchemy import text
                result = db.execute(
                    text("SELECT id, email, username, hashed_password, is_active, admin_role FROM admin_users WHERE id = :user_id"),
                    {"user_id": int(user_id)}
                ).first()
                if result:
                    class SimpleAdminUser:
                        def __init__(self, row):
                            self.id = row[0]
                            self.email = row[1]
                            self.username = row[2]
                            self.hashed_password = row[3]
                            self.is_active = row[4]
                            self.admin_role = row[5]
                            self.full_name = ''
                            self.permissions = []
                            self.two_factor_enabled = False
                    admin_user = SimpleAdminUser(result)
            except Exception as sql_error:
                logger.error(f"Raw SQL query also failed: {sql_error}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database error"
                )
        
        if not admin_user or not admin_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Get role-based permissions
        try:
            user_role = AdminRole(admin_user.admin_role)
            role_permissions = get_permissions_for_role(user_role)
            custom_permissions = admin_user.permissions or []
            all_permissions = list(role_permissions) + [p for p in custom_permissions if p not in role_permissions]
        except ValueError:
            all_permissions = admin_user.permissions or []
        
        # Create new tokens
        token_data = {
            "sub": str(admin_user.id),
            "email": admin_user.email,
            "admin_role": admin_user.admin_role,
            "type": "admin"
        }
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)
        
        return AdminLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": admin_user.id,
                "email": admin_user.email,
                "username": admin_user.username,
                "full_name": admin_user.full_name,
                "admin_role": admin_user.admin_role,
                "permissions": all_permissions
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error during admin token refresh: {e}")
        logger.error(f"Full traceback: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/logout")
async def admin_logout(
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Admin logout endpoint"""
    # In a real implementation, you might want to blacklist the token
    return {"message": "Logged out successfully"}


@router.get("/profile", response_model=AdminProfileResponse)
async def get_admin_profile(
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Get current admin user profile"""
    # Get role-based permissions
    try:
        user_role = AdminRole(current_user.admin_role)
        role_permissions = get_permissions_for_role(user_role)
        custom_permissions = current_user.permissions or []
        all_permissions = list(role_permissions) + [p for p in custom_permissions if p not in role_permissions]
    except ValueError:
        all_permissions = current_user.permissions or []
    
    # Handle SimpleAdminUser objects that might not have all attributes
    is_verified = getattr(current_user, 'is_verified', True)  # Default to True if not present
    last_login = getattr(current_user, 'last_login', None)
    created_at = getattr(current_user, 'created_at', None)
    full_name = getattr(current_user, 'full_name', '')
    username = getattr(current_user, 'username', current_user.email if hasattr(current_user, 'email') else '')
    
    return AdminProfileResponse(
        id=current_user.id,
        email=current_user.email,
        username=username,
        full_name=full_name,
        admin_role=current_user.admin_role,
        permissions=all_permissions,
        is_active=current_user.is_active,
        is_verified=is_verified,
        last_login=last_login,
        created_at=created_at or datetime.utcnow()  # Default to current time if None
    )


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    success: bool
    message: str


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """Request password reset for admin user"""
    try:
        # Find admin user
        admin_user = db.query(AdminUser).filter(AdminUser.email == request.email).first()
        
        # Always return success message (security best practice - don't reveal if email exists)
        if admin_user:
            # Rate limiting: Check for recent password reset requests (last hour)
            # Note: Admin users use JWT tokens, so we check by email in logs
            # In production, you might want to add a separate table for admin reset tokens
            
            # Generate reset token
            reset_token = create_access_token(
                data={"sub": str(admin_user.id), "email": admin_user.email},
                expires_delta=timedelta(hours=24),
                token_type="password_reset"
            )
            
            # Send password reset email via Brevo
            reset_link = f"{settings.admin_url}/admin/reset-password.html?token={reset_token}"
            email_context = {
                "username": admin_user.username or admin_user.full_name,
                "user_email": admin_user.email,
                "reset_link": reset_link,
                "expiry_hours": 24,
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "is_admin": True
            }
            
            email_result = brevo_email_service.send_template_email(
                to_emails=[admin_user.email],
                template_name="password_reset.html",
                template_context=email_context,
                subject="Admin Password Reset Request - Crane Intelligence",
                tags=["password-reset", "security", "admin"]
            )
            
            if not email_result.get("success"):
                logger.error(f"Failed to send admin password reset email: {email_result.get('message')}")
            else:
                logger.info(f"Password reset email sent to admin: {admin_user.email}")
        
        return ForgotPasswordResponse(
            success=True,
            message="If an account with that email exists, a password reset link has been sent."
        )
    except Exception as e:
        logger.error(f"Error in forgot password: {e}")
        # Still return success for security
        return ForgotPasswordResponse(
            success=True,
            message="If an account with that email exists, a password reset link has been sent."
        )


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/reset-password", response_model=ForgotPasswordResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Reset admin password using reset token"""
    try:
        # Verify token
        payload = verify_token(request.token)
        
        if payload.get("type") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        # Get admin user
        admin_user = db.query(AdminUser).filter(AdminUser.id == int(user_id)).first()
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        admin_user.hashed_password = auth_service.get_password_hash(request.new_password)
        db.commit()
        
        # Send password reset confirmation email via Brevo
        email_context = {
            "username": admin_user.username or admin_user.full_name,
            "user_email": admin_user.email,
            "reset_timestamp": datetime.utcnow().strftime("%B %d, %Y at %I:%M %p"),
            "login_url": f"{settings.admin_url}/admin-login.html",
            "platform_name": settings.app_name,
            "support_email": settings.mail_from_email,
            "is_admin": True
        }
        
        email_result = brevo_email_service.send_template_email(
            to_emails=[admin_user.email],
            template_name="password_reset_success.html",
            template_context=email_context,
            subject="Admin Password Reset Successful - Crane Intelligence",
            tags=["password-reset", "security", "admin", "confirmation"]
        )
        
        if not email_result.get("success"):
            logger.error(f"Failed to send admin password reset confirmation email: {email_result.get('message')}")
        
        return ForgotPasswordResponse(
            success=True,
            message="Password has been reset successfully. You can now log in with your new password."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )

