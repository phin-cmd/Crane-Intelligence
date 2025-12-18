"""
Turnaround Time Tracker Service
Manages turnaround time tracking for FMV reports with milestone notifications
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from ..models.fmv_report import FMVReport, FMVReportStatus, FMVReportType
from .email_service_unified import UnifiedEmailService

logger = logging.getLogger(__name__)


class TurnaroundTracker:
    """Service for tracking turnaround times and sending milestone notifications"""
    
    # Turnaround times in hours
    TURNAROUND_TIMES = {
        FMVReportType.SPOT_CHECK: 24,
        FMVReportType.PROFESSIONAL: 24,
        FMVReportType.FLEET_VALUATION: 72  # 36-72 hours, using 72 for safety
    }
    
    # Milestone percentages for notifications
    MILESTONES = {
        0.5: "12-hour_reminder",  # 12 hours remaining (50% of 24h)
        0.25: "6-hour_warning",    # 6 hours remaining (25% of 24h)
        0.0: "overdue"             # Past deadline
    }
    
    def __init__(self, db: Session):
        self.db = db
        # Use the unified email service (Brevo-backed) for turnaround notifications
        self.email_service = UnifiedEmailService()
    
    def calculate_deadline(self, report_type: FMVReportType, start_time: datetime) -> datetime:
        """Calculate turnaround deadline based on report type"""
        hours = self.TURNAROUND_TIMES.get(report_type, 24)
        return start_time + timedelta(hours=hours)
    
    def set_turnaround_deadline(self, report: FMVReport) -> FMVReport:
        """Set turnaround deadline when report is paid"""
        if not report.paid_at:
            logger.warning(f"Report {report.id} has no paid_at timestamp, cannot set deadline")
            return report
        
        # Get report type enum
        if isinstance(report.report_type, str):
            try:
                report_type = FMVReportType(report.report_type)
            except ValueError:
                logger.error(f"Invalid report type: {report.report_type}")
                report_type = FMVReportType.PROFESSIONAL  # Default
        else:
            report_type = report.report_type
        
        # Calculate deadline from paid_at time
        deadline = self.calculate_deadline(report_type, report.paid_at)
        report.turnaround_deadline = deadline
        
        self.db.commit()
        self.db.refresh(report)
        
        logger.info(f"Set turnaround deadline for report {report.id}: {deadline}")
        return report
    
    def get_time_remaining(self, report: FMVReport) -> Optional[Dict[str, Any]]:
        """Get time remaining until deadline"""
        if not report.turnaround_deadline:
            return None
        
        now = datetime.utcnow()
        if report.turnaround_deadline.tzinfo:
            # Convert to UTC if timezone-aware
            from datetime import timezone
            if report.turnaround_deadline.tzinfo != timezone.utc:
                now = now.replace(tzinfo=timezone.utc)
        
        time_remaining = report.turnaround_deadline - now
        
        if time_remaining.total_seconds() < 0:
            # Overdue
            return {
                "is_overdue": True,
                "hours_remaining": 0,
                "minutes_remaining": 0,
                "seconds_remaining": 0,
                "total_seconds": int(time_remaining.total_seconds()),
                "deadline": report.turnaround_deadline.isoformat()
            }
        
        total_seconds = int(time_remaining.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return {
            "is_overdue": False,
            "hours_remaining": hours,
            "minutes_remaining": minutes,
            "seconds_remaining": seconds,
            "total_seconds": total_seconds,
            "deadline": report.turnaround_deadline.isoformat()
        }
    
    def check_milestones(self, report: FMVReport) -> List[str]:
        """Check if any milestones have been reached and return list of milestone keys"""
        if not report.turnaround_deadline:
            return []
        
        time_info = self.get_time_remaining(report)
        if not time_info:
            return []
        
        if time_info["is_overdue"]:
            return ["overdue"]
        
        # Calculate percentage of time remaining
        if isinstance(report.report_type, str):
            try:
                report_type = FMVReportType(report.report_type)
            except ValueError:
                report_type = FMVReportType.PROFESSIONAL
        else:
            report_type = report.report_type
        
        total_hours = self.TURNAROUND_TIMES.get(report_type, 24)
        hours_remaining = time_info["hours_remaining"]
        percentage_remaining = hours_remaining / total_hours if total_hours > 0 else 0
        
        milestones_reached = []
        
        # Check each milestone
        for threshold, milestone_key in self.MILESTONES.items():
            if percentage_remaining <= threshold and milestone_key != "overdue":
                milestones_reached.append(milestone_key)
        
        return milestones_reached
    
    def send_milestone_notification(self, report: FMVReport, milestone: str) -> bool:
        """Send email notification for milestone"""
        if not report.user:
            logger.warning(f"Report {report.id} has no associated user")
            return False
        
        user_email = report.user.email
        if not user_email:
            logger.warning(f"User {report.user.id} has no email")
            return False
        
        # Get report type name
        report_type_name = "Report"
        if isinstance(report.report_type, str):
            report_type_name = report.report_type.replace("_", " ").title()
        else:
            report_type_name = report.report_type.value.replace("_", " ").title()
        
        time_info = self.get_time_remaining(report)
        
        subject = f"FMV {report_type_name} Update - {milestone.replace('_', ' ').title()}"
        
        # Build email content using templates
        from pathlib import Path
        from jinja2 import Environment, FileSystemLoader
        
        # Get template directory
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        if not template_dir.exists():
            template_dir.mkdir(parents=True, exist_ok=True)
        
        jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        # Select template based on milestone
        template_name = None
        if milestone == "12-hour_reminder":
            template_name = "turnaround_12hour_reminder.html"
        elif milestone == "6-hour_warning":
            template_name = "turnaround_6hour_warning.html"
        elif milestone == "overdue":
            template_name = "turnaround_overdue.html"
        
        # Render template if available, otherwise use simple HTML
        if template_name and template_dir.joinpath(template_name).exists():
            try:
                template = jinja_env.get_template(template_name)
                deadline_str = report.turnaround_deadline.strftime("%Y-%m-%d %H:%M:%S UTC") if report.turnaround_deadline else "N/A"
                dashboard_url = f"https://craneintelligence.tech/fmv-reports.html"
                
                body = template.render(
                    report_type=report_type_name,
                    report_id=report.id,
                    deadline=deadline_str,
                    dashboard_url=dashboard_url
                )
            except Exception as e:
                logger.warning(f"Failed to render email template {template_name}: {e}, using fallback")
                body = self._get_fallback_email_body(milestone, report_type_name, report.id)
        else:
            body = self._get_fallback_email_body(milestone, report_type_name, report.id)
        
        try:
            self.email_service.send_email(
                to_email=user_email,
                subject=subject,
                html_content=body
            )
            logger.info(f"Sent {milestone} notification for report {report.id} to {user_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send milestone notification: {e}")
            return False
    
    def process_all_reports(self) -> Dict[str, Any]:
        """Process all active reports to check milestones and send notifications"""
        # Get all reports that are in progress and have a deadline
        active_reports = self.db.query(FMVReport).filter(
            FMVReport.turnaround_deadline.isnot(None),
            FMVReport.status.in_([
                FMVReportStatus.PAID,
                FMVReportStatus.IN_REVIEW,
                FMVReportStatus.IN_PROGRESS
            ])
        ).all()
        
        results = {
            "processed": 0,
            "notifications_sent": 0,
            "overdue_count": 0
        }
        
        for report in active_reports:
            results["processed"] += 1
            
            milestones = self.check_milestones(report)
            
            if "overdue" in milestones:
                results["overdue_count"] += 1
                # Update status to overdue if not already
                if report.status != FMVReportStatus.DELIVERED:
                    # Note: We don't have an OVERDUE status, so we'll track it in metadata
                    if not report.report_metadata:
                        report.report_metadata = {}
                    report.report_metadata["is_overdue"] = True
                    self.db.commit()
            
            # Send notifications for milestones
            for milestone in milestones:
                if self.send_milestone_notification(report, milestone):
                    results["notifications_sent"] += 1
                    # Track sent milestones in metadata to avoid duplicates
                    if not report.report_metadata:
                        report.report_metadata = {}
                    if "milestones_sent" not in report.report_metadata:
                        report.report_metadata["milestones_sent"] = []
                    if milestone not in report.report_metadata["milestones_sent"]:
                        report.report_metadata["milestones_sent"].append(milestone)
                        self.db.commit()
        
        return results
    
    def _get_fallback_email_body(self, milestone: str, report_type_name: str, report_id: int) -> str:
        """Fallback email body if template rendering fails"""
        if milestone == "12-hour_reminder":
            return f"""
            <p>This is a reminder that your FMV {report_type_name} (Report ID: {report_id}) is due in approximately 12 hours.</p>
            <p>Our team is working on your report and will deliver it on time.</p>
            """
        elif milestone == "6-hour_warning":
            return f"""
            <p>Your FMV {report_type_name} (Report ID: {report_id}) is due in approximately 6 hours.</p>
            <p>We're in the final stages of completing your report.</p>
            """
        elif milestone == "overdue":
            return f"""
            <p>We apologize for the delay. Your FMV {report_type_name} (Report ID: {report_id}) is past its deadline.</p>
            <p>Our team is prioritizing your report and will deliver it as soon as possible.</p>
            <p>If you have any concerns, please contact our support team.</p>
            """
        else:
            return f"""
            <p>Update on your FMV {report_type_name} (Report ID: {report_id}).</p>
            """
    
    def get_overdue_reports(self) -> List[FMVReport]:
        """Get all overdue reports"""
        now = datetime.utcnow()
        
        # Handle timezone-aware comparisons
        from datetime import timezone
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        
        overdue_reports = self.db.query(FMVReport).filter(
            FMVReport.turnaround_deadline.isnot(None),
            FMVReport.turnaround_deadline < now,
            FMVReport.status.in_([
                FMVReportStatus.PAID,
                FMVReportStatus.IN_REVIEW,
                FMVReportStatus.IN_PROGRESS
            ])
        ).all()
        
        return overdue_reports

