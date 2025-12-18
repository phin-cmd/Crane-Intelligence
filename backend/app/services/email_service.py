"""
Email service for Crane Intelligence Platform
Handles sending emails using Google Workspace SMTP
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
from jinja2 import Environment, FileSystemLoader, Template
import os

from ..core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Email service for sending various types of emails"""
    
    def __init__(self):
        self.smtp_server = settings.mail_server
        self.smtp_port = settings.mail_port
        self.username = settings.mail_username
        self.password = settings.mail_password
        self.use_tls = settings.mail_use_tls
        self.from_name = settings.mail_from_name
        self.from_email = settings.mail_from_email
        
        # Setup Jinja2 environment for email templates
        template_dir = Path(settings.email_templates_dir)
        if template_dir.exists():
            self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        else:
            # Create templates directory if it doesn't exist
            template_dir.mkdir(parents=True, exist_ok=True)
            self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    def _create_smtp_connection(self) -> smtplib.SMTP:
        """Create and configure SMTP connection"""
        try:
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
            # Return a simple fallback template
            return f"""
            <html>
            <body>
                <h2>{context.get('subject', 'Notification from Crane Intelligence')}</h2>
                <p>{context.get('message', 'You have a new notification.')}</p>
                <p>Best regards,<br>Crane Intelligence Team</p>
            </body>
            </html>
            """
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send email to recipients"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = ", ".join(to_emails)
            msg['Subject'] = subject
            
            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Add attachments if provided
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
            
            # Send email
            server = self._create_smtp_connection()
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new user"""
        context = {
            'user_name': user_name,
            'user_email': user_email,
            'subject': 'Welcome to Crane Intelligence Platform!',
            'message': f'Welcome {user_name}! Your account has been successfully created.',
            'login_url': f"{settings.allowed_origins[0]}/login.html"
        }
        
        html_content = self._render_template('welcome.html', context)
        text_content = f"""
        Welcome to Crane Intelligence Platform!
        
        Hello {user_name},
        
        Your account has been successfully created with email: {user_email}
        
        You can now log in to access our comprehensive crane valuation and market analysis tools.
        
        Best regards,
        Crane Intelligence Team
        """
        
        return self.send_email([user_email], context['subject'], html_content, text_content)
    
    def send_password_reset_email(self, user_email: str, user_name: str, reset_token: str) -> bool:
        """Send password reset email"""
        reset_url = f"{settings.allowed_origins[0]}/reset-password.html?token={reset_token}"
        
        context = {
            'user_name': user_name,
            'user_email': user_email,
            'reset_url': reset_url,
            'subject': 'Password Reset Request - Crane Intelligence',
            'message': 'You have requested a password reset for your account.'
        }
        
        html_content = self._render_template('password_reset.html', context)
        text_content = f"""
        Password Reset Request
        
        Hello {user_name},
        
        You have requested a password reset for your Crane Intelligence account.
        
        Click the link below to reset your password:
        {reset_url}
        
        If you didn't request this reset, please ignore this email.
        
        Best regards,
        Crane Intelligence Team
        """
        
        return self.send_email([user_email], context['subject'], html_content, text_content)
    
    def send_valuation_report_email(
        self,
        user_email: str,
        user_name: str,
        report_data: Dict[str, Any],
        report_file_path: Optional[str] = None
    ) -> bool:
        """Send valuation report email"""
        context = {
            'user_name': user_name,
            'user_email': user_email,
            'crane_model': report_data.get('crane_model', 'N/A'),
            'valuation_amount': report_data.get('valuation_amount', 'N/A'),
            'subject': 'Your Crane Valuation Report is Ready',
            'message': 'Your crane valuation report has been generated and is ready for review.'
        }
        
        html_content = self._render_template('valuation_report.html', context)
        text_content = f"""
        Crane Valuation Report
        
        Hello {user_name},
        
        Your crane valuation report for {context['crane_model']} is ready.
        Estimated Value: ${context['valuation_amount']}
        
        Please find the detailed report attached.
        
        Best regards,
        Crane Intelligence Team
        """
        
        attachments = []
        if report_file_path and os.path.exists(report_file_path):
            attachments.append({
                'file_path': report_file_path,
                'filename': f"valuation_report_{report_data.get('crane_model', 'unknown')}.pdf"
            })
        
        return self.send_email([user_email], context['subject'], html_content, text_content, attachments)
    
    def send_notification_email(
        self,
        user_email: str,
        user_name: str,
        notification_type: str,
        message: str,
        action_url: Optional[str] = None
    ) -> bool:
        """Send general notification email"""
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
        text_content = f"""
        {notification_type}
        
        Hello {user_name},
        
        {message}
        
        {f"Action required: {action_url}" if action_url else ""}
        
        Best regards,
        Crane Intelligence Team
        """
        
        return self.send_email([user_email], context['subject'], html_content, text_content)
    
    def send_admin_notification(
        self,
        admin_emails: List[str],
        notification_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send notification to admin users"""
        context = {
            'notification_type': notification_type,
            'message': message,
            'details': details or {},
            'subject': f'Admin Alert: {notification_type}',
            'app_name': settings.app_name
        }
        
        html_content = self._render_template('admin_notification.html', context)
        text_content = f"""
        Admin Alert: {notification_type}
        
        {message}
        
        Details: {details or 'No additional details'}
        
        Please review and take appropriate action.
        
        Best regards,
        Crane Intelligence System
        """
        
        return self.send_email(admin_emails, context['subject'], html_content, text_content)

# Global email service instance
email_service = EmailService()
