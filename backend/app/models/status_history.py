"""
Status History Model
Tracks status changes for FMV reports
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base


class StatusHistory(Base):
    """Status history model for tracking FMV report status changes"""
    
    __tablename__ = "status_history"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("fmv_reports.id"), nullable=False, index=True)
    
    # Status information
    old_status = Column(String(50), nullable=True)  # Previous status
    new_status = Column(String(50), nullable=False)  # New status
    
    # Change metadata
    changed_by = Column(String(255), nullable=True)  # User ID or email who made the change
    change_reason = Column(Text, nullable=True)  # Optional reason for status change
    notes = Column(Text, nullable=True)  # Additional notes
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    report = relationship("FMVReport", backref="status_history")
    
    def __repr__(self):
        return f"<StatusHistory(id={self.id}, report_id={self.report_id}, {self.old_status} -> {self.new_status})>"

