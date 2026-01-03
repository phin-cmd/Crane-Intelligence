"""
Admin authentication and authorization for Crane Intelligence Platform
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
import logging

from .database import get_db
from ..models.admin import AdminUser
from ..core.config import settings

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Increased to 60 minutes to reduce frequent logouts
REFRESH_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, token_type: str = "access"):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": token_type})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT refresh token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> AdminUser:
    """Get current authenticated admin user"""
    try:
        # Check if credentials are provided
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Verify token
        payload = verify_token(credentials.credentials)
        
        # Check token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Get user ID from token
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from database - handle missing columns gracefully
        user = None
        try:
            user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
        except Exception as db_error:
            # If query fails due to missing columns, rollback and use raw SQL
            logger.warning(f"AdminUser query failed in get_current_admin_user (possible schema mismatch), using raw SQL: {db_error}")
            db.rollback()
            try:
                from sqlalchemy import text
                result = db.execute(
                    text("SELECT id, email, username, is_active, admin_role FROM admin_users WHERE id = :user_id"),
                    {"user_id": user_id}
                ).first()
                if result:
                    class SimpleAdminUser:
                        def __init__(self, row):
                            self.id = row[0]
                            self.email = row[1]
                            self.username = row[2]
                            self.is_active = row[3]
                            self.admin_role = row[4]
                            self.full_name = ''
                            self.permissions = []
                            self.two_factor_enabled = False
                            self.two_factor_secret = None
                            self.two_factor_backup_codes = []
                            self.is_verified = True  # Default to verified for admin users
                            self.last_login = None
                            self.created_at = datetime.utcnow()  # Default to current time
                            self.updated_at = datetime.utcnow()  # Default to current time
                            self.failed_login_attempts = 0
                            self.account_locked_until = None
                            self.last_ip_address = None
                            self.last_user_agent = None
                    user = SimpleAdminUser(result)
                else:
                    user = None
            except Exception as sql_error:
                logger.error(f"Raw SQL query also failed: {sql_error}")
                user = None
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is deactivated"
            )
        
        # Update last login (skip if SimpleAdminUser or if it fails)
        try:
            if hasattr(user, 'last_login'):
                user.last_login = datetime.utcnow()
                db.commit()
        except Exception as e:
            logger.warning(f"Could not update last_login: {e}")
            db.rollback()
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current admin user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


def get_current_admin_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[AdminUser]:
    """Get current authenticated admin user (optional)"""
    if not credentials:
        return None
    
    try:
        return get_current_admin_user(credentials, db)
    except HTTPException:
        return None


def require_permission(permission: str):
    """Decorator to require specific permission"""
    from ..core.admin_permissions import Permission, has_permission, AdminRole
    
    def permission_checker(current_user: AdminUser = Depends(get_current_admin_user)):
        # Check role-based permissions first
        try:
            user_role = AdminRole(current_user.admin_role)
            perm = Permission(permission)
            if has_permission(user_role, perm):
                return current_user
        except (ValueError, KeyError):
            pass
        
        # Check custom permissions if set
        if current_user.permissions and permission in current_user.permissions:
            return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{permission}' required"
        )
    return permission_checker


def require_role(required_roles: list):
    """Decorator to require specific role(s)"""
    def role_checker(current_user: AdminUser = Depends(get_current_admin_user)):
        if current_user.admin_role not in [r.value if hasattr(r, 'value') else r for r in required_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {required_roles} required"
            )
        return current_user
    return role_checker


def require_super_admin(current_user: AdminUser = Depends(get_current_admin_user)):
    """Require super admin role"""
    from ..models.admin import AdminRole
    if current_user.admin_role != AdminRole.SUPER_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


def require_admin_or_super_admin(current_user: AdminUser = Depends(get_current_admin_user)):
    """Require admin or super admin role"""
    from ..models.admin import AdminRole
    if current_user.admin_role not in [AdminRole.ADMIN.value, AdminRole.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or super admin access required"
        )
    return current_user


def require_no_delete_restriction(current_user: AdminUser = Depends(get_current_admin_user)):
    """Require role that can delete (not manager or support)"""
    from ..models.admin import AdminRole
    from ..core.admin_permissions import can_delete
    
    try:
        user_role = AdminRole(current_user.admin_role)
        if not can_delete(user_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Delete access not allowed for your role"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin role"
        )
    return current_user


def require_can_manage_admin_users(current_user: AdminUser = Depends(get_current_admin_user)):
    """Require role that can manage admin users (only super admin)"""
    from ..models.admin import AdminRole
    from ..core.admin_permissions import can_manage_admin_users
    
    try:
        user_role = AdminRole(current_user.admin_role)
        if not can_manage_admin_users(user_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin user management restricted to super admin only"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin role"
        )
    return current_user


def require_can_view_admin_users(current_user: AdminUser = Depends(get_current_admin_user)):
    """Require permission to view admin users (read-only access)"""
    from ..core.admin_permissions import Permission, has_permission, AdminRole
    
    try:
        user_role = AdminRole(current_user.admin_role)
        if has_permission(user_role, Permission.VIEW_ADMIN_USERS):
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewing admin users requires VIEW_ADMIN_USERS permission"
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin role"
        )


def require_can_impersonate(current_user: AdminUser = Depends(get_current_admin_user)):
    """Require role that can impersonate users"""
    from ..models.admin import AdminRole
    from ..core.admin_permissions import can_impersonate
    
    try:
        user_role = AdminRole(current_user.admin_role)
        if not can_impersonate(user_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Impersonation not allowed for your role"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin role"
        )
    return current_user


def require_can_view_financial_data(current_user: AdminUser = Depends(get_current_admin_user)):
    """Require role that can view financial data"""
    from ..models.admin import AdminRole
    from ..core.admin_permissions import can_view_financial_data
    
    try:
        user_role = AdminRole(current_user.admin_role)
        if not can_view_financial_data(user_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Financial data access not allowed for your role"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin role"
        )
    return current_user


# Admin authentication endpoints
from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from ..services.auth_service import auth_service

admin_auth_router = APIRouter(prefix="/admin/auth", tags=["admin-auth"])


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    user: dict


class AdminRefreshRequest(BaseModel):
    refresh_token: str


@admin_auth_router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    login_data: AdminLoginRequest,
    db: Session = Depends(get_db)
):
    """Admin login endpoint"""
    try:
        # Find admin user
        admin_user = db.query(AdminUser).filter(AdminUser.email == login_data.email).first()
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not auth_service.verify_password(login_data.password, admin_user.hashed_password):
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
        
        # Create tokens
        access_token = create_access_token(data={"sub": str(admin_user.id)})
        refresh_token = create_refresh_token(data={"sub": str(admin_user.id)})
        
        # Update last login
        admin_user.last_login = datetime.utcnow()
        db.commit()
        
        return AdminLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": admin_user.id,
                "email": admin_user.email,
                "username": admin_user.username,
                "full_name": admin_user.full_name,
                "admin_role": admin_user.admin_role,
                "permissions": admin_user.permissions or []
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during admin login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@admin_auth_router.post("/refresh", response_model=AdminLoginResponse)
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
        
        # Get admin user
        admin_user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
        if not admin_user or not admin_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        access_token = create_access_token(data={"sub": str(admin_user.id)})
        refresh_token = create_refresh_token(data={"sub": str(admin_user.id)})
        
        return AdminLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": admin_user.id,
                "email": admin_user.email,
                "username": admin_user.username,
                "full_name": admin_user.full_name,
                "admin_role": admin_user.admin_role,
                "permissions": admin_user.permissions or []
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during admin token refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@admin_auth_router.post("/logout")
async def admin_logout(
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Admin logout endpoint"""
    # In a real implementation, you might want to blacklist the token
    # For now, we'll just return a success message
    return {"message": "Logged out successfully"}


@admin_auth_router.get("/me")
async def get_admin_profile(
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Get current admin user profile"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "admin_role": current_user.admin_role,
        "permissions": current_user.permissions or [],
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "last_login": current_user.last_login,
        "created_at": current_user.created_at
    }
