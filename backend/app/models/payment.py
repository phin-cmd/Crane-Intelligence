"""
Payment and Refund Models
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base


class PaymentStatus(enum.Enum):
    """Payment status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    CANCELLED = "cancelled"


class RefundStatus(enum.Enum):
    """Refund status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Payment(Base):
    """Payment records"""
    
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Stripe information
    stripe_payment_intent_id = Column(String, unique=True, index=True, nullable=True)
    stripe_charge_id = Column(String, nullable=True)
    stripe_customer_id = Column(String, nullable=True, index=True)
    
    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, default=PaymentStatus.PENDING.value, index=True)
    
    # Related entities
    fmv_report_id = Column(Integer, ForeignKey("fmv_reports.id"), nullable=True)
    subscription_tier = Column(String, nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    payment_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' to avoid SQLAlchemy reserved name conflict
    
    # Reconciliation
    is_reconciled = Column(Boolean, default=False)
    reconciled_at = Column(DateTime, nullable=True)
    reconciled_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    paid_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", backref="payments")
    fmv_report = relationship("FMVReport", backref="payment")
    reconciler = relationship("AdminUser", foreign_keys=[reconciled_by])
    
    def __repr__(self):
        return f"<Payment(id={self.id}, user_id={self.user_id}, amount={self.amount}, status={self.status})>"


class Refund(Base):
    """Refund records"""
    
    __tablename__ = "refunds"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Stripe information
    stripe_refund_id = Column(String, unique=True, index=True, nullable=True)
    
    # Refund details
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, default=RefundStatus.PENDING.value, index=True)
    reason = Column(String, nullable=True)  # duplicate, fraudulent, requested_by_customer
    
    # Admin information
    processed_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    payment = relationship("Payment", backref="refunds")
    user = relationship("User", backref="refunds")
    processor = relationship("AdminUser", foreign_keys=[processed_by])
    
    def __repr__(self):
        return f"<Refund(id={self.id}, payment_id={self.payment_id}, amount={self.amount}, status={self.status})>"

