"""
Visitor Tracking Model
Tracks website visitors, demographics, and behavior
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, Index
from sqlalchemy.sql import func
from datetime import datetime
from .base import Base
import json


class VisitorTracking(Base):
    __tablename__ = "visitor_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Visitor Identification
    visitor_id = Column(String(255), index=True, nullable=False)  # Unique visitor identifier (cookie/session)
    session_id = Column(String(255), index=True, nullable=False)  # Session identifier
    user_id = Column(Integer, index=True, nullable=True)  # If logged in user
    
    # Page/Route Information
    page_url = Column(Text, nullable=False)
    page_title = Column(String(500), nullable=True)
    referrer = Column(Text, nullable=True)
    referrer_domain = Column(String(255), nullable=True)
    
    # Device & Browser Information
    user_agent = Column(Text, nullable=True)
    browser = Column(String(100), nullable=True)  # Chrome, Firefox, Safari, etc.
    browser_version = Column(String(50), nullable=True)
    device_type = Column(String(50), nullable=True)  # desktop, mobile, tablet
    device_brand = Column(String(100), nullable=True)  # Apple, Samsung, etc.
    device_model = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)  # Windows, macOS, iOS, Android, Linux
    os_version = Column(String(50), nullable=True)
    screen_width = Column(Integer, nullable=True)
    screen_height = Column(Integer, nullable=True)
    screen_resolution = Column(String(50), nullable=True)  # e.g., "1920x1080"
    
    # Location Information
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    country = Column(String(100), nullable=True)
    country_code = Column(String(2), nullable=True)  # ISO 3166-1 alpha-2
    region = Column(String(100), nullable=True)  # State/Province
    city = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timezone = Column(String(100), nullable=True)
    
    # Engagement Metrics
    time_on_page = Column(Integer, nullable=True)  # Seconds
    scroll_depth = Column(Integer, nullable=True)  # Percentage (0-100)
    exit_page = Column(Boolean, default=False)
    bounce = Column(Boolean, default=False)
    
    # Traffic Source
    traffic_source = Column(String(50), nullable=True)  # organic, direct, referral, social, email, paid
    campaign = Column(String(255), nullable=True)
    medium = Column(String(100), nullable=True)
    source = Column(String(255), nullable=True)
    keyword = Column(String(255), nullable=True)
    
    # Additional Metadata
    language = Column(String(10), nullable=True)  # e.g., "en-US"
    is_bot = Column(Boolean, default=False)
    is_mobile = Column(Boolean, default=False)
    is_tablet = Column(Boolean, default=False)
    is_desktop = Column(Boolean, default=False)
    
    # Timestamps
    visited_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Additional data as JSON (renamed from 'metadata' because it's reserved in SQLAlchemy)
    additional_metadata = Column(Text, nullable=True)  # JSON string for additional data
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_visitor_date', 'visitor_id', 'visited_at'),
        Index('idx_user_date', 'user_id', 'visited_at'),
        Index('idx_page_date', 'page_url', 'visited_at'),
        Index('idx_country_date', 'country', 'visited_at'),
        Index('idx_device_date', 'device_type', 'visited_at'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        metadata_dict = {}
        if self.additional_metadata:
            try:
                metadata_dict = json.loads(self.additional_metadata)
            except:
                pass
        
        return {
            'id': self.id,
            'visitor_id': self.visitor_id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'page_url': self.page_url,
            'page_title': self.page_title,
            'referrer': self.referrer,
            'referrer_domain': self.referrer_domain,
            'browser': self.browser,
            'browser_version': self.browser_version,
            'device_type': self.device_type,
            'device_brand': self.device_brand,
            'device_model': self.device_model,
            'os': self.os,
            'os_version': self.os_version,
            'screen_resolution': self.screen_resolution,
            'country': self.country,
            'country_code': self.country_code,
            'region': self.region,
            'city': self.city,
            'timezone': self.timezone,
            'time_on_page': self.time_on_page,
            'scroll_depth': self.scroll_depth,
            'traffic_source': self.traffic_source,
            'campaign': self.campaign,
            'medium': self.medium,
            'source': self.source,
            'keyword': self.keyword,
            'language': self.language,
            'is_bot': self.is_bot,
            'is_mobile': self.is_mobile,
            'is_tablet': self.is_tablet,
            'is_desktop': self.is_desktop,
            'visited_at': self.visited_at.isoformat() if self.visited_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'metadata': metadata_dict
        }

