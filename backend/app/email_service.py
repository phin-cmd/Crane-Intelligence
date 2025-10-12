"""
Comprehensive Email Service for Crane Intelligence Platform
Handles all email communications including verification, notifications, and alerts
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import secrets
import logging
from typing import Optional, List
import jwt
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

# Configure logging
logger = logging.getLogger(__name__)

# Email configuration
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "pgenerelly@craneintelligence.tech")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "your-gmail-app-password-here")
MAIL_FROM = os.getenv("MAIL_FROM", "pgenerelly@craneintelligence.tech")
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"

# Company information
COMPANY_NAME = os.getenv("COMPANY_NAME", "Crane Intelligence")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "pgenerelly@craneintelligence.tech")
WEBSITE_URL = os.getenv("WEBSITE_URL", "https://craneintelligence.tech")

# Security settings
EMAIL_VERIFICATION_EXPIRE_HOURS = int(os.getenv("EMAIL_VERIFICATION_EXPIRE_HOURS", "24"))
PASSWORD_RESET_EXPIRE_HOURS = int(os.getenv("PASSWORD_RESET_EXPIRE_HOURS", "1"))

class EmailService:
    """Comprehensive email service for Crane Intelligence"""
    
    def __init__(self):
        self.smtp_server = None
        self.smtp_port = MAIL_PORT
        self.username = MAIL_USERNAME
        self.password = MAIL_PASSWORD
        self.from_email = MAIL_FROM
        
    def _create_smtp_connection(self):
        """Create SMTP connection"""
        try:
            context = ssl.create_default_context()
            server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
            if MAIL_USE_TLS:
                server.starttls(context=context)
            server.login(self.username, self.password)
            return server
        except Exception as e:
            logger.error(f"Failed to create SMTP connection: {str(e)}")
            return None
    
    def _send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Send email with HTML and text content"""
        try:
            server = self._create_smtp_connection()
            if not server:
                return False
                
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def _get_email_template(self, template_name: str, **kwargs) -> tuple:
        """Get email template with subject and content"""
        templates = {
            'welcome': self._get_welcome_template(**kwargs),
            'verification': self._get_verification_template(**kwargs),
            'password_reset': self._get_password_reset_template(**kwargs),
            'consultation_confirmation': self._get_consultation_confirmation_template(**kwargs),
            'admin_new_user': self._get_admin_new_user_template(**kwargs),
            'admin_consultation': self._get_admin_consultation_template(**kwargs),
            'subscription_confirmation': self._get_subscription_confirmation_template(**kwargs),
            'report_generated': self._get_report_generated_template(**kwargs),
            'alert_notification': self._get_alert_notification_template(**kwargs),
            'admin_communication': self._get_admin_communication_template(**kwargs)
        }
        return templates.get(template_name, ("", "", ""))
    
    def _get_welcome_template(self, user_name: str, **kwargs) -> tuple:
        """Welcome email template"""
        subject = f"Welcome to {COMPANY_NAME}!"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Welcome to {COMPANY_NAME}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ background: #34495e; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                .button {{ background: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to {COMPANY_NAME}!</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>Welcome to {COMPANY_NAME} - your premier platform for crane valuation and market analysis!</p>
                    <p>Your account has been successfully created. You can now access all our features:</p>
                    <ul>
                        <li>Professional crane valuations</li>
                        <li>Real-time market analysis</li>
                        <li>Equipment listings and comparisons</li>
                        <li>Expert consultations</li>
                    </ul>
                    <p style="text-align: center;">
                        <a href="{WEBSITE_URL}/dashboard.html" class="button">Access Your Dashboard</a>
                    </p>
                    <p>If you have any questions, feel free to contact our support team.</p>
                </div>
                <div class="footer">
                    <p>{COMPANY_NAME} | {WEBSITE_URL}</p>
                    <p>Contact: {SUPPORT_EMAIL}</p>
                </div>
            </div>
        </body>
        </html>
        """
        text_content = f"""
        Welcome to {COMPANY_NAME}!
        
        Hello {user_name},
        
        Welcome to {COMPANY_NAME} - your premier platform for crane valuation and market analysis!
        
        Your account has been successfully created. You can now access all our features:
        - Professional crane valuations
        - Real-time market analysis
        - Equipment listings and comparisons
        - Expert consultations
        
        Access your dashboard: {WEBSITE_URL}/dashboard.html
        
        If you have any questions, feel free to contact our support team.
        
        {COMPANY_NAME} | {WEBSITE_URL}
        Contact: {SUPPORT_EMAIL}
        """
        return subject, html_content, text_content
    
    def _get_verification_template(self, user_name: str, verification_token: str, **kwargs) -> tuple:
        """Email verification template"""
        subject = f"Verify Your Email - {COMPANY_NAME}"
        verification_url = f"{WEBSITE_URL}/verify-email?token={verification_token}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Verify Your Email</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #e74c3c; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ background: #34495e; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                .button {{ background: #27ae60; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }}
                .warning {{ background: #f39c12; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Verify Your Email Address</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>Thank you for registering with {COMPANY_NAME}!</p>
                    <p>To complete your registration and activate your account, please verify your email address by clicking the button below:</p>
                    <p style="text-align: center;">
                        <a href="{verification_url}" class="button">Verify Email Address</a>
                    </p>
                    <div class="warning">
                        <strong>Important:</strong> This verification link will expire in {EMAIL_VERIFICATION_EXPIRE_HOURS} hours.
                    </div>
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background: #ecf0f1; padding: 10px; border-radius: 5px;">
                        {verification_url}
                    </p>
                </div>
                <div class="footer">
                    <p>{COMPANY_NAME} | {WEBSITE_URL}</p>
                    <p>Contact: {SUPPORT_EMAIL}</p>
                </div>
            </div>
        </body>
        </html>
        """
        text_content = f"""
        Verify Your Email Address - {COMPANY_NAME}
        
        Hello {user_name},
        
        Thank you for registering with {COMPANY_NAME}!
        
        To complete your registration and activate your account, please verify your email address by visiting this link:
        {verification_url}
        
        Important: This verification link will expire in {EMAIL_VERIFICATION_EXPIRE_HOURS} hours.
        
        {COMPANY_NAME} | {WEBSITE_URL}
        Contact: {SUPPORT_EMAIL}
        """
        return subject, html_content, text_content
    
    def _get_password_reset_template(self, user_name: str, reset_token: str, **kwargs) -> tuple:
        """Password reset template"""
        subject = f"Password Reset Request - {COMPANY_NAME}"
        reset_url = f"{WEBSITE_URL}/reset-password?token={reset_token}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Password Reset</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #f39c12; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ background: #34495e; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                .button {{ background: #e74c3c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }}
                .warning {{ background: #e74c3c; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>We received a request to reset your password for your {COMPANY_NAME} account.</p>
                    <p>To reset your password, click the button below:</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </p>
                    <div class="warning">
                        <strong>Security Notice:</strong> This link will expire in {PASSWORD_RESET_EXPIRE_HOURS} hour(s) for your security.
                    </div>
                    <p>If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; background: #ecf0f1; padding: 10px; border-radius: 5px;">
                        {reset_url}
                    </p>
                </div>
                <div class="footer">
                    <p>{COMPANY_NAME} | {WEBSITE_URL}</p>
                    <p>Contact: {SUPPORT_EMAIL}</p>
                </div>
            </div>
        </body>
        </html>
        """
        text_content = f"""
        Password Reset Request - {COMPANY_NAME}
        
        Hello {user_name},
        
        We received a request to reset your password for your {COMPANY_NAME} account.
        
        To reset your password, visit this link:
        {reset_url}
        
        Security Notice: This link will expire in {PASSWORD_RESET_EXPIRE_HOURS} hour(s) for your security.
        
        If you didn't request this password reset, please ignore this email. Your password will remain unchanged.
        
        {COMPANY_NAME} | {WEBSITE_URL}
        Contact: {SUPPORT_EMAIL}
        """
        return subject, html_content, text_content
    
    def _get_consultation_confirmation_template(self, user_name: str, consultation_id: str, **kwargs) -> tuple:
        """Consultation confirmation template"""
        subject = f"Consultation Request Received - {COMPANY_NAME}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Consultation Confirmation</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #27ae60; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ background: #34495e; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                .info-box {{ background: #3498db; color: white; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Consultation Request Received</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>Thank you for your consultation request with {COMPANY_NAME}!</p>
                    <div class="info-box">
                        <strong>Consultation ID:</strong> #{consultation_id}<br>
                        <strong>Status:</strong> Under Review<br>
                        <strong>Expected Response:</strong> Within 24 hours
                    </div>
                    <p>Our expert team will review your request and get back to you with detailed recommendations.</p>
                    <p>You can track your consultation status by logging into your dashboard.</p>
                </div>
                <div class="footer">
                    <p>{COMPANY_NAME} | {WEBSITE_URL}</p>
                    <p>Contact: {SUPPORT_EMAIL}</p>
                </div>
            </div>
        </body>
        </html>
        """
        text_content = f"""
        Consultation Request Received - {COMPANY_NAME}
        
        Hello {user_name},
        
        Thank you for your consultation request with {COMPANY_NAME}!
        
        Consultation ID: #{consultation_id}
        Status: Under Review
        Expected Response: Within 24 hours
        
        Our expert team will review your request and get back to you with detailed recommendations.
        
        You can track your consultation status by logging into your dashboard.
        
        {COMPANY_NAME} | {WEBSITE_URL}
        Contact: {SUPPORT_EMAIL}
        """
        return subject, html_content, text_content
    
    def _get_admin_new_user_template(self, user_name: str, user_email: str, **kwargs) -> tuple:
        """Admin notification for new user registration"""
        subject = f"New User Registration - {COMPANY_NAME}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>New User Registration</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #9b59b6; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ background: #34495e; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                .user-info {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>New User Registration</h1>
                </div>
                <div class="content">
                    <h2>New User Registered</h2>
                    <div class="user-info">
                        <strong>Name:</strong> {user_name}<br>
                        <strong>Email:</strong> {user_email}<br>
                        <strong>Registration Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                    <p>A new user has registered on the {COMPANY_NAME} platform.</p>
                    <p>You can view user details in the admin dashboard.</p>
                </div>
                <div class="footer">
                    <p>{COMPANY_NAME} Admin Panel</p>
                </div>
            </div>
        </body>
        </html>
        """
        text_content = f"""
        New User Registration - {COMPANY_NAME}
        
        New User Registered:
        Name: {user_name}
        Email: {user_email}
        Registration Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        A new user has registered on the {COMPANY_NAME} platform.
        You can view user details in the admin dashboard.
        
        {COMPANY_NAME} Admin Panel
        """
        return subject, html_content, text_content
    
    def _get_admin_consultation_template(self, user_name: str, user_email: str, consultation_id: str, message: str, **kwargs) -> tuple:
        """Admin notification for new consultation"""
        subject = f"New Consultation Request - {COMPANY_NAME}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>New Consultation Request</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #e67e22; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ background: #34495e; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                .consultation-info {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .message-box {{ background: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>New Consultation Request</h1>
                </div>
                <div class="content">
                    <h2>Consultation Request Received</h2>
                    <div class="consultation-info">
                        <strong>Consultation ID:</strong> #{consultation_id}<br>
                        <strong>User Name:</strong> {user_name}<br>
                        <strong>User Email:</strong> {user_email}<br>
                        <strong>Request Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                    <h3>Message:</h3>
                    <div class="message-box">
                        {message}
                    </div>
                    <p>Please review and respond to this consultation request.</p>
                </div>
                <div class="footer">
                    <p>{COMPANY_NAME} Admin Panel</p>
                </div>
            </div>
        </body>
        </html>
        """
        text_content = f"""
        New Consultation Request - {COMPANY_NAME}
        
        Consultation Request Received:
        Consultation ID: #{consultation_id}
        User Name: {user_name}
        User Email: {user_email}
        Request Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Message:
        {message}
        
        Please review and respond to this consultation request.
        
        {COMPANY_NAME} Admin Panel
        """
        return subject, html_content, text_content
    
    def _get_subscription_confirmation_template(self, user_name: str, subscription_plan: str, **kwargs) -> tuple:
        """Subscription confirmation template"""
        subject = f"Subscription Confirmed - {COMPANY_NAME}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Subscription Confirmed</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #27ae60; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ background: #34495e; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                .subscription-info {{ background: #2ecc71; color: white; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Subscription Confirmed</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>Your subscription has been successfully confirmed!</p>
                    <div class="subscription-info">
                        <strong>Plan:</strong> {subscription_plan}<br>
                        <strong>Status:</strong> Active<br>
                        <strong>Activation Date:</strong> {datetime.now().strftime('%Y-%m-%d')}
                    </div>
                    <p>You now have access to all premium features of {COMPANY_NAME}.</p>
                </div>
                <div class="footer">
                    <p>{COMPANY_NAME} | {WEBSITE_URL}</p>
                    <p>Contact: {SUPPORT_EMAIL}</p>
                </div>
            </div>
        </body>
        </html>
        """
        text_content = f"""
        Subscription Confirmed - {COMPANY_NAME}
        
        Hello {user_name},
        
        Your subscription has been successfully confirmed!
        
        Plan: {subscription_plan}
        Status: Active
        Activation Date: {datetime.now().strftime('%Y-%m-%d')}
        
        You now have access to all premium features of {COMPANY_NAME}.
        
        {COMPANY_NAME} | {WEBSITE_URL}
        Contact: {SUPPORT_EMAIL}
        """
        return subject, html_content, text_content
    
    def _get_report_generated_template(self, user_name: str, report_name: str, download_url: str, **kwargs) -> tuple:
        """Report generation notification template"""
        subject = f"Report Generated - {COMPANY_NAME}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Report Generated</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #8e44ad; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ background: #34495e; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                .button {{ background: #8e44ad; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Report Generated</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>Your requested report has been generated and is ready for download.</p>
                    <p><strong>Report Name:</strong> {report_name}</p>
                    <p style="text-align: center;">
                        <a href="{download_url}" class="button">Download Report</a>
                    </p>
                    <p><em>Note: This download link will expire in 7 days for security reasons.</em></p>
                </div>
                <div class="footer">
                    <p>{COMPANY_NAME} | {WEBSITE_URL}</p>
                    <p>Contact: {SUPPORT_EMAIL}</p>
                </div>
            </div>
        </body>
        </html>
        """
        text_content = f"""
        Report Generated - {COMPANY_NAME}
        
        Hello {user_name},
        
        Your requested report has been generated and is ready for download.
        
        Report Name: {report_name}
        Download Link: {download_url}
        
        Note: This download link will expire in 7 days for security reasons.
        
        {COMPANY_NAME} | {WEBSITE_URL}
        Contact: {SUPPORT_EMAIL}
        """
        return subject, html_content, text_content
    
    def _get_alert_notification_template(self, user_name: str, alert_type: str, alert_message: str, **kwargs) -> tuple:
        """Alert notification template"""
        subject = f"Alert: {alert_type} - {COMPANY_NAME}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Alert Notification</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #e74c3c; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ background: #34495e; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                .alert-box {{ background: #f39c12; color: white; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Alert Notification</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <div class="alert-box">
                        <strong>Alert Type:</strong> {alert_type}<br>
                        <strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                    <p>{alert_message}</p>
                </div>
                <div class="footer">
                    <p>{COMPANY_NAME} | {WEBSITE_URL}</p>
                    <p>Contact: {SUPPORT_EMAIL}</p>
                </div>
            </div>
        </body>
        </html>
        """
        text_content = f"""
        Alert: {alert_type} - {COMPANY_NAME}
        
        Hello {user_name},
        
        Alert Type: {alert_type}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        {alert_message}
        
        {COMPANY_NAME} | {WEBSITE_URL}
        Contact: {SUPPORT_EMAIL}
        """
        return subject, html_content, text_content
    
    def _get_admin_communication_template(self, admin_name: str, message: str, **kwargs) -> tuple:
        """Admin communication template"""
        subject = f"Admin Communication - {COMPANY_NAME}"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Admin Communication</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #34495e; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ background: #34495e; color: white; padding: 15px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Admin Communication</h1>
                </div>
                <div class="content">
                    <h2>From: {admin_name}</h2>
                    <p>{message}</p>
                </div>
                <div class="footer">
                    <p>{COMPANY_NAME} Admin Panel</p>
                </div>
            </div>
        </body>
        </html>
        """
        text_content = f"""
        Admin Communication - {COMPANY_NAME}
        
        From: {admin_name}
        
        {message}
        
        {COMPANY_NAME} Admin Panel
        """
        return subject, html_content, text_content
    
    # Public methods for sending emails
    def send_welcome_email(self, user_name: str, user_email: str) -> bool:
        """Send welcome email to new user"""
        subject, html_content, text_content = self._get_email_template('welcome', user_name=user_name)
        return self._send_email(user_email, subject, html_content, text_content)
    
    def send_verification_email(self, user_name: str, user_email: str, verification_token: str) -> bool:
        """Send email verification"""
        subject, html_content, text_content = self._get_email_template('verification', 
            user_name=user_name, verification_token=verification_token)
        return self._send_email(user_email, subject, html_content, text_content)
    
    def send_password_reset_email(self, user_name: str, user_email: str, reset_token: str) -> bool:
        """Send password reset email"""
        subject, html_content, text_content = self._get_email_template('password_reset', 
            user_name=user_name, reset_token=reset_token)
        return self._send_email(user_email, subject, html_content, text_content)
    
    def send_consultation_confirmation(self, user_name: str, user_email: str, consultation_id: str) -> bool:
        """Send consultation confirmation"""
        subject, html_content, text_content = self._get_email_template('consultation_confirmation', 
            user_name=user_name, consultation_id=consultation_id)
        return self._send_email(user_email, subject, html_content, text_content)
    
    def send_admin_new_user_notification(self, user_name: str, user_email: str) -> bool:
        """Send admin notification for new user"""
        subject, html_content, text_content = self._get_email_template('admin_new_user', 
            user_name=user_name, user_email=user_email)
        return self._send_email(SUPPORT_EMAIL, subject, html_content, text_content)
    
    def send_admin_consultation_notification(self, user_name: str, user_email: str, consultation_id: str, message: str) -> bool:
        """Send admin notification for new consultation"""
        subject, html_content, text_content = self._get_email_template('admin_consultation', 
            user_name=user_name, user_email=user_email, consultation_id=consultation_id, message=message)
        return self._send_email(SUPPORT_EMAIL, subject, html_content, text_content)
    
    def send_subscription_confirmation(self, user_name: str, user_email: str, subscription_plan: str) -> bool:
        """Send subscription confirmation"""
        subject, html_content, text_content = self._get_email_template('subscription_confirmation', 
            user_name=user_name, subscription_plan=subscription_plan)
        return self._send_email(user_email, subject, html_content, text_content)
    
    def send_report_generated_notification(self, user_name: str, user_email: str, report_name: str, download_url: str) -> bool:
        """Send report generation notification"""
        subject, html_content, text_content = self._get_email_template('report_generated', 
            user_name=user_name, report_name=report_name, download_url=download_url)
        return self._send_email(user_email, subject, html_content, text_content)
    
    def send_alert_notification(self, user_name: str, user_email: str, alert_type: str, alert_message: str) -> bool:
        """Send alert notification"""
        subject, html_content, text_content = self._get_email_template('alert_notification', 
            user_name=user_name, alert_type=alert_type, alert_message=alert_message)
        return self._send_email(user_email, subject, html_content, text_content)
    
    def send_admin_communication(self, admin_name: str, message: str) -> bool:
        """Send admin communication"""
        subject, html_content, text_content = self._get_email_template('admin_communication', 
            admin_name=admin_name, message=message)
        return self._send_email(SUPPORT_EMAIL, subject, html_content, text_content)

# Global email service instance
email_service = EmailService()
