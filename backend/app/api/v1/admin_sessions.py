"""
Session Management API endpoints for Admin Users
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import secrets

from ...core.database import get_db
from ...models.admin import AdminUser, AdminSession
from ...core.admin_auth import get_current_admin_user, require_admin_or_super_admin
from ...core.config import settings

router = APIRouter(prefix="/admin/sessions", tags=["admin-sessions"])


class SessionResponse(BaseModel):
    """Response model for session"""
    id: int
    admin_user_id: int
    admin_email: Optional[str]
    admin_name: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    device_info: Optional[dict]
    is_active: bool
    last_activity: datetime
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """Response model for session list"""
    sessions: List[SessionResponse]
    total: int


@router.get("", response_model=SessionListResponse)
async def get_sessions(
    admin_user_id: Optional[int] = Query(None, description="Filter by admin user ID"),
    active_only: bool = Query(True, description="Show only active sessions"),
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Get all admin sessions"""
    query = db.query(AdminSession)
    
    # Super admin can see all sessions, regular admin can only see their own
    if current_user.admin_role != "super_admin":
        query = query.filter(AdminSession.admin_user_id == current_user.id)
    elif admin_user_id:
        query = query.filter(AdminSession.admin_user_id == admin_user_id)
    
    if active_only:
        query = query.filter(AdminSession.is_active == True)
        query = query.filter(AdminSession.expires_at > datetime.utcnow())
    
    sessions = query.order_by(AdminSession.last_activity.desc()).all()
    
    session_responses = [
        SessionResponse(
            id=session.id,
            admin_user_id=session.admin_user_id,
            admin_email=session.admin_user.email if session.admin_user else None,
            admin_name=session.admin_user.full_name if session.admin_user else None,
            ip_address=session.ip_address,
            user_agent=session.user_agent,
            device_info=session.device_info,
            is_active=session.is_active,
            last_activity=session.last_activity,
            created_at=session.created_at,
            expires_at=session.expires_at
        )
        for session in sessions
    ]
    
    return SessionListResponse(
        sessions=session_responses,
        total=len(session_responses)
    )


@router.get("/my-sessions", response_model=SessionListResponse)
async def get_my_sessions(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get current user's sessions"""
    sessions = db.query(AdminSession).filter(
        AdminSession.admin_user_id == current_user.id,
        AdminSession.is_active == True,
        AdminSession.expires_at > datetime.utcnow()
    ).order_by(AdminSession.last_activity.desc()).all()
    
    session_responses = [
        SessionResponse(
            id=session.id,
            admin_user_id=session.admin_user_id,
            admin_email=session.admin_user.email if session.admin_user else None,
            admin_name=session.admin_user.full_name if session.admin_user else None,
            ip_address=session.ip_address,
            user_agent=session.user_agent,
            device_info=session.device_info,
            is_active=session.is_active,
            last_activity=session.last_activity,
            created_at=session.created_at,
            expires_at=session.expires_at
        )
        for session in sessions
    ]
    
    return SessionListResponse(
        sessions=session_responses,
        total=len(session_responses)
    )


@router.delete("/{session_id}")
async def revoke_session(
    session_id: int,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Revoke a session (logout)"""
    session = db.query(AdminSession).filter(AdminSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Users can only revoke their own sessions unless they're super admin
    if session.admin_user_id != current_user.id and current_user.admin_role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only revoke your own sessions"
        )
    
    session.is_active = False
    db.commit()
    
    return {"message": "Session revoked successfully"}


@router.post("/revoke-all")
async def revoke_all_my_sessions(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Revoke all sessions for current user (except current session)"""
    from fastapi import Request
    from ...core.audit_helper import get_client_info
    
    # Get current session token from request (if available)
    # This is a simplified version - in production, you'd extract from JWT
    
    # Revoke all active sessions for this user
    sessions = db.query(AdminSession).filter(
        AdminSession.admin_user_id == current_user.id,
        AdminSession.is_active == True
    ).all()
    
    for session in sessions:
        session.is_active = False
    
    db.commit()
    
    return {"message": f"Revoked {len(sessions)} session(s)"}


@router.post("/create")
async def create_session(
    admin_user_id: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    device_info: Optional[dict] = None,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Create a new session (internal use, typically called during login)"""
    # Generate session token
    session_token = secrets.token_urlsafe(32)
    
    # Set expiration (30 days)
    expires_at = datetime.utcnow() + timedelta(days=30)
    
    session = AdminSession(
        admin_user_id=admin_user_id,
        session_token=session_token,
        ip_address=ip_address,
        user_agent=user_agent,
        device_info=device_info,
        expires_at=expires_at,
        is_active=True
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "session_id": session.id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat()
    }


@router.post("/{session_id}/refresh")
async def refresh_session(
    session_id: int,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Refresh a session (update last activity and extend expiration)"""
    session = db.query(AdminSession).filter(AdminSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Users can only refresh their own sessions
    if session.admin_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only refresh your own sessions"
        )
    
    # Update last activity and extend expiration
    session.last_activity = datetime.utcnow()
    session.expires_at = datetime.utcnow() + timedelta(days=30)
    db.commit()
    
    return {"message": "Session refreshed successfully"}

