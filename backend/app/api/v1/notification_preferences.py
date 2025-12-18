"""
Notification Preferences API
Allows users to manage their email notification preferences
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json

from ...core.database import get_db
from ...models.user import User
from ...models.notification_preference import NotificationPreference
from ...api.v1.auth import get_current_user
from ...services.account_email_service import AccountEmailService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notification Preferences"])

account_email_service = AccountEmailService()


class NotificationPreferencesRequest(BaseModel):
    """Request model for updating notification preferences"""
    email_notifications_enabled: Optional[bool] = None
    fmv_report_notifications: Optional[bool] = None
    fmv_report_important_only: Optional[bool] = None
    payment_notifications: Optional[bool] = None
    payment_important_only: Optional[bool] = None
    account_management_notifications: Optional[bool] = None
    account_management_important_only: Optional[bool] = None
    marketing_emails: Optional[bool] = None


class NotificationPreferencesResponse(BaseModel):
    """Response model for notification preferences"""
    user_id: int
    email_notifications_enabled: bool
    fmv_report_notifications: bool
    fmv_report_important_only: bool
    payment_notifications: bool
    payment_important_only: bool
    account_management_notifications: bool
    account_management_important_only: bool
    marketing_emails: bool


@router.get("/preferences", response_model=NotificationPreferencesResponse)
async def get_notification_preferences(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's notification preferences"""
    try:
        user_id = int(current_user.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user has notification_preferences JSON field
        if user.notification_preferences:
            try:
                prefs = json.loads(user.notification_preferences)
                return NotificationPreferencesResponse(
                    user_id=user_id,
                    email_notifications_enabled=prefs.get("email_notifications_enabled", True),
                    fmv_report_notifications=prefs.get("fmv_report_notifications", True),
                    fmv_report_important_only=prefs.get("fmv_report_important_only", False),
                    payment_notifications=prefs.get("payment_notifications", True),
                    payment_important_only=prefs.get("payment_important_only", False),
                    account_management_notifications=prefs.get("account_management_notifications", True),
                    account_management_important_only=prefs.get("account_management_important_only", False),
                    marketing_emails=prefs.get("marketing_emails", False)
                )
            except:
                pass
        
        # Fallback to NotificationPreference table
        pref = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()
        
        if pref:
            return NotificationPreferencesResponse(
                user_id=user_id,
                email_notifications_enabled=pref.email_notifications_enabled,
                fmv_report_notifications=pref.fmv_report_notifications,
                fmv_report_important_only=pref.fmv_report_important_only,
                payment_notifications=pref.payment_notifications,
                payment_important_only=pref.payment_important_only,
                account_management_notifications=pref.account_management_notifications,
                account_management_important_only=pref.account_management_important_only,
                marketing_emails=pref.marketing_emails
            )
        
        # Return defaults if no preferences found
        return NotificationPreferencesResponse(
            user_id=user_id,
            email_notifications_enabled=True,
            fmv_report_notifications=True,
            fmv_report_important_only=False,
            payment_notifications=True,
            payment_important_only=False,
            account_management_notifications=True,
            account_management_important_only=False,
            marketing_emails=False
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notification preferences"
        )


@router.put("/preferences", response_model=NotificationPreferencesResponse)
async def update_notification_preferences(
    preferences: NotificationPreferencesRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's notification preferences"""
    try:
        user_id = int(current_user.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get current preferences
        current_prefs = {}
        if user.notification_preferences:
            try:
                current_prefs = json.loads(user.notification_preferences)
            except:
                pass
        
        # Update preferences
        updated_prefs = {
            "email_notifications_enabled": preferences.email_notifications_enabled if preferences.email_notifications_enabled is not None else current_prefs.get("email_notifications_enabled", True),
            "fmv_report_notifications": preferences.fmv_report_notifications if preferences.fmv_report_notifications is not None else current_prefs.get("fmv_report_notifications", True),
            "fmv_report_important_only": preferences.fmv_report_important_only if preferences.fmv_report_important_only is not None else current_prefs.get("fmv_report_important_only", False),
            "payment_notifications": preferences.payment_notifications if preferences.payment_notifications is not None else current_prefs.get("payment_notifications", True),
            "payment_important_only": preferences.payment_important_only if preferences.payment_important_only is not None else current_prefs.get("payment_important_only", False),
            "account_management_notifications": preferences.account_management_notifications if preferences.account_management_notifications is not None else current_prefs.get("account_management_notifications", True),
            "account_management_important_only": preferences.account_management_important_only if preferences.account_management_important_only is not None else current_prefs.get("account_management_important_only", False),
            "marketing_emails": preferences.marketing_emails if preferences.marketing_emails is not None else current_prefs.get("marketing_emails", False)
        }
        
        # Save to user.notification_preferences JSON field
        user.notification_preferences = json.dumps(updated_prefs)
        db.commit()
        db.refresh(user)
        
        # Also update NotificationPreference table for compatibility
        pref = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()
        
        if pref:
            pref.email_notifications_enabled = updated_prefs["email_notifications_enabled"]
            pref.fmv_report_notifications = updated_prefs["fmv_report_notifications"]
            pref.fmv_report_important_only = updated_prefs["fmv_report_important_only"]
            pref.payment_notifications = updated_prefs["payment_notifications"]
            pref.payment_important_only = updated_prefs["payment_important_only"]
            pref.account_management_notifications = updated_prefs["account_management_notifications"]
            pref.account_management_important_only = updated_prefs["account_management_important_only"]
            pref.marketing_emails = updated_prefs["marketing_emails"]
        else:
            pref = NotificationPreference(
                user_id=user_id,
                email_notifications_enabled=updated_prefs["email_notifications_enabled"],
                fmv_report_notifications=updated_prefs["fmv_report_notifications"],
                fmv_report_important_only=updated_prefs["fmv_report_important_only"],
                payment_notifications=updated_prefs["payment_notifications"],
                payment_important_only=updated_prefs["payment_important_only"],
                account_management_notifications=updated_prefs["account_management_notifications"],
                account_management_important_only=updated_prefs["account_management_important_only"],
                marketing_emails=updated_prefs["marketing_emails"]
            )
            db.add(pref)
        
        db.commit()
        
        # Send notification preferences updated email
        try:
            account_email_service.send_notification_preferences_updated_notification(
                user_email=user.email,
                user_name=user.full_name
            )
        except Exception as e:
            logger.error(f"Error sending notification preferences updated email: {e}")
        
        return NotificationPreferencesResponse(
            user_id=user_id,
            **updated_prefs
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification preferences"
        )

