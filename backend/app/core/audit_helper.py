"""
Helper functions for audit logging in admin endpoints
"""
from fastapi import Request
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from ..models.admin import AdminUser
from ..services.audit_service import AuditService


def get_client_info(request: Request) -> Dict[str, Optional[str]]:
    """Extract client IP and user agent from request"""
    # Get IP address
    ip_address = request.client.host if request.client else None
    # Check for forwarded IP (if behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        ip_address = forwarded_for.split(",")[0].strip()
    
    # Get user agent
    user_agent = request.headers.get("User-Agent")
    
    return {
        "ip_address": ip_address,
        "user_agent": user_agent
    }


def log_admin_action(
    db: Session,
    admin_user: AdminUser,
    action: str,
    resource_type: str,
    resource_id: str,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    request: Optional[Request] = None
):
    """Helper to log admin actions with request context"""
    client_info = get_client_info(request) if request else {}
    
    AuditService.log_action(
        db=db,
        admin_user_id=admin_user.id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        old_values=old_values,
        new_values=new_values,
        description=description,
        ip_address=client_info.get("ip_address"),
        user_agent=client_info.get("user_agent")
    )

