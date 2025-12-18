"""
Centralized Notification Service
Orchestrates all email notifications with preference checking and logging
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from .brevo_email_service import BrevoEmailService
from .fmv_email_service import FMVEmailService
from .payment_email_service import PaymentEmailService
from .account_email_service import AccountEmailService
from .admin_email_service import AdminEmailService
from ..core.config import settings
from ..core.database import SessionLocal

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Centralized notification orchestration service
    Checks user preferences before sending notifications
    Logs all notification attempts
    """
    
    def __init__(self):
        try:
            self.brevo_service = BrevoEmailService()
            self.fmv_email_service = FMVEmailService()
            self.payment_email_service = PaymentEmailService()
            self.account_email_service = AccountEmailService()
            self.admin_email_service = AdminEmailService()
        except Exception as e:
            logger.warning(f"Failed to initialize notification service: {e}")
            self.brevo_service = None
    
    def _get_user_preferences(self, user_id: int, db) -> Dict[str, Any]:
        """Get user notification preferences"""
        try:
            from ..models.notification_preference import NotificationPreference
            from ..models.user import User
            
            # First check if user has notification_preferences JSON field
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.notification_preferences:
                try:
                    return json.loads(user.notification_preferences)
                except:
                    pass
            
            # Fallback to NotificationPreference table
            pref = db.query(NotificationPreference).filter(
                NotificationPreference.user_id == user_id
            ).first()
            
            if pref:
                return {
                    "email_notifications_enabled": pref.email_notifications_enabled,
                    "fmv_report_notifications": pref.fmv_report_notifications,
                    "fmv_report_important_only": pref.fmv_report_important_only,
                    "payment_notifications": pref.payment_notifications,
                    "payment_important_only": pref.payment_important_only,
                    "account_management_notifications": pref.account_management_notifications,
                    "account_management_important_only": pref.account_management_important_only,
                    "marketing_emails": pref.marketing_emails
                }
            
            # Default preferences (all enabled except marketing)
            return {
                "email_notifications_enabled": True,
                "fmv_report_notifications": True,
                "fmv_report_important_only": False,
                "payment_notifications": True,
                "payment_important_only": False,
                "account_management_notifications": True,
                "account_management_important_only": False,
                "marketing_emails": False
            }
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            # Return default preferences on error
            return {
                "email_notifications_enabled": True,
                "fmv_report_notifications": True,
                "fmv_report_important_only": False,
                "payment_notifications": True,
                "payment_important_only": False,
                "account_management_notifications": True,
                "account_management_important_only": False,
                "marketing_emails": False
            }
    
    def _should_send_notification(
        self,
        user_id: Optional[int],
        notification_type: str,
        notification_category: str,
        is_important: bool = False
    ) -> bool:
        """
        Check if notification should be sent based on user preferences
        
        Args:
            user_id: User ID (None for admin notifications)
            notification_type: Type of notification
            notification_category: Category (fmv_report, payment, account_management, marketing)
            is_important: Whether this is an important notification
        
        Returns:
            bool: True if notification should be sent
        """
        # Admin notifications always sent
        if user_id is None:
            return True
        
        # Get user preferences
        db = SessionLocal()
        try:
            preferences = self._get_user_preferences(user_id, db)
            
            if not preferences.get("email_notifications_enabled", True):
                return False
            
            if notification_category == "fmv_report":
                if preferences.get("fmv_report_important_only", False):
                    return is_important
                return preferences.get("fmv_report_notifications", True)
            
            elif notification_category == "payment":
                if preferences.get("payment_important_only", False):
                    return is_important
                return preferences.get("payment_notifications", True)
            
            elif notification_category == "account_management":
                if preferences.get("account_management_important_only", False):
                    return is_important
                return preferences.get("account_management_notifications", True)
            
            elif notification_category == "marketing":
                return preferences.get("marketing_emails", False)
            
            # Default: send all non-marketing notifications
            return notification_category != "marketing"
        finally:
            db.close()
    
    def _log_notification(
        self,
        user_id: Optional[int],
        admin_user_id: Optional[int],
        notification_type: str,
        notification_category: str,
        recipient_email: str,
        subject: str,
        template_name: Optional[str],
        success: bool,
        message_id: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log notification attempt"""
        try:
            from ..models.notification_preference import NotificationLog
            db = SessionLocal()
            try:
                log_entry = NotificationLog(
                    user_id=user_id,
                    admin_user_id=admin_user_id,
                    notification_type=notification_type,
                    notification_category=notification_category,
                    recipient_email=recipient_email,
                    subject=subject,
                    template_name=template_name,
                    success=success,
                    message_id=message_id,
                    error_message=error_message,
                    metadata=metadata
                )
                db.add(log_entry)
                db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error logging notification: {e}")
    
    def send_fmv_report_notification(
        self,
        user_id: int,
        user_email: str,
        user_name: str,
        notification_type: str,
        report_data: Dict[str, Any],
        db=None
    ) -> bool:
        """
        Send FMV report notification with preference checking
        
        Args:
            user_id: User ID
            user_email: User email
            user_name: User name
            notification_type: Type of notification (submitted, paid, in_review, etc.)
            report_data: Report data
            db: Database session (optional)
        
        Returns:
            bool: True if notification sent successfully
        """
        if not self.fmv_email_service:
            return False
        
        # Determine if notification is important
        important_statuses = ["delivered", "rejected", "cancelled", "paid"]
        is_important = notification_type.lower() in important_statuses
        
        # Check preferences
        if db is None:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        
        try:
            if not self._should_send_notification(user_id, notification_type, "fmv_report", is_important):
                logger.info(f"Skipping FMV report notification for user {user_id} due to preferences")
                return False
            
            # Send notification based on type
            result = False
            if notification_type == "submitted":
                result = self.fmv_email_service.send_submitted_notification(
                    user_email, user_name, report_data
                )
            elif notification_type == "payment_pending":
                result = self.fmv_email_service.send_payment_pending_notification(
                    user_email, user_name, report_data
                )
            elif notification_type == "paid":
                result = self.fmv_email_service.send_paid_notification(
                    user_email, user_name, report_data
                )
            elif notification_type == "in_review":
                result = self.fmv_email_service.send_in_review_notification(
                    user_email, user_name, report_data
                )
            elif notification_type == "in_progress":
                result = self.fmv_email_service.send_in_progress_notification(
                    user_email, user_name, report_data
                )
            elif notification_type == "completed":
                result = self.fmv_email_service.send_completed_notification(
                    user_email, user_name, report_data
                )
            elif notification_type == "delivered":
                result = self.fmv_email_service.send_delivered_notification(
                    user_email, user_name, report_data
                )
            elif notification_type == "rejected":
                result = self.fmv_email_service.send_rejected_notification(
                    user_email, user_name, report_data
                )
            elif notification_type == "cancelled":
                result = self.fmv_email_service.send_cancelled_notification(
                    user_email, user_name, report_data
                )
            
            # Log notification
            self._log_notification(
                user_id=user_id,
                admin_user_id=None,
                notification_type=notification_type,
                notification_category="fmv_report",
                recipient_email=user_email,
                subject=f"FMV Report {notification_type.replace('_', ' ').title()} - Report #{report_data.get('report_id')}",
                template_name=f"fmv_report_{notification_type}.html",
                success=result,
                metadata=report_data
            )
            
            return result
        finally:
            if close_db:
                db.close()
    
    def send_payment_notification(
        self,
        user_id: int,
        user_email: str,
        user_name: str,
        notification_type: str,
        payment_data: Dict[str, Any],
        db=None
    ) -> bool:
        """Send payment notification with preference checking"""
        if not self.payment_email_service:
            return False
        
        # Determine if notification is important
        important_types = ["failed", "refunded"]
        is_important = notification_type.lower() in important_types
        
        # Check preferences
        if db is None:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        
        try:
            if not self._should_send_notification(user_id, notification_type, "payment", is_important):
                logger.info(f"Skipping payment notification for user {user_id} due to preferences")
                return False
            
            # Send notification based on type
            result = False
            if notification_type == "initiated":
                result = self.payment_email_service.send_payment_initiated_notification(
                    user_email, user_name, payment_data
                )
            elif notification_type == "success":
                result = self.payment_email_service.send_payment_success_notification(
                    user_email, user_name, payment_data
                )
            elif notification_type == "failed":
                result = self.payment_email_service.send_payment_failed_notification(
                    user_email, user_name, payment_data
                )
            elif notification_type == "cancelled":
                result = self.payment_email_service.send_payment_cancelled_notification(
                    user_email, user_name, payment_data
                )
            elif notification_type == "refunded":
                result = self.payment_email_service.send_payment_refunded_notification(
                    user_email, user_name, payment_data
                )
            elif notification_type == "subscription_success":
                result = self.payment_email_service.send_subscription_payment_success_notification(
                    user_email, user_name, payment_data
                )
            elif notification_type == "subscription_failed":
                result = self.payment_email_service.send_subscription_payment_failed_notification(
                    user_email, user_name, payment_data
                )
            
            # Log notification
            self._log_notification(
                user_id=user_id,
                admin_user_id=None,
                notification_type=notification_type,
                notification_category="payment",
                recipient_email=user_email,
                subject=f"Payment {notification_type.replace('_', ' ').title()} - {settings.app_name}",
                template_name=f"payment_{notification_type}.html" if not notification_type.startswith("subscription") else f"subscription_payment_{notification_type.split('_')[1]}.html",
                success=result,
                metadata=payment_data
            )
            
            return result
        finally:
            if close_db:
                db.close()
    
    def send_account_management_notification(
        self,
        user_id: int,
        user_email: str,
        user_name: str,
        notification_type: str,
        notification_data: Dict[str, Any],
        db=None
    ) -> bool:
        """Send account management notification with preference checking"""
        if not self.account_email_service:
            return False
        
        # Determine if notification is important
        important_types = ["deletion_request", "deleted", "password_changed", "email_changed"]
        is_important = notification_type.lower() in important_types
        
        # Check preferences
        if db is None:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        
        try:
            if not self._should_send_notification(user_id, notification_type, "account_management", is_important):
                logger.info(f"Skipping account management notification for user {user_id} due to preferences")
                return False
            
            # Send notification based on type
            result = False
            if notification_type == "deletion_request":
                result = self.account_email_service.send_account_deletion_request_notification(
                    user_email, user_name, notification_data
                )
            elif notification_type == "deleted":
                result = self.account_email_service.send_account_deleted_notification(
                    user_email, user_name
                )
            elif notification_type == "email_change_request":
                result = self.account_email_service.send_email_change_request_notification(
                    user_email, user_name, notification_data.get("new_email"), notification_data.get("verification_token")
                )
            elif notification_type == "email_changed":
                result = self.account_email_service.send_email_changed_notification(
                    notification_data.get("old_email"), notification_data.get("new_email"), user_name
                )
            elif notification_type == "password_changed":
                result = self.account_email_service.send_password_changed_notification(
                    user_email, user_name
                )
            elif notification_type == "profile_updated":
                result = self.account_email_service.send_profile_updated_notification(
                    user_email, user_name, notification_data.get("changes", {})
                )
            elif notification_type == "subscription_changed":
                result = self.account_email_service.send_subscription_changed_notification(
                    user_email, user_name, notification_data
                )
            elif notification_type == "notification_preferences_updated":
                result = self.account_email_service.send_notification_preferences_updated_notification(
                    user_email, user_name
                )
            
            # Log notification
            self._log_notification(
                user_id=user_id,
                admin_user_id=None,
                notification_type=notification_type,
                notification_category="account_management",
                recipient_email=user_email,
                subject=f"Account {notification_type.replace('_', ' ').title()} - {settings.app_name}",
                template_name=f"{notification_type}.html",
                success=result,
                metadata=notification_data
            )
            
            return result
        finally:
            if close_db:
                db.close()
    
    def send_admin_notification(
        self,
        admin_emails: List[str],
        notification_type: str,
        notification_data: Dict[str, Any],
        db=None
    ) -> bool:
        """Send admin notification (no preference checking)"""
        if not self.admin_email_service:
            return False
        
        try:
            result = False
            if notification_type == "user_registration":
                result = self.admin_email_service.send_admin_user_registration_alert(
                    admin_emails, notification_data, db
                )
            elif notification_type == "system_alert":
                result = self.admin_email_service.send_admin_system_alert(
                    admin_emails, notification_data, db
                )
            elif notification_type == "user_management":
                result = self.admin_email_service.send_admin_user_management_alert(
                    admin_emails, notification_data, db
                )
            elif notification_type == "security_alert":
                result = self.admin_email_service.send_admin_security_alert(
                    admin_emails, notification_data, db
                )
            elif notification_type == "analytics_report":
                result = self.admin_email_service.send_admin_analytics_report(
                    admin_emails, notification_data, db
                )
            
            # Log notifications for each admin
            for admin_email in admin_emails:
                self._log_notification(
                    user_id=None,
                    admin_user_id=None,  # Could be enhanced to get admin_user_id from email
                    notification_type=notification_type,
                    notification_category="admin",
                    recipient_email=admin_email,
                    subject=f"Admin {notification_type.replace('_', ' ').title()} - {settings.app_name}",
                    template_name=f"admin_{notification_type}.html",
                    success=result,
                    metadata=notification_data
                )
            
            return result
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}")
            return False

