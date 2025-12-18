#!/usr/bin/env python3
"""
Script to fix report #20 payment status
Updates report status from DRAFT to SUBMITTED and sends notifications
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.fmv_report import FMVReport, FMVReportStatus
from app.models.user import User
from app.models.notification import UserNotification
from app.services.fmv_report_service import FMVReportService
from app.services.fmv_email_service import FMVEmailService
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_report_20():
    """Fix report #20 payment status"""
    db = SessionLocal()
    try:
        # Find report #20
        report = db.query(FMVReport).filter(FMVReport.id == 20).first()
        if not report:
            logger.error("Report #20 not found")
            return False
        
        logger.info(f"Found report #20: status={report.status.value}, payment_status={report.payment_status}, amount_paid={report.amount_paid}, payment_intent_id={report.payment_intent_id}")
        
        # Check if payment was successful
        # Since payment_intent_id exists (pi_3SfRzvBME5ZRi6sp4KAOAgkX), payment was successful
        # We'll use the amount from the payment (Spot Check = $495)
        if report.payment_intent_id:
            # Payment intent exists, so payment was successful
            # Determine amount based on report type
            service = FMVReportService(db)
            
            # Get amount from report metadata or use default based on report type
            if report.amount_paid and report.amount_paid > 0:
                amount_dollars = report.amount_paid
            else:
                # Determine amount from report type
                report_type = report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type)
                if report_type == "spot_check":
                    amount_dollars = 495.0
                elif report_type == "professional":
                    amount_dollars = 995.0
                elif report_type == "fleet_valuation":
                    # Use tiered pricing
                    if report.unit_count and report.unit_count <= 5:
                        amount_dollars = 1495.0
                    elif report.unit_count and report.unit_count <= 10:
                        amount_dollars = 2495.0
                    elif report.unit_count and report.unit_count <= 25:
                        amount_dollars = 4995.0
                    else:
                        amount_dollars = 7995.0
                else:
                    amount_dollars = 495.0  # Default to spot check price
            
            logger.info(f"Using amount: ${amount_dollars} for report type: {report_type}")
            
            # Directly update report status (bypass service to avoid import issues)
            report.amount_paid = amount_dollars
            report.payment_status = "succeeded"
            report.status = FMVReportStatus.SUBMITTED
            report.submitted_at = datetime.utcnow()
            report.paid_at = datetime.utcnow()
            
            db.commit()
            db.refresh(report)
            logger.info(f"✅ Updated report #20: status={report.status.value}, amount_paid=${report.amount_paid}, payment_status={report.payment_status}")
            
            updated_report = report
            
            # Get user
            user = db.query(User).filter(User.id == updated_report.user_id).first()
            if user:
                # Send notifications
                email_service = FMVEmailService()
                
                # Send submission notification
                try:
                    email_service.send_submitted_notification(
                        user_email=user.email,
                        user_name=user.full_name,
                        report_data={
                            "report_id": updated_report.id,
                            "report_type": updated_report.report_type.value if hasattr(updated_report.report_type, 'value') else str(updated_report.report_type),
                            "amount": amount_dollars,
                            "payment_intent_id": updated_report.payment_intent_id
                        }
                    )
                    logger.info("✅ Sent submission notification")
                except Exception as e:
                    logger.error(f"❌ Failed to send submission notification: {e}")
                
                # Send payment receipt
                try:
                    email_service.send_payment_receipt(
                        user_email=user.email,
                        user_name=user.full_name,
                        report_data={
                            "report_id": updated_report.id,
                            "amount": amount_dollars,
                            "payment_intent_id": updated_report.payment_intent_id,
                            "transaction_id": updated_report.payment_intent_id
                        }
                    )
                    logger.info("✅ Sent payment receipt")
                except Exception as e:
                    logger.error(f"❌ Failed to send payment receipt: {e}")
                
                # Create user notification
                try:
                    # Check if notification already exists
                    existing_notif = db.query(UserNotification).filter(
                        UserNotification.user_id == user.id,
                        UserNotification.type == "fmv_report_submitted",
                        UserNotification.title.like(f"%Report #{updated_report.id}%")
                    ).first()
                    
                    if not existing_notif:
                        user_notification = UserNotification(
                            user_id=user.id,
                            title=f"FMV Report #{updated_report.id} Submitted",
                            message=f"Your FMV Report #{updated_report.id} has been submitted successfully. Payment received: ${amount_dollars:,.2f}",
                            type="fmv_report_submitted",
                            read=False
                        )
                        db.add(user_notification)
                        db.commit()
                        logger.info("✅ Created user notification")
                    else:
                        logger.info("ℹ️ Notification already exists")
                except Exception as e:
                    logger.error(f"❌ Failed to create notification: {e}")
                    db.rollback()
            else:
                logger.error("User not found for report #20")
            
            return True
        else:
            logger.warning("Report #20 has no payment_intent_id")
            return False
            
    except Exception as e:
        logger.error(f"Error fixing report #20: {e}", exc_info=True)
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting fix for report #20...")
    success = fix_report_20()
    if success:
        logger.info("✅ Report #20 fixed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Failed to fix report #20")
        sys.exit(1)

