#!/usr/bin/env python3
"""
Fix payment intent for a specific payment that succeeded but report wasn't created
Usage: python3 fix_payment_intent.py pi_3Se8b1BME5ZRi6sp1lMYfUJa kankanamitra01@gmail.com
"""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Use the backend's database connection
from app.core.database import SessionLocal
from app.models.fmv_report import FMVReport, FMVReportStatus
from app.models.user import User
from app.services.fmv_report_service import FMVReportService

def fix_payment_intent(payment_intent_id: str, user_email: str):
    """Fix a payment intent that succeeded but report wasn't created"""
    db = SessionLocal()
    
    try:
        # Find user by email
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            print(f"❌ User not found: {user_email}")
            return False
        
        print(f"✅ Found user: {user.id} - {user.email}")
        
        # Check if report already exists for this payment intent
        existing_report = db.query(FMVReport).filter(
            FMVReport.payment_intent_id == payment_intent_id
        ).first()
        
        if existing_report:
            print(f"✅ Report already exists: {existing_report.id}")
            print(f"   Status: {existing_report.status.value}")
            print(f"   Payment Status: {existing_report.payment_status}")
            
            # If report exists but payment not marked, mark it
            if existing_report.payment_status != "succeeded":
                service = FMVReportService(db)
                # Get amount from Stripe or use default
                amount = existing_report.amount_paid or 495.00
                report = service.mark_payment_received(existing_report.id, payment_intent_id, amount)
                db.commit()
                print(f"✅ Payment marked as received for report {report.id}")
                print(f"   New status: {report.status.value}")
            return True
        
        # Find most recent draft report for this user
        service = FMVReportService(db)
        draft_reports = service.get_user_reports(user.id, "draft")
        
        if draft_reports:
            # Sort by created_at descending
            draft_reports.sort(key=lambda r: r.created_at, reverse=True)
            most_recent = draft_reports[0]
            
            print(f"✅ Found draft report: {most_recent.id}")
            print(f"   Created: {most_recent.created_at}")
            
            # Associate payment intent and mark payment received
            amount = most_recent.amount_paid or 495.00  # Default to $495 for spot check
            report = service.mark_payment_received(most_recent.id, payment_intent_id, amount)
            db.commit()
            
            print(f"✅ Payment marked as received for report {report.id}")
            print(f"   Payment Intent ID: {report.payment_intent_id}")
            print(f"   Amount Paid: ${report.amount_paid}")
            print(f"   Status: {report.status.value}")
            print(f"   Payment Status: {report.payment_status}")
            return True
        else:
            print(f"❌ No draft report found for user {user.id}")
            print("   Cannot automatically fix - report needs to be created manually")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 fix_payment_intent.py <payment_intent_id> <user_email>")
        print("Example: python3 fix_payment_intent.py pi_3Se8b1BME5ZRi6sp1lMYfUJa kankanamitra01@gmail.com")
        sys.exit(1)
    
    payment_intent_id = sys.argv[1]
    user_email = sys.argv[2]
    
    print("="*70)
    print("Fixing Payment Intent")
    print("="*70)
    print(f"Payment Intent ID: {payment_intent_id}")
    print(f"User Email: {user_email}")
    print("="*70)
    print()
    
    success = fix_payment_intent(payment_intent_id, user_email)
    
    if success:
        print("\n✅ Payment intent fixed successfully!")
    else:
        print("\n❌ Failed to fix payment intent")
        sys.exit(1)

