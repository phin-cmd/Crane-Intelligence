"""
Unified Email Service for Crane Intelligence Platform
Consolidates: email_service.py and comprehensive_email_service.py
Provides all email capabilities in a single, maintainable module
Supports both sync (SMTP) and async (FastMail) methods
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import asyncio
import os

try:
    from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
    FASTMAIL_AVAILABLE = True
except ImportError:
    FASTMAIL_AVAILABLE = False
    logging.warning("fastapi-mail not available, async methods will use SMTP fallback")

from ..core.config import settings

# Try to import Brevo service
try:
    from .brevo_email_service import BrevoEmailService
    BREVO_AVAILABLE = True
except ImportError:
    BREVO_AVAILABLE = False
    logging.warning("Brevo email service not available")

logger = logging.getLogger(__name__)


class UnifiedEmailService:
    """
    Unified email service supporting both sync and async operations
    Combines features from email_service.py and comprehensive_email_service.py
    """
    
    def __init__(self, prefer_async: bool = True):
        self.prefer_async = prefer_async and FASTMAIL_AVAILABLE
        
        # Check if Brevo API should be used
        self.use_brevo_api = getattr(settings, 'use_brevo_api', False) and BREVO_AVAILABLE and settings.brevo_api_key
        
        # Initialize Brevo service if enabled
        if self.use_brevo_api:
            try:
                self.brevo_service = BrevoEmailService()
                logger.info("Brevo email service initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Brevo service, falling back to SMTP: {e}")
                self.use_brevo_api = False
        
        # SMTP configuration
        self.smtp_server = settings.mail_server
        self.smtp_port = settings.mail_port
        self.username = settings.mail_username
        self.password = settings.mail_password
        self.use_tls = settings.mail_use_tls
        self.use_ssl = getattr(settings, 'mail_use_ssl', False)
        self.from_name = settings.mail_from_name
        self.from_email = settings.mail_from_email
        
        # Setup Jinja2 environment for email templates
        template_dir = Path(settings.email_templates_dir)
        if not template_dir.exists():
            template_dir.mkdir(parents=True, exist_ok=True)
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # FastMail configuration (if available)
        if self.prefer_async and FASTMAIL_AVAILABLE:
            try:
                self.conf = ConnectionConfig(
                    MAIL_USERNAME=self.username,
                    MAIL_PASSWORD=self.password,
                    MAIL_FROM=self.from_email,
                    MAIL_PORT=self.smtp_port,
                    MAIL_SERVER=self.smtp_server,
                    MAIL_FROM_NAME=self.from_name,
                    MAIL_TLS=self.use_tls,
                    MAIL_SSL=self.use_ssl,
                    USE_CREDENTIALS=True,
                    VALIDATE_CERTS=True
                )
                self.fm = FastMail(self.conf)
            except Exception as e:
                logger.warning(f"FastMail initialization failed, using SMTP: {e}")
                self.prefer_async = False
        
        # Email templates mapping
        self.templates = {
            # Main Website Emails
            'user_registration': 'user_registration.html',
            'password_reset': 'password_reset.html',
            'valuation_report': 'valuation_report.html',
            'equipment_inspection': 'equipment_inspection.html',
            'welcome': 'welcome.html',
            'notification': 'notification.html',
            'notification_general': 'notification_general.html',
            'notification_system_maintenance': 'notification_system_maintenance.html',
            
            # Admin Portal Emails
            'admin_user_registration': 'admin_user_registration.html',
            'admin_system_alert': 'admin_system_alert.html',
            'admin_analytics_report': 'admin_analytics_report.html',
            'admin_notification': 'admin_notification.html',
            'admin_user_management': 'admin_user_management.html',
            'admin_security_alert': 'admin_security_alert.html',
            'admin_data_management': 'admin_data_management.html',
            'admin_system_backup': 'admin_system_backup.html',
            'admin_content_management': 'admin_content_management.html',
        }
    
    # ==================== CORE EMAIL METHODS ====================
    
    def _create_smtp_connection(self) -> smtplib.SMTP:
        """Create and configure SMTP connection"""
        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.use_tls:
                    server.starttls()
            server.login(self.username, self.password)
            return server
        except Exception as e:
            logger.error(f"Failed to create SMTP connection: {e}")
            raise
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render email template with context"""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            # Return fallback template
            return f"""
            <html>
            <body>
                <h2>{context.get('subject', 'Notification from Crane Intelligence')}</h2>
                <p>{context.get('message', 'You have a new notification.')}</p>
                <p>Best regards,<br>Crane Intelligence Team</p>
            </body>
            </html>
            """
    
    # ==================== SYNC METHODS ====================
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send email synchronously using Brevo API or SMTP"""
        # Use Brevo API if enabled
        if self.use_brevo_api:
            result = self.brevo_service.send_email(
                to_emails=to_emails,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                attachments=attachments
            )
            return result.get("success", False)
        
        # Fallback to SMTP
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = ", ".join(to_emails)
            msg['Subject'] = subject
            
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            if attachments:
                for attachment in attachments:
                    with open(attachment['file_path'], 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {attachment["filename"]}'
                        )
                        msg.attach(part)
            
            server = self._create_smtp_connection()
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    # ==================== ASYNC METHODS ====================
    
    async def send_email_async(
        self,
        recipients: List[str],
        subject: str,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        html_content: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send email asynchronously using FastMail or SMTP fallback"""
        try:
            # Render template if provided
            if template_name and context:
                html_content = self._render_template(template_name, context)
            elif not html_content:
                raise ValueError("Either template_name+context or html_content must be provided")
            
            # Use FastMail if available and preferred
            if self.prefer_async and FASTMAIL_AVAILABLE:
                message = MessageSchema(
                    subject=subject,
                    recipients=recipients,
                    html_body=html_content,
                    subtype="html",
                    attachments=attachments
                )
                await self.fm.send_message(message)
                logger.info(f"Email sent successfully to {', '.join(recipients)}")
                return {"success": True, "message": f"Email sent to {', '.join(recipients)}"}
            else:
                # Fallback to sync SMTP
                result = self.send_email(recipients, subject, html_content)
                return {"success": result, "message": f"Email sent via SMTP to {', '.join(recipients)}"}
                
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {"success": False, "message": f"Failed to send email: {e}"}
    
    # ==================== MAIN WEBSITE EMAIL METHODS ====================
    
    def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new user (sync)"""
        context = {
            'user_name': user_name,
            'user_email': user_email,
            'subject': 'Welcome to Crane Intelligence Platform!',
            'message': f'Welcome {user_name}! Your account has been successfully created.',
            'login_url': f"{getattr(settings, 'frontend_url', 'https://craneintelligence.tech')}/login.html"
        }
        html_content = self._render_template('welcome.html', context)
        text_content = f"Welcome to Crane Intelligence Platform!\n\nHello {user_name},\n\nYour account has been created."
        return self.send_email([user_email], context['subject'], html_content, text_content)
    
    async def send_user_registration_email(self, user_email: str, username: str, 
                                         account_type: str = "Standard") -> Dict[str, Any]:
        """Send welcome email to new user (async)"""
        subject = "Welcome to Crane Intelligence Platform!"
        context = {
            "username": username,
            "user_email": user_email,
            "account_type": account_type,
            "registration_date": datetime.now().strftime("%B %d, %Y"),
            "dashboard_url": f"{getattr(settings, 'frontend_url', 'https://craneintelligence.tech')}/dashboard.html",
            "platform_name": settings.app_name
        }
        return await self.send_email_async([user_email], subject, self.templates['user_registration'], context)
    
    def send_password_reset_email(self, user_email: str, user_name: str, reset_token: str) -> bool:
        """Send password reset email (sync)"""
        reset_url = f"{getattr(settings, 'frontend_url', 'https://craneintelligence.tech')}/reset-password.html?token={reset_token}"
        context = {
            'user_name': user_name,
            'user_email': user_email,
            'reset_url': reset_url,
            'subject': 'Password Reset Request - Crane Intelligence',
            'message': 'You have requested a password reset for your account.'
        }
        html_content = self._render_template('password_reset.html', context)
        text_content = f"Password Reset Request\n\nHello {user_name},\n\nClick to reset: {reset_url}"
        return self.send_email([user_email], context['subject'], html_content, text_content)
    
    async def send_password_reset_email_async(self, user_email: str, username: str, 
                                            reset_token: str) -> Dict[str, Any]:
        """Send password reset email (async)"""
        subject = "Password Reset Request - Crane Intelligence"
        reset_link = f"{getattr(settings, 'frontend_url', 'https://craneintelligence.tech')}/reset-password.html?token={reset_token}"
        context = {
            "username": username,
            "user_email": user_email,
            "reset_link": reset_link,
            "expiry_hours": 24,
            "platform_name": settings.app_name
        }
        return await self.send_email_async([user_email], subject, self.templates['password_reset'], context)
    
    def send_valuation_report_email(
        self,
        user_email: str,
        user_name: str,
        report_data: Dict[str, Any],
        report_file_path: Optional[str] = None
    ) -> bool:
        """Send valuation report email (sync)"""
        context = {
            'user_name': user_name,
            'user_email': user_email,
            'crane_model': report_data.get('crane_model', 'N/A'),
            'valuation_amount': report_data.get('valuation_amount', 'N/A'),
            'subject': 'Your Crane Valuation Report is Ready',
            'message': 'Your crane valuation report has been generated.'
        }
        html_content = self._render_template('valuation_report.html', context)
        text_content = f"Crane Valuation Report\n\nHello {user_name},\n\nReport for {context['crane_model']} is ready."
        
        attachments = []
        if report_file_path and os.path.exists(report_file_path):
            attachments.append({
                'file_path': report_file_path,
                'filename': f"valuation_report_{report_data.get('crane_model', 'unknown')}.pdf"
            })
        
        return self.send_email([user_email], context['subject'], html_content, text_content, attachments)
    
    async def send_valuation_report_email_async(self, user_email: str, username: str, 
                                              report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send valuation report email (async)"""
        subject = f"Your Valuation Report is Ready - {report_data.get('equipment_name', 'Equipment')}"
        context = {
            "username": username,
            "user_email": user_email,
            "report_id": report_data.get('report_id'),
            "generation_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "equipment_name": report_data.get('equipment_name'),
            "valuation_type": report_data.get('valuation_type', 'Standard'),
            "estimated_value": report_data.get('estimated_value', 'N/A'),
            "confidence_level": report_data.get('confidence_level', 85),
            "manufacturer": report_data.get('manufacturer'),
            "model": report_data.get('model'),
            "year": report_data.get('year'),
            "operating_hours": report_data.get('operating_hours'),
            "condition": report_data.get('condition'),
            "report_link": f"{getattr(settings, 'frontend_url', 'https://craneintelligence.tech')}/reports/{report_data.get('report_id')}",
            "platform_name": settings.app_name
        }
        return await self.send_email_async([user_email], subject, self.templates['valuation_report'], context)
    
    def send_notification_email(
        self,
        user_email: str,
        user_name: str,
        notification_type: str,
        message: str,
        action_url: Optional[str] = None
    ) -> bool:
        """Send general notification email (sync)"""
        context = {
            'user_name': user_name,
            'user_email': user_email,
            'notification_type': notification_type,
            'message': message,
            'action_url': action_url,
            'subject': f'Notification: {notification_type}',
            'app_name': settings.app_name
        }
        html_content = self._render_template('notification.html', context)
        text_content = f"{notification_type}\n\nHello {user_name},\n\n{message}"
        return self.send_email([user_email], context['subject'], html_content, text_content)
    
    async def send_general_notification(self, user_email: str, username: str, 
                                      notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send general notification email (async)"""
        subject = f"Notification: {notification_data.get('notification_title')}"
        context = {
            "username": username,
            "user_email": user_email,
            "notification_type": notification_data.get('notification_type'),
            "priority": notification_data.get('priority'),
            "notification_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "category": notification_data.get('category'),
            "priority_level": notification_data.get('priority_level', 'medium'),
            "notification_title": notification_data.get('notification_title'),
            "notification_message": notification_data.get('notification_message'),
            "action_url": notification_data.get('action_url'),
            "dashboard_url": f"{getattr(settings, 'frontend_url', 'https://craneintelligence.tech')}/dashboard.html",
            "platform_name": settings.app_name
        }
        return await self.send_email_async([user_email], subject, self.templates['notification_general'], context)
    
    def send_admin_notification(
        self,
        admin_emails: List[str],
        notification_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send notification to admin users (sync)"""
        context = {
            'notification_type': notification_type,
            'message': message,
            'details': details or {},
            'subject': f'Admin Alert: {notification_type}',
            'app_name': settings.app_name
        }
        html_content = self._render_template('admin_notification.html', context)
        text_content = f"Admin Alert: {notification_type}\n\n{message}"
        return self.send_email(admin_emails, context['subject'], html_content, text_content)
    
    # ==================== ADMIN PORTAL EMAIL METHODS ====================
    
    async def send_admin_user_registration_alert(self, admin_emails: List[str], 
                                                user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send admin alert for new user registration"""
        subject = f"New User Registration Alert - {user_data.get('user_name')}"
        context = {
            "user_name": user_data.get('user_name'),
            "user_email": user_data.get('user_email'),
            "company_name": user_data.get('company_name'),
            "registration_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "account_type": user_data.get('account_type'),
            "admin_user_management_url": f"{getattr(settings, 'admin_url', 'https://craneintelligence.tech')}/admin/users.html",
            "platform_name": settings.app_name
        }
        return await self.send_email_async(admin_emails, subject, self.templates['admin_user_registration'], context)
    
    async def send_admin_system_alert(self, admin_emails: List[str], 
                                     alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send system alert to admins"""
        subject = f"System Alert: {alert_data.get('alert_type')} - {alert_data.get('alert_level')}"
        context = {
            "alert_type": alert_data.get('alert_type'),
            "alert_level": alert_data.get('alert_level'),
            "alert_timestamp": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "alert_description": alert_data.get('alert_description'),
            "admin_dashboard_url": f"{getattr(settings, 'admin_url', 'https://craneintelligence.tech')}/admin/dashboard.html",
            "platform_name": settings.app_name
        }
        return await self.send_email_async(admin_emails, subject, self.templates['admin_system_alert'], context)
    
    async def send_admin_analytics_report(self, admin_emails: List[str], 
                                        analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send weekly analytics report to admins"""
        subject = f"Weekly Analytics Report - {analytics_data.get('report_period')}"
        context = {
            "report_period": analytics_data.get('report_period'),
            "generation_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "total_users": analytics_data.get('total_users', 0),
            "new_users_week": analytics_data.get('new_users_week', 0),
            "total_valuations": analytics_data.get('total_valuations', 0),
            "analytics_dashboard_url": f"{getattr(settings, 'admin_url', 'https://craneintelligence.tech')}/admin/analytics.html",
            "platform_name": settings.app_name
        }
        return await self.send_email_async(admin_emails, subject, self.templates['admin_analytics_report'], context)
    
    async def send_equipment_inspection_email(self, user_email: str, username: str, 
                                             inspection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send equipment inspection scheduled email"""
        subject = "Equipment Inspection Scheduled - Crane Intelligence"
        context = {
            "username": username,
            "user_email": user_email,
            "equipment_name": inspection_data.get('equipment_name'),
            "inspection_date": inspection_data.get('inspection_date'),
            "inspection_time": inspection_data.get('inspection_time'),
            "platform_name": settings.app_name
        }
        return await self.send_email_async([user_email], subject, self.templates['equipment_inspection'], context)
    
    async def send_system_maintenance_notification(self, user_emails: List[str], 
                                                  maintenance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send system maintenance notification"""
        subject = f"Scheduled Maintenance: {maintenance_data.get('maintenance_date')}"
        context = {
            "maintenance_date": maintenance_data.get('maintenance_date'),
            "start_time": maintenance_data.get('start_time'),
            "end_time": maintenance_data.get('end_time'),
            "platform_name": settings.app_name
        }
        return await self.send_email_async(user_emails, subject, self.templates['notification_system_maintenance'], context)
    
    async def send_bulk_notifications(self, user_emails: List[str], 
                                    notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send bulk notifications to multiple users"""
        results = []
        for email in user_emails:
            result = await self.send_general_notification(
                email, 
                notification_data.get('username', 'User'), 
                notification_data
            )
            results.append(result)
        
        success_count = sum(1 for r in results if r.get('success', False))
        return {
            "success": success_count > 0,
            "message": f"Sent {success_count}/{len(user_emails)} notifications successfully",
            "results": results
        }
    
    # Additional admin methods (simplified signatures)
    async def send_admin_user_management_alert(self, admin_emails: List[str], **kwargs) -> Dict[str, Any]:
        """Send admin alert for user management actions"""
        subject = f"User Management Action: {kwargs.get('action_type')} - {settings.app_name}"
        context = {
            "platform_name": settings.app_name,
            "action_type": kwargs.get('action_type'),
            "admin_name": kwargs.get('admin_name'),
            "username": kwargs.get('username'),
            "user_email": kwargs.get('user_email'),
            "action_description": kwargs.get('action_description'),
            **kwargs
        }
        return await self.send_email_async(admin_emails, subject, self.templates['admin_user_management'], context)
    
    async def send_admin_security_alert(self, admin_emails: List[str], **kwargs) -> Dict[str, Any]:
        """Send admin security alert"""
        subject = f"Security Alert: {kwargs.get('alert_type')} - {settings.app_name}"
        context = {
            "platform_name": settings.app_name,
            "alert_type": kwargs.get('alert_type'),
            "alert_level": kwargs.get('alert_level'),
            "alert_description": kwargs.get('alert_description'),
            **kwargs
        }
        return await self.send_email_async(admin_emails, subject, self.templates['admin_security_alert'], context)
    
    async def send_admin_data_management_alert(self, admin_emails: List[str], **kwargs) -> Dict[str, Any]:
        """Send admin data management alert"""
        subject = f"Data Management Action: {kwargs.get('action_type')} - {settings.app_name}"
        context = {
            "platform_name": settings.app_name,
            "action_type": kwargs.get('action_type'),
            **kwargs
        }
        return await self.send_email_async(admin_emails, subject, self.templates['admin_data_management'], context)
    
    async def send_admin_system_backup_notification(self, admin_emails: List[str], **kwargs) -> Dict[str, Any]:
        """Send admin system backup notification"""
        subject = f"System Backup {kwargs.get('backup_status')}: {kwargs.get('backup_name')} - {settings.app_name}"
        context = {
            "platform_name": settings.app_name,
            "backup_status": kwargs.get('backup_status'),
            **kwargs
        }
        return await self.send_email_async(admin_emails, subject, self.templates['admin_system_backup'], context)
    
    async def send_admin_content_management_alert(self, admin_emails: List[str], **kwargs) -> Dict[str, Any]:
        """Send admin content management alert"""
        subject = f"Content Management Action: {kwargs.get('action_type')} - {settings.app_name}"
        context = {
            "platform_name": settings.app_name,
            "action_type": kwargs.get('action_type'),
            **kwargs
        }
        return await self.send_email_async(admin_emails, subject, self.templates['admin_content_management'], context)


# ==================== BACKWARD COMPATIBILITY ====================

# Global instances for backward compatibility
email_service = UnifiedEmailService(prefer_async=False)  # Sync by default
comprehensive_email_service = UnifiedEmailService(prefer_async=True)  # Async by default

