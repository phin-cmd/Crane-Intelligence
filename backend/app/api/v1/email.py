"""
Email API endpoints for Crane Intelligence Platform
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime

from ...core.database import get_db
from ...services.email_service_unified import email_service
from ...models.user import User

router = APIRouter()

# Pydantic models for email requests
class EmailRequest(BaseModel):
    to_emails: List[EmailStr]
    subject: str
    message: str
    html_content: Optional[str] = None

class WelcomeEmailRequest(BaseModel):
    user_email: EmailStr
    user_name: str

class PasswordResetEmailRequest(BaseModel):
    user_email: EmailStr
    user_name: str
    reset_token: str

class ValuationReportEmailRequest(BaseModel):
    user_email: EmailStr
    user_name: str
    crane_model: str
    valuation_amount: str
    report_file_path: Optional[str] = None

class NotificationEmailRequest(BaseModel):
    user_email: EmailStr
    user_name: str
    notification_type: str
    message: str
    action_url: Optional[str] = None

class AdminNotificationRequest(BaseModel):
    admin_emails: List[EmailStr]
    notification_type: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ConsultationRequest(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    message: str
    type: str = "consultation_request"

class EmailResponse(BaseModel):
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None

@router.post("/send-email", response_model=EmailResponse)
async def send_email(request: EmailRequest):
    """Send a custom email"""
    try:
        success = email_service.send_email(
            to_emails=request.to_emails,
            subject=request.subject,
            html_content=request.html_content or f"<p>{request.message}</p>",
            text_content=request.message
        )
        
        if success:
            return EmailResponse(
                success=True,
                message="Email sent successfully",
                details={"recipients": request.to_emails, "subject": request.subject}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email sending failed: {str(e)}"
        )

@router.post("/send-welcome-email", response_model=EmailResponse)
async def send_welcome_email(request: WelcomeEmailRequest):
    """Send welcome email to new user"""
    try:
        success = email_service.send_welcome_email(
            user_email=request.user_email,
            user_name=request.user_name
        )
        
        if success:
            return EmailResponse(
                success=True,
                message="Welcome email sent successfully",
                details={"user_email": request.user_email, "user_name": request.user_name}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send welcome email"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Welcome email sending failed: {str(e)}"
        )

@router.post("/send-password-reset-email", response_model=EmailResponse)
async def send_password_reset_email(request: PasswordResetEmailRequest):
    """Send password reset email"""
    try:
        success = email_service.send_password_reset_email(
            user_email=request.user_email,
            user_name=request.user_name,
            reset_token=request.reset_token
        )
        
        if success:
            return EmailResponse(
                success=True,
                message="Password reset email sent successfully",
                details={"user_email": request.user_email}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send password reset email"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password reset email sending failed: {str(e)}"
        )

@router.post("/send-valuation-report-email", response_model=EmailResponse)
async def send_valuation_report_email(request: ValuationReportEmailRequest):
    """Send valuation report email"""
    try:
        report_data = {
            "crane_model": request.crane_model,
            "valuation_amount": request.valuation_amount
        }
        
        success = email_service.send_valuation_report_email(
            user_email=request.user_email,
            user_name=request.user_name,
            report_data=report_data,
            report_file_path=request.report_file_path
        )
        
        if success:
            return EmailResponse(
                success=True,
                message="Valuation report email sent successfully",
                details={
                    "user_email": request.user_email,
                    "crane_model": request.crane_model,
                    "valuation_amount": request.valuation_amount
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send valuation report email"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Valuation report email sending failed: {str(e)}"
        )

@router.post("/send-notification-email", response_model=EmailResponse)
async def send_notification_email(request: NotificationEmailRequest):
    """Send notification email to user"""
    try:
        success = email_service.send_notification_email(
            user_email=request.user_email,
            user_name=request.user_name,
            notification_type=request.notification_type,
            message=request.message,
            action_url=request.action_url
        )
        
        if success:
            return EmailResponse(
                success=True,
                message="Notification email sent successfully",
                details={
                    "user_email": request.user_email,
                    "notification_type": request.notification_type
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send notification email"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Notification email sending failed: {str(e)}"
        )

@router.post("/send-admin-notification", response_model=EmailResponse)
async def send_admin_notification(request: AdminNotificationRequest):
    """Send notification email to admin users"""
    try:
        success = email_service.send_admin_notification(
            admin_emails=request.admin_emails,
            notification_type=request.notification_type,
            message=request.message,
            details=request.details
        )
        
        if success:
            return EmailResponse(
                success=True,
                message="Admin notification sent successfully",
                details={
                    "admin_emails": request.admin_emails,
                    "notification_type": request.notification_type
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send admin notification"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Admin notification sending failed: {str(e)}"
        )

@router.post("/consultation/submit", response_model=EmailResponse)
async def submit_consultation(request: ConsultationRequest):
    """Submit consultation request and send emails to user and admin"""
    try:
        # Send confirmation email to user
        user_email_success = email_service.send_email(
            to_emails=[request.email],
            subject="Consultation Request Received - Crane Intelligence",
            html_content=f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #00FF85;">Thank you for your consultation request!</h2>
                <p>Dear {request.name},</p>
                <p>We have received your consultation request and will contact you within 24 hours to schedule your free consultation.</p>
                
                <h3>Your Request Details:</h3>
                <ul>
                    <li><strong>Name:</strong> {request.name}</li>
                    <li><strong>Email:</strong> {request.email}</li>
                    <li><strong>Company:</strong> {request.company or 'Not provided'}</li>
                    <li><strong>Message:</strong> {request.message}</li>
                </ul>
                
                <p>Our team will review your requirements and get back to you soon.</p>
                <p>Best regards,<br>The Crane Intelligence Team</p>
            </div>
            """,
            text_content=f"Thank you for your consultation request! We will contact you within 24 hours. Details: Name: {request.name}, Email: {request.email}, Company: {request.company or 'Not provided'}, Message: {request.message}"
        )
        
        # Send notification email to admin
        admin_email_success = email_service.send_email(
            to_emails=["pgenerelly@craneintelligence.tech"],  # Admin email
            subject=f"New Consultation Request from {request.name}",
            html_content=f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #00FF85;">New Consultation Request</h2>
                <p>A new consultation request has been submitted through the website.</p>
                
                <h3>Contact Details:</h3>
                <ul>
                    <li><strong>Name:</strong> {request.name}</li>
                    <li><strong>Email:</strong> {request.email}</li>
                    <li><strong>Company:</strong> {request.company or 'Not provided'}</li>
                    <li><strong>Message:</strong> {request.message}</li>
                    <li><strong>Submitted:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                </ul>
                
                <p>Please follow up with this potential client within 24 hours.</p>
            </div>
            """,
            text_content=f"New consultation request from {request.name} ({request.email}). Company: {request.company or 'Not provided'}. Message: {request.message}. Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        if user_email_success and admin_email_success:
            return EmailResponse(
                success=True,
                message="Consultation request submitted successfully. Confirmation emails sent.",
                details={
                    "user_email": request.email,
                    "admin_notified": True,
                    "submission_time": datetime.now().isoformat()
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send confirmation emails"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Consultation submission failed: {str(e)}"
        )

@router.get("/test-email-connection")
async def test_email_connection():
    """Test email service connection"""
    try:
        # Test SMTP connection
        from smtplib import SMTP
        import ssl
        
        server = SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("pgenerelly@craneintelligence.tech", "your-app-password")
        server.quit()
        
        return {
            "success": True,
            "message": "Email connection test successful",
            "details": {
                "smtp_server": "smtp.gmail.com",
                "port": 587,
                "username": "pgenerelly@craneintelligence.tech"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Email connection test failed: {str(e)}",
            "details": None
        }

@router.post("/send-test-email")
async def send_test_email():
    """Send a test email to verify email functionality"""
    try:
        test_email = "pgenerelly@craneintelligence.tech"
        
        success = email_service.send_email(
            to_emails=[test_email],
            subject="Crane Intelligence - Test Email",
            html_content="""
            <html>
            <body>
                <h2>🧪 Test Email from Crane Intelligence</h2>
                <p>This is a test email to verify that the email system is working correctly.</p>
                <p><strong>Timestamp:</strong> {}</p>
                <p>If you received this email, the email system is functioning properly!</p>
                <p>Best regards,<br>Crane Intelligence Team</p>
            </body>
            </html>
            """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            text_content="Test email from Crane Intelligence Platform - Email system is working!"
        )
        
        if success:
            return EmailResponse(
                success=True,
                message="Test email sent successfully",
                details={"test_email": test_email}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send test email"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test email sending failed: {str(e)}"
        )
