"""
Fallback Request Model
Handles manual valuation requests for cranes not found in the database
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base


class FallbackRequestStatus(enum.Enum):
    """Fallback request statuses"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    VALUATION_IN_PROGRESS = "valuation_in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class FallbackRequest(Base):
    """Fallback request model for manual crane valuations"""
    
    __tablename__ = "fallback_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Nullable for unauthenticated users
    user_email = Column(String(255), nullable=False, index=True)  # Email for unauthenticated users
    
    # Crane details
    manufacturer = Column(String(255), nullable=False)
    model = Column(String(255), nullable=False)
    year = Column(Integer, nullable=False)
    serial_number = Column(String(255), nullable=True)
    capacity_tons = Column(Float, nullable=False)
    crane_type = Column(String(100), nullable=False)
    operating_hours = Column(Integer, nullable=False)
    mileage = Column(Integer, nullable=True)
    boom_length = Column(Float, nullable=True)
    jib_length = Column(Float, nullable=True)
    max_hook_height = Column(Float, nullable=True)
    max_radius = Column(Float, nullable=True)
    region = Column(String(100), nullable=False)
    condition = Column(String(50), nullable=False)
    additional_specs = Column(Text, nullable=True)
    special_features = Column(Text, nullable=True)
    usage_history = Column(Text, nullable=True)
    
    # Status and workflow
    status = Column(String(50), default=FallbackRequestStatus.PENDING.value, nullable=False, index=True)
    
    # Admin/analyst fields
    assigned_analyst = Column(String(255), nullable=True)
    analyst_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Linked FMV report (created after valuation)
    linked_fmv_report_id = Column(Integer, ForeignKey("fmv_reports.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    in_review_at = Column(DateTime(timezone=True), nullable=True)
    valuation_started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="fallback_requests")
    linked_fmv_report = relationship("FMVReport", foreign_keys=[linked_fmv_report_id])
    
    def __repr__(self):
        return f"<FallbackRequest(id={self.id}, manufacturer='{self.manufacturer}', model='{self.model}', status='{self.status}')>"

