"""
Admin service layer for Crane Intelligence Platform
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
import json
import os
import uuid
from fastapi import BackgroundTasks

from ..models.admin import (
    AdminUser, ContentItem, MediaFile, SystemSetting, SystemLog, AuditLog,
    Notification, DataSource, BackgroundJob, EmailTemplate, SecurityEvent
)
from ..models.user import User, UsageLog, SubscriptionPlan
from ..schemas.admin_comprehensive import *
from ..core.auth import get_password_hash, verify_password

logger = logging.getLogger(__name__)


class AdminService:
    """Admin service for platform management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    # Dashboard Methods
    async def get_dashboard_metrics(self, db: Session) -> DashboardMetrics:
        """Get real-time dashboard metrics"""
        try:
            # User metrics
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            
            # Revenue calculation
            basic_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == "basic").first()
            pro_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == "pro").first()
            fleet_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == "fleet_valuation").first()
            
            # Subscription tier tracking removed - no longer tracking by tier
            free_users = 0
            spot_check_users = 0
            professional_users = 0
            fleet_users = 0
            
            total_revenue = 0
            if spot_check_plan:
                total_revenue += spot_check_users * spot_check_plan.monthly_price
            if professional_plan:
                total_revenue += professional_users * professional_plan.monthly_price
            if fleet_plan:
                total_revenue += fleet_users * fleet_plan.monthly_price
            
            # Reports and API calls
            reports_generated = db.query(UsageLog).filter(UsageLog.action_type == "valuation").count()
            api_calls = db.query(UsageLog).filter(UsageLog.action_type == "api_call").count()
            
            # System health (mock data - in real implementation, check actual system metrics)
            system_health = 98.5
            storage_used = 67.2
            error_rate = 0.1
            uptime = 99.9
            
            return DashboardMetrics(
                active_users=active_users,
                total_revenue=total_revenue,
                system_health=system_health,
                storage_used=storage_used,
                reports_generated=reports_generated,
                api_calls=api_calls,
                error_rate=error_rate,
                uptime=uptime
            )
        except Exception as e:
            self.logger.error(f"Error getting dashboard metrics: {e}")
            raise
    
    async def get_dashboard_data(self, db: Session) -> DashboardData:
        """Get complete dashboard data"""
        try:
            metrics = await self.get_dashboard_metrics(db)
            
            # User activity chart data (last 30 days)
            user_activity_data = await self._get_user_activity_chart_data(db)
            
            # Revenue trends (last 12 months)
            revenue_data = await self._get_revenue_chart_data(db)
            
            # Geographic distribution
            geographic_data = await self._get_geographic_data(db)
            
            # System performance
            system_performance = SystemPerformance(
                cpu_usage=45.2,
                memory_usage=67.8,
                disk_usage=34.5,
                network_io=12.3
            )
            
            # Recent activity
            recent_activity = await self._get_recent_activity(db)
            
            return DashboardData(
                metrics=metrics,
                user_activity=user_activity_data,
                revenue_trends=revenue_data,
                geographic_distribution=geographic_data,
                system_performance=system_performance,
                recent_activity=recent_activity
            )
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}")
            raise
    
    async def _get_user_activity_chart_data(self, db: Session) -> UserActivityChart:
        """Get user activity chart data"""
        # Mock data - in real implementation, query actual user activity
        labels = [f"Day {i}" for i in range(1, 31)]
        datasets = [{
            "label": "Active Users",
            "data": [100 + i * 2 + (i % 7) * 5 for i in range(30)],
            "borderColor": "#007BFF",
            "backgroundColor": "rgba(0, 123, 255, 0.1)"
        }]
        return UserActivityChart(labels=labels, datasets=datasets)
    
    async def _get_revenue_chart_data(self, db: Session) -> RevenueChart:
        """Get revenue chart data"""
        # Mock data - in real implementation, query actual revenue data
        labels = [f"Month {i}" for i in range(1, 13)]
        datasets = [{
            "label": "Monthly Revenue",
            "data": [10000 + i * 1000 + (i % 3) * 2000 for i in range(12)],
            "borderColor": "#28A745",
            "backgroundColor": "rgba(40, 167, 69, 0.1)"
        }]
        return RevenueChart(labels=labels, datasets=datasets)
    
    async def _get_geographic_data(self, db: Session) -> List[GeographicData]:
        """Get geographic distribution data"""
        # Mock data - in real implementation, query actual geographic data
        return [
            GeographicData(country="United States", users=1250, revenue=45000),
            GeographicData(country="Canada", users=320, revenue=12000),
            GeographicData(country="United Kingdom", users=180, revenue=8000),
            GeographicData(country="Germany", users=150, revenue=7000),
            GeographicData(country="Australia", users=90, revenue=4000)
        ]
    
    async def _get_recent_activity(self, db: Session) -> List[Dict[str, Any]]:
        """Get recent activity data"""
        try:
            # Get recent usage logs
            recent_logs = db.query(UsageLog).order_by(desc(UsageLog.timestamp)).limit(10).all()
            
            activities = []
            for log in recent_logs:
                user = db.query(User).filter(User.id == log.user_id).first()
                activities.append({
                    "id": str(log.id),
                    "type": log.action_type,
                    "description": f"User {user.full_name if user else 'Unknown'} performed {log.action_type}",
                    "timestamp": log.timestamp.isoformat(),
                    "user_id": str(log.user_id)
                })
            
            return activities
        except Exception as e:
            self.logger.error(f"Error getting recent activity: {e}")
            return []
    
    # Admin User Management
    async def get_admin_users(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> AdminUserListResponse:
        """Get admin users with filtering"""
        try:
            query = db.query(AdminUser)
            
            # Apply filters
            if search:
                query = query.filter(
                    or_(
                        AdminUser.full_name.ilike(f"%{search}%"),
                        AdminUser.email.ilike(f"%{search}%"),
                        AdminUser.username.ilike(f"%{search}%")
                    )
                )
            if role:
                query = query.filter(AdminUser.admin_role == role)
            if is_active is not None:
                query = query.filter(AdminUser.is_active == is_active)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            users = query.offset(skip).limit(limit).all()
            
            # Convert to response models
            user_responses = [
                AdminUserResponse(
                    id=user.id,
                    email=user.email,
                    username=user.username,
                    full_name=user.full_name,
                    admin_role=user.admin_role,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    last_login=user.last_login,
                    permissions=user.permissions or [],
                    created_at=user.created_at,
                    updated_at=user.updated_at
                )
                for user in users
            ]
            
            return AdminUserListResponse(
                users=user_responses,
                total=total,
                skip=skip,
                limit=limit
            )
        except Exception as e:
            self.logger.error(f"Error getting admin users: {e}")
            raise
    
    async def create_admin_user(self, db: Session, user_data: AdminUserCreate) -> AdminUserResponse:
        """Create new admin user"""
        try:
            # Check if email already exists
            existing_user = db.query(AdminUser).filter(AdminUser.email == user_data.email).first()
            if existing_user:
                raise ValueError("Email already registered")
            
            # Check if username already exists
            existing_username = db.query(AdminUser).filter(AdminUser.username == user_data.username).first()
            if existing_username:
                raise ValueError("Username already taken")
            
            # Create new admin user
            hashed_password = get_password_hash(user_data.password)
            admin_user = AdminUser(
                email=user_data.email,
                username=user_data.username,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                admin_role=user_data.admin_role.value,
                permissions=user_data.permissions or []
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            return AdminUserResponse(
                id=admin_user.id,
                email=admin_user.email,
                username=admin_user.username,
                full_name=admin_user.full_name,
                admin_role=admin_user.admin_role,
                is_active=admin_user.is_active,
                is_verified=admin_user.is_verified,
                last_login=admin_user.last_login,
                permissions=admin_user.permissions or [],
                created_at=admin_user.created_at,
                updated_at=admin_user.updated_at
            )
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error creating admin user: {e}")
            raise
    
    async def update_admin_user(self, db: Session, user_id: int, user_data: AdminUserUpdate) -> AdminUserResponse:
        """Update admin user"""
        try:
            admin_user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
            if not admin_user:
                raise ValueError("Admin user not found")
            
            # Update fields
            if user_data.email is not None:
                # Check if email is being changed and if it already exists
                if user_data.email != admin_user.email:
                    existing_user = db.query(AdminUser).filter(AdminUser.email == user_data.email).first()
                    if existing_user:
                        raise ValueError("Email already registered")
                admin_user.email = user_data.email
            
            if user_data.username is not None:
                # Check if username is being changed and if it already exists
                if user_data.username != admin_user.username:
                    existing_username = db.query(AdminUser).filter(AdminUser.username == user_data.username).first()
                    if existing_username:
                        raise ValueError("Username already taken")
                admin_user.username = user_data.username
            
            if user_data.full_name is not None:
                admin_user.full_name = user_data.full_name
            if user_data.admin_role is not None:
                admin_user.admin_role = user_data.admin_role.value
            if user_data.permissions is not None:
                admin_user.permissions = user_data.permissions
            if user_data.is_active is not None:
                admin_user.is_active = user_data.is_active
            
            admin_user.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(admin_user)
            
            return AdminUserResponse(
                id=admin_user.id,
                email=admin_user.email,
                username=admin_user.username,
                full_name=admin_user.full_name,
                admin_role=admin_user.admin_role,
                is_active=admin_user.is_active,
                is_verified=admin_user.is_verified,
                last_login=admin_user.last_login,
                permissions=admin_user.permissions or [],
                created_at=admin_user.created_at,
                updated_at=admin_user.updated_at
            )
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error updating admin user: {e}")
            raise
    
    async def delete_admin_user(self, db: Session, user_id: int) -> None:
        """Delete admin user"""
        try:
            admin_user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
            if not admin_user:
                raise ValueError("Admin user not found")
            
            db.delete(admin_user)
            db.commit()
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error deleting admin user: {e}")
            raise
    
    # Content Management
    async def get_content_items(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        content_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> ContentListResponse:
        """Get content items with filtering"""
        try:
            query = db.query(ContentItem)
            
            # Apply filters
            if content_type:
                query = query.filter(ContentItem.content_type == content_type)
            if status:
                query = query.filter(ContentItem.status == status)
            if search:
                query = query.filter(
                    or_(
                        ContentItem.title.ilike(f"%{search}%"),
                        ContentItem.content.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            items = query.offset(skip).limit(limit).all()
            
            # Convert to response models
            item_responses = [
                ContentItemResponse(
                    id=item.id,
                    title=item.title,
                    slug=item.slug,
                    content_type=item.content_type,
                    content=item.content,
                    excerpt=item.excerpt,
                    meta_title=item.meta_title,
                    meta_description=item.meta_description,
                    meta_keywords=item.meta_keywords,
                    status=item.status,
                    author_id=item.author_id,
                    reviewer_id=item.reviewer_id,
                    published_at=item.published_at,
                    scheduled_at=item.scheduled_at,
                    featured_image=item.featured_image,
                    media_files=item.media_files or [],
                    view_count=item.view_count,
                    like_count=item.like_count,
                    share_count=item.share_count,
                    created_at=item.created_at,
                    updated_at=item.updated_at
                )
                for item in items
            ]
            
            return ContentListResponse(
                items=item_responses,
                total=total,
                skip=skip,
                limit=limit
            )
        except Exception as e:
            self.logger.error(f"Error getting content items: {e}")
            raise
    
    async def create_content_item(self, db: Session, content_data: ContentItemCreate, author_id: int) -> ContentItemResponse:
        """Create new content item"""
        try:
            # Generate slug if not provided
            slug = content_data.slug
            if not slug:
                slug = content_data.title.lower().replace(' ', '-').replace('_', '-')
            
            # Ensure slug is unique
            counter = 1
            original_slug = slug
            while db.query(ContentItem).filter(ContentItem.slug == slug).first():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            content_item = ContentItem(
                title=content_data.title,
                slug=slug,
                content_type=content_data.content_type.value,
                content=content_data.content,
                excerpt=content_data.excerpt,
                meta_title=content_data.meta_title,
                meta_description=content_data.meta_description,
                meta_keywords=content_data.meta_keywords,
                author_id=author_id,
                featured_image=content_data.featured_image,
                media_files=content_data.media_files or [],
                scheduled_at=content_data.scheduled_at
            )
            
            db.add(content_item)
            db.commit()
            db.refresh(content_item)
            
            return ContentItemResponse(
                id=content_item.id,
                title=content_item.title,
                slug=content_item.slug,
                content_type=content_item.content_type,
                content=content_item.content,
                excerpt=content_item.excerpt,
                meta_title=content_item.meta_title,
                meta_description=content_item.meta_description,
                meta_keywords=content_item.meta_keywords,
                status=content_item.status,
                author_id=content_item.author_id,
                reviewer_id=content_item.reviewer_id,
                published_at=content_item.published_at,
                scheduled_at=content_item.scheduled_at,
                featured_image=content_item.featured_image,
                media_files=content_item.media_files or [],
                view_count=content_item.view_count,
                like_count=content_item.like_count,
                share_count=content_item.share_count,
                created_at=content_item.created_at,
                updated_at=content_item.updated_at
            )
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error creating content item: {e}")
            raise
    
    async def update_content_item(self, db: Session, item_id: int, content_data: ContentItemUpdate) -> ContentItemResponse:
        """Update content item"""
        try:
            content_item = db.query(ContentItem).filter(ContentItem.id == item_id).first()
            if not content_item:
                raise ValueError("Content item not found")
            
            # Update fields
            if content_data.title is not None:
                content_item.title = content_data.title
            if content_data.slug is not None:
                content_item.slug = content_data.slug
            if content_data.content_type is not None:
                content_item.content_type = content_data.content_type.value
            if content_data.content is not None:
                content_item.content = content_data.content
            if content_data.excerpt is not None:
                content_item.excerpt = content_data.excerpt
            if content_data.meta_title is not None:
                content_item.meta_title = content_data.meta_title
            if content_data.meta_description is not None:
                content_item.meta_description = content_data.meta_description
            if content_data.meta_keywords is not None:
                content_item.meta_keywords = content_data.meta_keywords
            if content_data.status is not None:
                content_item.status = content_data.status.value
            if content_data.featured_image is not None:
                content_item.featured_image = content_data.featured_image
            if content_data.media_files is not None:
                content_item.media_files = content_data.media_files
            if content_data.scheduled_at is not None:
                content_item.scheduled_at = content_data.scheduled_at
            
            content_item.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(content_item)
            
            return ContentItemResponse(
                id=content_item.id,
                title=content_item.title,
                slug=content_item.slug,
                content_type=content_item.content_type,
                content=content_item.content,
                excerpt=content_item.excerpt,
                meta_title=content_item.meta_title,
                meta_description=content_item.meta_description,
                meta_keywords=content_item.meta_keywords,
                status=content_item.status,
                author_id=content_item.author_id,
                reviewer_id=content_item.reviewer_id,
                published_at=content_item.published_at,
                scheduled_at=content_item.scheduled_at,
                featured_image=content_item.featured_image,
                media_files=content_item.media_files or [],
                view_count=content_item.view_count,
                like_count=content_item.like_count,
                share_count=content_item.share_count,
                created_at=content_item.created_at,
                updated_at=content_item.updated_at
            )
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error updating content item: {e}")
            raise
    
    async def delete_content_item(self, db: Session, item_id: int) -> None:
        """Delete content item"""
        try:
            content_item = db.query(ContentItem).filter(ContentItem.id == item_id).first()
            if not content_item:
                raise ValueError("Content item not found")
            
            db.delete(content_item)
            db.commit()
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error deleting content item: {e}")
            raise
    
    # Placeholder methods for other admin functions
    # These would be implemented similarly to the above methods
    
    async def get_analytics_overview(self, db: Session) -> AnalyticsOverview:
        """Get analytics overview - placeholder implementation"""
        return AnalyticsOverview(
            total_users=1000,
            active_users=750,
            new_users_today=25,
            new_users_this_week=150,
            new_users_this_month=600,
            total_revenue=50000.0,
            monthly_revenue=50000.0,
            daily_revenue=1666.67,
            reports_generated=5000,
            reports_today=50,
            reports_this_month=2000,
            api_calls=10000,
            api_calls_today=100,
            storage_used=67.5,
            storage_total=100.0,
            system_uptime=99.9,
            error_rate=0.1
        )
    
    async def get_user_analytics(self, db: Session, period: str) -> UserAnalytics:
        """Get user analytics - placeholder implementation"""
        return UserAnalytics(
            registration_trends=[],
            geographic_distribution=[],
            user_engagement=[],
            subscription_distribution={"free": 500, "spot_check": 200, "professional": 150, "fleet_valuation": 50},
            churn_rate=5.2,
            retention_rate=94.8
        )
    
    async def get_financial_analytics(self, db: Session, period: str) -> FinancialAnalytics:
        """Get financial analytics - placeholder implementation"""
        return FinancialAnalytics(
            revenue_trends=[],
            subscription_analytics={},
            payment_analytics={},
            forecasting={}
        )
    
    async def get_technical_analytics(self, db: Session, period: str) -> TechnicalAnalytics:
        """Get technical analytics - placeholder implementation"""
        return TechnicalAnalytics(
            performance_metrics={},
            error_tracking={},
            resource_usage={},
            api_analytics={}
        )
    
    # Additional placeholder methods for other admin functions
    # These would be implemented with full functionality in a production system
    
    async def get_system_settings(self, db: Session) -> SystemSettingsResponse:
        """Get system settings - placeholder implementation"""
        return SystemSettingsResponse(
            general=[],
            api=[],
            email=[],
            billing=[],
            security=[],
            advanced=[]
        )
    
    async def update_system_setting(self, db: Session, setting_id: int, setting_data: SystemSettingUpdate) -> SystemSettingResponse:
        """Update system setting - placeholder implementation"""
        pass
    
    async def get_system_logs(self, db: Session, **kwargs) -> LogListResponse:
        """Get system logs - placeholder implementation"""
        return LogListResponse(logs=[], total=0, skip=0, limit=100)
    
    async def get_audit_logs(self, db: Session, **kwargs) -> AuditLogListResponse:
        """Get audit logs - placeholder implementation"""
        return AuditLogListResponse(logs=[], total=0, skip=0, limit=100)
    
    async def get_notifications(self, db: Session, admin_user_id: int, **kwargs) -> NotificationListResponse:
        """Get notifications - placeholder implementation"""
        return NotificationListResponse(notifications=[], total=0, unread_count=0)
    
    async def create_notification(self, db: Session, notification_data: NotificationCreate) -> NotificationResponse:
        """Create notification - placeholder implementation"""
        pass
    
    async def mark_notification_read(self, db: Session, notification_id: int, admin_user_id: int) -> None:
        """Mark notification as read - placeholder implementation"""
        pass
    
    async def get_data_sources(self, db: Session) -> DataSourceListResponse:
        """Get data sources - placeholder implementation"""
        return DataSourceListResponse(sources=[], total=0)
    
    async def create_data_source(self, db: Session, source_data: DataSourceCreate) -> DataSourceResponse:
        """Create data source - placeholder implementation"""
        pass
    
    async def get_data_quality_metrics(self, db: Session) -> DataQualityMetrics:
        """Get data quality metrics - placeholder implementation"""
        return DataQualityMetrics(
            overall_score=92.5,
            accuracy=94.0,
            completeness=87.0,
            freshness=92.0,
            consistency=89.0,
            sources=[]
        )
    
    async def get_background_jobs(self, db: Session, **kwargs) -> JobListResponse:
        """Get background jobs - placeholder implementation"""
        return JobListResponse(jobs=[], total=0, skip=0, limit=100)
    
    async def cancel_background_job(self, db: Session, job_id: int) -> None:
        """Cancel background job - placeholder implementation"""
        pass
    
    async def get_security_dashboard(self, db: Session) -> SecurityDashboard:
        """Get security dashboard - placeholder implementation"""
        return SecurityDashboard(
            security_score=92.0,
            threat_level="low",
            recent_events=[],
            failed_logins=5,
            blocked_ips=2,
            active_sessions=45,
            security_recommendations=[]
        )
    
    async def get_security_events(self, db: Session, **kwargs) -> SecurityEventListResponse:
        """Get security events - placeholder implementation"""
        return SecurityEventListResponse(events=[], total=0, skip=0, limit=100)
    
    async def get_email_templates(self, db: Session, **kwargs) -> EmailTemplateListResponse:
        """Get email templates - placeholder implementation"""
        return EmailTemplateListResponse(templates=[], total=0)
    
    async def create_email_template(self, db: Session, template_data: EmailTemplateCreate) -> EmailTemplateResponse:
        """Create email template - placeholder implementation"""
        pass
    
    async def bulk_user_operation(self, db: Session, operation_data: BulkUserOperation, background_tasks: BackgroundTasks) -> BulkOperationResponse:
        """Perform bulk user operations - placeholder implementation"""
        pass
    
    async def bulk_content_operation(self, db: Session, operation_data: BulkContentOperation, background_tasks: BackgroundTasks) -> BulkOperationResponse:
        """Perform bulk content operations - placeholder implementation"""
        pass
    
    async def export_data(self, db: Session, export_request: DataExportRequest, background_tasks: BackgroundTasks) -> DataExportResponse:
        """Export data - placeholder implementation"""
        pass
    
    async def import_data(self, db: Session, import_request: DataImportRequest, background_tasks: BackgroundTasks) -> DataImportResponse:
        """Import data - placeholder implementation"""
        pass


# Create service instance
admin_service = AdminService()
