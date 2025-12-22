"""
Consultation Request Model
Handles consultation requests from the homepage
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from datetime import datetime
import enum
from ..core.database import Base


class ConsultationStatus(enum.Enum):
    """Consultation request statuses"""
    NEW = "new"
    CONTACTED = "contacted"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ConsultationRequest(Base):
    """Consultation request model for free consultation requests"""
    
    __tablename__ = "consultation_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Contact information
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True)
    subject = Column(String(255), nullable=True)  # Optional subject field for contact form
    message = Column(Text, nullable=False)
    
    # Status and workflow
    status = Column(String(50), default=ConsultationStatus.NEW.value, nullable=False, index=True)
    
    # Admin fields
    admin_notes = Column(Text, nullable=True)
    contacted_at = Column(DateTime(timezone=True), nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Email notification tracking
    email_sent = Column(Boolean, default=False, nullable=False)
    email_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<ConsultationRequest(id={self.id}, name='{self.name}', email='{self.email}', status='{self.status}')>"

