"""
Admin Impersonation API
Allows admins with impersonation permission to access user accounts
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

from ...core.database import get_db
from ...models.user import User
from ...models.admin import AdminUser
from ...core.admin_auth import get_current_admin_user, create_access_token
from ...core.admin_permissions import can_impersonate, AdminRole

router = APIRouter(prefix="/admin/impersonation", tags=["admin-impersonation"])


class ImpersonationRequest(BaseModel):
    user_id: int


class ImpersonationResponse(BaseModel):
    success: bool
    message: str
    impersonation_token: str
    user: Dict[str, Any]
    admin_user: Dict[str, Any]


@router.post("/start", response_model=ImpersonationResponse)
async def start_impersonation(
    request: ImpersonationRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Start impersonating a user (requires impersonation permission)"""
    from ...core.admin_permissions import can_impersonate
    
    # Check if admin can impersonate
    try:
        admin_role = AdminRole(current_admin.admin_role)
        if not can_impersonate(admin_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Impersonation not allowed for your role"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin role"
        )
    
    # Get the user to impersonate
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create impersonation token
    # Include both admin and user info in token
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "type": "impersonation",
        "admin_id": str(current_admin.id),
        "admin_email": current_admin.email,
        "admin_role": current_admin.admin_role,
        "impersonated_at": datetime.utcnow().isoformat()
    }
    
    impersonation_token = create_access_token(data=token_data)
    
    # Log impersonation event (you can add this to audit_logs table)
    # For now, we'll just return the token
    
    return ImpersonationResponse(
        success=True,
        message=f"Impersonating user {user.email}",
        impersonation_token=impersonation_token,
        user={
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "subscription_tier": user.subscription_tier.value if user.subscription_tier else "free",
            "user_role": user.user_role.value if user.user_role else "others"
        },
        admin_user={
            "id": current_admin.id,
            "email": current_admin.email,
            "admin_role": current_admin.admin_role
        }
    )


@router.post("/stop")
async def stop_impersonation(
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Stop impersonation (returns to admin account)"""
    # In a real implementation, you might want to invalidate the impersonation token
    return {
        "success": True,
        "message": "Impersonation stopped",
        "admin_user": {
            "id": current_admin.id,
            "email": current_admin.email,
            "admin_role": current_admin.admin_role
        }
    }


@router.get("/status")
async def get_impersonation_status(
    credentials: Any = None  # Will be handled by token verification
):
    """Get current impersonation status"""
    # This would check if the current token is an impersonation token
    # For now, return not impersonating
    return {
        "is_impersonating": False,
        "message": "Not currently impersonating"
    }

