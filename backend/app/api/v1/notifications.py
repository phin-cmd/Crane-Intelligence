"""
Notifications API Endpoints
Handles user and admin notifications
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ...core.database import get_db
from ...models.user import User
from ...services.auth_service import get_current_user
from ...core.admin_auth import get_current_admin_user
from ...models.notification import UserNotification

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str
    read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    success: bool
    message: str
    data: List[NotificationResponse]
    error: Optional[str] = None


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """
    Get notifications for the current user
    """
    try:
        user_id = int(current_user.get("sub"))
        print(f"[NOTIFICATIONS API] Getting notifications for user_id: {user_id}")
        
        notifications = db.query(UserNotification).filter(
            UserNotification.user_id == user_id
        ).order_by(
            UserNotification.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        print(f"[NOTIFICATIONS API] Found {len(notifications)} notifications for user_id {user_id}")
        for n in notifications:
            print(f"[NOTIFICATIONS API]   - ID: {n.id}, Title: {n.title}, Type: {n.type}, Read: {n.read}, Created: {n.created_at}")
        
        notification_responses = []
        for n in notifications:
            # Ensure created_at is a datetime object
            created_at = n.created_at
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    created_at = datetime.now()
            
            notification_responses.append(NotificationResponse(
                id=n.id,
                user_id=n.user_id,
                title=n.title,
                message=n.message,
                type=n.type,
                read=n.read,
                created_at=created_at
            ))
        
        print(f"[NOTIFICATIONS API] Returning {len(notification_responses)} notification responses")
        return NotificationListResponse(
            success=True,
            message="Notifications retrieved successfully",
            data=notification_responses
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving notifications: {str(e)}"
        )


@router.post("/{notification_id}/read", response_model=dict)
async def mark_notification_as_read(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a notification as read
    """
    try:
        user_id = int(current_user.get("sub"))
        
        notification = db.query(UserNotification).filter(
            UserNotification.id == notification_id,
            UserNotification.user_id == user_id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        notification.read = True
        db.commit()
        
        return {
            "success": True,
            "message": "Notification marked as read"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking notification as read: {str(e)}"
        )


@router.post("/read-all", response_model=dict)
async def mark_all_notifications_as_read(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark all notifications as read for the current user
    """
    try:
        user_id = int(current_user.get("sub"))
        
        db.query(UserNotification).filter(
            UserNotification.user_id == user_id,
            UserNotification.read == False
        ).update({"read": True})
        
        db.commit()
        
        return {
            "success": True,
            "message": "All notifications marked as read"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking all notifications as read: {str(e)}"
        )


# Admin notifications endpoints
@router.get("/admin/notifications", response_model=NotificationListResponse)
async def get_admin_notifications(
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """
    Get notifications for admin users
    """
    try:
        from ...models.admin import Notification, AdminUser
        
        # Get admin user ID
        admin_user_id = None
        if isinstance(current_user, dict):
            admin_user_id = current_user.get("sub") or current_user.get("id")
        elif hasattr(current_user, 'id'):
            admin_user_id = current_user.id
        elif hasattr(current_user, 'sub'):
            admin_user_id = current_user.sub
        
        if not admin_user_id:
            # If we can't get admin user ID, get all admin notifications
            notifications = db.query(Notification).order_by(
                Notification.created_at.desc()
            ).limit(limit).offset(offset).all()
        else:
            notifications = db.query(Notification).filter(
                Notification.admin_user_id == int(admin_user_id)
            ).order_by(
                Notification.created_at.desc()
            ).limit(limit).offset(offset).all()
        
        notification_responses = []
        for n in notifications:
            created_at = n.created_at
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    created_at = datetime.now()
            
            notification_responses.append(NotificationResponse(
                id=n.id,
                user_id=n.admin_user_id or 0,  # Use admin_user_id as user_id for compatibility
                title=n.title,
                message=n.message,
                type=n.notification_type or "admin",
                read=n.is_read,
                created_at=created_at
            ))
        
        return NotificationListResponse(
            success=True,
            message="Admin notifications retrieved successfully",
            data=notification_responses
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving admin notifications: {str(e)}"
        )


@router.post("/admin/notifications/{notification_id}/read", response_model=dict)
async def mark_admin_notification_as_read(
    notification_id: int,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Mark an admin notification as read
    """
    try:
        from ...models.admin import Notification
        
        # Get admin user ID
        admin_user_id = None
        if isinstance(current_user, dict):
            admin_user_id = current_user.get("sub") or current_user.get("id")
        elif hasattr(current_user, 'id'):
            admin_user_id = current_user.id
        elif hasattr(current_user, 'sub'):
            admin_user_id = current_user.sub
        
        notification = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Verify admin owns this notification (or is super admin)
        if admin_user_id and notification.admin_user_id != int(admin_user_id):
            # Check if user is super admin
            from ...models.admin import AdminUser
            admin = db.query(AdminUser).filter(AdminUser.id == int(admin_user_id)).first()
            if not admin or not admin.is_super_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "Notification marked as read"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking notification as read: {str(e)}"
        )


@router.post("/admin/notifications/read-all", response_model=dict)
async def mark_all_admin_notifications_as_read(
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Mark all admin notifications as read for the current admin user
    """
    try:
        from ...models.admin import Notification
        
        # Get admin user ID
        admin_user_id = None
        if isinstance(current_user, dict):
            admin_user_id = current_user.get("sub") or current_user.get("id")
        elif hasattr(current_user, 'id'):
            admin_user_id = current_user.id
        elif hasattr(current_user, 'sub'):
            admin_user_id = current_user.sub
        
        if not admin_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin user ID not found"
            )
        
        db.query(Notification).filter(
            Notification.admin_user_id == int(admin_user_id),
            Notification.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        
        db.commit()
        
        return {
            "success": True,
            "message": "All notifications marked as read"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking all notifications as read: {str(e)}"
        )

