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
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
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
        
        # Get user from database
        user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
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
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
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
    def permission_checker(current_user: AdminUser = Depends(get_current_admin_user)):
        if not current_user.permissions or permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    return permission_checker


def require_role(required_roles: list):
    """Decorator to require specific role(s)"""
    def role_checker(current_user: AdminUser = Depends(get_current_admin_user)):
        if current_user.admin_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {required_roles} required"
            )
        return current_user
    return role_checker


def require_super_admin(current_user: AdminUser = Depends(get_current_admin_user)):
    """Require super admin role"""
    if current_user.admin_role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


def require_admin_or_super_admin(current_user: AdminUser = Depends(get_current_admin_user)):
    """Require admin or super admin role"""
    if current_user.admin_role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or super admin access required"
        )
    return current_user


# Admin authentication endpoints
from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from ..core.auth import verify_password, get_password_hash

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
        if not verify_password(login_data.password, admin_user.hashed_password):
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
