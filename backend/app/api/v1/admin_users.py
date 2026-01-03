"""
Admin User Management API
CRUD operations for admin users with role-based access control
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...core.database import get_db
from ...models.admin import AdminUser, AdminRole
from ...core.admin_auth import (
    get_current_admin_user,
    require_can_manage_admin_users,
    require_can_view_admin_users,
    require_super_admin
)
from ...services.auth_service import auth_service
from ...services.admin_email_service import AdminEmailService
from ...core.admin_permissions import get_permissions_for_role

router = APIRouter(prefix="/admin", tags=["admin-users"])

# Initialize admin email service
admin_email_service = AdminEmailService()


class AdminUserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    admin_role: str
    permissions: Optional[List[str]] = None
    is_active: bool = True
    is_verified: bool = True


class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    admin_role: Optional[str] = None
    password: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class AdminUserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    admin_role: str
    permissions: List[str]
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime


# Removed /admin/users route to avoid conflict with /admin/users in admin.py (which returns regular website users)
# Use /admin/admin-users instead for admin users

# Route for /admin/admin-users (frontend compatibility)
@router.get("/admin-users", response_model=List[AdminUserResponse])
async def list_admin_users_alias(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: AdminUser = Depends(require_can_view_admin_users),  # Changed to allow viewing for more roles
    db: Session = Depends(get_db)
):
    """List admin users - allows viewing for roles with VIEW_ADMIN_USERS permission"""
    # Query admin users from database
    admin_users = db.query(AdminUser).offset(skip).limit(limit).all()
    
    result = []
    for user in admin_users:
        # Get role-based permissions
        try:
            user_role = AdminRole(user.admin_role)
            role_permissions = get_permissions_for_role(user_role)
            custom_permissions = user.permissions or []
            all_permissions = list(role_permissions) + [p for p in custom_permissions if p not in role_permissions]
        except ValueError:
            all_permissions = user.permissions or []
        
        result.append(AdminUserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            admin_role=user.admin_role,
            permissions=all_permissions,
            is_active=user.is_active,
            is_verified=user.is_verified,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        ))
    
    return result


@router.post("", response_model=AdminUserResponse)
async def create_admin_user(
    user_data: AdminUserCreate,
    request: Request,
    current_user: AdminUser = Depends(require_can_manage_admin_users),
    db: Session = Depends(get_db)
):
    """Create a new admin user (Super Admin only)"""
    from ...core.audit_helper import log_admin_action
    
    # Validate admin role
    try:
        AdminRole(user_data.admin_role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid admin role: {user_data.admin_role}"
        )
    
    # Check if email already exists
    existing_user = db.query(AdminUser).filter(AdminUser.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(AdminUser).filter(AdminUser.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new admin user
    new_user = AdminUser(
        email=user_data.email,
        username=user_data.username,
        hashed_password=auth_service.get_password_hash(user_data.password),
        full_name=user_data.full_name,
        admin_role=user_data.admin_role,
        permissions=user_data.permissions,
        is_active=user_data.is_active,
        is_verified=user_data.is_verified
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Log audit action
    log_admin_action(
        db=db,
        admin_user=current_user,
        action="create",
        resource_type="admin_user",
        resource_id=str(new_user.id),
        new_values={
            "email": new_user.email,
            "username": new_user.username,
            "full_name": new_user.full_name,
            "admin_role": new_user.admin_role,
            "is_active": new_user.is_active
        },
        description=f"Created admin user: {new_user.email}",
        request=request
    )
    
    # Send admin notification for new admin user creation
    try:
        admin_email_service.send_admin_user_management_alert(
            admin_emails=[],
            action_data={
                "action_type": "Admin User Created",
                "admin_name": current_user.full_name,
                "username": new_user.username,
                "user_email": new_user.email,
                "action_description": f"New admin user '{new_user.full_name}' created with role '{new_user.admin_role}'",
                "admin_users_url": f"{settings.admin_url}/admin/users.html"
            },
            db=db
        )
    except Exception as e:
        logger.error(f"Error sending admin user creation notification: {e}")
    
    # Get role-based permissions
    try:
        user_role = AdminRole(new_user.admin_role)
        role_permissions = get_permissions_for_role(user_role)
        custom_permissions = new_user.permissions or []
        all_permissions = list(role_permissions) + [p for p in custom_permissions if p not in role_permissions]
    except ValueError:
        all_permissions = new_user.permissions or []
    
    return AdminUserResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        full_name=new_user.full_name,
        admin_role=new_user.admin_role,
        permissions=all_permissions,
        is_active=new_user.is_active,
        is_verified=new_user.is_verified,
        last_login=new_user.last_login,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at
    )


@router.get("/admin-users/{user_id}", response_model=AdminUserResponse)
async def get_admin_user(
    user_id: int,
    current_user: AdminUser = Depends(require_can_manage_admin_users),
    db: Session = Depends(get_db)
):
    """Get a specific admin user (Super Admin only)"""
    admin_user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Get role-based permissions
    try:
        user_role = AdminRole(admin_user.admin_role)
        role_permissions = get_permissions_for_role(user_role)
        custom_permissions = admin_user.permissions or []
        all_permissions = list(role_permissions) + [p for p in custom_permissions if p not in role_permissions]
    except ValueError:
        all_permissions = admin_user.permissions or []
    
    return AdminUserResponse(
        id=admin_user.id,
        email=admin_user.email,
        username=admin_user.username,
        full_name=admin_user.full_name,
        admin_role=admin_user.admin_role,
        permissions=all_permissions,
        is_active=admin_user.is_active,
        is_verified=admin_user.is_verified,
        last_login=admin_user.last_login,
        created_at=admin_user.created_at,
        updated_at=admin_user.updated_at
    )


@router.put("/admin-users/{user_id}", response_model=AdminUserResponse)
async def update_admin_user(
    user_id: int,
    user_data: AdminUserUpdate,
    request: Request,
    current_user: AdminUser = Depends(require_can_manage_admin_users),
    db: Session = Depends(get_db)
):
    """Update an admin user (Super Admin only)"""
    from ...core.audit_helper import log_admin_action
    
    admin_user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Prevent modifying super admin (except by super admin themselves)
    if admin_user.admin_role == AdminRole.SUPER_ADMIN.value and current_user.id != admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify super admin user"
        )
    
    # Update fields
    if user_data.email is not None:
        # Check if email is already taken by another user
        existing = db.query(AdminUser).filter(
            AdminUser.email == user_data.email,
            AdminUser.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        admin_user.email = user_data.email
    
    if user_data.username is not None:
        # Check if username is already taken by another user
        existing = db.query(AdminUser).filter(
            AdminUser.username == user_data.username,
            AdminUser.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        admin_user.username = user_data.username
    
    if user_data.full_name is not None:
        admin_user.full_name = user_data.full_name
    
    if user_data.admin_role is not None:
        # Validate role
        try:
            AdminRole(user_data.admin_role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid admin role: {user_data.admin_role}"
            )
        # Prevent changing super admin role
        if admin_user.admin_role == AdminRole.SUPER_ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change super admin role"
            )
        admin_user.admin_role = user_data.admin_role
    
    if user_data.password is not None:
        admin_user.hashed_password = auth_service.get_password_hash(user_data.password)
    
    if user_data.permissions is not None:
        admin_user.permissions = user_data.permissions
    
    if user_data.is_active is not None:
        # Prevent deactivating super admin
        if admin_user.admin_role == AdminRole.SUPER_ADMIN.value and not user_data.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot deactivate super admin"
            )
        admin_user.is_active = user_data.is_active
    
    if user_data.is_verified is not None:
        admin_user.is_verified = user_data.is_verified
    
    # Store old values for audit log
    old_values = {
        "email": admin_user.email,
        "username": admin_user.username,
        "full_name": admin_user.full_name,
        "admin_role": admin_user.admin_role,
        "is_active": admin_user.is_active,
        "is_verified": admin_user.is_verified
    }
    
    admin_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(admin_user)
    
    # Log audit action
    new_values = {
        "email": admin_user.email,
        "username": admin_user.username,
        "full_name": admin_user.full_name,
        "admin_role": admin_user.admin_role,
        "is_active": admin_user.is_active,
        "is_verified": admin_user.is_verified
    }
    log_admin_action(
        db=db,
        admin_user=current_user,
        action="update",
        resource_type="admin_user",
        resource_id=str(user_id),
        old_values=old_values,
        new_values=new_values,
        description=f"Updated admin user: {admin_user.email}",
        request=request
    )
    
    # Send admin notification for admin user update
    try:
        changes = []
        if user_data.email is not None:
            changes.append(f"Email changed")
        if user_data.admin_role is not None:
            changes.append(f"Role changed to {user_data.admin_role}")
        if user_data.is_active is not None:
            changes.append(f"Status changed to {'Active' if user_data.is_active else 'Inactive'}")
        if user_data.password is not None:
            changes.append("Password reset")
        
        if changes:
            admin_email_service.send_admin_user_management_alert(
                admin_emails=[],
                action_data={
                    "action_type": "Admin User Updated",
                    "admin_name": current_user.full_name,
                    "username": admin_user.username,
                    "user_email": admin_user.email,
                    "action_description": f"Admin user '{admin_user.full_name}' updated: {', '.join(changes)}",
                    "admin_users_url": f"{settings.admin_url}/admin/users.html"
                },
                db=db
            )
    except Exception as e:
        logger.error(f"Error sending admin user update notification: {e}")
    
    # Get role-based permissions
    try:
        user_role = AdminRole(admin_user.admin_role)
        role_permissions = get_permissions_for_role(user_role)
        custom_permissions = admin_user.permissions or []
        all_permissions = list(role_permissions) + [p for p in custom_permissions if p not in role_permissions]
    except ValueError:
        all_permissions = admin_user.permissions or []
    
    return AdminUserResponse(
        id=admin_user.id,
        email=admin_user.email,
        username=admin_user.username,
        full_name=admin_user.full_name,
        admin_role=admin_user.admin_role,
        permissions=all_permissions,
        is_active=admin_user.is_active,
        is_verified=admin_user.is_verified,
        last_login=admin_user.last_login,
        created_at=admin_user.created_at,
        updated_at=admin_user.updated_at
    )


@router.delete("/admin-users/{user_id}")
async def delete_admin_user(
    user_id: int,
    current_user: AdminUser = Depends(require_can_manage_admin_users),
    db: Session = Depends(get_db)
):
    """Delete an admin user (Super Admin only)"""
    admin_user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    # Prevent deleting super admin
    if admin_user.admin_role == AdminRole.SUPER_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete super admin user"
        )
    
    # Prevent deleting yourself
    if admin_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Store old values for audit log before deletion
    old_values = {
        "email": admin_user.email,
        "username": admin_user.username,
        "full_name": admin_user.full_name,
        "admin_role": admin_user.admin_role,
        "is_active": admin_user.is_active
    }
    
    # Log audit action before deletion
    log_admin_action(
        db=db,
        admin_user=current_user,
        action="delete",
        resource_type="admin_user",
        resource_id=str(user_id),
        old_values=old_values,
        description=f"Deleted admin user: {admin_user.email}",
        request=request
    )
    
    db.delete(admin_user)
    db.commit()
    
    return {"message": "Admin user deleted successfully"}

