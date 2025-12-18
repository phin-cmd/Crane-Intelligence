"""
Admin Role Settings Management API
CRUD operations for role-based access control settings
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

from ...core.database import get_db
from ...models.admin import AdminUser, AdminRole
from ...core.admin_auth import get_current_admin_user, require_super_admin
from ...core.admin_permissions import get_permissions_for_role, Permission

router = APIRouter(prefix="/admin/roles", tags=["admin-roles"])


class RolePermissionResponse(BaseModel):
    role: str
    permissions: List[str]
    description: str


class RoleUpdateRequest(BaseModel):
    permissions: List[str]


@router.get("", response_model=List[RolePermissionResponse])
async def list_roles(
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """List all admin roles with their permissions"""
    roles = []
    
    for role in AdminRole:
        permissions = get_permissions_for_role(role)
        roles.append(RolePermissionResponse(
            role=role.value,
            permissions=[p.value for p in permissions],
            description=f"Admin role: {role.value}"
        ))
    
    return roles


@router.get("/{role_name}", response_model=RolePermissionResponse)
async def get_role(
    role_name: str,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Get permissions for a specific role"""
    try:
        role = AdminRole(role_name)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role not found: {role_name}"
        )
    
    permissions = get_permissions_for_role(role)
    return RolePermissionResponse(
        role=role.value,
        permissions=[p.value for p in permissions],
        description=f"Admin role: {role.value}"
    )


@router.get("/permissions/all", response_model=List[str])
async def list_all_permissions(
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """List all available permissions"""
    return [p.value for p in Permission]


@router.get("/users/{user_id}/permissions")
async def get_user_permissions(
    user_id: int,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Get permissions for a specific admin user"""
    user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found"
        )
    
    try:
        user_role = AdminRole(user.admin_role)
        role_permissions = get_permissions_for_role(user_role)
        custom_permissions = user.permissions or []
        all_permissions = list(role_permissions) + [p for p in custom_permissions if p not in [rp.value for rp in role_permissions]]
    except ValueError:
        all_permissions = user.permissions or []
    
    return {
        "user_id": user.id,
        "email": user.email,
        "role": user.admin_role,
        "permissions": [p.value if hasattr(p, 'value') else p for p in all_permissions],
        "custom_permissions": custom_permissions
    }

