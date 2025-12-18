"""
Account Management Email Service
Handles all email notifications for account management actions using Brevo
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .brevo_email_service import BrevoEmailService
from ..core.config import settings

logger = logging.getLogger(__name__)


class AccountEmailService:
    """Email service for account management notifications using Brevo"""
    
    def __init__(self):
        try:
            self.email_service = BrevoEmailService()
        except Exception as e:
            logger.warning(f"Failed to initialize account email service: {e}")
            self.email_service = None
    
    def _extract_first_name(self, user_name: str) -> str:
        """Extract first name from full name"""
        if not user_name:
            return "User"
        return user_name.split()[0] if user_name.split() else user_name
    
    def send_account_deletion_request_notification(
        self, 
        user_email: str, 
        user_name: str,
        deletion_data: Dict[str, Any]
    ) -> bool:
        """Send notification when account deletion is requested"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "request_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "confirmation_url": deletion_data.get('confirmation_url', f"{settings.frontend_url}/account/confirm-deletion"),
                "cancellation_url": deletion_data.get('cancellation_url', f"{settings.frontend_url}/account/cancel-deletion"),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="account_deletion_request.html",
                template_context=template_context,
                subject=f"Account Deletion Request - {settings.app_name}",
                tags=["account-management", "deletion-request"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending account deletion request notification: {e}")
            return False
    
    def send_account_deleted_notification(
        self, 
        user_email: str, 
        user_name: str
    ) -> bool:
        """Send notification when account is deleted"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "deletion_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="account_deleted.html",
                template_context=template_context,
                subject=f"Account Deleted - {settings.app_name}",
                tags=["account-management", "deleted"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending account deleted notification: {e}")
            return False
    
    def send_email_change_request_notification(
        self, 
        user_email: str, 
        user_name: str,
        new_email: str,
        verification_token: str
    ) -> bool:
        """Send notification when email change is requested"""
        if not self.email_service:
            return False
        try:
            verification_url = f"{settings.frontend_url}/verify-email-change?token={verification_token}"
            
            template_context = {
                "username": user_name,
                "user_email": user_email,
                "new_email": new_email,
                "verification_url": verification_url,
                "request_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email
            }
            
            result = self.email_service.send_template_email(
                to_emails=[new_email],  # Send to new email for verification
                template_name="email_change_request.html",
                template_context=template_context,
                subject=f"Email Change Request - {settings.app_name}",
                tags=["account-management", "email-change"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending email change request notification: {e}")
            return False
    
    def send_email_changed_notification(
        self, 
        old_email: str,
        new_email: str, 
        user_name: str
    ) -> bool:
        """Send notification when email is changed"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "old_email": old_email,
                "new_email": new_email,
                "change_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email
            }
            
            # Send to both old and new email
            result1 = self.email_service.send_template_email(
                to_emails=[old_email],
                template_name="email_changed.html",
                template_context=template_context,
                subject=f"Email Address Changed - {settings.app_name}",
                tags=["account-management", "email-changed"]
            )
            
            result2 = self.email_service.send_template_email(
                to_emails=[new_email],
                template_name="email_changed.html",
                template_context=template_context,
                subject=f"Email Address Changed - {settings.app_name}",
                tags=["account-management", "email-changed"]
            )
            
            return result1.get("success", False) or result2.get("success", False)
        except Exception as e:
            logger.error(f"Error sending email changed notification: {e}")
            return False
    
    def send_password_changed_notification(
        self, 
        user_email: str, 
        user_name: str
    ) -> bool:
        """Send notification when password is changed"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "change_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "login_url": f"{settings.frontend_url}/login.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="password_changed.html",
                template_context=template_context,
                subject=f"Password Changed - {settings.app_name}",
                tags=["account-management", "password-changed", "security"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending password changed notification: {e}")
            return False
    
    def send_profile_updated_notification(
        self, 
        user_email: str, 
        user_name: str,
        changes: Dict[str, Any]
    ) -> bool:
        """Send notification when profile is updated (optional)"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "changes": changes,
                "update_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "dashboard_url": f"{settings.frontend_url}/dashboard.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="profile_updated.html",
                template_context=template_context,
                subject=f"Profile Updated - {settings.app_name}",
                tags=["account-management", "profile-updated"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending profile updated notification: {e}")
            return False
    
    def send_subscription_changed_notification(
        self, 
        user_email: str, 
        user_name: str,
        subscription_data: Dict[str, Any]
    ) -> bool:
        """Send notification when subscription tier changes"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "old_tier": subscription_data.get('old_tier', 'N/A'),
                "new_tier": subscription_data.get('new_tier', 'N/A'),
                "change_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "dashboard_url": f"{settings.frontend_url}/dashboard.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="subscription_changed.html",
                template_context=template_context,
                subject=f"Subscription Updated - {settings.app_name}",
                tags=["account-management", "subscription-changed"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending subscription changed notification: {e}")
            return False
    
    def send_notification_preferences_updated_notification(
        self, 
        user_email: str, 
        user_name: str
    ) -> bool:
        """Send notification when notification preferences are updated"""
        if not self.email_service:
            return False
        try:
            first_name = self._extract_first_name(user_name)
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user_email,
                "update_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "preferences_url": f"{settings.frontend_url}/settings.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=[user_email],
                template_name="notification_preferences_updated.html",
                template_context=template_context,
                subject=f"Notification Preferences Updated - {settings.app_name}",
                tags=["account-management", "preferences-updated"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending notification preferences updated notification: {e}")
            return False

