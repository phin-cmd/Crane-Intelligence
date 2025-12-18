"""
Comprehensive admin schemas for Crane Intelligence Platform
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


# Enums
class AdminRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    SUPPORT = "support"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContentType(str, Enum):
    ARTICLE = "article"
    BLOG_POST = "blog_post"
    NEWS = "news"
    RESOURCE = "resource"
    WHITEPAPER = "whitepaper"
    CASE_STUDY = "case_study"


class SystemLogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SecuritySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Dashboard Schemas
class DashboardMetrics(BaseModel):
    active_users: int
    total_revenue: float
    system_health: float
    storage_used: float
    reports_generated: int
    api_calls: int
    error_rate: float
    uptime: float


class UserActivityChart(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]


class RevenueChart(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]


class GeographicData(BaseModel):
    country: str
    users: int
    revenue: float


class SystemPerformance(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: float


class DashboardData(BaseModel):
    metrics: DashboardMetrics
    user_activity: UserActivityChart
    revenue_trends: RevenueChart
    geographic_distribution: List[GeographicData]
    system_performance: SystemPerformance
    recent_activity: List[Dict[str, Any]]


# Admin User Management Schemas
class AdminUserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    admin_role: AdminRole = AdminRole.ADMIN
    permissions: Optional[List[str]] = []


class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    admin_role: Optional[AdminRole] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class AdminUserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    admin_role: str
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    permissions: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminUserListResponse(BaseModel):
    users: List[AdminUserResponse]
    total: int
    skip: int
    limit: int


# Content Management Schemas
class ContentItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: Optional[str] = None
    content_type: ContentType = ContentType.ARTICLE
    content: str = Field(..., min_length=1)
    excerpt: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    featured_image: Optional[str] = None
    media_files: Optional[List[str]] = []
    scheduled_at: Optional[datetime] = None

    @validator('slug', always=True)
    def generate_slug(cls, v, values):
        if not v and 'title' in values:
            return values['title'].lower().replace(' ', '-').replace('_', '-')
        return v


class ContentItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = None
    content_type: Optional[ContentType] = None
    content: Optional[str] = Field(None, min_length=1)
    excerpt: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    status: Optional[ContentStatus] = None
    featured_image: Optional[str] = None
    media_files: Optional[List[str]] = None
    scheduled_at: Optional[datetime] = None


class ContentItemResponse(BaseModel):
    id: int
    title: str
    slug: str
    content_type: str
    content: str
    excerpt: Optional[str]
    meta_title: Optional[str]
    meta_description: Optional[str]
    meta_keywords: Optional[str]
    status: str
    author_id: int
    reviewer_id: Optional[int]
    published_at: Optional[datetime]
    scheduled_at: Optional[datetime]
    featured_image: Optional[str]
    media_files: List[str]
    view_count: int
    like_count: int
    share_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContentListResponse(BaseModel):
    items: List[ContentItemResponse]
    total: int
    skip: int
    limit: int


# Media Management Schemas
class MediaFileUpload(BaseModel):
    filename: str
    folder_path: str = "/"
    alt_text: Optional[str] = None
    caption: Optional[str] = None
    tags: Optional[List[str]] = []


class MediaFileResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    width: Optional[int]
    height: Optional[int]
    alt_text: Optional[str]
    caption: Optional[str]
    folder_path: str
    tags: List[str]
    usage_count: int
    last_used: Optional[datetime]
    uploaded_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class MediaListResponse(BaseModel):
    files: List[MediaFileResponse]
    total: int
    skip: int
    limit: int


# Analytics Schemas
class AnalyticsOverview(BaseModel):
    total_users: int
    active_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    total_revenue: float
    monthly_revenue: float
    daily_revenue: float
    reports_generated: int
    reports_today: int
    reports_this_month: int
    api_calls: int
    api_calls_today: int
    storage_used: float
    storage_total: float
    system_uptime: float
    error_rate: float


class UserAnalytics(BaseModel):
    registration_trends: List[Dict[str, Any]]
    geographic_distribution: List[GeographicData]
    user_engagement: List[Dict[str, Any]]
    subscription_distribution: Dict[str, int]
    churn_rate: float
    retention_rate: float


class FinancialAnalytics(BaseModel):
    revenue_trends: List[Dict[str, Any]]
    subscription_analytics: Dict[str, Any]
    payment_analytics: Dict[str, Any]
    forecasting: Dict[str, Any]


class TechnicalAnalytics(BaseModel):
    performance_metrics: Dict[str, Any]
    error_tracking: Dict[str, Any]
    resource_usage: Dict[str, Any]
    api_analytics: Dict[str, Any]


class AnalyticsData(BaseModel):
    overview: AnalyticsOverview
    users: UserAnalytics
    financial: FinancialAnalytics
    technical: TechnicalAnalytics


# System Settings Schemas
class SystemSettingCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=100)
    value: str
    value_type: str = "string"
    category: str = "general"
    description: Optional[str] = None
    is_public: bool = False


class SystemSettingUpdate(BaseModel):
    value: Optional[str] = None
    value_type: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class SystemSettingResponse(BaseModel):
    id: int
    key: str
    value: str
    value_type: str
    category: str
    description: Optional[str]
    is_public: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SystemSettingsResponse(BaseModel):
    general: List[SystemSettingResponse]
    api: List[SystemSettingResponse]
    email: List[SystemSettingResponse]
    billing: List[SystemSettingResponse]
    security: List[SystemSettingResponse]
    advanced: List[SystemSettingResponse]


# Logging Schemas
class SystemLogResponse(BaseModel):
    id: int
    level: str
    message: str
    module: Optional[str]
    function: Optional[str]
    user_id: Optional[int]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_id: Optional[str]
    extra_data: Optional[Dict[str, Any]]
    stack_trace: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class LogListResponse(BaseModel):
    logs: List[SystemLogResponse]
    total: int
    skip: int
    limit: int


class AuditLogResponse(BaseModel):
    id: int
    admin_user_id: int
    action: str
    resource_type: str
    resource_id: str
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    description: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    session_id: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    logs: List[AuditLogResponse]
    total: int
    skip: int
    limit: int


# Notification Schemas
class NotificationCreate(BaseModel):
    admin_user_id: int
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    notification_type: NotificationType = NotificationType.INFO
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    expires_at: Optional[datetime] = None


class NotificationResponse(BaseModel):
    id: int
    admin_user_id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    read_at: Optional[datetime]
    action_url: Optional[str]
    action_text: Optional[str]
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]
    total: int
    unread_count: int


# Data Management Schemas
class DataSourceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    source_type: str = Field(..., pattern="^(api|file|database|webhook)$")
    endpoint_url: Optional[str] = None
    api_key: Optional[str] = None
    sync_frequency: int = 3600


class DataSourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    endpoint_url: Optional[str] = None
    api_key: Optional[str] = None
    is_active: Optional[bool] = None
    sync_frequency: Optional[int] = None


class DataSourceResponse(BaseModel):
    id: int
    name: str
    source_type: str
    endpoint_url: Optional[str]
    is_active: bool
    last_sync: Optional[datetime]
    sync_frequency: int
    sync_status: str
    data_accuracy: float
    data_completeness: float
    data_freshness: float
    last_error: Optional[str]
    error_count: int
    consecutive_errors: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DataSourceListResponse(BaseModel):
    sources: List[DataSourceResponse]
    total: int


class DataQualityMetrics(BaseModel):
    overall_score: float
    accuracy: float
    completeness: float
    freshness: float
    consistency: float
    sources: List[Dict[str, Any]]


# Background Job Schemas
class BackgroundJobResponse(BaseModel):
    id: int
    job_name: str
    job_type: str
    status: str
    parameters: Optional[Dict[str, Any]]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    progress: int
    total_items: int
    processed_items: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_duration: Optional[int]
    retry_count: int
    max_retries: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    jobs: List[BackgroundJobResponse]
    total: int
    skip: int
    limit: int


# Security Schemas
class SecurityEventResponse(BaseModel):
    id: int
    event_type: str
    severity: str
    description: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    user_id: Optional[int]
    is_resolved: bool
    resolved_at: Optional[datetime]
    resolved_by: Optional[int]
    resolution_notes: Optional[str]
    extra_data: Optional[Dict[str, Any]]
    timestamp: datetime

    class Config:
        from_attributes = True


class SecurityEventListResponse(BaseModel):
    events: List[SecurityEventResponse]
    total: int
    skip: int
    limit: int


class SecurityDashboard(BaseModel):
    security_score: float
    threat_level: str
    recent_events: List[SecurityEventResponse]
    failed_logins: int
    blocked_ips: int
    active_sessions: int
    security_recommendations: List[str]


# Email Template Schemas
class EmailTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    subject: str = Field(..., min_length=1, max_length=200)
    body_html: str = Field(..., min_length=1)
    body_text: Optional[str] = None
    template_type: str = Field(..., pattern="^(notification|marketing|system)$")
    variables: Optional[List[str]] = []


class EmailTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    subject: Optional[str] = Field(None, min_length=1, max_length=200)
    body_html: Optional[str] = Field(None, min_length=1)
    body_text: Optional[str] = None
    template_type: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class EmailTemplateResponse(BaseModel):
    id: int
    name: str
    subject: str
    body_html: str
    body_text: Optional[str]
    template_type: str
    variables: List[str]
    is_active: bool
    usage_count: int
    last_used: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmailTemplateListResponse(BaseModel):
    templates: List[EmailTemplateResponse]
    total: int


# Export/Import Schemas
class DataExportRequest(BaseModel):
    data_type: str = Field(..., pattern="^(users|content|logs|analytics)$")
    format: str = Field(..., pattern="^(csv|json|excel)$")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    filters: Optional[Dict[str, Any]] = None


class DataExportResponse(BaseModel):
    export_id: str
    status: str
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    created_at: datetime
    expires_at: datetime


class DataImportRequest(BaseModel):
    data_type: str = Field(..., pattern="^(users|content|settings)$")
    file_path: str
    overwrite_existing: bool = False
    validate_data: bool = True


class DataImportResponse(BaseModel):
    import_id: str
    status: str
    processed_records: int
    successful_records: int
    failed_records: int
    errors: List[str]
    created_at: datetime


# Bulk Operations Schemas
class BulkUserOperation(BaseModel):
    user_ids: List[int]
    operation: str = Field(..., pattern="^(activate|deactivate|delete|change_role|reset_password)$")
    parameters: Optional[Dict[str, Any]] = None


class BulkContentOperation(BaseModel):
    content_ids: List[int]
    operation: str = Field(..., pattern="^(publish|unpublish|archive|delete|change_status)$")
    parameters: Optional[Dict[str, Any]] = None


class BulkOperationResponse(BaseModel):
    operation_id: str
    status: str
    total_items: int
    processed_items: int
    successful_items: int
    failed_items: int
    errors: List[str]
    created_at: datetime
    completed_at: Optional[datetime] = None
