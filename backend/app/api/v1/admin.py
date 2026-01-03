"""
Admin API endpoints for Crane Intelligence Platform
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ...core.database import get_db
from ...models.user import User, UserRole
from ...models.crane import Crane
from ...models.admin import AdminUser
from ...core.admin_auth import (
    get_current_admin_user,
    require_super_admin,
    require_admin_or_super_admin,
    require_no_delete_restriction,
    require_can_view_financial_data
)
from ...core.admin_permissions import (
    Permission,
    has_permission,
    AdminRole,
    can_delete,
    can_view_financial_data
)
# from ...models.enhanced_crane import CraneListing, DataRefreshLog  # Tables don't exist yet
from ...schemas.admin import (
    DashboardStats, UserStats, ReportStats, SystemStatusInfo, SystemStatus,
    UserListResponse, UserUpdate, UserCreate, UserResponse,
    ReportListResponse, ReportResponse,
    ActivityItem
)
from ...core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

# Analytics Endpoint
@router.get("/analytics")
async def get_admin_analytics(
    timeRange: Optional[str] = Query("30d", description="Time range: 7d, 30d, 90d, 1y"),
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics for admin dashboard
    Combines visitor tracking data with business metrics
    Only available in production environment
    """
    # Check if analytics is enabled (production only)
    environment = os.getenv("ENVIRONMENT", "prod").lower()
    if environment not in ["prod", "production"]:
        raise HTTPException(
            status_code=403,
            detail="Analytics endpoint is only available in production environment"
        )
    
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        # Calculate date range
        end_date = datetime.now()
        if timeRange == "7d":
            start_date = end_date - timedelta(days=7)
        elif timeRange == "30d":
            start_date = end_date - timedelta(days=30)
        elif timeRange == "90d":
            start_date = end_date - timedelta(days=90)
        elif timeRange == "1y":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Get visitor tracking stats if table exists
        visitor_stats = {}
        try:
            from ...models.visitor_tracking import VisitorTracking
            total_visitors = db.query(func.count(func.distinct(VisitorTracking.visitor_id))).filter(
                VisitorTracking.visited_at >= start_date,
                VisitorTracking.visited_at <= end_date,
                VisitorTracking.is_bot == False
            ).scalar() or 0
            
            total_page_views = db.query(func.count(VisitorTracking.id)).filter(
                VisitorTracking.visited_at >= start_date,
                VisitorTracking.visited_at <= end_date,
                VisitorTracking.is_bot == False
            ).scalar() or 0
            
            unique_sessions = db.query(func.count(func.distinct(VisitorTracking.session_id))).filter(
                VisitorTracking.visited_at >= start_date,
                VisitorTracking.visited_at <= end_date,
                VisitorTracking.is_bot == False
            ).scalar() or 0
            
            visitor_stats = {
                "total_visitors": total_visitors,
                "total_page_views": total_page_views,
                "unique_sessions": unique_sessions,
                "bounce_rate": 0.0,
                "avg_time_on_page": 0
            }
        except Exception as e:
            # Table might not exist yet - that's okay
            import logging
            logging.getLogger(__name__).warning(f"Visitor tracking table not available: {e}")
        
        # Get business metrics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        
        from ...models.fmv_report import FMVReport
        total_reports = db.query(FMVReport).count()
        reports_this_period = db.query(FMVReport).filter(
            FMVReport.created_at >= start_date
        ).count()
        
        total_revenue_result = db.query(func.sum(FMVReport.amount_paid)).filter(
            FMVReport.amount_paid.isnot(None),
            FMVReport.amount_paid > 0
        ).scalar()
        total_revenue = float(total_revenue_result) if total_revenue_result else 0.0
        
        revenue_this_period_result = db.query(func.sum(FMVReport.amount_paid)).filter(
            FMVReport.amount_paid.isnot(None),
            FMVReport.amount_paid > 0,
            FMVReport.paid_at >= start_date
        ).scalar()
        revenue_this_period = float(revenue_this_period_result) if revenue_this_period_result else 0.0
        
        return {
            "success": True,
            "analytics": {
                "overview": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "total_reports": total_reports,
                    "reports_this_period": reports_this_period,
                    "total_revenue": total_revenue,
                    "revenue_this_period": revenue_this_period
                },
                "visitors": visitor_stats,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "range": timeRange
                }
            }
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching admin analytics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")

# Test endpoint to verify routing
@router.get("/analytics/test")
async def test_analytics_route():
    """Test endpoint to verify analytics route is accessible"""
    return {"success": True, "message": "Analytics route is working", "path": "/api/v1/admin/analytics"}

# Role-based access control helpers
def require_admin_access(current_user: AdminUser = Depends(get_current_admin_user)):
    """Require any admin role (not regular users)"""
    return current_user

def require_can_delete(current_user: AdminUser = Depends(get_current_admin_user)):
    """Require role that can delete resources"""
    try:
        user_role = AdminRole(current_user.admin_role)
        if not can_delete(user_role):
            raise HTTPException(status_code=403, detail="Delete access not allowed for your role")
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid admin role")
    return current_user

# Dashboard Endpoints
@router.get("/dashboard")
async def get_dashboard(
    current_user: AdminUser = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Get dashboard data - main dashboard endpoint"""
    try:
        # Get dashboard stats
        stats = await get_dashboard_stats(current_user, db)
        # Get dashboard activity  
        activity = await get_recent_activity(10, current_user, db)
        # Get system status
        status_info = await get_system_status(current_user, db)
        
        return {
            "success": True,
            "stats": stats.dict() if hasattr(stats, 'dict') else stats,
            "activity": [item.dict() if hasattr(item, 'dict') else item for item in activity],
            "status": status_info.dict() if hasattr(status_info, 'dict') else status_info
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard data"
        )

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: AdminUser = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    try:
        # Get user statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        new_users_today = db.query(User).filter(
            User.created_at >= datetime.now().date()
        ).count()
        
        # Get report statistics from FMV reports
        from ...models.fmv_report import FMVReport
        total_reports = db.query(FMVReport).count()
        reports_today = db.query(FMVReport).filter(
            FMVReport.created_at >= datetime.now().date()
        ).count()
        reports_this_month = db.query(FMVReport).filter(
            FMVReport.created_at >= datetime.now().replace(day=1).date()
        ).count()
        
        # Get revenue statistics from FMV reports (amount_paid)
        from sqlalchemy import func
        total_revenue_result = db.query(func.sum(FMVReport.amount_paid)).filter(
            FMVReport.amount_paid.isnot(None),
            FMVReport.amount_paid > 0
        ).scalar()
        total_revenue = float(total_revenue_result) if total_revenue_result else 0.0
        
        revenue_today_result = db.query(func.sum(FMVReport.amount_paid)).filter(
            FMVReport.amount_paid.isnot(None),
            FMVReport.amount_paid > 0,
            FMVReport.paid_at >= datetime.now().date()
        ).scalar()
        revenue_today = float(revenue_today_result) if revenue_today_result else 0.0
        
        revenue_this_month_result = db.query(func.sum(FMVReport.amount_paid)).filter(
            FMVReport.amount_paid.isnot(None),
            FMVReport.amount_paid > 0,
            FMVReport.paid_at >= datetime.now().replace(day=1).date()
        ).scalar()
        revenue_this_month = float(revenue_this_month_result) if revenue_this_month_result else 0.0
        
        # Get system status
        system_uptime = 99.9
        api_response_time = 120  # milliseconds
        
        # Calculate users by role
        users_by_role = {}
        if db:
            try:
                from sqlalchemy import func
                role_counts = db.query(User.user_role, func.count(User.id)).group_by(User.user_role).all()
                for role, count in role_counts:
                    # Convert role enum to string
                    role_str = role.value if hasattr(role, 'value') else str(role)
                    users_by_role[role_str] = count
            except Exception as e:
                logger.warning(f"Could not get users by role: {e}")
                users_by_role = {}
        
        return DashboardStats(
            users=UserStats(
                total=total_users,
                active=active_users,
                new_today=new_users_today,
                by_role=users_by_role,
                by_tier={}  # No subscription tiers - using report types instead
            ),
            reports=ReportStats(
                total=total_reports,
                today=reports_today,
                this_month=reports_this_month
            ),
            revenue={
                'total': total_revenue,
                'today': revenue_today,
                'this_month': revenue_this_month
            },
            system=SystemStatusInfo(
                uptime=system_uptime,
                api_response_time=api_response_time,
                status=SystemStatus.ONLINE
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard stats: {str(e)}")

@router.get("/dashboard/activity", response_model=List[ActivityItem])
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=100),
    current_user: AdminUser = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Get recent activity"""
    try:
        # Get real activity data from usage logs
        from ...models.user import UsageLog
        
        # Get recent usage logs
        recent_logs = db.query(UsageLog).order_by(UsageLog.timestamp.desc()).limit(limit).all()
        
        activities = []
        for log in recent_logs:
            # Get user info
            user = db.query(User).filter(User.id == log.user_id).first()
            user_name = user.full_name if user else f"User {log.user_id}"
            
            # Create activity item based on log type
            if log.action_type == 'valuation':
                activities.append(ActivityItem(
                    id=str(log.id),
                    type="report",
                    title="Report Generated",
                    description=f"Valuation report for {log.crane_manufacturer} {log.crane_model}",
                    timestamp=log.timestamp,
                    user_id=str(log.user_id),
                    metadata={
                        "report_type": "valuation",
                        "crane_manufacturer": log.crane_manufacturer,
                        "crane_model": log.crane_model,
                        "crane_capacity": log.crane_capacity,
                        "success": log.success
                    }
                ))
            elif log.action_type == 'login':
                activities.append(ActivityItem(
                    id=str(log.id),
                    type="user",
                    title="User Login",
                    description=f"{user_name} logged in",
                    timestamp=log.timestamp,
                    user_id=str(log.user_id),
                    metadata={"ip_address": log.ip_address, "success": log.success}
                ))
            else:
                activities.append(ActivityItem(
                    id=str(log.id),
                    type="system",
                    title=f"{log.action_type.title()} Action",
                    description=f"{user_name} performed {log.action_type}",
                    timestamp=log.timestamp,
                    user_id=str(log.user_id),
                    metadata={"endpoint": log.endpoint, "success": log.success}
                ))
        
        return activities
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent activity: {str(e)}")

@router.get("/dashboard/status", response_model=SystemStatusInfo)
async def get_system_status(
    current_user: AdminUser = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Get system status"""
    try:
        # Check database connection
        db.query(User).first()
        
        # Mock system status - in real implementation, this would check actual system components
        return SystemStatusInfo(
            uptime=99.9,
            api_response_time=120,
            status=SystemStatus.ONLINE,
            components={
                'database': 'online',
                'api_server': 'online',
                'file_storage': 'online',
                'email_service': 'online'
            }
        )
    except Exception as e:
        return SystemStatusInfo(
            uptime=0.0,
            api_response_time=0,
            status=SystemStatus.OFFLINE,
            components={
                'database': 'offline',
                'api_server': 'online',
                'file_storage': 'unknown',
                'email_service': 'unknown'
            }
        )

# User Management Endpoints
@router.get("/users", response_model=UserListResponse, name="get_main_website_users")
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[str] = Query(None),
    subscription_tier: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    status: Optional[str] = Query(None),  # New status filter: "active", "pending", "suspended"
    search: Optional[str] = Query(None),
    current_user: AdminUser = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """
    Get main website users (regular users, NOT admin users) with filtering and pagination.
    This endpoint returns users from the User model (main website users).
    For admin users, use /admin/admin-users endpoint.
    """
    try:
        # Query the User model (main website users), NOT AdminUser
        # This is critical - we want regular website users, not admin portal users
        # Explicitly import both models to ensure we're using the right one
        from ...models.user import User as UserModel
        from ...models.admin import AdminUser as AdminUserModel
        
        # Verify we're using the correct model
        assert UserModel is not AdminUserModel, "CRITICAL: User and AdminUser models are the same!"
        
        query = db.query(UserModel)
        logger.info(f"Querying User model (main website users), not AdminUser model")
        logger.info(f"User model class: {UserModel}, table name: {UserModel.__tablename__}")
        
        # Apply filters
        if role:
            query = query.filter(User.user_role == role)
        if subscription_tier:
            # Subscription tier removed, but keeping for backward compatibility
            pass
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # Apply status filter (takes precedence over is_active)
        if status:
            if status == "active":
                # Active = is_active=True AND is_verified=True
                query = query.filter(User.is_active == True, User.is_verified == True)
            elif status == "pending":
                # Pending = is_verified=False (regardless of is_active)
                query = query.filter(User.is_verified == False)
            elif status == "suspended":
                # Suspended = is_active=False
                query = query.filter(User.is_active == False)
        
        if search:
            query = query.filter(
                (User.full_name.ilike(f"%{search}%")) |
                (User.email.ilike(f"%{search}%")) |
                (User.username.ilike(f"%{search}%"))
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        users = query.offset(skip).limit(limit).all()
        
        # Log what we're returning for debugging
        logger.info(f"Found {len(users)} regular users (User model), total: {total}")
        if users:
            logger.info(f"Sample user email: {users[0].email}, role: {users[0].user_role}, type: {type(users[0])}")
            # Verify we're using User model, not AdminUser
            from ...models.user import User as UserModel
            from ...models.admin import AdminUser as AdminUserModel
            if isinstance(users[0], AdminUserModel):
                logger.error("ERROR: Query returned AdminUser instead of User! This is a bug!")
            elif isinstance(users[0], UserModel):
                logger.info("✓ Confirmed: Query returned User model (correct)")
        
        # Convert to response models
        user_responses = [
            UserResponse(
                id=str(user.id),
                name=user.full_name or user.username or 'N/A',
                email=user.email,
                role=user.user_role.value if hasattr(user.user_role, 'value') else str(user.user_role),
                is_active=user.is_active,
                is_verified=user.is_verified if hasattr(user, 'is_verified') else False,
                last_login=user.last_login if hasattr(user, 'last_login') else None,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            for user in users
        ]
        
        logger.info(f"Returning {len(user_responses)} users in response")
        if user_responses:
            logger.info(f"First response user: {user_responses[0].email}, role: {user_responses[0].role}")
        
        # Create response object explicitly
        response_obj = UserListResponse(
            users=user_responses,
            total=total,
            skip=skip,
            limit=limit
        )
        
        logger.info(f"Response object type: {type(response_obj)}, users count: {len(response_obj.users)}")
        logger.info(f"Response will be serialized as: users={len(response_obj.users)}, total={response_obj.total}")
        
        return response_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    current_user: AdminUser = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Get specific user by ID"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: AdminUser = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Create new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Create new user
        user = User(
            name=user_data.name,
            email=user_data.email,
            role=user_data.role,
            subscription_tier=user_data.subscription_tier,
            is_active=user_data.is_active
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Convert to response model
        return UserResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            role=user.role,
            subscription_tier=user.subscription_tier,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: AdminUser = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Update user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user fields
        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        # Convert to response model
        return UserResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            role=user.role,
            subscription_tier=user.subscription_tier,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: AdminUser = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Delete user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent deleting super admin users
        if user.role == 'super_admin':
            raise HTTPException(status_code=400, detail="Cannot delete super admin users")
        
        db.delete(user)
        db.commit()
        
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_data: Dict[str, str],
    current_user: AdminUser = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Update user role"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_role = role_data.get('role')
        if new_role not in ['free', 'spot_check', 'professional', 'fleet_valuation', 'admin', 'super_admin']:
            raise HTTPException(status_code=400, detail="Invalid role")
        
        user.role = new_role
        db.commit()
        
        return {"message": "User role updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user role: {str(e)}")

# Reports Management Endpoints
@router.get("/reports", response_model=ReportListResponse)
async def get_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    report_type: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    current_user: AdminUser = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Get reports with filtering and pagination"""
    try:
        # Mock reports data - in real implementation, this would come from a reports table
        reports = [
            {
                "id": "report_001",
                "type": "market_intelligence",
                "user_email": "user@example.com",
                "created_at": datetime.now() - timedelta(hours=1),
                "status": "completed",
                "file_path": "/reports/report_001_market_intelligence.html"
            },
            {
                "id": "report_002",
                "type": "cover_letter",
                "user_email": "admin@example.com",
                "created_at": datetime.now() - timedelta(hours=2),
                "status": "completed",
                "file_path": "/reports/report_002_cover_letter.html"
            }
        ]
        
        # Apply filters
        if report_type:
            reports = [r for r in reports if r['type'] == report_type]
        if user_id:
            reports = [r for r in reports if r['user_email'] == user_id]
        
        # Apply pagination
        total = len(reports)
        paginated_reports = reports[skip:skip + limit]
        
        return ReportListResponse(
            reports=paginated_reports,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reports: {str(e)}")

@router.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    current_user: AdminUser = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Get specific report by ID"""
    try:
        # Mock report data
        report = {
            "id": report_id,
            "type": "market_intelligence",
            "user_email": "user@example.com",
            "created_at": datetime.now() - timedelta(hours=1),
            "status": "completed",
            "file_path": f"/reports/{report_id}_market_intelligence.html"
        }
        
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching report: {str(e)}")

@router.delete("/reports/{report_id}")
async def delete_report(
    report_id: str,
    current_user: AdminUser = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Delete report"""
    try:
        # Mock deletion - in real implementation, this would delete from database and file system
        return {"message": "Report deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting report: {str(e)}")

# System Management Endpoints
@router.get("/settings")
async def get_system_settings(
    current_user: AdminUser = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Get system settings"""
    try:
        # Mock settings - in real implementation, this would come from a settings table
        settings = {
            "site_name": "Crane Intelligence Platform",
            "site_description": "Professional Crane Valuation and Market Analysis Platform",
            "max_users": 1000,
            "max_reports_per_user": 100,
            "email_notifications": True,
            "maintenance_mode": False,
            "api_rate_limit": 1000
        }
        
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching settings: {str(e)}")

@router.put("/settings")
async def update_system_settings(
    settings: Dict[str, Any],
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Update system settings"""
    try:
        # Mock update - in real implementation, this would update a settings table
        return {"message": "Settings updated successfully", "settings": settings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating settings: {str(e)}")

@router.get("/logs")
async def get_system_logs(
    level: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    current_user: AdminUser = Depends(require_admin_access),
    db: Session = Depends(get_db)
):
    """Get system logs"""
    try:
        # Mock logs - in real implementation, this would come from a logs table
        logs = [
            {
                "id": "log_001",
                "level": "INFO",
                "message": "User login successful",
                "timestamp": datetime.now() - timedelta(minutes=5),
                "user_id": "user_123",
                "ip_address": "192.168.1.100"
            },
            {
                "id": "log_002",
                "level": "WARNING",
                "message": "High API usage detected",
                "timestamp": datetime.now() - timedelta(minutes=10),
                "user_id": None,
                "ip_address": None
            }
        ]
        
        return {"logs": logs, "total": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching logs: {str(e)}")

# Health Check
@router.get("/health")
async def admin_health_check():
    """Admin API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }
