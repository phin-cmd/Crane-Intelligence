"""
Notification Preference Models
Handles user notification preferences for email notifications
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from datetime import datetime
from ..core.database import Base


class NotificationPreference(Base):
    """Notification preference model for user email notification settings"""
    
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Email notification preferences
    email_notifications_enabled = Column(Boolean, default=True)
    
    # Category preferences
    fmv_report_notifications = Column(Boolean, default=True)  # All FMV report notifications
    fmv_report_important_only = Column(Boolean, default=False)  # Only important (delivered, rejected, cancelled)
    payment_notifications = Column(Boolean, default=True)  # All payment notifications
    payment_important_only = Column(Boolean, default=False)  # Only important (failed, refunded)
    account_management_notifications = Column(Boolean, default=True)  # All account management notifications
    account_management_important_only = Column(Boolean, default=False)  # Only important (deletion, security)
    marketing_emails = Column(Boolean, default=False)  # Marketing/promotional emails (opt-in)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<NotificationPreference(user_id={self.user_id}, email_enabled={self.email_notifications_enabled})>"
    
    def should_send_notification(self, notification_type: str, is_important: bool = False) -> bool:
        """
        Check if a notification should be sent based on preferences
        
        Args:
            notification_type: Type of notification (fmv_report, payment, account_management, marketing)
            is_important: Whether this is an important notification
        
        Returns:
            bool: True if notification should be sent
        """
        if not self.email_notifications_enabled:
            return False
        
        if notification_type == "fmv_report":
            if self.fmv_report_important_only:
                return is_important
            return self.fmv_report_notifications
        
        elif notification_type == "payment":
            if self.payment_important_only:
                return is_important
            return self.payment_notifications
        
        elif notification_type == "account_management":
            if self.account_management_important_only:
                return is_important
            return self.account_management_notifications
        
        elif notification_type == "marketing":
            return self.marketing_emails
        
        # Default: send all non-marketing notifications
        return notification_type != "marketing"


class NotificationLog(Base):
    """Notification log for tracking sent notifications"""
    
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)  # Nullable for admin notifications
    admin_user_id = Column(Integer, nullable=True, index=True)  # For admin-specific notifications
    
    notification_type = Column(String, nullable=False, index=True)
    notification_category = Column(String, nullable=False)  # fmv_report, payment, account_management, etc.
    recipient_email = Column(String, nullable=False, index=True)
    subject = Column(String, nullable=False)
    template_name = Column(String, nullable=True)
    
    # Delivery status
    sent_at = Column(DateTime, default=func.now(), nullable=False)
    success = Column(Boolean, default=True)
    error_message = Column(String, nullable=True)
    message_id = Column(String, nullable=True)  # Brevo message ID
    
    # Metadata
    metadata = Column(JSON, nullable=True)  # Additional context data
    
    def __repr__(self):
        return f"<NotificationLog(id={self.id}, type='{self.notification_type}', success={self.success})>"

