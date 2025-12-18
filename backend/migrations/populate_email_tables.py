#!/usr/bin/env python3
"""
Populate email_subscriptions and email_templates tables with sample data
"""
import sys
import os
from datetime import datetime, timedelta
import json

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.models.subscription import EmailSubscription
from app.models.admin import EmailTemplate

def populate_email_subscriptions(db):
    """Populate email_subscriptions table with sample data"""
    print("📧 Populating email_subscriptions table...")
    
    sample_subscriptions = [
        {
            "email": "john.doe@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "company": "ABC Construction",
            "subscription_type": "newsletter",
            "status": "active",
            "source": "homepage",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "subscribed_at": datetime.utcnow() - timedelta(days=30),
            "email_count": 4,
            "preferences": json.dumps({"frequency": "weekly", "categories": ["news", "updates"]})
        },
        {
            "email": "jane.smith@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "company": "XYZ Equipment",
            "subscription_type": "blog",
            "status": "active",
            "source": "blog",
            "ip_address": "192.168.1.101",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "subscribed_at": datetime.utcnow() - timedelta(days=15),
            "email_count": 2,
            "preferences": json.dumps({"frequency": "bi-weekly", "categories": ["blog", "tips"]})
        },
        {
            "email": "bob.wilson@example.com",
            "first_name": "Bob",
            "last_name": "Wilson",
            "company": "Wilson Crane Services",
            "subscription_type": "newsletter",
            "status": "active",
            "source": "contact",
            "ip_address": "192.168.1.102",
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
            "subscribed_at": datetime.utcnow() - timedelta(days=7),
            "email_count": 1,
            "preferences": json.dumps({"frequency": "monthly", "categories": ["news"]})
        },
        {
            "email": "sarah.johnson@example.com",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "company": "Johnson Heavy Equipment",
            "subscription_type": "updates",
            "status": "active",
            "source": "homepage",
            "ip_address": "192.168.1.103",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "subscribed_at": datetime.utcnow() - timedelta(days=3),
            "email_count": 0,
            "preferences": json.dumps({"frequency": "weekly", "categories": ["updates", "news"]})
        },
        {
            "email": "mike.brown@example.com",
            "first_name": "Mike",
            "last_name": "Brown",
            "company": "Brown Construction Co",
            "subscription_type": "newsletter",
            "status": "unsubscribed",
            "source": "homepage",
            "ip_address": "192.168.1.104",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "subscribed_at": datetime.utcnow() - timedelta(days=60),
            "unsubscribed_at": datetime.utcnow() - timedelta(days=10),
            "email_count": 5,
            "preferences": json.dumps({"frequency": "weekly"})
        },
        {
            "email": "lisa.davis@example.com",
            "first_name": "Lisa",
            "last_name": "Davis",
            "company": "Davis Equipment Rental",
            "subscription_type": "blog",
            "status": "active",
            "source": "blog",
            "ip_address": "192.168.1.105",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "subscribed_at": datetime.utcnow() - timedelta(days=1),
            "email_count": 0,
            "preferences": json.dumps({"frequency": "weekly", "categories": ["blog"]})
        },
        {
            "email": "david.miller@example.com",
            "first_name": "David",
            "last_name": "Miller",
            "company": "Miller Crane Solutions",
            "subscription_type": "newsletter",
            "status": "active",
            "source": "contact",
            "ip_address": "192.168.1.106",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "subscribed_at": datetime.utcnow() - timedelta(days=20),
            "last_email_sent": datetime.utcnow() - timedelta(days=2),
            "email_count": 3,
            "preferences": json.dumps({"frequency": "weekly", "categories": ["news", "updates", "tips"]})
        },
        {
            "email": "emily.taylor@example.com",
            "first_name": "Emily",
            "last_name": "Taylor",
            "company": "Taylor Heavy Machinery",
            "subscription_type": "updates",
            "status": "active",
            "source": "homepage",
            "ip_address": "192.168.1.107",
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
            "subscribed_at": datetime.utcnow() - timedelta(days=5),
            "email_count": 1,
            "preferences": json.dumps({"frequency": "bi-weekly", "categories": ["updates"]})
        }
    ]
    
    count = 0
    for sub_data in sample_subscriptions:
        try:
            # Check if subscription already exists
            existing = db.query(EmailSubscription).filter(
                EmailSubscription.email == sub_data["email"]
            ).first()
            
            if existing:
                print(f"  ⚠️  Subscription for {sub_data['email']} already exists, skipping...")
                continue
            
            subscription = EmailSubscription(**sub_data)
            db.add(subscription)
            count += 1
        except Exception as e:
            print(f"  ❌ Error creating subscription for {sub_data['email']}: {e}")
            db.rollback()
            continue
    
    try:
        db.commit()
        print(f"  ✅ Successfully added {count} email subscriptions")
        return count
    except Exception as e:
        db.rollback()
        print(f"  ❌ Error committing subscriptions: {e}")
        return 0


def populate_email_templates(db):
    """Populate email_templates table with sample templates"""
    print("\n📝 Populating email_templates table...")
    
    sample_templates = [
        {
            "name": "welcome_email",
            "subject": "Welcome to Crane Intelligence!",
            "body_html": """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #00FF85; color: #000; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9f9f9; }
                    .button { display: inline-block; padding: 10px 20px; background: #00FF85; color: #000; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                    .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to Crane Intelligence!</h1>
                    </div>
                    <div class="content">
                        <p>Hello {{first_name}},</p>
                        <p>Thank you for subscribing to our newsletter! We're excited to have you on board.</p>
                        <p>You'll receive regular updates about:</p>
                        <ul>
                            <li>Latest crane market trends</li>
                            <li>Equipment valuation insights</li>
                            <li>Industry news and updates</li>
                            <li>Exclusive offers and promotions</li>
                        </ul>
                        <p>If you have any questions, feel free to reach out to us.</p>
                        <a href="{{dashboard_url}}" class="button">Visit Dashboard</a>
                    </div>
                    <div class="footer">
                        <p>Crane Intelligence Platform</p>
                        <p><a href="{{unsubscribe_url}}">Unsubscribe</a></p>
                    </div>
                </div>
            </body>
            </html>
            """,
            "body_text": """
            Welcome to Crane Intelligence!
            
            Hello {{first_name}},
            
            Thank you for subscribing to our newsletter! We're excited to have you on board.
            
            You'll receive regular updates about:
            - Latest crane market trends
            - Equipment valuation insights
            - Industry news and updates
            - Exclusive offers and promotions
            
            If you have any questions, feel free to reach out to us.
            
            Visit Dashboard: {{dashboard_url}}
            
            ---
            Crane Intelligence Platform
            Unsubscribe: {{unsubscribe_url}}
            """,
            "template_type": "marketing",
            "variables": json.dumps(["first_name", "dashboard_url", "unsubscribe_url"]),
            "is_active": True,
            "usage_count": 0
        },
        {
            "name": "newsletter_weekly",
            "subject": "Weekly Crane Intelligence Newsletter - {{date}}",
            "body_html": """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #00FF85; color: #000; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9f9f9; }
                    .article { margin: 20px 0; padding: 15px; background: white; border-left: 4px solid #00FF85; }
                    .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Weekly Newsletter</h1>
                        <p>{{date}}</p>
                    </div>
                    <div class="content">
                        <p>Hello {{first_name}},</p>
                        <p>Here's your weekly update from Crane Intelligence:</p>
                        
                        <div class="article">
                            <h3>{{article_1_title}}</h3>
                            <p>{{article_1_summary}}</p>
                            <a href="{{article_1_url}}">Read more →</a>
                        </div>
                        
                        <div class="article">
                            <h3>{{article_2_title}}</h3>
                            <p>{{article_2_summary}}</p>
                            <a href="{{article_2_url}}">Read more →</a>
                        </div>
                        
                        <p>Thank you for being part of our community!</p>
                    </div>
                    <div class="footer">
                        <p>Crane Intelligence Platform</p>
                        <p><a href="{{unsubscribe_url}}">Unsubscribe</a></p>
                    </div>
                </div>
            </body>
            </html>
            """,
            "body_text": """
            Weekly Newsletter - {{date}}
            
            Hello {{first_name}},
            
            Here's your weekly update from Crane Intelligence:
            
            {{article_1_title}}
            {{article_1_summary}}
            Read more: {{article_1_url}}
            
            {{article_2_title}}
            {{article_2_summary}}
            Read more: {{article_2_url}}
            
            Thank you for being part of our community!
            
            ---
            Crane Intelligence Platform
            Unsubscribe: {{unsubscribe_url}}
            """,
            "template_type": "marketing",
            "variables": json.dumps(["first_name", "date", "article_1_title", "article_1_summary", "article_1_url", "article_2_title", "article_2_summary", "article_2_url", "unsubscribe_url"]),
            "is_active": True,
            "usage_count": 0
        },
        {
            "name": "report_completed",
            "subject": "Your FMV Report is Ready - Report #{{report_id}}",
            "body_html": """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #00FF85; color: #000; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9f9f9; }
                    .button { display: inline-block; padding: 10px 20px; background: #00FF85; color: #000; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                    .info-box { background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #00FF85; }
                    .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Your Report is Ready!</h1>
                    </div>
                    <div class="content">
                        <p>Hello {{user_name}},</p>
                        <p>Great news! Your FMV Report #{{report_id}} has been completed.</p>
                        
                        <div class="info-box">
                            <strong>Report Details:</strong><br>
                            Type: {{report_type}}<br>
                            Crane: {{crane_details}}<br>
                            Valuation: {{valuation_amount}}
                        </div>
                        
                        <p>You can view and download your report from your dashboard.</p>
                        <a href="{{report_url}}" class="button">View Report</a>
                        
                        <p>Thank you for using Crane Intelligence!</p>
                    </div>
                    <div class="footer">
                        <p>Crane Intelligence Platform</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            "body_text": """
            Your Report is Ready!
            
            Hello {{user_name}},
            
            Great news! Your FMV Report #{{report_id}} has been completed.
            
            Report Details:
            Type: {{report_type}}
            Crane: {{crane_details}}
            Valuation: {{valuation_amount}}
            
            You can view and download your report from your dashboard.
            View Report: {{report_url}}
            
            Thank you for using Crane Intelligence!
            
            ---
            Crane Intelligence Platform
            """,
            "template_type": "notification",
            "variables": json.dumps(["user_name", "report_id", "report_type", "crane_details", "valuation_amount", "report_url"]),
            "is_active": True,
            "usage_count": 0
        },
        {
            "name": "payment_received",
            "subject": "Payment Received - Report #{{report_id}}",
            "body_html": """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #00FF85; color: #000; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9f9f9; }
                    .info-box { background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #00FF85; }
                    .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Payment Received</h1>
                    </div>
                    <div class="content">
                        <p>Hello {{user_name}},</p>
                        <p>We've successfully received your payment for Report #{{report_id}}.</p>
                        
                        <div class="info-box">
                            <strong>Payment Details:</strong><br>
                            Amount: {{amount}}<br>
                            Transaction ID: {{transaction_id}}<br>
                            Date: {{payment_date}}
                        </div>
                        
                        <p>Your report is now being processed. We'll notify you once it's ready.</p>
                        <p>Thank you for your business!</p>
                    </div>
                    <div class="footer">
                        <p>Crane Intelligence Platform</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            "body_text": """
            Payment Received
            
            Hello {{user_name}},
            
            We've successfully received your payment for Report #{{report_id}}.
            
            Payment Details:
            Amount: {{amount}}
            Transaction ID: {{transaction_id}}
            Date: {{payment_date}}
            
            Your report is now being processed. We'll notify you once it's ready.
            
            Thank you for your business!
            
            ---
            Crane Intelligence Platform
            """,
            "template_type": "notification",
            "variables": json.dumps(["user_name", "report_id", "amount", "transaction_id", "payment_date"]),
            "is_active": True,
            "usage_count": 0
        },
        {
            "name": "password_reset",
            "subject": "Reset Your Password - Crane Intelligence",
            "body_html": """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #00FF85; color: #000; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9f9f9; }
                    .button { display: inline-block; padding: 10px 20px; background: #00FF85; color: #000; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                    .warning { background: #fff3cd; padding: 15px; margin: 15px 0; border-left: 4px solid #ffc107; }
                    .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Password Reset Request</h1>
                    </div>
                    <div class="content">
                        <p>Hello {{user_name}},</p>
                        <p>We received a request to reset your password for your Crane Intelligence account.</p>
                        
                        <p>Click the button below to reset your password:</p>
                        <a href="{{reset_url}}" class="button">Reset Password</a>
                        
                        <div class="warning">
                            <strong>Security Notice:</strong><br>
                            This link will expire in {{expiry_hours}} hours. If you didn't request this, please ignore this email.
                        </div>
                        
                        <p>If the button doesn't work, copy and paste this link into your browser:</p>
                        <p style="word-break: break-all; color: #666;">{{reset_url}}</p>
                    </div>
                    <div class="footer">
                        <p>Crane Intelligence Platform</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            "body_text": """
            Password Reset Request
            
            Hello {{user_name}},
            
            We received a request to reset your password for your Crane Intelligence account.
            
            Click the link below to reset your password:
            {{reset_url}}
            
            Security Notice:
            This link will expire in {{expiry_hours}} hours. If you didn't request this, please ignore this email.
            
            ---
            Crane Intelligence Platform
            """,
            "template_type": "system",
            "variables": json.dumps(["user_name", "reset_url", "expiry_hours"]),
            "is_active": True,
            "usage_count": 0
        },
        {
            "name": "account_verification",
            "subject": "Verify Your Email - Crane Intelligence",
            "body_html": """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #00FF85; color: #000; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9f9f9; }
                    .button { display: inline-block; padding: 10px 20px; background: #00FF85; color: #000; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                    .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Verify Your Email</h1>
                    </div>
                    <div class="content">
                        <p>Hello {{user_name}},</p>
                        <p>Thank you for signing up for Crane Intelligence! Please verify your email address to complete your registration.</p>
                        
                        <p>Click the button below to verify your email:</p>
                        <a href="{{verification_url}}" class="button">Verify Email</a>
                        
                        <p>If the button doesn't work, copy and paste this link into your browser:</p>
                        <p style="word-break: break-all; color: #666;">{{verification_url}}</p>
                        
                        <p>This link will expire in {{expiry_hours}} hours.</p>
                    </div>
                    <div class="footer">
                        <p>Crane Intelligence Platform</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            "body_text": """
            Verify Your Email
            
            Hello {{user_name}},
            
            Thank you for signing up for Crane Intelligence! Please verify your email address to complete your registration.
            
            Click the link below to verify your email:
            {{verification_url}}
            
            This link will expire in {{expiry_hours}} hours.
            
            ---
            Crane Intelligence Platform
            """,
            "template_type": "system",
            "variables": json.dumps(["user_name", "verification_url", "expiry_hours"]),
            "is_active": True,
            "usage_count": 0
        },
        {
            "name": "unsubscribe_confirmation",
            "subject": "You've Been Unsubscribed",
            "body_html": """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #666; color: #fff; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9f9f9; }
                    .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Unsubscribed</h1>
                    </div>
                    <div class="content">
                        <p>Hello {{first_name}},</p>
                        <p>You have been successfully unsubscribed from our newsletter.</p>
                        <p>We're sorry to see you go! If you change your mind, you can always resubscribe at any time.</p>
                        <p>Thank you for being part of our community.</p>
                    </div>
                    <div class="footer">
                        <p>Crane Intelligence Platform</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            "body_text": """
            Unsubscribed
            
            Hello {{first_name}},
            
            You have been successfully unsubscribed from our newsletter.
            
            We're sorry to see you go! If you change your mind, you can always resubscribe at any time.
            
            Thank you for being part of our community.
            
            ---
            Crane Intelligence Platform
            """,
            "template_type": "system",
            "variables": json.dumps(["first_name"]),
            "is_active": True,
            "usage_count": 0
        }
    ]
    
    count = 0
    for template_data in sample_templates:
        try:
            # Check if template already exists
            existing = db.query(EmailTemplate).filter(
                EmailTemplate.name == template_data["name"]
            ).first()
            
            if existing:
                print(f"  ⚠️  Template '{template_data['name']}' already exists, skipping...")
                continue
            
            template = EmailTemplate(**template_data)
            db.add(template)
            count += 1
        except Exception as e:
            print(f"  ❌ Error creating template '{template_data['name']}': {e}")
            db.rollback()
            continue
    
    try:
        db.commit()
        print(f"  ✅ Successfully added {count} email templates")
        return count
    except Exception as e:
        db.rollback()
        print(f"  ❌ Error committing templates: {e}")
        return 0


def main():
    """Main function to populate both tables"""
    print("=" * 60)
    print("Populating Email Tables")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Populate email_subscriptions
        sub_count = populate_email_subscriptions(db)
        
        # Populate email_templates
        template_count = populate_email_templates(db)
        
        print("\n" + "=" * 60)
        print("Summary:")
        print(f"  Email Subscriptions: {sub_count} records added")
        print(f"  Email Templates: {template_count} records added")
        print("=" * 60)
        print("\n✅ Population complete!")
        
    except Exception as e:
        print(f"\n❌ Error during population: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()

