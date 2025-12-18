"""
Fleet Valuation Usage Tracker
Tracks usage of Fleet Valuation payments (5 valuations per payment)
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime
import logging

from ..models.fmv_report import FMVReport, FMVReportStatus, FMVReportType
from ..models.user import User

logger = logging.getLogger(__name__)


class FleetUsageTracker:
    """Service for tracking Fleet Valuation usage per payment"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_remaining_valuations(self, user_id: int, payment_intent_id: str) -> Dict[str, Any]:
        """
        Get remaining valuations for a Fleet Valuation payment
        Returns: {
            "payment_intent_id": str,
            "total_included": int,  # 5 for Fleet Valuation
            "used": int,
            "remaining": int,
            "can_use": bool
        }
        """
        # Find the report associated with this payment
        report = self.db.query(FMVReport).filter(
            and_(
                FMVReport.payment_intent_id == payment_intent_id,
                FMVReport.user_id == user_id,
                FMVReport.report_type == FMVReportType.FLEET_VALUATION.value
            )
        ).first()
        
        if not report or not report.report_metadata:
            return {
                "payment_intent_id": payment_intent_id,
                "total_included": 0,
                "used": 0,
                "remaining": 0,
                "can_use": False
            }
        
        metadata = report.report_metadata
        total_included = metadata.get("valuations_included", 5)
        used = metadata.get("valuations_used", 0)
        
        # Count all reports using this payment_intent_id
        all_reports = self.db.query(FMVReport).filter(
            and_(
                FMVReport.payment_intent_id == payment_intent_id,
                FMVReport.user_id == user_id,
                FMVReport.report_type == FMVReportType.FLEET_VALUATION.value
            )
        ).count()
        
        used = all_reports  # Actual count of reports created with this payment
        remaining = max(0, total_included - used)
        
        return {
            "payment_intent_id": payment_intent_id,
            "total_included": total_included,
            "used": used,
            "remaining": remaining,
            "can_use": remaining > 0
        }
    
    def can_create_fleet_report(self, user_id: int, payment_intent_id: Optional[str] = None) -> tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Check if user can create a Fleet Valuation report
        Returns: (can_create: bool, message: str, usage_info: Optional[Dict])
        """
        if not payment_intent_id:
            # No payment - must pay first
            return False, "Payment required for Fleet Valuation reports", None
        
        usage_info = self.get_remaining_valuations(user_id, payment_intent_id)
        
        if not usage_info["can_use"]:
            return False, f"You have used all {usage_info['total_included']} valuations from this payment. Please make a new payment to create more Fleet Valuation reports.", usage_info
        
        return True, f"You have {usage_info['remaining']} remaining valuations from this payment.", usage_info
    
    def get_user_fleet_payments(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all Fleet Valuation payments for a user with usage info"""
        # Get all paid Fleet Valuation reports
        reports = self.db.query(FMVReport).filter(
            and_(
                FMVReport.user_id == user_id,
                FMVReport.report_type == FMVReportType.FLEET_VALUATION.value,
                FMVReport.payment_status == "succeeded",
                FMVReport.payment_intent_id.isnot(None)
            )
        ).all()
        
        # Group by payment_intent_id
        payments = {}
        for report in reports:
            payment_id = report.payment_intent_id
            if payment_id not in payments:
                payments[payment_id] = {
                    "payment_intent_id": payment_id,
                    "amount_paid": report.amount_paid,
                    "paid_at": report.paid_at,
                    "total_included": 5,  # Fleet Valuation always includes 5
                    "reports": []
                }
            payments[payment_id]["reports"].append({
                "report_id": report.id,
                "created_at": report.created_at,
                "status": report.status.value if hasattr(report.status, 'value') else str(report.status)
            })
        
        # Calculate usage for each payment
        result = []
        for payment_id, payment_data in payments.items():
            used = len(payment_data["reports"])
            remaining = max(0, payment_data["total_included"] - used)
            payment_data["used"] = used
            payment_data["remaining"] = remaining
            payment_data["can_use"] = remaining > 0
            result.append(payment_data)
        
        # Sort by paid_at descending (most recent first)
        result.sort(key=lambda x: x["paid_at"] if x["paid_at"] else datetime.min, reverse=True)
        
        return result

