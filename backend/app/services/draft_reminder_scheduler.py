"""
Draft Report Reminder Scheduler
Sends email reminders every 8 hours for draft reports
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List

from ..core.database import SessionLocal
from ..core.config import settings
from ..models.fmv_report import FMVReport, FMVReportStatus
from ..models.user import User
from .fmv_email_service import FMVEmailService
from .fmv_report_service import FMVReportService

logger = logging.getLogger(__name__)


def send_draft_reminders(db: Session = None) -> dict:
    """
    Send reminder emails for all draft reports that need reminders
    Sends reminders every 8 hours after initial creation
    """
    if db is None:
        db = SessionLocal()
    
    try:
        # Get all draft reports
        draft_reports = db.query(FMVReport).filter(
            FMVReport.status == FMVReportStatus.DRAFT
        ).all()
        
        if not draft_reports:
            logger.info("No draft reports found for reminders")
            return {"sent": 0, "skipped": 0, "errors": 0}
        
        email_service = FMVEmailService()
        report_service = FMVReportService(db)
        sent_count = 0
        skipped_count = 0
        error_count = 0
        
        current_time = datetime.utcnow()
        
        for report in draft_reports:
            try:
                # Calculate hours since creation
                hours_since_creation = (current_time - report.created_at).total_seconds() / 3600
                
                # Send reminder every 8 hours (0, 8, 16, 24, 32, 40, 48, etc.)
                # Check if it's time for a reminder (within 1 hour window of 8-hour intervals)
                reminder_interval = int(hours_since_creation // 8)
                next_reminder_hour = (reminder_interval + 1) * 8
                hours_until_next = next_reminder_hour - hours_since_creation
                
                # Only send if we're within 1 hour of the next 8-hour interval
                # or if it's been exactly 8, 16, 24, etc. hours
                should_send = False
                reminder_type = "initial"
                
                if hours_since_creation < 1:
                    # Initial reminder (already sent, but check if we need to send again)
                    should_send = False  # Initial reminder is sent immediately on creation
                elif hours_since_creation >= 8 and hours_until_next <= 1:
                    # Time for 8-hour reminder
                    should_send = True
                    reminder_type = f"{reminder_interval * 8}-hour"
                elif hours_since_creation >= 8 and (hours_since_creation % 8) < 1:
                    # Within 1 hour of an 8-hour interval
                    should_send = True
                    reminder_type = f"{int(hours_since_creation // 8) * 8}-hour"
                
                if not should_send:
                    skipped_count += 1
                    continue
                
                # Get user
                user = db.query(User).filter(User.id == report.user_id).first()
                if not user:
                    logger.warning(f"User not found for report {report.id}")
                    skipped_count += 1
                    continue
                
                # Calculate report amount
                report_type_value = report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type)
                if report_type_value == 'spot_check':
                    amount = 495.00
                elif report_type_value == 'professional':
                    amount = 995.00
                elif report_type_value == 'fleet_valuation':
                    if report.fleet_pricing_tier:
                        amount = report_service.calculate_fleet_price(report.fleet_pricing_tier)
                    else:
                        amount = 1495.00
                else:
                    amount = 995.00
                
                # Send reminder email
                email_result = email_service.send_draft_reminder_notification(
                    user_email=user.email,
                    user_name=user.full_name or user.username,
                    report_data={
                        "report_id": report.id,
                        "report_type": report_type_value,
                        "amount": amount,
                        "hours_since_creation": hours_since_creation,
                        "reminder_interval": reminder_type,
                        "payment_url": f"{settings.frontend_url}/report-generation.html",
                        "report_type_display": report_type_value.replace('_', ' ').title()
                    }
                )
                
                if email_result:
                    sent_count += 1
                    logger.info(f"✅ Sent {reminder_type} reminder email for draft report {report.id} to {user.email}")
                    
                    # Create notification for user
                    try:
                        from ..models.notification import UserNotification
                        user_notification = UserNotification(
                            user_id=user.id,
                            title=f"Reminder: Complete Your FMV Report Payment - Report #{report.id}",
                            message=f"Your FMV Report #{report.id} is still waiting for payment. Complete your purchase to submit the report.",
                            type="fmv_report_draft_reminder",
                            read=False
                        )
                        db.add(user_notification)
                        db.commit()
                        logger.info(f"✅ Created reminder notification for draft report {report.id}")
                    except Exception as notif_error:
                        logger.warning(f"⚠️ Failed to create reminder notification: {notif_error}")
                        db.rollback()
                else:
                    error_count += 1
                    logger.warning(f"⚠️ Failed to send reminder email for draft report {report.id}")
                    
            except Exception as e:
                error_count += 1
                logger.error(f"❌ Error processing draft report {report.id}: {e}", exc_info=True)
        
        result = {
            "sent": sent_count,
            "skipped": skipped_count,
            "errors": error_count,
            "total": len(draft_reports)
        }
        
        logger.info(f"📧 Draft reminder summary: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in send_draft_reminders: {e}", exc_info=True)
        return {"sent": 0, "skipped": 0, "errors": 1, "error": str(e)}
    finally:
        if db is not None:
            db.close()

