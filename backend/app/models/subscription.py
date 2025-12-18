from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from ..core.database import Base


class EmailSubscription(Base):
    __tablename__ = "email_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    company = Column(String(200), nullable=True)
    subscription_type = Column(String(50), default="newsletter")  # newsletter, blog, updates, etc.
    status = Column(String(20), default="active")  # active, unsubscribed, bounced
    source = Column(String(100), nullable=True)  # blog, homepage, contact, etc.
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    subscribed_at = Column(DateTime(timezone=True), server_default=func.now())
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)
    last_email_sent = Column(DateTime(timezone=True), nullable=True)
    email_count = Column(Integer, default=0)
    preferences = Column(Text, nullable=True)  # JSON string for email preferences
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<EmailSubscription(email='{self.email}', status='{self.status}')>"


class UnsubscribeToken(Base):
    __tablename__ = "unsubscribe_tokens"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    is_used = Column(Boolean, default=False)

    def __repr__(self):
        return f"<UnsubscribeToken(email='{self.email}', token='{self.token[:10]}...')>"
