"""
FMV Report Models
Handles Fair Market Value report requests and workflow management
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum, Float, Text, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base


class FMVReportStatus(enum.Enum):
    """FMV Report workflow statuses"""
    DRAFT = "draft"  # Form filled, purchase clicked but payment not completed
    SUBMITTED = "submitted"  # Form filled, payment successful
    IN_PROGRESS = "in_progress"  # Admin views report and changes status to in_progress
    COMPLETED = "completed"  # Admin completes the FMV report
    DELIVERED = "delivered"  # Admin uploads PDF and clicks "Upload and send to customer"
    NEED_MORE_INFO = "need_more_info"  # Admin needs more information to complete report
    OVERDUE = "overdue"  # Admin didn't complete within 24 hours (calculated status)
    DELETED = "deleted"  # User deleted the report (soft delete)


class FMVReportType(enum.Enum):
    """FMV Report types based on subscription tier"""
    SPOT_CHECK = "spot_check"
    PROFESSIONAL = "professional"
    FLEET_VALUATION = "fleet_valuation"


class FleetPricingTier(enum.Enum):
    """Fleet pricing tiers - Tiered pricing model"""
    TIER_1_5 = "1-5"      # $1,495 ($299 per crane)
    TIER_6_10 = "6-10"    # $2,495 ($249 per crane)
    TIER_11_25 = "11-25"  # $4,995 ($199 per crane)
    TIER_26_50 = "26-50"  # $7,995 (~$159 per crane)


class FMVReport(Base):
    """FMV Report model for managing report requests and workflow"""
    
    __tablename__ = "fmv_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Report type
    report_type = Column(Enum(FMVReportType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    
    # Status and workflow
    status = Column(Enum(FMVReportStatus, values_callable=lambda x: [e.value for e in x]), 
                    default=FMVReportStatus.DRAFT, nullable=False, index=True)
    
    # Crane details (JSON field for flexibility)
    crane_details = Column(JSON, nullable=False)  # manufacturer, model, year, capacity, hours, etc.
    service_records = Column(JSON, nullable=True)  # Service history, maintenance records (can be file URLs or structured data)
    service_record_files = Column(JSON, nullable=True)  # Array of service record file URLs
    
    # Fleet-specific fields
    fleet_pricing_tier = Column(Enum(FleetPricingTier, values_callable=lambda x: [e.value for e in x]), nullable=True)
    unit_count = Column(Integer, nullable=True)  # Number of cranes for fleet reports
    
    # Payment information
    amount_paid = Column(Float, nullable=True)
    payment_intent_id = Column(String(255), nullable=True, index=True)
    payment_status = Column(String(50), nullable=True)
    
    # Timestamps for status transitions
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)  # When payment received
    in_progress_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    need_more_info_at = Column(DateTime(timezone=True), nullable=True)  # When admin requests more info
    overdue_at = Column(DateTime(timezone=True), nullable=True)  # When report becomes overdue
    # Note: deleted_at column removed - not present in database table
    # deleted_at = Column(DateTime(timezone=True), nullable=True)  # When report was deleted (soft delete)
    # Legacy fields kept for backward compatibility (paid_at maps to submitted_at)
    paid_at = Column(DateTime(timezone=True), nullable=True)  # Deprecated - use submitted_at
    
    # Turnaround time tracking
    turnaround_deadline = Column(DateTime(timezone=True), nullable=True)  # Deadline for report completion
    
    # Report delivery
    pdf_url = Column(String(500), nullable=True)
    pdf_uploaded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Admin/analyst fields
    analyst_notes = Column(Text, nullable=True)
    need_more_info_reason = Column(Text, nullable=True)  # Reason why more info is needed
    assigned_analyst = Column(String(255), nullable=True)
    # Legacy field kept for backward compatibility
    rejection_reason = Column(Text, nullable=True)  # Deprecated - use need_more_info_reason
    
    # Additional metadata (renamed to avoid SQLAlchemy reserved name conflict)
    report_metadata = Column("metadata", JSON, nullable=True)  # Additional flexible data
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="fmv_reports")
    
    def __repr__(self):
        status_val = self.status.value if hasattr(self.status, 'value') else str(self.status)
        type_val = self.report_type.value if hasattr(self.report_type, 'value') else str(self.report_type)
        return f"<FMVReport(id={self.id}, user_id={self.user_id}, status='{status_val}', type='{type_val}')>"
    
    def get_status_timeline(self):
        """Get timeline of status transitions"""
        timeline = []
        
        if self.created_at:
            timeline.append({
                "status": "draft",
                "timestamp": self.created_at,
                "details": "Report draft created"
            })
        
        if self.submitted_at:
            timeline.append({
                "status": "submitted",
                "timestamp": self.submitted_at,
                "details": f"Order received - Payment confirmed: ${self.amount_paid:,.2f}" if self.amount_paid else "Order received"
            })
        
        # Legacy: paid_at maps to submitted_at for backward compatibility
        if self.paid_at and not self.submitted_at:
            timeline.append({
                "status": "submitted",
                "timestamp": self.paid_at,
                "details": f"Order received - Payment confirmed: ${self.amount_paid:,.2f}" if self.amount_paid else "Order received"
            })
        
        if self.in_progress_at:
            timeline.append({
                "status": "in_progress",
                "timestamp": self.in_progress_at,
                "details": f"Analyst working: {self.assigned_analyst}" if self.assigned_analyst else "Analyst working"
            })
        
        if self.completed_at:
            timeline.append({
                "status": "completed",
                "timestamp": self.completed_at,
                "details": "PDF ready"
            })
        
        if self.delivered_at:
            timeline.append({
                "status": "delivered",
                "timestamp": self.delivered_at,
                "details": "Email sent - Report delivered"
            })
        
        if self.need_more_info_at:
            timeline.append({
                "status": "need_more_info",
                "timestamp": self.need_more_info_at,
                "details": self.need_more_info_reason or "More information needed"
            })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x["timestamp"])
        return timeline

