"""
Comprehensive Admin API endpoints for Crane Intelligence Platform
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import json

from ...core.database import get_db
from ...models.admin import (
    AdminUser, ContentItem, MediaFile, SystemSetting, SystemLog, AuditLog,
    Notification, DataSource, BackgroundJob, EmailTemplate, SecurityEvent
)
from ...models.user import User, UsageLog
from ...schemas.admin_comprehensive import *
from ...services.admin_service import admin_service
from ...core.auth import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["admin-comprehensive"])
logger = logging.getLogger(__name__)


# Dashboard Endpoints
@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get real-time dashboard metrics"""
    try:
        metrics = await admin_service.get_dashboard_metrics(db)
        return metrics
    except Exception as e:
        logger.error(f"Error fetching dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard metrics")


@router.get("/dashboard/data", response_model=DashboardData)
async def get_dashboard_data(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get complete dashboard data"""
    try:
        data = await admin_service.get_dashboard_data(db)
        return data
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")


# Admin User Management
@router.get("/users", response_model=AdminUserListResponse)
async def get_admin_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get admin users with filtering and pagination"""
    try:
        users = await admin_service.get_admin_users(
            db, skip=skip, limit=limit, search=search, 
            role=role, is_active=is_active
        )
        return users
    except Exception as e:
        logger.error(f"Error fetching admin users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch admin users")


@router.post("/users", response_model=AdminUserResponse)
async def create_admin_user(
    user_data: AdminUserCreate,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create new admin user"""
    try:
        # Check permissions
        if current_user.admin_role not in ["super_admin", "admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        user = await admin_service.create_admin_user(db, user_data)
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create admin user")


@router.put("/users/{user_id}", response_model=AdminUserResponse)
async def update_admin_user(
    user_id: int,
    user_data: AdminUserUpdate,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update admin user"""
    try:
        # Check permissions
        if current_user.admin_role not in ["super_admin", "admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        user = await admin_service.update_admin_user(db, user_id, user_data)
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating admin user: {e}")
        raise HTTPException(status_code=500, detail="Failed to update admin user")


@router.delete("/users/{user_id}")
async def delete_admin_user(
    user_id: int,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete admin user"""
    try:
        # Check permissions
        if current_user.admin_role != "super_admin":
            raise HTTPException(status_code=403, detail="Super admin access required")
        
        # Prevent self-deletion
        if user_id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
        await admin_service.delete_admin_user(db, user_id)
        return {"message": "Admin user deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting admin user: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete admin user")


# Content Management
@router.get("/content", response_model=ContentListResponse)
async def get_content_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    content_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get content items with filtering"""
    try:
        items = await admin_service.get_content_items(
            db, skip=skip, limit=limit, content_type=content_type,
            status=status, search=search
        )
        return items
    except Exception as e:
        logger.error(f"Error fetching content items: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch content items")


@router.post("/content", response_model=ContentItemResponse)
async def create_content_item(
    content_data: ContentItemCreate,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create new content item"""
    try:
        item = await admin_service.create_content_item(db, content_data, current_user.id)
        return item
    except Exception as e:
        logger.error(f"Error creating content item: {e}")
        raise HTTPException(status_code=500, detail="Failed to create content item")


@router.put("/content/{item_id}", response_model=ContentItemResponse)
async def update_content_item(
    item_id: int,
    content_data: ContentItemUpdate,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update content item"""
    try:
        item = await admin_service.update_content_item(db, item_id, content_data)
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating content item: {e}")
        raise HTTPException(status_code=500, detail="Failed to update content item")


@router.delete("/content/{item_id}")
async def delete_content_item(
    item_id: int,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete content item"""
    try:
        await admin_service.delete_content_item(db, item_id)
        return {"message": "Content item deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting content item: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete content item")


# Media Management
@router.post("/media/upload", response_model=MediaFileResponse)
async def upload_media_file(
    file: UploadFile = File(...),
    folder_path: str = "/",
    alt_text: Optional[str] = None,
    caption: Optional[str] = None,
    tags: Optional[str] = None,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Upload media file"""
    try:
        tags_list = json.loads(tags) if tags else []
        media_file = await admin_service.upload_media_file(
            db, file, folder_path, alt_text, caption, tags_list, current_user.id
        )
        return media_file
    except Exception as e:
        logger.error(f"Error uploading media file: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload media file")


@router.get("/media", response_model=MediaListResponse)
async def get_media_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    folder_path: Optional[str] = None,
    mime_type: Optional[str] = None,
    search: Optional[str] = None,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get media files with filtering"""
    try:
        files = await admin_service.get_media_files(
            db, skip=skip, limit=limit, folder_path=folder_path,
            mime_type=mime_type, search=search
        )
        return files
    except Exception as e:
        logger.error(f"Error fetching media files: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch media files")


@router.delete("/media/{file_id}")
async def delete_media_file(
    file_id: int,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete media file"""
    try:
        await admin_service.delete_media_file(db, file_id)
        return {"message": "Media file deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting media file: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete media file")


# Analytics
@router.get("/analytics/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get analytics overview"""
    try:
        overview = await admin_service.get_analytics_overview(db)
        return overview
    except Exception as e:
        logger.error(f"Error fetching analytics overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics overview")


@router.get("/analytics/users", response_model=UserAnalytics)
async def get_user_analytics(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get user analytics"""
    try:
        analytics = await admin_service.get_user_analytics(db, period)
        return analytics
    except Exception as e:
        logger.error(f"Error fetching user analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user analytics")


@router.get("/analytics/financial", response_model=FinancialAnalytics)
async def get_financial_analytics(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get financial analytics"""
    try:
        analytics = await admin_service.get_financial_analytics(db, period)
        return analytics
    except Exception as e:
        logger.error(f"Error fetching financial analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch financial analytics")


@router.get("/analytics/technical", response_model=TechnicalAnalytics)
async def get_technical_analytics(
    period: str = Query("24h", regex="^(1h|24h|7d|30d)$"),
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get technical analytics"""
    try:
        analytics = await admin_service.get_technical_analytics(db, period)
        return analytics
    except Exception as e:
        logger.error(f"Error fetching technical analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch technical analytics")


# System Settings
@router.get("/settings", response_model=SystemSettingsResponse)
async def get_system_settings(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get system settings by category"""
    try:
        settings = await admin_service.get_system_settings(db)
        return settings
    except Exception as e:
        logger.error(f"Error fetching system settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch system settings")


@router.put("/settings/{setting_id}", response_model=SystemSettingResponse)
async def update_system_setting(
    setting_id: int,
    setting_data: SystemSettingUpdate,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update system setting"""
    try:
        # Check permissions
        if current_user.admin_role not in ["super_admin", "admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        setting = await admin_service.update_system_setting(db, setting_id, setting_data)
        return setting
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating system setting: {e}")
        raise HTTPException(status_code=500, detail="Failed to update system setting")


# Logging
@router.get("/logs/system", response_model=LogListResponse)
async def get_system_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    level: Optional[str] = None,
    module: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get system logs with filtering"""
    try:
        logs = await admin_service.get_system_logs(
            db, skip=skip, limit=limit, level=level, module=module,
            start_date=start_date, end_date=end_date
        )
        return logs
    except Exception as e:
        logger.error(f"Error fetching system logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch system logs")


@router.get("/logs/audit", response_model=AuditLogListResponse)
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get audit logs with filtering"""
    try:
        logs = await admin_service.get_audit_logs(
            db, skip=skip, limit=limit, action=action, resource_type=resource_type,
            user_id=user_id, start_date=start_date, end_date=end_date
        )
        return logs
    except Exception as e:
        logger.error(f"Error fetching audit logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch audit logs")


# Notifications
@router.get("/notifications", response_model=NotificationListResponse)
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_read: Optional[bool] = None,
    notification_type: Optional[str] = None,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get notifications for current admin user"""
    try:
        notifications = await admin_service.get_notifications(
            db, current_user.id, skip=skip, limit=limit,
            is_read=is_read, notification_type=notification_type
        )
        return notifications
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch notifications")


@router.post("/notifications", response_model=NotificationResponse)
async def create_notification(
    notification_data: NotificationCreate,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create notification"""
    try:
        notification = await admin_service.create_notification(db, notification_data)
        return notification
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to create notification")


@router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    try:
        await admin_service.mark_notification_read(db, notification_id, current_user.id)
        return {"message": "Notification marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark notification as read")


# Data Management
@router.get("/data/sources", response_model=DataSourceListResponse)
async def get_data_sources(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get data sources"""
    try:
        sources = await admin_service.get_data_sources(db)
        return sources
    except Exception as e:
        logger.error(f"Error fetching data sources: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch data sources")


@router.post("/data/sources", response_model=DataSourceResponse)
async def create_data_source(
    source_data: DataSourceCreate,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create data source"""
    try:
        source = await admin_service.create_data_source(db, source_data)
        return source
    except Exception as e:
        logger.error(f"Error creating data source: {e}")
        raise HTTPException(status_code=500, detail="Failed to create data source")


@router.get("/data/quality", response_model=DataQualityMetrics)
async def get_data_quality_metrics(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get data quality metrics"""
    try:
        metrics = await admin_service.get_data_quality_metrics(db)
        return metrics
    except Exception as e:
        logger.error(f"Error fetching data quality metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch data quality metrics")


# Background Jobs
@router.get("/jobs", response_model=JobListResponse)
async def get_background_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    job_type: Optional[str] = None,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get background jobs"""
    try:
        jobs = await admin_service.get_background_jobs(
            db, skip=skip, limit=limit, status=status, job_type=job_type
        )
        return jobs
    except Exception as e:
        logger.error(f"Error fetching background jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch background jobs")


@router.post("/jobs/{job_id}/cancel")
async def cancel_background_job(
    job_id: int,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Cancel background job"""
    try:
        await admin_service.cancel_background_job(db, job_id)
        return {"message": "Job cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling background job: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel background job")


# Security
@router.get("/security/dashboard", response_model=SecurityDashboard)
async def get_security_dashboard(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get security dashboard"""
    try:
        dashboard = await admin_service.get_security_dashboard(db)
        return dashboard
    except Exception as e:
        logger.error(f"Error fetching security dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch security dashboard")


@router.get("/security/events", response_model=SecurityEventListResponse)
async def get_security_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get security events"""
    try:
        events = await admin_service.get_security_events(
            db, skip=skip, limit=limit, event_type=event_type,
            severity=severity, is_resolved=is_resolved
        )
        return events
    except Exception as e:
        logger.error(f"Error fetching security events: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch security events")


# Email Templates
@router.get("/email/templates", response_model=EmailTemplateListResponse)
async def get_email_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    template_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get email templates"""
    try:
        templates = await admin_service.get_email_templates(
            db, skip=skip, limit=limit, template_type=template_type, is_active=is_active
        )
        return templates
    except Exception as e:
        logger.error(f"Error fetching email templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch email templates")


@router.post("/email/templates", response_model=EmailTemplateResponse)
async def create_email_template(
    template_data: EmailTemplateCreate,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create email template"""
    try:
        template = await admin_service.create_email_template(db, template_data)
        return template
    except Exception as e:
        logger.error(f"Error creating email template: {e}")
        raise HTTPException(status_code=500, detail="Failed to create email template")


# Bulk Operations
@router.post("/bulk/users", response_model=BulkOperationResponse)
async def bulk_user_operation(
    operation_data: BulkUserOperation,
    background_tasks: BackgroundTasks,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Perform bulk user operations"""
    try:
        # Check permissions
        if current_user.admin_role not in ["super_admin", "admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        result = await admin_service.bulk_user_operation(db, operation_data, background_tasks)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing bulk user operation: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform bulk user operation")


@router.post("/bulk/content", response_model=BulkOperationResponse)
async def bulk_content_operation(
    operation_data: BulkContentOperation,
    background_tasks: BackgroundTasks,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Perform bulk content operations"""
    try:
        result = await admin_service.bulk_content_operation(db, operation_data, background_tasks)
        return result
    except Exception as e:
        logger.error(f"Error performing bulk content operation: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform bulk content operation")


# Data Export/Import
@router.post("/data/export", response_model=DataExportResponse)
async def export_data(
    export_request: DataExportRequest,
    background_tasks: BackgroundTasks,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Export data"""
    try:
        result = await admin_service.export_data(db, export_request, background_tasks)
        return result
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        raise HTTPException(status_code=500, detail="Failed to export data")


@router.post("/data/import", response_model=DataImportResponse)
async def import_data(
    import_request: DataImportRequest,
    background_tasks: BackgroundTasks,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Import data"""
    try:
        # Check permissions
        if current_user.admin_role not in ["super_admin", "admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        result = await admin_service.import_data(db, import_request, background_tasks)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing data: {e}")
        raise HTTPException(status_code=500, detail="Failed to import data")
