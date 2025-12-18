"""
Admin Email Service
Handles all email notifications for admin users and admin actions using Brevo
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .brevo_email_service import BrevoEmailService
from ..core.config import settings

logger = logging.getLogger(__name__)


class AdminEmailService:
    """Email service for admin notifications using Brevo"""
    
    def __init__(self):
        try:
            self.email_service = BrevoEmailService()
        except Exception as e:
            logger.warning(f"Failed to initialize admin email service: {e}")
            self.email_service = None
    
    def _get_admin_emails(self, db) -> List[str]:
        """Get all active admin email addresses"""
        try:
            from ...models.admin import AdminUser
            admin_users = db.query(AdminUser).filter(
                AdminUser.is_active == True,
                AdminUser.is_verified == True
            ).all()
            return [admin.email for admin in admin_users]
        except Exception as e:
            logger.error(f"Error getting admin emails: {e}")
            return []
    
    def send_admin_user_registration_alert(
        self,
        admin_emails: List[str],
        user_data: Dict[str, Any],
        db=None
    ) -> bool:
        """Send admin alert for new user registration"""
        if not self.email_service:
            return False
        try:
            if not admin_emails and db:
                admin_emails = self._get_admin_emails(db)
            
            if not admin_emails:
                return False
            
            template_context = {
                "user_name": user_data.get('user_name'),
                "user_email": user_data.get('user_email'),
                "username": user_data.get('username'),
                "company_name": user_data.get('company_name'),
                "registration_date": user_data.get('registration_date', datetime.now().strftime('%B %d, %Y at %I:%M %p')),
                "account_type": user_data.get('account_type'),
                "user_role": user_data.get('user_role'),
                "admin_user_management_url": f"{settings.admin_url}/admin/users.html",
                "platform_name": settings.app_name
            }
            
            result = self.email_service.send_template_email(
                to_emails=admin_emails,
                template_name="admin_user_registration.html",
                template_context=template_context,
                subject=f"New User Registration: {user_data.get('user_name')}",
                tags=["admin-notification", "user-registration"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending admin user registration alert: {e}")
            return False
    
    def send_admin_system_alert(
        self,
        admin_emails: List[str],
        alert_data: Dict[str, Any],
        db=None
    ) -> bool:
        """Send system alert to admins"""
        if not self.email_service:
            return False
        try:
            if not admin_emails and db:
                admin_emails = self._get_admin_emails(db)
            
            if not admin_emails:
                return False
            
            template_context = {
                "alert_type": alert_data.get('alert_type'),
                "alert_level": alert_data.get('alert_level'),
                "alert_timestamp": alert_data.get('alert_timestamp', datetime.now().strftime('%B %d, %Y at %I:%M %p')),
                "alert_description": alert_data.get('alert_description'),
                "admin_dashboard_url": f"{settings.admin_url}/admin/dashboard.html",
                "platform_name": settings.app_name,
                **alert_data
            }
            
            result = self.email_service.send_template_email(
                to_emails=admin_emails,
                template_name="admin_system_alert.html",
                template_context=template_context,
                subject=f"System Alert: {alert_data.get('alert_type')} - {alert_data.get('alert_level')}",
                tags=["admin-notification", "system-alert", alert_data.get('alert_level', 'medium').lower()]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending admin system alert: {e}")
            return False
    
    def send_admin_user_management_alert(
        self,
        admin_emails: List[str],
        action_data: Dict[str, Any],
        db=None
    ) -> bool:
        """Send admin alert for user management actions"""
        if not self.email_service:
            return False
        try:
            if not admin_emails and db:
                admin_emails = self._get_admin_emails(db)
            
            if not admin_emails:
                return False
            
            template_context = {
                "platform_name": settings.app_name,
                "action_type": action_data.get('action_type'),
                "admin_name": action_data.get('admin_name'),
                "username": action_data.get('username'),
                "user_email": action_data.get('user_email'),
                "action_description": action_data.get('action_description'),
                "action_timestamp": action_data.get('action_timestamp', datetime.now().strftime('%B %d, %Y at %I:%M %p')),
                "admin_users_url": f"{settings.admin_url}/admin/users.html",
                **action_data
            }
            
            result = self.email_service.send_template_email(
                to_emails=admin_emails,
                template_name="admin_user_management.html",
                template_context=template_context,
                subject=f"User Management Action: {action_data.get('action_type')} - {settings.app_name}",
                tags=["admin-notification", "user-management", action_data.get('action_type', '').lower()]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending admin user management alert: {e}")
            return False
    
    def send_admin_security_alert(
        self,
        admin_emails: List[str],
        alert_data: Dict[str, Any],
        db=None
    ) -> bool:
        """Send admin security alert"""
        if not self.email_service:
            return False
        try:
            if not admin_emails and db:
                admin_emails = self._get_admin_emails(db)
            
            if not admin_emails:
                return False
            
            template_context = {
                "platform_name": settings.app_name,
                "alert_type": alert_data.get('alert_type'),
                "alert_level": alert_data.get('alert_level'),
                "alert_description": alert_data.get('alert_description'),
                "alert_timestamp": alert_data.get('alert_timestamp', datetime.now().strftime('%B %d, %Y at %I:%M %p')),
                "security_dashboard_url": f"{settings.admin_url}/admin/security.html",
                **alert_data
            }
            
            result = self.email_service.send_template_email(
                to_emails=admin_emails,
                template_name="admin_security_alert.html",
                template_context=template_context,
                subject=f"Security Alert: {alert_data.get('alert_type')} - {settings.app_name}",
                tags=["admin-notification", "security-alert", alert_data.get('alert_level', 'medium').lower()]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending admin security alert: {e}")
            return False
    
    def send_admin_analytics_report(
        self,
        admin_emails: List[str],
        analytics_data: Dict[str, Any],
        db=None
    ) -> bool:
        """Send analytics report to admins"""
        if not self.email_service:
            return False
        try:
            if not admin_emails and db:
                admin_emails = self._get_admin_emails(db)
            
            if not admin_emails:
                return False
            
            template_context = {
                "report_period": analytics_data.get('report_period'),
                "generation_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "analytics_dashboard_url": f"{settings.admin_url}/admin/analytics.html",
                "platform_name": settings.app_name,
                **analytics_data
            }
            
            result = self.email_service.send_template_email(
                to_emails=admin_emails,
                template_name="admin_analytics_report.html",
                template_context=template_context,
                subject=f"Weekly Analytics Report - {analytics_data.get('report_period')}",
                tags=["admin-notification", "analytics-report"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending admin analytics report: {e}")
            return False
    
    def send_admin_account_settings_changed_notification(
        self,
        admin_email: str,
        admin_name: str,
        changes: Dict[str, Any]
    ) -> bool:
        """Send notification when admin account settings are changed"""
        if not self.email_service:
            return False
        try:
            template_context = {
                "username": admin_name,
                "user_email": admin_email,
                "changes": changes,
                "update_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "admin_dashboard_url": f"{settings.admin_url}/admin/dashboard.html"
            }
            
            result = self.email_service.send_template_email(
                to_emails=[admin_email],
                template_name="admin_account_settings_changed.html",
                template_context=template_context,
                subject=f"Admin Account Settings Changed - {settings.app_name}",
                tags=["admin-notification", "account-settings"]
            )
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error sending admin account settings changed notification: {e}")
            return False

