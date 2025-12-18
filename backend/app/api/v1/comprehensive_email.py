#!/usr/bin/env python3
"""
Comprehensive Email API for Crane Intelligence Platform
All email triggers for main website and admin portal
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...services.email_service_unified import comprehensive_email_service
from ...core.config import settings

router = APIRouter(prefix="/email", tags=["Comprehensive Email"])

# ==================== REQUEST MODELS ====================

class UserRegistrationRequest(BaseModel):
    user_email: EmailStr
    username: str
    account_type: str = "Standard"

class PasswordResetRequest(BaseModel):
    user_email: EmailStr
    username: str
    reset_token: str

class ValuationReportRequest(BaseModel):
    user_email: EmailStr
    username: str
    report_data: Dict[str, Any]

class EquipmentInspectionRequest(BaseModel):
    user_email: EmailStr
    username: str
    inspection_data: Dict[str, Any]

class AdminUserRegistrationRequest(BaseModel):
    admin_emails: List[EmailStr]
    user_data: Dict[str, Any]

class AdminSystemAlertRequest(BaseModel):
    admin_emails: List[EmailStr]
    alert_data: Dict[str, Any]

class AdminAnalyticsReportRequest(BaseModel):
    admin_emails: List[EmailStr]
    analytics_data: Dict[str, Any]

class GeneralNotificationRequest(BaseModel):
    user_email: EmailStr
    username: str
    notification_data: Dict[str, Any]

class SystemMaintenanceRequest(BaseModel):
    user_emails: List[EmailStr]
    maintenance_data: Dict[str, Any]

class BulkNotificationRequest(BaseModel):
    user_emails: List[EmailStr]
    notification_data: Dict[str, Any]

# ==================== MAIN WEBSITE EMAIL ENDPOINTS ====================

@router.post("/send-user-registration", summary="Send user registration welcome email")
async def send_user_registration_email(request: UserRegistrationRequest):
    """Send welcome email to new user"""
    result = await comprehensive_email_service.send_user_registration_email(
        request.user_email, 
        request.username, 
        request.account_type
    )
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
    return {"message": "User registration email sent successfully", "details": result["message"]}

@router.post("/send-password-reset", summary="Send password reset email")
async def send_password_reset_email(request: PasswordResetRequest):
    """Send password reset email to user"""
    result = await comprehensive_email_service.send_password_reset_email(
        request.user_email, 
        request.username, 
        request.reset_token
    )
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
    return {"message": "Password reset email sent successfully", "details": result["message"]}

@router.post("/send-valuation-report", summary="Send valuation report email")
async def send_valuation_report_email(request: ValuationReportRequest):
    """Send valuation report email to user"""
    result = await comprehensive_email_service.send_valuation_report_email(
        request.user_email, 
        request.username, 
        request.report_data
    )
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
    return {"message": "Valuation report email sent successfully", "details": result["message"]}

@router.post("/send-equipment-inspection", summary="Send equipment inspection email")
async def send_equipment_inspection_email(request: EquipmentInspectionRequest):
    """Send equipment inspection scheduled email"""
    result = await comprehensive_email_service.send_equipment_inspection_email(
        request.user_email, 
        request.username, 
        request.inspection_data
    )
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
    return {"message": "Equipment inspection email sent successfully", "details": result["message"]}

# ==================== ADMIN PORTAL EMAIL ENDPOINTS ====================

@router.post("/send-admin-user-registration", summary="Send admin alert for new user registration")
async def send_admin_user_registration_alert(request: AdminUserRegistrationRequest):
    """Send admin alert for new user registration"""
    result = await comprehensive_email_service.send_admin_user_registration_alert(
        request.admin_emails, 
        request.user_data
    )
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
    return {"message": "Admin user registration alert sent successfully", "details": result["message"]}

@router.post("/send-admin-system-alert", summary="Send system alert to admins")
async def send_admin_system_alert(request: AdminSystemAlertRequest):
    """Send system alert to admin users"""
    result = await comprehensive_email_service.send_admin_system_alert(
        request.admin_emails, 
        request.alert_data
    )
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
    return {"message": "Admin system alert sent successfully", "details": result["message"]}

@router.post("/send-admin-analytics-report", summary="Send analytics report to admins")
async def send_admin_analytics_report(request: AdminAnalyticsReportRequest):
    """Send weekly analytics report to admin users"""
    result = await comprehensive_email_service.send_admin_analytics_report(
        request.admin_emails, 
        request.analytics_data
    )
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
    return {"message": "Admin analytics report sent successfully", "details": result["message"]}

# ==================== NOTIFICATION EMAIL ENDPOINTS ====================

@router.post("/send-general-notification", summary="Send general notification email")
async def send_general_notification(request: GeneralNotificationRequest):
    """Send general notification email to user"""
    result = await comprehensive_email_service.send_general_notification(
        request.user_email, 
        request.username, 
        request.notification_data
    )
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
    return {"message": "General notification email sent successfully", "details": result["message"]}

@router.post("/send-system-maintenance", summary="Send system maintenance notification")
async def send_system_maintenance_notification(request: SystemMaintenanceRequest):
    """Send system maintenance notification to users"""
    result = await comprehensive_email_service.send_system_maintenance_notification(
        request.user_emails, 
        request.maintenance_data
    )
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
    return {"message": "System maintenance notification sent successfully", "details": result["message"]}

# ==================== BULK EMAIL ENDPOINTS ====================

@router.post("/send-bulk-notifications", summary="Send bulk notifications to multiple users")
async def send_bulk_notifications(request: BulkNotificationRequest):
    """Send bulk notifications to multiple users"""
    result = await comprehensive_email_service.send_bulk_notifications(
        request.user_emails, 
        request.notification_data
    )
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
    return {"message": "Bulk notifications sent successfully", "details": result["message"]}

@router.post("/send-admin-bulk-alert", summary="Send bulk alert to all admins")
async def send_admin_bulk_alert(request: AdminSystemAlertRequest):
    """Send bulk alert to all admin users"""
    result = await comprehensive_email_service.send_admin_bulk_alert(
        request.admin_emails, 
        request.alert_data
    )
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
    return {"message": "Admin bulk alert sent successfully", "details": result["message"]}

# ==================== EMAIL TESTING ENDPOINTS ====================

@router.get("/test-email-connection", summary="Test email server connection")
async def test_email_connection():
    """Test the email server connection"""
    try:
        # Test SMTP connection
        import smtplib
        import ssl
        
        context = ssl.create_default_context()
        with smtplib.SMTP(settings.mail_server, settings.mail_port) as server:
            server.starttls(context=context)
            server.login(settings.mail_username, settings.mail_password)
            
        return {
            "success": True,
            "message": "Email connection test successful!",
            "details": {
                "smtp_server": settings.mail_server,
                "port": settings.mail_port,
                "username": settings.mail_username,
                "tls_enabled": settings.mail_use_tls,
                "ssl_enabled": settings.mail_use_ssl
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Email connection test failed: {e}",
            "details": None
        }

@router.post("/test-all-email-templates", summary="Test all email templates")
async def test_all_email_templates():
    """Test all email templates with sample data"""
    test_results = []
    
    # Test user registration email
    try:
        result = await comprehensive_email_service.send_user_registration_email(
            "test@example.com", "Test User", "Standard"
        )
        test_results.append({"template": "user_registration", "result": result})
    except Exception as e:
        test_results.append({"template": "user_registration", "result": {"success": False, "message": str(e)}})
    
    # Test password reset email
    try:
        result = await comprehensive_email_service.send_password_reset_email(
            "test@example.com", "Test User", "test_token_123"
        )
        test_results.append({"template": "password_reset", "result": result})
    except Exception as e:
        test_results.append({"template": "password_reset", "result": {"success": False, "message": str(e)}})
    
    # Test valuation report email
    try:
        result = await comprehensive_email_service.send_valuation_report_email(
            "test@example.com", "Test User", {
                "report_id": "RPT-001",
                "equipment_name": "Test Crane",
                "estimated_value": "$150,000",
                "confidence_level": 85
            }
        )
        test_results.append({"template": "valuation_report", "result": result})
    except Exception as e:
        test_results.append({"template": "valuation_report", "result": {"success": False, "message": str(e)}})
    
    return {
        "message": "Email template testing completed",
        "results": test_results
    }

# ==================== EMAIL STATISTICS ENDPOINTS ====================

@router.get("/email-statistics", summary="Get email statistics")
async def get_email_statistics():
    """Get email sending statistics"""
    return {
        "total_templates": len(comprehensive_email_service.templates),
        "available_templates": list(comprehensive_email_service.templates.keys()),
        "email_config": {
            "smtp_server": settings.mail_server,
            "port": settings.mail_port,
            "username": settings.mail_username,
            "tls_enabled": settings.mail_use_tls,
            "ssl_enabled": settings.mail_use_ssl
        },
        "supported_features": [
            "User registration emails",
            "Password reset emails", 
            "Valuation report emails",
            "Equipment inspection emails",
            "Admin alerts",
            "System notifications",
            "Bulk email sending",
            "Template customization"
        ]
    }
    
    # --- Additional Admin Portal Email Endpoints ---
    @router.post("/send-admin-user-management-alert", summary="Send admin user management alert")
    async def send_admin_user_management_alert(
        admin_emails: List[EmailStr],
        action_type: str,
        admin_name: str,
        action_timestamp: str,
        admin_ip: str,
        admin_user_agent: str,
        user_id: str,
        username: str,
        user_email: EmailStr,
        previous_status: str,
        new_status: str,
        user_role: str,
        last_login: str,
        action_description: str,
        action_reason: str,
        action_impact: str,
        total_users: int,
        active_users: int,
        suspended_users: int,
        admin_actions_today: int,
        admin_users_url: str = "http://localhost:3000/admin/users.html"
    ):
        result = await comprehensive_email_service.send_admin_user_management_alert(
            admin_emails=admin_emails,
            action_type=action_type,
            admin_name=admin_name,
            action_timestamp=action_timestamp,
            admin_ip=admin_ip,
            admin_user_agent=admin_user_agent,
            user_id=user_id,
            username=username,
            user_email=user_email,
            previous_status=previous_status,
            new_status=new_status,
            user_role=user_role,
            last_login=last_login,
            action_description=action_description,
            action_reason=action_reason,
            action_impact=action_impact,
            total_users=total_users,
            active_users=active_users,
            suspended_users=suspended_users,
            admin_actions_today=admin_actions_today,
            admin_users_url=admin_users_url
        )
        if not result["success"]:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
        return {"message": "Admin user management alert sent successfully", "details": result["message"]}
    
    @router.post("/send-admin-security-alert", summary="Send admin security alert")
    async def send_admin_security_alert(
        admin_emails: List[EmailStr],
        alert_type: str,
        alert_level: str,
        alert_timestamp: str,
        alert_source: str,
        alert_id: str,
        severity: str,
        category: str,
        alert_description: str,
        affected_systems: str,
        source_ip: str,
        user_agent: str,
        geo_location: str,
        attempt_count: int,
        time_window: str,
        impact_description: str,
        affected_users: str,
        data_at_risk: str,
        immediate_action: str,
        recommendation_1: str,
        recommendation_2: str,
        recommendation_3: str,
        recommendation_4: str,
        failed_logins_24h: int,
        blocked_ips: int,
        active_sessions: int,
        security_score: int,
        security_dashboard_url: str = "http://localhost:3000/admin/security.html"
    ):
        result = await comprehensive_email_service.send_admin_security_alert(
            admin_emails=admin_emails,
            alert_type=alert_type,
            alert_level=alert_level,
            alert_timestamp=alert_timestamp,
            alert_source=alert_source,
            alert_id=alert_id,
            severity=severity,
            category=category,
            alert_description=alert_description,
            affected_systems=affected_systems,
            source_ip=source_ip,
            user_agent=user_agent,
            geo_location=geo_location,
            attempt_count=attempt_count,
            time_window=time_window,
            impact_description=impact_description,
            affected_users=affected_users,
            data_at_risk=data_at_risk,
            immediate_action=immediate_action,
            recommendation_1=recommendation_1,
            recommendation_2=recommendation_2,
            recommendation_3=recommendation_3,
            recommendation_4=recommendation_4,
            failed_logins_24h=failed_logins_24h,
            blocked_ips=blocked_ips,
            active_sessions=active_sessions,
            security_score=security_score,
            security_dashboard_url=security_dashboard_url
        )
        if not result["success"]:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
        return {"message": "Admin security alert sent successfully", "details": result["message"]}
    
    @router.post("/send-admin-data-management-alert", summary="Send admin data management alert")
    async def send_admin_data_management_alert(
        admin_emails: List[EmailStr],
        action_type: str,
        admin_name: str,
        action_timestamp: str,
        data_type: str,
        records_affected: int,
        dataset_name: str,
        data_source: str,
        file_size: str,
        record_count: int,
        data_quality_score: int,
        last_updated: str,
        total_records: int,
        active_records: int,
        archived_records: int,
        storage_used: str,
        backup_status: str,
        action_description: str,
        action_impact: str,
        next_steps: str,
        completeness: int,
        accuracy: int,
        consistency: int,
        validity: int,
        timeliness: int,
        recommendation_1: str,
        recommendation_2: str,
        recommendation_3: str,
        data_management_url: str = "http://localhost:3000/admin/data.html"
    ):
        result = await comprehensive_email_service.send_admin_data_management_alert(
            admin_emails=admin_emails,
            action_type=action_type,
            admin_name=admin_name,
            action_timestamp=action_timestamp,
            data_type=data_type,
            records_affected=records_affected,
            dataset_name=dataset_name,
            data_source=data_source,
            file_size=file_size,
            record_count=record_count,
            data_quality_score=data_quality_score,
            last_updated=last_updated,
            total_records=total_records,
            active_records=active_records,
            archived_records=archived_records,
            storage_used=storage_used,
            backup_status=backup_status,
            action_description=action_description,
            action_impact=action_impact,
            next_steps=next_steps,
            completeness=completeness,
            accuracy=accuracy,
            consistency=consistency,
            validity=validity,
            timeliness=timeliness,
            recommendation_1=recommendation_1,
            recommendation_2=recommendation_2,
            recommendation_3=recommendation_3,
            data_management_url=data_management_url
        )
        if not result["success"]:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
        return {"message": "Admin data management alert sent successfully", "details": result["message"]}
    
    @router.post("/send-admin-system-backup-notification", summary="Send admin system backup notification")
    async def send_admin_system_backup_notification(
        admin_emails: List[EmailStr],
        backup_status: str,
        backup_type: str,
        backup_timestamp: str,
        backup_id: str,
        backup_name: str,
        backup_duration: str,
        backup_size: str,
        compression_ratio: str,
        encryption_status: str,
        server_name: str,
        database_name: str,
        tables_count: int,
        records_count: int,
        backup_location: str,
        retention_period: str,
        total_storage: str,
        used_storage: str,
        available_storage: str,
        storage_usage: int,
        oldest_backup: str,
        newest_backup: str,
        backup_message: str,
        next_backup: str,
        backup_frequency: str,
        integrity_check: str,
        restore_test: str,
        file_count: int,
        checksum: str,
        recovery_time: str,
        recovery_process: str,
        support_contact: str,
        backup_management_url: str = "http://localhost:3000/admin/database.html"
    ):
        result = await comprehensive_email_service.send_admin_system_backup_notification(
            admin_emails=admin_emails,
            backup_status=backup_status,
            backup_type=backup_type,
            backup_timestamp=backup_timestamp,
            backup_id=backup_id,
            backup_name=backup_name,
            backup_duration=backup_duration,
            backup_size=backup_size,
            compression_ratio=compression_ratio,
            encryption_status=encryption_status,
            server_name=server_name,
            database_name=database_name,
            tables_count=tables_count,
            records_count=records_count,
            backup_location=backup_location,
            retention_period=retention_period,
            total_storage=total_storage,
            used_storage=used_storage,
            available_storage=available_storage,
            storage_usage=storage_usage,
            oldest_backup=oldest_backup,
            newest_backup=newest_backup,
            backup_message=backup_message,
            next_backup=next_backup,
            backup_frequency=backup_frequency,
            integrity_check=integrity_check,
            restore_test=restore_test,
            file_count=file_count,
            checksum=checksum,
            recovery_time=recovery_time,
            recovery_process=recovery_process,
            support_contact=support_contact,
            backup_management_url=backup_management_url
        )
        if not result["success"]:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
        return {"message": "Admin system backup notification sent successfully", "details": result["message"]}
    
    @router.post("/send-admin-content-management-alert", summary="Send admin content management alert")
    async def send_admin_content_management_alert(
        admin_emails: List[EmailStr],
        action_type: str,
        admin_name: str,
        action_timestamp: str,
        content_type: str,
        content_id: str,
        content_title: str,
        content_author: str,
        content_category: str,
        content_tags: str,
        content_status: str,
        content_created: str,
        content_modified: str,
        publish_status: str,
        publish_date: str,
        expiry_date: str,
        visibility: str,
        seo_score: int,
        readability_score: int,
        content_views: int,
        content_shares: int,
        content_comments: int,
        engagement_rate: float,
        bounce_rate: float,
        time_on_page: str,
        action_description: str,
        action_impact: str,
        next_steps: str,
        word_count: int,
        reading_time: str,
        image_count: int,
        link_count: int,
        media_files: int,
        search_ranking: int,
        social_shares: int,
        email_shares: int,
        direct_traffic: int,
        referral_traffic: int,
        recommendation_1: str,
        recommendation_2: str,
        recommendation_3: str,
        content_management_url: str = "http://localhost:3000/admin/content.html"
    ):
        result = await comprehensive_email_service.send_admin_content_management_alert(
            admin_emails=admin_emails,
            action_type=action_type,
            admin_name=admin_name,
            action_timestamp=action_timestamp,
            content_type=content_type,
            content_id=content_id,
            content_title=content_title,
            content_author=content_author,
            content_category=content_category,
            content_tags=content_tags,
            content_status=content_status,
            content_created=content_created,
            content_modified=content_modified,
            publish_status=publish_status,
            publish_date=publish_date,
            expiry_date=expiry_date,
            visibility=visibility,
            seo_score=seo_score,
            readability_score=readability_score,
            content_views=content_views,
            content_shares=content_shares,
            content_comments=content_comments,
            engagement_rate=engagement_rate,
            bounce_rate=bounce_rate,
            time_on_page=time_on_page,
            action_description=action_description,
            action_impact=action_impact,
            next_steps=next_steps,
            word_count=word_count,
            reading_time=reading_time,
            image_count=image_count,
            link_count=link_count,
            media_files=media_files,
            search_ranking=search_ranking,
            social_shares=social_shares,
            email_shares=email_shares,
            direct_traffic=direct_traffic,
            referral_traffic=referral_traffic,
            recommendation_1=recommendation_1,
            recommendation_2=recommendation_2,
            recommendation_3=recommendation_3,
            content_management_url=content_management_url
        )
        if not result["success"]:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["message"])
        return {"message": "Admin content management alert sent successfully", "details": result["message"]}
