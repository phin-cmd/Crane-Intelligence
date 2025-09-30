#!/usr/bin/env python3
"""
Comprehensive Email Service for Crane Intelligence Platform
Handles all email triggers for main website and admin portal
"""
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging

from ...core.config import settings

logger = logging.getLogger(__name__)

class ComprehensiveEmailService:
    def __init__(self):
        """Initialize the comprehensive email service"""
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.mail_username,
            MAIL_PASSWORD=settings.mail_password,
            MAIL_FROM=settings.mail_from_email,
            MAIL_PORT=settings.mail_port,
            MAIL_SERVER=settings.mail_server,
            MAIL_FROM_NAME=settings.mail_from_name,
            MAIL_TLS=settings.mail_use_tls,
            MAIL_SSL=settings.mail_use_ssl,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        self.fm = FastMail(self.conf)
        self.env = Environment(loader=FileSystemLoader(Path(settings.email_templates_dir)))
        
        # Email templates mapping
        self.templates = {
            # Main Website Emails
            'user_registration': 'user_registration.html',
            'password_reset': 'password_reset.html',
            'valuation_report': 'valuation_report.html',
            'equipment_inspection': 'equipment_inspection.html',
            'welcome': 'welcome.html',
            'notification': 'notification.html',
            
            # Admin Portal Emails
            'admin_user_registration': 'admin_user_registration.html',
            'admin_system_alert': 'admin_system_alert.html',
            'admin_analytics_report': 'admin_analytics_report.html',
            'admin_notification': 'admin_notification.html',
            'admin_user_management': 'admin_user_management.html',
            'admin_security_alert': 'admin_security_alert.html',
            'admin_data_management': 'admin_data_management.html',
            'admin_system_backup': 'admin_system_backup.html',
            'admin_content_management': 'admin_content_management.html',
            
            # Notification Emails
            'notification_general': 'notification_general.html',
            'notification_system_maintenance': 'notification_system_maintenance.html',
        }

    async def send_email(self, recipients: List[str], subject: str, template_name: str, 
                        context: Dict[str, Any], attachments: List[str] = None) -> Dict[str, Any]:
        """Send a generic email using a template"""
        try:
            template = self.env.get_template(template_name)
            html_content = template.render(context)
            
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                html_body=html_content,
                subtype="html",
                attachments=attachments
            )
            
            await self.fm.send_message(message)
            logger.info(f"Email sent successfully to {', '.join(recipients)}")
            return {"success": True, "message": f"Email sent to {', '.join(recipients)}"}
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {"success": False, "message": f"Failed to send email: {e}"}

    # ==================== MAIN WEBSITE EMAIL TRIGGERS ====================
    
    async def send_user_registration_email(self, user_email: str, username: str, 
                                         account_type: str = "Standard") -> Dict[str, Any]:
        """Send welcome email to new user"""
        subject = "Welcome to Crane Intelligence Platform!"
        context = {
            "username": username,
            "user_email": user_email,
            "account_type": account_type,
            "registration_date": datetime.now().strftime("%B %d, %Y"),
            "dashboard_url": f"{settings.frontend_url}/dashboard.html",
            "platform_name": settings.app_name
        }
        return await self.send_email([user_email], subject, self.templates['user_registration'], context)

    async def send_password_reset_email(self, user_email: str, username: str, 
                                      reset_token: str) -> Dict[str, Any]:
        """Send password reset email"""
        subject = "Password Reset Request - Crane Intelligence"
        reset_link = f"{settings.frontend_url}/reset-password.html?token={reset_token}"
        context = {
            "username": username,
            "user_email": user_email,
            "reset_link": reset_link,
            "expiry_hours": 24,
            "platform_name": settings.app_name
        }
        return await self.send_email([user_email], subject, self.templates['password_reset'], context)

    async def send_valuation_report_email(self, user_email: str, username: str, 
                                         report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send valuation report email"""
        subject = f"Your Valuation Report is Ready - {report_data.get('equipment_name', 'Equipment')}"
        context = {
            "username": username,
            "user_email": user_email,
            "report_id": report_data.get('report_id'),
            "generation_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "equipment_name": report_data.get('equipment_name'),
            "valuation_type": report_data.get('valuation_type', 'Standard'),
            "estimated_value": report_data.get('estimated_value', 'N/A'),
            "confidence_level": report_data.get('confidence_level', 85),
            "manufacturer": report_data.get('manufacturer'),
            "model": report_data.get('model'),
            "year": report_data.get('year'),
            "operating_hours": report_data.get('operating_hours'),
            "condition": report_data.get('condition'),
            "report_link": f"{settings.frontend_url}/reports/{report_data.get('report_id')}",
            "platform_name": settings.app_name
        }
        return await self.send_email([user_email], subject, self.templates['valuation_report'], context)

    async def send_equipment_inspection_email(self, user_email: str, username: str, 
                                            inspection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send equipment inspection scheduled email"""
        subject = "Equipment Inspection Scheduled - Crane Intelligence"
        context = {
            "username": username,
            "user_email": user_email,
            "equipment_name": inspection_data.get('equipment_name'),
            "inspection_date": inspection_data.get('inspection_date'),
            "inspection_time": inspection_data.get('inspection_time'),
            "estimated_duration": inspection_data.get('estimated_duration', '2-3 hours'),
            "inspector_name": inspection_data.get('inspector_name'),
            "inspection_location": inspection_data.get('inspection_location'),
            "inspector_phone": inspection_data.get('inspector_phone'),
            "inspector_email": inspection_data.get('inspector_email'),
            "inspector_certification": inspection_data.get('inspector_certification'),
            "inspection_portal_link": f"{settings.frontend_url}/inspections/{inspection_data.get('inspection_id')}",
            "scheduling_date": datetime.now().strftime("%B %d, %Y"),
            "platform_name": settings.app_name
        }
        return await self.send_email([user_email], subject, self.templates['equipment_inspection'], context)

    # ==================== ADMIN PORTAL EMAIL TRIGGERS ====================
    
    async def send_admin_user_registration_alert(self, admin_emails: List[str], 
                                               user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send admin alert for new user registration"""
        subject = f"New User Registration Alert - {user_data.get('user_name')}"
        context = {
            "user_name": user_data.get('user_name'),
            "user_email": user_data.get('user_email'),
            "company_name": user_data.get('company_name'),
            "registration_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "account_type": user_data.get('account_type'),
            "ip_address": user_data.get('ip_address'),
            "user_agent": user_data.get('user_agent'),
            "email_verified": user_data.get('email_verified', False),
            "phone_verified": user_data.get('phone_verified', False),
            "registration_source": user_data.get('registration_source', 'Website'),
            "risk_score": user_data.get('risk_score', 25),
            "industry": user_data.get('industry'),
            "company_size": user_data.get('company_size'),
            "use_case": user_data.get('use_case'),
            "expected_usage": user_data.get('expected_usage'),
            "admin_user_management_url": f"{settings.admin_url}/admin/users.html",
            "total_users": user_data.get('total_users', 0),
            "new_users_week": user_data.get('new_users_week', 0),
            "active_users": user_data.get('active_users', 0),
            "pending_approvals": user_data.get('pending_approvals', 0),
            "admin_email": admin_emails[0],
            "notification_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "platform_name": settings.app_name
        }
        return await self.send_email(admin_emails, subject, self.templates['admin_user_registration'], context)

    async def send_admin_system_alert(self, admin_emails: List[str], 
                                    alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send system alert to admins"""
        subject = f"System Alert: {alert_data.get('alert_type')} - {alert_data.get('alert_level')}"
        context = {
            "alert_type": alert_data.get('alert_type'),
            "alert_level": alert_data.get('alert_level'),
            "alert_color": alert_data.get('alert_color', '#dc3545'),
            "alert_timestamp": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "system_component": alert_data.get('system_component'),
            "alert_id": alert_data.get('alert_id'),
            "severity": alert_data.get('severity'),
            "category": alert_data.get('category'),
            "alert_source": alert_data.get('alert_source'),
            "alert_description": alert_data.get('alert_description'),
            "cpu_usage": alert_data.get('cpu_usage', 0),
            "memory_usage": alert_data.get('memory_usage', 0),
            "disk_usage": alert_data.get('disk_usage', 0),
            "db_connections": alert_data.get('db_connections', 0),
            "active_users": alert_data.get('active_users', 0),
            "response_time": alert_data.get('response_time', 0),
            "action_description": alert_data.get('action_description'),
            "action_1": alert_data.get('action_1'),
            "action_2": alert_data.get('action_2'),
            "action_3": alert_data.get('action_3'),
            "impact_description": alert_data.get('impact_description'),
            "affected_users": alert_data.get('affected_users', 0),
            "estimated_resolution": alert_data.get('estimated_resolution'),
            "admin_dashboard_url": f"{settings.admin_url}/admin/dashboard.html",
            "primary_admin": alert_data.get('primary_admin'),
            "technical_lead": alert_data.get('technical_lead'),
            "oncall_engineer": alert_data.get('oncall_engineer'),
            "similar_alerts_24h": alert_data.get('similar_alerts_24h', 0),
            "system_uptime": alert_data.get('system_uptime', '99.9%'),
            "last_maintenance": alert_data.get('last_maintenance'),
            "performance_trend": alert_data.get('performance_trend', 'Stable'),
            "admin_email": admin_emails[0],
            "platform_name": settings.app_name
        }
        return await self.send_email(admin_emails, subject, self.templates['admin_system_alert'], context)

    async def send_admin_analytics_report(self, admin_emails: List[str], 
                                        analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send weekly analytics report to admins"""
        subject = f"Weekly Analytics Report - {analytics_data.get('report_period')}"
        context = {
            "report_period": analytics_data.get('report_period'),
            "generation_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "report_type": analytics_data.get('report_type', 'Weekly'),
            "total_users": analytics_data.get('total_users', 0),
            "new_users_week": analytics_data.get('new_users_week', 0),
            "active_users": analytics_data.get('active_users', 0),
            "total_valuations": analytics_data.get('total_valuations', 0),
            "user_growth": analytics_data.get('user_growth', 0),
            "valuation_requests": analytics_data.get('valuation_requests', 0),
            "avg_session_duration": analytics_data.get('avg_session_duration', '0m'),
            "uptime": analytics_data.get('uptime', 99.9),
            "satisfaction_score": analytics_data.get('satisfaction_score', 8.5),
            "peak_usage_time": analytics_data.get('peak_usage_time', '2-4 PM'),
            "popular_feature": analytics_data.get('popular_feature', 'Equipment Valuation'),
            "top_regions": analytics_data.get('top_regions', 'North America'),
            "device_breakdown": analytics_data.get('device_breakdown', 'Desktop: 60%, Mobile: 40%'),
            "conversion_rate": analytics_data.get('conversion_rate', 15.5),
            "valuation_usage": analytics_data.get('valuation_usage', 85),
            "market_analysis_usage": analytics_data.get('market_analysis_usage', 65),
            "report_generation_usage": analytics_data.get('report_generation_usage', 45),
            "admin_portal_usage": analytics_data.get('admin_portal_usage', 25),
            "recommendation_1": analytics_data.get('recommendation_1'),
            "recommendation_2": analytics_data.get('recommendation_2'),
            "recommendation_3": analytics_data.get('recommendation_3'),
            "recommendation_4": analytics_data.get('recommendation_4'),
            "bounce_rate": analytics_data.get('bounce_rate', 35),
            "support_tickets": analytics_data.get('support_tickets', 0),
            "error_rate": analytics_data.get('error_rate', 0.5),
            "performance_issues": analytics_data.get('performance_issues', 0),
            "analytics_dashboard_url": f"{settings.admin_url}/admin/analytics.html",
            "technical_issues_count": analytics_data.get('technical_issues_count', 0),
            "user_support_count": analytics_data.get('user_support_count', 0),
            "feature_requests_count": analytics_data.get('feature_requests_count', 0),
            "avg_response_time": analytics_data.get('avg_response_time', '2.5 hours'),
            "admin_email": admin_emails[0],
            "platform_name": settings.app_name
        }
        return await self.send_email(admin_emails, subject, self.templates['admin_analytics_report'], context)

    # ==================== NOTIFICATION EMAIL TRIGGERS ====================
    
    async def send_general_notification(self, user_email: str, username: str, 
                                      notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send general notification email"""
        subject = f"Notification: {notification_data.get('notification_title')}"
        context = {
            "username": username,
            "user_email": user_email,
            "notification_type": notification_data.get('notification_type'),
            "priority": notification_data.get('priority'),
            "notification_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "category": notification_data.get('category'),
            "priority_level": notification_data.get('priority_level', 'medium'),
            "priority_icon": notification_data.get('priority_icon', '🔔'),
            "notification_title": notification_data.get('notification_title'),
            "notification_message": notification_data.get('notification_message'),
            "related_item": notification_data.get('related_item'),
            "action_required": notification_data.get('action_required'),
            "deadline": notification_data.get('deadline'),
            "contact_info": notification_data.get('contact_info'),
            "action_url": notification_data.get('action_url'),
            "dashboard_url": f"{settings.frontend_url}/dashboard.html",
            "notifications_url": f"{settings.frontend_url}/notifications.html",
            "settings_url": f"{settings.frontend_url}/settings.html",
            "support_url": f"{settings.frontend_url}/support.html",
            "email_notifications": notification_data.get('email_notifications', True),
            "push_notifications": notification_data.get('push_notifications', True),
            "sms_notifications": notification_data.get('sms_notifications', False),
            "notification_frequency": notification_data.get('notification_frequency', 'Real-time'),
            "unsubscribe_url": f"{settings.frontend_url}/unsubscribe?email={user_email}",
            "preferences_url": f"{settings.frontend_url}/preferences.html",
            "platform_name": settings.app_name
        }
        return await self.send_email([user_email], subject, self.templates['notification_general'], context)

    async def send_system_maintenance_notification(self, user_emails: List[str], 
                                                 maintenance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send system maintenance notification"""
        subject = f"Scheduled Maintenance: {maintenance_data.get('maintenance_date')}"
        context = {
            "username": "Valued User",
            "user_email": user_emails[0],
            "maintenance_date": maintenance_data.get('maintenance_date'),
            "start_time": maintenance_data.get('start_time'),
            "end_time": maintenance_data.get('end_time'),
            "estimated_duration": maintenance_data.get('estimated_duration'),
            "maintenance_type": maintenance_data.get('maintenance_type'),
            "maintenance_reason": maintenance_data.get('maintenance_reason'),
            "affected_service_1": maintenance_data.get('affected_service_1'),
            "affected_service_2": maintenance_data.get('affected_service_2'),
            "affected_service_3": maintenance_data.get('affected_service_3'),
            "expected_downtime": maintenance_data.get('expected_downtime'),
            "mid_time": maintenance_data.get('mid_time'),
            "verification_time": maintenance_data.get('verification_time'),
            "system_updates": maintenance_data.get('system_updates'),
            "security_patches": maintenance_data.get('security_patches'),
            "performance_improvements": maintenance_data.get('performance_improvements'),
            "new_features": maintenance_data.get('new_features'),
            "status_page_url": f"{settings.frontend_url}/status.html",
            "notification_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "unsubscribe_url": f"{settings.frontend_url}/unsubscribe",
            "preferences_url": f"{settings.frontend_url}/preferences.html",
            "platform_name": settings.app_name
        }
        return await self.send_email(user_emails, subject, self.templates['notification_system_maintenance'], context)

    # ==================== BULK EMAIL FUNCTIONS ====================
    
    async def send_bulk_notifications(self, user_emails: List[str], 
                                    notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send bulk notifications to multiple users"""
        results = []
        for email in user_emails:
            result = await self.send_general_notification(
                email, 
                notification_data.get('username', 'User'), 
                notification_data
            )
            results.append(result)
        
        success_count = sum(1 for r in results if r.get('success', False))
        return {
            "success": success_count > 0,
            "message": f"Sent {success_count}/{len(user_emails)} notifications successfully",
            "results": results
        }

    async def send_admin_bulk_alert(self, admin_emails: List[str], 
                                  alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send bulk alerts to all admins"""
        return await self.send_admin_system_alert(admin_emails, alert_data)
    
    # ==================== ADDITIONAL ADMIN PORTAL EMAIL FUNCTIONS ====================
    
    async def send_admin_user_management_alert(self, admin_emails: List[str], action_type: str, admin_name: str, 
                                            action_timestamp: str, admin_ip: str, admin_user_agent: str,
                                            user_id: str, username: str, user_email: str, previous_status: str,
                                            new_status: str, user_role: str, last_login: str, action_description: str,
                                            action_reason: str, action_impact: str, total_users: int, active_users: int,
                                            suspended_users: int, admin_actions_today: int, admin_users_url: str):
        """Send admin alert for user management actions"""
        subject = f"User Management Action: {action_type} - {settings.app_name}"
        context = {
            "platform_name": settings.app_name,
            "action_type": action_type,
            "admin_name": admin_name,
            "action_timestamp": action_timestamp,
            "admin_ip": admin_ip,
            "admin_user_agent": admin_user_agent,
            "user_id": user_id,
            "username": username,
            "user_email": user_email,
            "previous_status": previous_status,
            "new_status": new_status,
            "user_role": user_role,
            "last_login": last_login,
            "action_description": action_description,
            "action_reason": action_reason,
            "action_impact": action_impact,
            "total_users": total_users,
            "active_users": active_users,
            "suspended_users": suspended_users,
            "admin_actions_today": admin_actions_today,
            "admin_users_url": admin_users_url,
            "admin_email": admin_emails[0],
            "notification_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "year": datetime.now().year
        }
        return await self.send_email(admin_emails, subject, self.templates['admin_user_management'], context)
    
    async def send_admin_security_alert(self, admin_emails: List[str], alert_type: str, alert_level: str,
                                      alert_timestamp: str, alert_source: str, alert_id: str, severity: str,
                                      category: str, alert_description: str, affected_systems: str,
                                      source_ip: str, user_agent: str, geo_location: str, attempt_count: int,
                                      time_window: str, impact_description: str, affected_users: str,
                                      data_at_risk: str, immediate_action: str, recommendation_1: str,
                                      recommendation_2: str, recommendation_3: str, recommendation_4: str,
                                      failed_logins_24h: int, blocked_ips: int, active_sessions: int,
                                      security_score: int, security_dashboard_url: str):
        """Send admin security alert"""
        alert_color = "#dc3545" if alert_level == "CRITICAL" else "#ffc107" if alert_level == "HIGH" else "#17a2b8"
        subject = f"Security Alert: {alert_type} - {settings.app_name}"
        context = {
            "platform_name": settings.app_name,
            "alert_type": alert_type,
            "alert_level": alert_level,
            "alert_color": alert_color,
            "alert_timestamp": alert_timestamp,
            "alert_source": alert_source,
            "alert_id": alert_id,
            "severity": severity,
            "category": category,
            "alert_description": alert_description,
            "affected_systems": affected_systems,
            "source_ip": source_ip,
            "user_agent": user_agent,
            "geo_location": geo_location,
            "attempt_count": attempt_count,
            "time_window": time_window,
            "impact_description": impact_description,
            "affected_users": affected_users,
            "data_at_risk": data_at_risk,
            "immediate_action": immediate_action,
            "recommendation_1": recommendation_1,
            "recommendation_2": recommendation_2,
            "recommendation_3": recommendation_3,
            "recommendation_4": recommendation_4,
            "failed_logins_24h": failed_logins_24h,
            "blocked_ips": blocked_ips,
            "active_sessions": active_sessions,
            "security_score": security_score,
            "security_dashboard_url": security_dashboard_url,
            "admin_email": admin_emails[0],
            "year": datetime.now().year
        }
        return await self.send_email(admin_emails, subject, self.templates['admin_security_alert'], context)
    
    async def send_admin_data_management_alert(self, admin_emails: List[str], action_type: str, admin_name: str,
                                             action_timestamp: str, data_type: str, records_affected: int,
                                             dataset_name: str, data_source: str, file_size: str, record_count: int,
                                             data_quality_score: int, last_updated: str, total_records: int,
                                             active_records: int, archived_records: int, storage_used: str,
                                             backup_status: str, action_description: str, action_impact: str,
                                             next_steps: str, completeness: int, accuracy: int, consistency: int,
                                             validity: int, timeliness: int, recommendation_1: str,
                                             recommendation_2: str, recommendation_3: str, data_management_url: str):
        """Send admin data management alert"""
        subject = f"Data Management Action: {action_type} - {settings.app_name}"
        context = {
            "platform_name": settings.app_name,
            "action_type": action_type,
            "admin_name": admin_name,
            "action_timestamp": action_timestamp,
            "data_type": data_type,
            "records_affected": records_affected,
            "dataset_name": dataset_name,
            "data_source": data_source,
            "file_size": file_size,
            "record_count": record_count,
            "data_quality_score": data_quality_score,
            "last_updated": last_updated,
            "total_records": total_records,
            "active_records": active_records,
            "archived_records": archived_records,
            "storage_used": storage_used,
            "backup_status": backup_status,
            "action_description": action_description,
            "action_impact": action_impact,
            "next_steps": next_steps,
            "completeness": completeness,
            "accuracy": accuracy,
            "consistency": consistency,
            "validity": validity,
            "timeliness": timeliness,
            "recommendation_1": recommendation_1,
            "recommendation_2": recommendation_2,
            "recommendation_3": recommendation_3,
            "data_management_url": data_management_url,
            "admin_email": admin_emails[0],
            "notification_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "year": datetime.now().year
        }
        return await self.send_email(admin_emails, subject, self.templates['admin_data_management'], context)
    
    async def send_admin_system_backup_notification(self, admin_emails: List[str], backup_status: str, backup_type: str,
                                                  backup_timestamp: str, backup_id: str, backup_name: str,
                                                  backup_duration: str, backup_size: str, compression_ratio: str,
                                                  encryption_status: str, server_name: str, database_name: str,
                                                  tables_count: int, records_count: int, backup_location: str,
                                                  retention_period: str, total_storage: str, used_storage: str,
                                                  available_storage: str, storage_usage: int, oldest_backup: str,
                                                  newest_backup: str, backup_message: str, next_backup: str,
                                                  backup_frequency: str, integrity_check: str, restore_test: str,
                                                  file_count: int, checksum: str, recovery_time: str,
                                                  recovery_process: str, support_contact: str, backup_management_url: str):
        """Send admin system backup notification"""
        status_color = "#28a745" if backup_status == "SUCCESS" else "#dc3545" if backup_status == "FAILED" else "#ffc107"
        subject = f"System Backup {backup_status}: {backup_name} - {settings.app_name}"
        context = {
            "platform_name": settings.app_name,
            "backup_status": backup_status,
            "status_color": status_color,
            "backup_type": backup_type,
            "backup_timestamp": backup_timestamp,
            "backup_id": backup_id,
            "backup_name": backup_name,
            "backup_duration": backup_duration,
            "backup_size": backup_size,
            "compression_ratio": compression_ratio,
            "encryption_status": encryption_status,
            "server_name": server_name,
            "database_name": database_name,
            "tables_count": tables_count,
            "records_count": records_count,
            "backup_location": backup_location,
            "retention_period": retention_period,
            "total_storage": total_storage,
            "used_storage": used_storage,
            "available_storage": available_storage,
            "storage_usage": storage_usage,
            "oldest_backup": oldest_backup,
            "newest_backup": newest_backup,
            "backup_message": backup_message,
            "next_backup": next_backup,
            "backup_frequency": backup_frequency,
            "integrity_check": integrity_check,
            "restore_test": restore_test,
            "file_count": file_count,
            "checksum": checksum,
            "recovery_time": recovery_time,
            "recovery_process": recovery_process,
            "support_contact": support_contact,
            "backup_management_url": backup_management_url,
            "admin_email": admin_emails[0],
            "year": datetime.now().year
        }
        return await self.send_email(admin_emails, subject, self.templates['admin_system_backup'], context)
    
    async def send_admin_content_management_alert(self, admin_emails: List[str], action_type: str, admin_name: str,
                                                action_timestamp: str, content_type: str, content_id: str,
                                                content_title: str, content_author: str, content_category: str,
                                                content_tags: str, content_status: str, content_created: str,
                                                content_modified: str, publish_status: str, publish_date: str,
                                                expiry_date: str, visibility: str, seo_score: int,
                                                readability_score: int, content_views: int, content_shares: int,
                                                content_comments: int, engagement_rate: float, bounce_rate: float,
                                                time_on_page: str, action_description: str, action_impact: str,
                                                next_steps: str, word_count: int, reading_time: str,
                                                image_count: int, link_count: int, media_files: int,
                                                search_ranking: int, social_shares: int, email_shares: int,
                                                direct_traffic: int, referral_traffic: int, recommendation_1: str,
                                                recommendation_2: str, recommendation_3: str, content_management_url: str):
        """Send admin content management alert"""
        subject = f"Content Management Action: {action_type} - {settings.app_name}"
        context = {
            "platform_name": settings.app_name,
            "action_type": action_type,
            "admin_name": admin_name,
            "action_timestamp": action_timestamp,
            "content_type": content_type,
            "content_id": content_id,
            "content_title": content_title,
            "content_author": content_author,
            "content_category": content_category,
            "content_tags": content_tags,
            "content_status": content_status,
            "content_created": content_created,
            "content_modified": content_modified,
            "publish_status": publish_status,
            "publish_date": publish_date,
            "expiry_date": expiry_date,
            "visibility": visibility,
            "seo_score": seo_score,
            "readability_score": readability_score,
            "content_views": content_views,
            "content_shares": content_shares,
            "content_comments": content_comments,
            "engagement_rate": engagement_rate,
            "bounce_rate": bounce_rate,
            "time_on_page": time_on_page,
            "action_description": action_description,
            "action_impact": action_impact,
            "next_steps": next_steps,
            "word_count": word_count,
            "reading_time": reading_time,
            "image_count": image_count,
            "link_count": link_count,
            "media_files": media_files,
            "search_ranking": search_ranking,
            "social_shares": social_shares,
            "email_shares": email_shares,
            "direct_traffic": direct_traffic,
            "referral_traffic": referral_traffic,
            "recommendation_1": recommendation_1,
            "recommendation_2": recommendation_2,
            "recommendation_3": recommendation_3,
            "content_management_url": content_management_url,
            "admin_email": admin_emails[0],
            "notification_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "year": datetime.now().year
        }
        return await self.send_email(admin_emails, subject, self.templates['admin_content_management'], context)

# Create global instance
comprehensive_email_service = ComprehensiveEmailService()
