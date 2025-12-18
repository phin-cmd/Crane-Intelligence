"""
Admin-specific models for Crane Intelligence Platform
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base


class AdminRole(enum.Enum):
    """Admin roles for platform management"""
    SUPER_ADMIN = "super_admin"      # Full platform access (can manage admin users)
    ADMIN = "admin"                  # Full access without managing admin users
    MANAGER = "manager"              # All pages except delete access
    SUPPORT = "support"              # Read only and minimal managing access
    IMPERSONATOR = "impersonator"    # Access as live customers (impersonation only)


class ContentStatus(enum.Enum):
    """Content publication status"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContentType(enum.Enum):
    """Content types for CMS"""
    ARTICLE = "article"
    BLOG_POST = "blog_post"
    NEWS = "news"
    RESOURCE = "resource"
    WHITEPAPER = "whitepaper"
    CASE_STUDY = "case_study"


class SystemLogLevel(enum.Enum):
    """System log levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AdminUser(Base):
    """Admin users for platform management"""
    
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    admin_role = Column(String, nullable=False, default=AdminRole.ADMIN.value)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)
    
    # Two-Factor Authentication
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String, nullable=True)  # Encrypted TOTP secret
    two_factor_backup_codes = Column(JSON, nullable=True)  # Backup codes for 2FA
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime, nullable=True)
    
    # Session management
    last_ip_address = Column(String, nullable=True)
    last_user_agent = Column(Text, nullable=True)
    
    # Permissions
    permissions = Column(JSON)  # JSON array of specific permissions
    
    # Relationships
    sessions = relationship("AdminSession", back_populates="admin_user", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<AdminUser(id={self.id}, email='{self.email}', role='{self.admin_role}')>"


class ContentItem(Base):
    """Content management system items"""
    
    __tablename__ = "content_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    content_type = Column(String, nullable=False, default=ContentType.ARTICLE.value)
    content = Column(Text, nullable=False)
    excerpt = Column(Text)
    
    # SEO
    meta_title = Column(String)
    meta_description = Column(Text)
    meta_keywords = Column(Text)
    
    # Status and workflow
    status = Column(String, default=ContentStatus.DRAFT.value)
    author_id = Column(Integer, ForeignKey("admin_users.id"))
    reviewer_id = Column(Integer, ForeignKey("admin_users.id"))
    
    # Publishing
    published_at = Column(DateTime)
    scheduled_at = Column(DateTime)
    
    # Media
    featured_image = Column(String)
    media_files = Column(JSON)  # Array of media file references
    
    # Analytics
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    author = relationship("AdminUser", foreign_keys=[author_id])
    reviewer = relationship("AdminUser", foreign_keys=[reviewer_id])
    
    def __repr__(self):
        return f"<ContentItem(id={self.id}, title='{self.title}', status='{self.status}')>"


class MediaFile(Base):
    """Media files for content management"""
    
    __tablename__ = "media_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    
    # Image specific
    width = Column(Integer)
    height = Column(Integer)
    alt_text = Column(String)
    caption = Column(Text)
    
    # Organization
    folder_path = Column(String, default="/")
    tags = Column(JSON)  # Array of tags
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Upload info
    uploaded_by = Column(Integer, ForeignKey("admin_users.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    uploader = relationship("AdminUser")
    
    def __repr__(self):
        return f"<MediaFile(id={self.id}, filename='{self.filename}')>"


class SystemSetting(Base):
    """System configuration settings"""
    
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    value_type = Column(String, default="string")  # string, int, float, bool, json
    category = Column(String, default="general")
    description = Column(Text)
    is_public = Column(Boolean, default=False)  # Can be accessed by non-admin users
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SystemSetting(key='{self.key}', value='{self.value}')>"


class SystemLog(Base):
    """System logs for monitoring and debugging"""
    
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, nullable=False, index=True)
    message = Column(Text, nullable=False)
    module = Column(String)
    function = Column(String)
    
    # Context
    user_id = Column(Integer, ForeignKey("admin_users.id"))
    ip_address = Column(String)
    user_agent = Column(Text)
    request_id = Column(String)
    
    # Additional data
    extra_data = Column(JSON)
    stack_trace = Column(Text)
    
    # Timestamps
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    user = relationship("AdminUser")
    
    def __repr__(self):
        return f"<SystemLog(id={self.id}, level='{self.level}', message='{self.message[:50]}...')>"


class AuditLog(Base):
    """Audit trail for admin actions"""
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    action = Column(String, nullable=False, index=True)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    
    # Details
    old_values = Column(JSON)
    new_values = Column(JSON)
    description = Column(Text)
    
    # Context
    ip_address = Column(String)
    user_agent = Column(Text)
    session_id = Column(String)
    
    # Timestamps
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    admin_user = relationship("AdminUser")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', resource='{self.resource_type}')>"


class Notification(Base):
    """System notifications for admin users"""
    
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, default="info")  # info, warning, error, success
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    
    # Action
    action_url = Column(String)
    action_text = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), index=True)
    expires_at = Column(DateTime)
    
    # Relationships
    admin_user = relationship("AdminUser")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, title='{self.title}', is_read={self.is_read})>"


class DataSource(Base):
    """External data sources for integration monitoring"""
    
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # api, file, database, webhook
    endpoint_url = Column(String)
    api_key = Column(String)  # Encrypted
    
    # Status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    sync_frequency = Column(Integer, default=3600)  # seconds
    sync_status = Column(String, default="pending")  # pending, running, success, error
    
    # Data quality
    data_accuracy = Column(Float, default=0.0)
    data_completeness = Column(Float, default=0.0)
    data_freshness = Column(Float, default=0.0)
    
    # Error handling
    last_error = Column(Text)
    error_count = Column(Integer, default=0)
    consecutive_errors = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<DataSource(id={self.id}, name='{self.name}', status='{self.sync_status}')>"


class BackgroundJob(Base):
    """Background job processing"""
    
    __tablename__ = "background_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String, nullable=False)
    job_type = Column(String, nullable=False)  # data_sync, report_generation, cleanup, etc.
    status = Column(String, default="pending")  # pending, running, completed, failed, cancelled
    
    # Job details
    parameters = Column(JSON)
    result = Column(JSON)
    error_message = Column(Text)
    
    # Progress tracking
    progress = Column(Integer, default=0)  # 0-100
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    
    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    estimated_duration = Column(Integer)  # seconds
    
    # Retry logic
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<BackgroundJob(id={self.id}, name='{self.job_name}', status='{self.status}')>"


class EmailTemplate(Base):
    """Email templates for system notifications"""
    
    __tablename__ = "email_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    subject = Column(String, nullable=False)
    body_html = Column(Text, nullable=False)
    body_text = Column(Text)
    template_type = Column(String, nullable=False)  # notification, marketing, system
    
    # Variables
    variables = Column(JSON)  # Array of available variables
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Usage
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<EmailTemplate(id={self.id}, name='{self.name}', type='{self.template_type}')>"


class SecurityEvent(Base):
    """Security events and threat detection"""
    
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False, index=True)  # login_failed, suspicious_activity, etc.
    severity = Column(String, nullable=False)  # low, medium, high, critical
    
    # Event details
    description = Column(Text, nullable=False)
    ip_address = Column(String, index=True)
    user_agent = Column(Text)
    user_id = Column(Integer, ForeignKey("admin_users.id"))
    
    # Response
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey("admin_users.id"))
    resolution_notes = Column(Text)
    
    # Additional data
    extra_data = Column(JSON)
    
    # Timestamps
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    user = relationship("AdminUser", foreign_keys=[user_id])
    resolver = relationship("AdminUser", foreign_keys=[resolved_by])
    
    def __repr__(self):
        return f"<SecurityEvent(id={self.id}, type='{self.event_type}', severity='{self.severity}')>"


class AdminSession(Base):
    """Active admin user sessions"""
    
    __tablename__ = "admin_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    session_token = Column(String, unique=True, index=True, nullable=False)
    
    # Session details
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    device_info = Column(JSON, nullable=True)  # Browser, OS, device type
    
    # Status
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime, default=func.now())
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), index=True)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationships
    admin_user = relationship("AdminUser", back_populates="sessions")
    
    def __repr__(self):
        return f"<AdminSession(id={self.id}, admin_user_id={self.admin_user_id}, is_active={self.is_active})>"
