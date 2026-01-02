#!/usr/bin/env python3
"""
Test script to send a test email using Brevo API
Tests email functionality across all environments
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.services.email_service_unified import email_service
from datetime import datetime

def send_test_email(to_email: str = "kankanamitra01@gmail.com"):
    """Send a test email to verify email functionality"""
    print("=" * 60)
    print("🧪 Testing Email Service")
    print("=" * 60)
    
    # Check configuration
    print("\n📋 Email Configuration:")
    print(f"   USE_BREVO_API: {os.getenv('USE_BREVO_API', 'not set')}")
    print(f"   BREVO_API_KEY: {'✓ Set' if os.getenv('BREVO_API_KEY') else '✗ Not set'}")
    print(f"   MAIL_FROM_EMAIL: {os.getenv('MAIL_FROM_EMAIL', 'not set')}")
    print(f"   MAIL_SERVER: {os.getenv('MAIL_SERVER', 'not set')}")
    
    # Prepare email content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = "🧪 Test Email from Crane Intelligence Platform"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px 8px 0 0;
                text-align: center;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 8px 8px;
            }}
            .success {{
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #666;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🧪 Test Email</h1>
            <p>Crane Intelligence Platform</p>
        </div>
        <div class="content">
            <div class="success">
                <strong>✓ Email System Test Successful!</strong>
            </div>
            <p>This is a test email to verify that the email system is working correctly.</p>
            <p><strong>Test Details:</strong></p>
            <ul>
                <li><strong>Timestamp:</strong> {timestamp}</li>
                <li><strong>Recipient:</strong> {to_email}</li>
                <li><strong>Email Service:</strong> Brevo API</li>
                <li><strong>Status:</strong> ✅ Operational</li>
            </ul>
            <p>If you received this email, the email system is functioning properly!</p>
            <p>This test confirms that:</p>
            <ul>
                <li>✅ Brevo API is configured correctly</li>
                <li>✅ Email sending is working</li>
                <li>✅ HTML email rendering is functional</li>
            </ul>
        </div>
        <div class="footer">
            <p>Best regards,<br><strong>Crane Intelligence Team</strong></p>
            <p>This is an automated test email. Please do not reply.</p>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Test Email from Crane Intelligence Platform
    
    This is a test email to verify that the email system is working correctly.
    
    Test Details:
    - Timestamp: {timestamp}
    - Recipient: {to_email}
    - Email Service: Brevo API
    - Status: Operational
    
    If you received this email, the email system is functioning properly!
    
    Best regards,
    Crane Intelligence Team
    """
    
    print(f"\n📧 Sending test email to: {to_email}")
    print(f"   Subject: {subject}")
    print(f"   Timestamp: {timestamp}")
    
    try:
        # Send email
        success = email_service.send_email(
            to_emails=[to_email],
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
        if success:
            print("\n✅ SUCCESS: Test email sent successfully!")
            print(f"   Check inbox: {to_email}")
            return True
        else:
            print("\n❌ FAILED: Email sending returned False")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: Failed to send test email: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Get recipient email from command line or use default
    recipient = sys.argv[1] if len(sys.argv) > 1 else "kankanamitra01@gmail.com"
    
    result = send_test_email(recipient)
    sys.exit(0 if result else 1)

