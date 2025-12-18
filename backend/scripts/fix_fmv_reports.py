"""
Script to fix FMV reports for user kankanamitra01@gmail.com
- Update reports with successful payments to PAID status
- Ensure all reports are visible in admin panel
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal, init_db
from app.models.user import User
from app.models.fmv_report import FMVReport, FMVReportStatus
from sqlalchemy import and_

def fix_user_reports():
    """Fix reports for kankanamitra01@gmail.com"""
    db = SessionLocal()
    try:
        # Find user by email
        user = db.query(User).filter(User.email == 'kankanamitra01@gmail.com').first()
        if not user:
            print(f"❌ User kankanamitra01@gmail.com not found")
            return
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Get all reports for this user
        reports = db.query(FMVReport).filter(FMVReport.user_id == user.id).all()
        print(f"📊 Found {len(reports)} reports for user")
        
        fixed_count = 0
        for report in reports:
            print(f"\n📋 Report ID: {report.id}")
            print(f"   Status: {report.status.value}")
            print(f"   Payment Status: {report.payment_status}")
            print(f"   Amount Paid: ${report.amount_paid or 0}")
            print(f"   Payment Intent ID: {report.payment_intent_id or 'None'}")
            
            # If payment was successful but status is still DRAFT, update to PAID
            if (report.status == FMVReportStatus.DRAFT and 
                report.payment_status == 'succeeded' and 
                report.amount_paid and 
                report.amount_paid > 0):
                print(f"   ⚠️  Status mismatch: Payment succeeded but status is DRAFT")
                report.status = FMVReportStatus.PAID
                if not report.paid_at:
                    from datetime import datetime
                    report.paid_at = datetime.utcnow()
                fixed_count += 1
                print(f"   ✅ Updated status to PAID")
            elif report.status == FMVReportStatus.DRAFT and report.payment_intent_id:
                # Check if payment intent exists and is successful
                print(f"   ℹ️  Has payment_intent_id but status is DRAFT - may need manual review")
        
        if fixed_count > 0:
            db.commit()
            print(f"\n✅ Fixed {fixed_count} report(s)")
        else:
            print(f"\n✅ No reports needed fixing")
        
        # Verify all reports are visible
        all_reports = db.query(FMVReport).filter(FMVReport.user_id == user.id).all()
        print(f"\n📊 Total reports for user: {len(all_reports)}")
        for report in all_reports:
            print(f"   - Report {report.id}: {report.status.value} (Payment: {report.payment_status}, Amount: ${report.amount_paid or 0})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Fixing FMV reports for kankanamitra01@gmail.com...\n")
    fix_user_reports()
    print("\n✅ Done!")

