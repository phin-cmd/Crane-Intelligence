"""
Standardized Email Template Service for Crane Intelligence
Provides brand-consistent email templates across all communications
"""

from typing import Optional, Dict, Any
from pathlib import Path


class EmailTemplateService:
    """Service for generating standardized email templates with brand guidelines"""
    
    # Brand Colors
    PRIMARY_BLACK = "#0F0F0F"
    SECONDARY_BLACK = "#1A1A1A"
    TERTIARY_BLACK = "#121212"
    ACCENT_GREEN = "#00FF85"
    ACCENT_YELLOW = "#FFD600"
    ACCENT_RED = "#FF4444"
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#B0B0B0"
    TEXT_MUTED = "#808080"
    BORDER_COLOR = "#333333"
    
    # Contact Information
    COMPANY_NAME = "Crane Intelligence"
    COMPANY_EMAIL = "phin@accranes.com"
    COMPANY_PHONE = "+1 (434) 531-7566"
    COMPANY_ADDRESS = "EAST COAST EQUIPMENT EXCHANGE LLC<br>4420 W Grace St<br>Richmond, VA 23230-3808"
    COMPANY_WEBSITE = "https://craneintelligence.tech"
    
    @staticmethod
    def get_base_template(
        title: str,
        content: str,
        user_email: Optional[str] = None,
        button_text: Optional[str] = None,
        button_url: Optional[str] = None,
        footer_extra: Optional[str] = None
    ) -> str:
        """
        Generate a standardized email template with brand guidelines
        
        Args:
            title: Email title/heading
            content: Main email content (HTML)
            user_email: Recipient email address
            button_text: Optional CTA button text
            button_url: Optional CTA button URL
            footer_extra: Optional additional footer content
            
        Returns:
            Complete HTML email template
        """
        button_html = ""
        if button_text and button_url:
            button_html = f"""
            <div style="text-align: center; margin: 30px 0;">
                <a href="{button_url}" style="display: inline-block; background-color: {EmailTemplateService.ACCENT_GREEN}; color: {EmailTemplateService.PRIMARY_BLACK}; padding: 14px 32px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px;">
                    {button_text}
                </a>
            </div>
            """
        
        footer_content = f"""
        <p style="margin: 0 0 10px 0; color: {EmailTemplateService.TEXT_PRIMARY}; font-size: 14px; font-weight: 600;">
            {EmailTemplateService.COMPANY_NAME}
        </p>
        <p style="margin: 5px 0; color: {EmailTemplateService.TEXT_SECONDARY}; font-size: 12px;">
            Professional Crane Valuation & Market Intelligence
        </p>
        <p style="margin: 15px 0 10px 0; color: {EmailTemplateService.TEXT_MUTED}; font-size: 11px; line-height: 1.6;">
            {EmailTemplateService.COMPANY_ADDRESS}
        </p>
        <p style="margin: 10px 0; color: {EmailTemplateService.TEXT_MUTED}; font-size: 11px;">
            Email: <a href="mailto:{EmailTemplateService.COMPANY_EMAIL}" style="color: {EmailTemplateService.ACCENT_GREEN}; text-decoration: none;">{EmailTemplateService.COMPANY_EMAIL}</a><br>
            Phone: <a href="tel:{EmailTemplateService.COMPANY_PHONE.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')}" style="color: {EmailTemplateService.ACCENT_GREEN}; text-decoration: none;">{EmailTemplateService.COMPANY_PHONE}</a><br>
            Website: <a href="{EmailTemplateService.COMPANY_WEBSITE}" style="color: {EmailTemplateService.ACCENT_GREEN}; text-decoration: none;">{EmailTemplateService.COMPANY_WEBSITE}</a>
        </p>
        """
        
        if footer_extra:
            footer_content += f'<p style="margin: 15px 0 10px 0; color: {EmailTemplateService.TEXT_MUTED}; font-size: 11px;">{footer_extra}</p>'
        
        if user_email:
            footer_content += f'<p style="margin: 15px 0 0 0; color: {EmailTemplateService.TEXT_MUTED}; font-size: 11px;">This email was sent to {user_email}.</p>'
        
        footer_content += f'<p style="margin: 15px 0 0 0; color: {EmailTemplateService.TEXT_MUTED}; font-size: 11px;">© 2025 {EmailTemplateService.COMPANY_NAME}. All rights reserved.</p>'
        
        return f"""
<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="x-apple-disable-message-reformatting">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
    <title>{title} - {EmailTemplateService.COMPANY_NAME}</title>
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        .email-wrapper {{
            max-width: 600px;
            margin: 0 auto;
            background-color: {EmailTemplateService.PRIMARY_BLACK};
        }}
        .email-container {{
            background-color: {EmailTemplateService.PRIMARY_BLACK};
            padding: 0;
        }}
        .email-header {{
            background: linear-gradient(135deg, {EmailTemplateService.SECONDARY_BLACK} 0%, {EmailTemplateService.TERTIARY_BLACK} 100%);
            padding: 40px 30px;
            text-align: center;
            border-bottom: 1px solid {EmailTemplateService.BORDER_COLOR};
        }}
        .logo-container {{
            margin-bottom: 20px;
        }}
        .logo-img {{
            height: 60px !important;
            width: auto !important;
            max-width: 200px !important;
            display: block !important;
            margin: 0 auto !important;
        }}
        .email-content {{
            background-color: {EmailTemplateService.SECONDARY_BLACK};
            padding: 40px 30px;
            color: {EmailTemplateService.TEXT_PRIMARY};
        }}
        .email-footer {{
            background-color: {EmailTemplateService.TERTIARY_BLACK};
            padding: 30px;
            text-align: center;
            border-top: 1px solid {EmailTemplateService.BORDER_COLOR};
            color: {EmailTemplateService.TEXT_SECONDARY};
            font-size: 12px;
            line-height: 1.6;
        }}
        h1, h2, h3 {{
            font-family: 'Roboto Condensed', 'Inter', sans-serif;
            font-weight: 600;
            color: {EmailTemplateService.TEXT_PRIMARY};
            margin-top: 0;
        }}
        h1 {{
            font-size: 28px;
            line-height: 1.2;
            color: {EmailTemplateService.ACCENT_GREEN};
        }}
        h2 {{
            font-size: 24px;
            line-height: 1.3;
            color: {EmailTemplateService.ACCENT_GREEN};
        }}
        h3 {{
            font-size: 20px;
            line-height: 1.4;
            color: {EmailTemplateService.TEXT_PRIMARY};
        }}
        p {{
            color: {EmailTemplateService.TEXT_SECONDARY};
            line-height: 1.6;
            margin: 16px 0;
        }}
        ul, ol {{
            color: {EmailTemplateService.TEXT_SECONDARY};
            line-height: 1.8;
            padding-left: 20px;
        }}
        li {{
            margin: 8px 0;
        }}
        a {{
            color: {EmailTemplateService.ACCENT_GREEN};
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .info-box {{
            background-color: rgba(0, 255, 133, 0.1);
            border-left: 4px solid {EmailTemplateService.ACCENT_GREEN};
            padding: 16px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .warning-box {{
            background-color: rgba(255, 214, 0, 0.1);
            border-left: 4px solid {EmailTemplateService.ACCENT_YELLOW};
            padding: 16px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .alert-box {{
            background-color: rgba(255, 68, 68, 0.1);
            border-left: 4px solid {EmailTemplateService.ACCENT_RED};
            padding: 16px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .divider {{
            height: 1px;
            background-color: {EmailTemplateService.BORDER_COLOR};
            margin: 30px 0;
        }}
        @media only screen and (max-width: 600px) {{
            .email-content {{
                padding: 30px 20px;
            }}
            .email-header {{
                padding: 30px 20px;
            }}
            .email-footer {{
                padding: 20px;
            }}
            h1 {{
                font-size: 24px;
            }}
            h2 {{
                font-size: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-wrapper" style="max-width: 600px; margin: 0 auto; background-color: {EmailTemplateService.PRIMARY_BLACK};">
        <div class="email-container" style="background-color: {EmailTemplateService.PRIMARY_BLACK}; padding: 0;">
            <div class="email-header" style="background: linear-gradient(135deg, {EmailTemplateService.SECONDARY_BLACK} 0%, {EmailTemplateService.TERTIARY_BLACK} 100%); padding: 40px 30px; text-align: center; border-bottom: 1px solid {EmailTemplateService.BORDER_COLOR};">
                <div class="logo-container" style="margin-bottom: 20px; text-align: center;">
                    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="margin: 0 auto;">
                        <tr>
                            <td align="center" style="padding: 0;">
                                <img src="https://craneintelligence.tech/images/logos/crane-intelligence-logo.png" alt="Crane Intelligence" width="200" height="60" style="display: block; margin: 0 auto; border: 0; outline: none; text-decoration: none; -ms-interpolation-mode: bicubic; max-width: 200px; height: auto;" />
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
            
            <div class="email-content" style="background-color: {EmailTemplateService.SECONDARY_BLACK}; padding: 40px 30px; color: {EmailTemplateService.TEXT_PRIMARY};">
                <h1 style="font-family: 'Roboto Condensed', 'Inter', sans-serif; font-weight: 600; font-size: 28px; line-height: 1.2; color: {EmailTemplateService.ACCENT_GREEN}; margin-top: 0;">{title}</h1>
                {content}
                {button_html}
            </div>
            
            <div class="email-footer" style="background-color: {EmailTemplateService.TERTIARY_BLACK}; padding: 30px; text-align: center; border-top: 1px solid {EmailTemplateService.BORDER_COLOR}; color: {EmailTemplateService.TEXT_SECONDARY}; font-size: 12px; line-height: 1.6;">
                {footer_content}
            </div>
        </div>
    </div>
</body>
</html>
        """
    
    @staticmethod
    def consultation_admin_notification(
        name: str,
        email: str,
        company: Optional[str],
        subject: Optional[str],
        message: str,
        consultation_id: int,
        created_at: str
    ) -> str:
        """Generate admin notification email for consultation requests using standard template and brand guide"""
        company_info = f'<p style="color: {EmailTemplateService.TEXT_SECONDARY}; margin: 5px 0;"><strong>Company:</strong> {company}</p>' if company else ''
        subject_info = f'<p style="color: {EmailTemplateService.TEXT_SECONDARY}; margin: 5px 0;"><strong>Subject:</strong> {subject}</p>' if subject else ''
        
        content = f"""
        <p style="color: {EmailTemplateService.TEXT_SECONDARY}; margin: 16px 0;">A new consultation request has been submitted through the website.</p>
        
        <div class="info-box" style="background-color: rgba(0, 255, 133, 0.1); border-left: 4px solid {EmailTemplateService.ACCENT_GREEN}; padding: 16px; margin: 20px 0; border-radius: 4px;">
            <h3 style="font-family: 'Roboto Condensed', 'Inter', sans-serif; font-weight: 600; font-size: 18px; line-height: 1.4; color: {EmailTemplateService.ACCENT_GREEN}; margin-top: 0;">Contact Information</h3>
            <p style="color: {EmailTemplateService.TEXT_SECONDARY}; margin: 5px 0;"><strong>Name:</strong> {name}</p>
            <p style="color: {EmailTemplateService.TEXT_SECONDARY}; margin: 5px 0;"><strong>Email:</strong> <a href="mailto:{email}" style="color: {EmailTemplateService.ACCENT_GREEN}; text-decoration: none;">{email}</a></p>
            {company_info}
            {subject_info}
        </div>
        
        <div class="info-box" style="background-color: rgba(0, 255, 133, 0.1); border-left: 4px solid {EmailTemplateService.ACCENT_GREEN}; padding: 16px; margin: 20px 0; border-radius: 4px;">
            <h3 style="font-family: 'Roboto Condensed', 'Inter', sans-serif; font-weight: 600; font-size: 18px; line-height: 1.4; color: {EmailTemplateService.ACCENT_GREEN}; margin-top: 0;">Message</h3>
            <p style="white-space: pre-wrap; color: {EmailTemplateService.TEXT_PRIMARY}; margin: 16px 0;">{message}</p>
        </div>
        
        <div class="divider" style="height: 1px; background-color: {EmailTemplateService.BORDER_COLOR}; margin: 30px 0;"></div>
        
        <p style="color: {EmailTemplateService.TEXT_MUTED}; font-size: 12px; line-height: 1.6; margin: 16px 0;">
            <strong>Request ID:</strong> {consultation_id}<br>
            <strong>Submitted:</strong> {created_at}
        </p>
        """
        
        return EmailTemplateService.get_base_template(
            title="New Consultation Request",
            content=content,
            button_text="View in Admin Panel",
            button_url="https://craneintelligence.tech/admin/consultations.html"
        )
    
    @staticmethod
    def consultation_user_confirmation(
        name: str,
        email: str,
        company: Optional[str],
        subject: Optional[str],
        message: str,
        consultation_id: int,
        created_at: str,
        is_contact_request: bool = False
    ) -> str:
        """Generate user confirmation email for consultation requests"""
        if is_contact_request:
            title = "Thank You for Contacting Us!"
            content = f"""
            <p>Dear {name},</p>
            
            <p>We have received your message and appreciate you reaching out to {EmailTemplateService.COMPANY_NAME}.</p>
            
            <div class="info-box">
                <h3 style="margin-top: 0; color: {EmailTemplateService.ACCENT_GREEN}; font-size: 18px;">Your Message Details</h3>
                <p><strong>Subject:</strong> {subject or 'General Inquiry'}</p>
                <p><strong>Message:</strong></p>
                <p style="white-space: pre-wrap; background: {EmailTemplateService.TERTIARY_BLACK}; padding: 15px; border-radius: 4px; color: {EmailTemplateService.TEXT_PRIMARY};">{message}</p>
            </div>
            
            <p>Our team will review your message and get back to you within 24 hours.</p>
            
            <p>If you have any urgent questions, please feel free to contact us directly:</p>
            <ul style="color: {EmailTemplateService.TEXT_SECONDARY};">
                <li>Email: <a href="mailto:{EmailTemplateService.COMPANY_EMAIL}" style="color: {EmailTemplateService.ACCENT_GREEN};">{EmailTemplateService.COMPANY_EMAIL}</a></li>
                <li>Phone: {EmailTemplateService.COMPANY_PHONE}</li>
            </ul>
            """
        else:
            title = "Thank You for Your Consultation Request"
            company_info = f'<p><strong>Company:</strong> {company}</p>' if company else ''
            content = f"""
            <p>Dear {name},</p>
            
            <p>Thank you for requesting a free consultation with {EmailTemplateService.COMPANY_NAME}. We're excited to help you optimize your crane valuation needs.</p>
            
            <div class="info-box">
                <h3 style="margin-top: 0; color: {EmailTemplateService.ACCENT_GREEN}; font-size: 18px;">Your Consultation Request</h3>
                <p><strong>Name:</strong> {name}</p>
                {company_info}
                <p><strong>Your Message:</strong></p>
                <p style="white-space: pre-wrap; background: {EmailTemplateService.TERTIARY_BLACK}; padding: 15px; border-radius: 4px; color: {EmailTemplateService.TEXT_PRIMARY};">{message}</p>
            </div>
            
            <p><strong>What happens next?</strong></p>
            <ul style="color: {EmailTemplateService.TEXT_SECONDARY};">
                <li>Our team will review your request within 24 hours</li>
                <li>We'll contact you to schedule your free consultation</li>
                <li>During the consultation, we'll discuss your crane valuation needs and how our platform can help</li>
            </ul>
            
            <p>If you have any questions in the meantime, please don't hesitate to reach out:</p>
            <ul style="color: {EmailTemplateService.TEXT_SECONDARY};">
                <li>Email: <a href="mailto:{EmailTemplateService.COMPANY_EMAIL}" style="color: {EmailTemplateService.ACCENT_GREEN};">{EmailTemplateService.COMPANY_EMAIL}</a></li>
                <li>Phone: {EmailTemplateService.COMPANY_PHONE} (Mon-Fri: 9 AM - 6 PM EST)</li>
            </ul>
            """
        
        footer_extra = f"""
        <p style="color: {EmailTemplateService.TEXT_MUTED}; font-size: 11px;">
            <strong>Request ID:</strong> {consultation_id}<br>
            <strong>Submitted:</strong> {created_at}
        </p>
        """
        
        return EmailTemplateService.get_base_template(
            title=title,
            content=content,
            user_email=email,
            footer_extra=footer_extra
        )
    
    @staticmethod
    def newsletter_welcome(
        email: str,
        first_name: Optional[str] = None
    ) -> str:
        """Generate welcome email for newsletter subscription"""
        greeting = f"Dear {first_name}," if first_name else "Hello,"
        
        content = f"""
        <p>{greeting}</p>
        
        <p>Thank you for subscribing to the {EmailTemplateService.COMPANY_NAME} newsletter!</p>
        
        <p>You'll now receive:</p>
        <ul style="color: {EmailTemplateService.TEXT_SECONDARY};">
            <li>Latest crane market insights and trends</li>
            <li>Valuation tips and best practices</li>
            <li>Industry news and updates</li>
            <li>Exclusive content and analysis</li>
            <li>Platform updates and new features</li>
        </ul>
        
        <p>We're excited to share valuable information about crane valuation and market analysis with you.</p>
        
        <div class="warning-box">
            <p style="margin: 0; color: {EmailTemplateService.TEXT_PRIMARY};">
                <strong>Unsubscribe:</strong> If you no longer wish to receive these emails, you can unsubscribe at any time by clicking the link in any newsletter email.
            </p>
        </div>
        """
        
        return EmailTemplateService.get_base_template(
            title="Welcome to Crane Intelligence Newsletter",
            content=content,
            user_email=email
        )

