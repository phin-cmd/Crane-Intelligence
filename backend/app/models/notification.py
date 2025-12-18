"""
Notification Model
Stores user notifications
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from ..core.database import Base


class UserNotification(Base):
    """User notification model for regular users"""
    
    __tablename__ = "user_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False, default="system")  # email_verification, payment_success, report_ready, system
    read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=func.now(), index=True)
    
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<UserNotification(id={self.id}, user_id={self.user_id}, title='{self.title}', read={self.read})>"

