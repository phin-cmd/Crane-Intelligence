"""
User Management Schemas
Pydantic models for user management operations
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

from ..models.user import UserRole


class UserResponse(BaseModel):
    """User response model"""
    id: int
    email: str
    username: str
    full_name: str
    company_name: str
    user_role: UserRole
    is_active: bool
    is_verified: bool
    total_payments: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """User creation model for webapp users"""
    email: EmailStr
    username: str
    password: str
    full_name: str
    company_name: str
    user_role: UserRole
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v


class UserUpdate(BaseModel):
    """User update model for webapp users"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError('Username must be at least 3 characters long')
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v


class AdminUserCreate(BaseModel):
    """Admin user creation model with additional fields"""
    email: EmailStr
    username: str
    password: str
    full_name: str
    company_name: str
    user_role: UserRole
    is_active: bool = True
    is_verified: bool = True
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v


class AdminUserUpdate(BaseModel):
    """Admin user update model with additional fields"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    user_role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    
    @validator('password')
    def validate_password(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError('Username must be at least 3 characters long')
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v


class UserListResponse(BaseModel):
    """User list response with pagination"""
    users: List[UserResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class UserUsageResponse(BaseModel):
    """User usage statistics response"""
    user_id: int
    monthly_valuations_used: int
    monthly_api_calls_used: int
    subscription_tier: str  # Kept for backward compatibility, will be "N/A"
    subscription_limits: dict
    usage_percentage: dict
    last_activity: Optional[datetime]


class PasswordChangeRequest(BaseModel):
    """Password change request model"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v


class PasswordResetRequest(BaseModel):
    """Password reset request model"""
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v


class UserFilterRequest(BaseModel):
    """User filtering request model"""
    search: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class UserStatsResponse(BaseModel):
    """User statistics response"""
    total_users: int
    active_users: int
    verified_users: int
    users_by_role: dict
    users_by_subscription: dict
    new_users_this_month: int
    new_users_this_week: int
