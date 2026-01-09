"""
Admin schemas for Crane Intelligence Platform
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    BASIC = "basic"
    PRO = "pro"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class ActivityType(str, Enum):
    USER = "user"
    REPORT = "report"
    SYSTEM = "system"
    NOTIFICATION = "notification"

class SystemStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

# Dashboard Schemas
class UserStats(BaseModel):
    total: int
    active: int
    new_today: int
    by_role: Dict[str, int]  # Changed from by_tier to by_role

class ReportStats(BaseModel):
    total: int
    today: int
    this_month: int

class SystemStatusInfo(BaseModel):
    uptime: float
    api_response_time: int
    status: SystemStatus
    components: Optional[Dict[str, str]] = None

class DashboardStats(BaseModel):
    users: UserStats
    reports: ReportStats
    revenue: Dict[str, float]
    system: SystemStatusInfo

# Activity Schemas
class ActivityItem(BaseModel):
    id: str
    type: ActivityType
    title: str
    description: str
    timestamp: datetime
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# User Management Schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: UserRole = UserRole.BASIC
    is_active: bool = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    is_active: bool
    is_verified: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Add phone and address fields
    phone: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    street_address: Optional[str] = None
    full_address: Optional[str] = None
    company_name: Optional[str] = None
    full_name: Optional[str] = None
    username: Optional[str] = None
    user_role: Optional[str] = None
    timezone: Optional[str] = None
    total_payments: Optional[float] = None

    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    skip: int
    limit: int

# Report Schemas
class ReportResponse(BaseModel):
    id: str
    type: str
    user_email: str
    created_at: datetime
    status: str
    file_path: str

class ReportListResponse(BaseModel):
    reports: List[ReportResponse]
    total: int
    skip: int
    limit: int

# Subscription Schemas
class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    tier: str
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    auto_renew: bool = True

class SubscriptionUpdate(BaseModel):
    tier: Optional[str] = None
    status: Optional[str] = None
    auto_renew: Optional[bool] = None

# Crane Listing Schemas
class CraneListingResponse(BaseModel):
    id: str
    title: str
    manufacturer: str
    year: int
    price: float
    location: str
    capacity_tons: float
    crane_type: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class CraneListingCreate(BaseModel):
    title: str
    manufacturer: str
    year: int
    price: float
    location: str
    capacity_tons: float
    crane_type: str

class CraneListingUpdate(BaseModel):
    title: Optional[str] = None
    manufacturer: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    location: Optional[str] = None
    capacity_tons: Optional[float] = None
    crane_type: Optional[str] = None
    status: Optional[str] = None

# Analytics Schemas
class UsageStats(BaseModel):
    total_users: int
    active_users: int
    reports_generated: int
    api_calls: int
    storage_used: float
    period: str

class RevenueStats(BaseModel):
    total_revenue: float
    monthly_revenue: float
    daily_revenue: float
    by_report_type: Dict[str, float]  # Changed from by_tier to by_report_type
    period: str

class PerformanceStats(BaseModel):
    avg_response_time: float
    uptime_percentage: float
    error_rate: float
    throughput: float
    period: str

# System Management Schemas
class SystemSettings(BaseModel):
    site_name: str
    site_description: str
    max_users: int
    max_reports_per_user: int
    email_notifications: bool
    maintenance_mode: bool
    api_rate_limit: int

class LogEntry(BaseModel):
    id: str
    level: str
    message: str
    timestamp: datetime
    user_id: Optional[str] = None
    ip_address: Optional[str] = None

class LogResponse(BaseModel):
    logs: List[LogEntry]
    total: int

# Backup Schemas
class BackupResponse(BaseModel):
    id: str
    name: str
    size: float
    created_at: datetime
    status: str
    type: str

class BackupCreate(BaseModel):
    name: str
    type: str = "full"
    include_files: bool = True

# Support Schemas
class SupportTicketResponse(BaseModel):
    id: str
    user_id: str
    subject: str
    description: str
    status: str
    priority: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    assigned_to: Optional[str] = None

class SupportTicketCreate(BaseModel):
    subject: str
    description: str
    priority: str = "medium"

class SupportTicketUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None

# Notification Schemas
class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime

class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    type: str = "info"

# File Management Schemas
class FileUploadResponse(BaseModel):
    id: str
    filename: str
    size: int
    type: str
    url: str
    created_at: datetime

class FileResponse(BaseModel):
    id: str
    filename: str
    size: int
    type: str
    url: str
    created_at: datetime
    user_id: str

# Email Schemas
class EmailTemplateResponse(BaseModel):
    id: str
    name: str
    subject: str
    body: str
    type: str
    is_active: bool
    created_at: datetime

class EmailTemplateCreate(BaseModel):
    name: str
    subject: str
    body: str
    type: str
    is_active: bool = True

class EmailSendRequest(BaseModel):
    to: List[EmailStr]
    subject: str
    body: str
    template_id: Optional[str] = None

# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: str
    user_id: str
    action: str
    resource: str
    resource_id: str
    details: Dict[str, Any]
    ip_address: str
    timestamp: datetime

# Data Management Schemas
class DataRefreshStatus(BaseModel):
    status: str
    progress: int
    message: str
    started_at: datetime
    completed_at: Optional[datetime] = None

class DataExportRequest(BaseModel):
    type: str
    format: str = "csv"
    filters: Optional[Dict[str, Any]] = None
    date_range: Optional[Dict[str, datetime]] = None

class DataImportRequest(BaseModel):
    type: str
    data: List[Dict[str, Any]]
    overwrite: bool = False
