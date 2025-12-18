#!/usr/bin/env python3
"""
Test script to send draft reminder email to rema@thecranehotlist.com
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.fmv_report import FMVReport, FMVReportStatus
from app.services.fmv_email_service import FMVEmailService
from app.services.fmv_report_service import FMVReportService
from app.core.config import settings

def send_test_draft_email():
    """Send test draft reminder email"""
    db = SessionLocal()
    try:
        # Find user
        user = db.query(User).filter(User.email == 'rema@thecranehotlist.com').first()
        if not user:
            print("❌ User rema@thecranehotlist.com not found")
            return False
        
        print(f"✅ User found: {user.full_name or user.username} (ID: {user.id})")
        
        # Find most recent draft report
        draft = db.query(FMVReport).filter(
            FMVReport.user_id == user.id,
            FMVReport.status == FMVReportStatus.DRAFT
        ).order_by(FMVReport.created_at.desc()).first()
        
        if not draft:
            print("⚠️  No draft report found. Creating test data...")
            # Create a test draft report
            from app.services.fmv_report_service import FMVReportService
            service = FMVReportService(db)
            
            from app.schemas.fmv_report import FMVReportCreate
            from app.models.fmv_report import FMVReportType
            
            test_data = FMVReportCreate(
                report_type=FMVReportType.SPOT_CHECK,
                crane_details={
                    "manufacturer": "Grove",
                    "model": "GMK5100",
                    "year": 2020,
                    "capacity": 100,
                    "operatingHours": 5000,
                    "region": "North America",
                    "craneType": "All Terrain"
                },
                metadata={
                    "user_email": user.email,
                    "test": True
                }
            )
            
            draft = service.create_report(user.id, test_data)
            db.commit()
            db.refresh(draft)
            print(f"✅ Created test draft report: ID={draft.id}")
        
        # Calculate report amount
        report_type_value = draft.report_type.value if hasattr(draft.report_type, 'value') else str(draft.report_type)
        if report_type_value == 'spot_check':
            amount = 495.00
        elif report_type_value == 'professional':
            amount = 995.00
        elif report_type_value == 'fleet_valuation':
            service = FMVReportService(db)
            if draft.fleet_pricing_tier:
                amount = service.calculate_fleet_price(draft.fleet_pricing_tier)
            else:
                amount = 1495.00
        else:
            amount = 995.00
        
        # Send email
        email_service = FMVEmailService()
        user_name = user.full_name or user.username
        
        print(f"\n📧 Sending draft reminder email to {user.email}...")
        print(f"   Report ID: {draft.id}")
        print(f"   Report Type: {report_type_value}")
        print(f"   Amount: ${amount}")
        
        # Send email directly using Brevo service to bypass admin notification issues
        try:
            from app.services.brevo_email_service import BrevoEmailService
            brevo_service = BrevoEmailService()
            
            first_name = user_name.split()[0] if user_name else "User"
            template_context = {
                "username": user_name.split()[0] if user_name else "User",
                "user_name": user_name,
                "first_name": first_name,
                "user_email": user.email,
                "report_id": draft.id,
                "amount": amount,
                "payment_url": f"{settings.frontend_url}/report-generation.html",
                "platform_name": settings.app_name,
                "support_email": settings.mail_from_email,
                "dashboard_url": f"{settings.frontend_url}/dashboard.html",
                "hours_since_creation": 0,
                "reminder_interval": "test",
                "urgency_message": "This is a test email for your draft report."
            }
            
            print(f"\n📧 Sending email via Brevo API...")
            result = brevo_service.send_template_email(
                to_emails=[user.email],
                template_name="fmv_report_draft_reminder.html",
                template_context=template_context,
                subject=f"Test: Complete Your FMV Report Payment - Report #{draft.id}",
                tags=["fmv-report", "draft-reminder", "test"]
            )
            
            if result.get("success"):
                print("✅ Draft reminder email sent successfully!")
                print(f"   Message ID: {result.get('message_id', 'N/A')}")
                return True
            else:
                print(f"❌ Failed to send email: {result.get('message', 'Unknown error')}")
                return False
        except Exception as email_error:
            print(f"❌ Error sending email: {email_error}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = send_test_draft_email()
    sys.exit(0 if success else 1)

