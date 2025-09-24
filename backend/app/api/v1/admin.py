"""
Admin API endpoints for Crane Intelligence Platform
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ...core.database import get_db
from ...services.auth_service import get_current_user
from ...models.user import User, UserRole
from ...models.crane import Crane
# from ...models.enhanced_crane import CraneListing, DataRefreshLog  # Tables don't exist yet
from ...schemas.admin import (
    DashboardStats, UserStats, ReportStats, SystemStatusInfo, SystemStatus,
    UserListResponse, UserUpdate, UserCreate, UserResponse,
    ReportListResponse, ReportResponse,
    ActivityItem
)

router = APIRouter(prefix="/admin", tags=["admin"])

# Role-based access control
def require_admin_role(current_user: dict = Depends(get_current_user)):
    """Require admin or super admin role"""
    if current_user.get('role') not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return current_user

def require_super_admin_role(current_user: dict = Depends(get_current_user)):
    """Require super admin role"""
    if current_user.get('role') != 'super_admin':
        raise HTTPException(status_code=403, detail="Super admin access required")
    return current_user

# Dashboard Endpoints
@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: dict = Depends(require_admin_role),
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
        
        # Get subscription statistics
        basic_users = db.query(User).filter(User.subscription_tier == 'basic').count()
        pro_users = db.query(User).filter(User.subscription_tier == 'pro').count()
        enterprise_users = db.query(User).filter(User.subscription_tier == 'enterprise').count()
        
        # Get report statistics from usage logs
        from ...models.user import UsageLog
        total_reports = db.query(UsageLog).filter(UsageLog.action_type == 'valuation').count()
        reports_today = db.query(UsageLog).filter(
            UsageLog.action_type == 'valuation',
            UsageLog.timestamp >= datetime.now().date()
        ).count()
        reports_this_month = db.query(UsageLog).filter(
            UsageLog.action_type == 'valuation',
            UsageLog.timestamp >= datetime.now().replace(day=1).date()
        ).count()
        
        # Get revenue statistics from subscription plans and users
        from ...models.user import SubscriptionPlan
        basic_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == 'basic').first()
        pro_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == 'pro').first()
        enterprise_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == 'enterprise').first()
        
        # Calculate revenue based on active subscriptions
        basic_revenue = basic_users * (basic_plan.monthly_price if basic_plan else 0)
        pro_revenue = pro_users * (pro_plan.monthly_price if pro_plan else 0)
        enterprise_revenue = enterprise_users * (enterprise_plan.monthly_price if enterprise_plan else 0)
        
        total_revenue = basic_revenue + pro_revenue + enterprise_revenue
        revenue_today = total_revenue / 30  # Approximate daily revenue
        revenue_this_month = total_revenue
        
        # Get system status
        system_uptime = 99.9
        api_response_time = 120  # milliseconds
        
        return DashboardStats(
            users=UserStats(
                total=total_users,
                active=active_users,
                new_today=new_users_today,
                by_tier={
                    'basic': basic_users,
                    'pro': pro_users,
                    'enterprise': enterprise_users
                }
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
    current_user: dict = Depends(require_admin_role),
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
    current_user: dict = Depends(require_admin_role),
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
@router.get("/users", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[str] = Query(None),
    subscription_tier: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: dict = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Get users with filtering and pagination"""
    try:
        query = db.query(User)
        
        # Apply filters
        if role:
            query = query.filter(User.role == role)
        if subscription_tier:
            query = query.filter(User.subscription_tier == subscription_tier)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if search:
            query = query.filter(
                (User.name.ilike(f"%{search}%")) |
                (User.email.ilike(f"%{search}%"))
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        users = query.offset(skip).limit(limit).all()
        
        # Convert to response models
        user_responses = [
            UserResponse(
                id=str(user.id),
                name=user.name,
                email=user.email,
                role=user.role,
                subscription_tier=user.subscription_tier,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            for user in users
        ]
        
        return UserListResponse(
            users=user_responses,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    current_user: dict = Depends(require_admin_role),
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
    current_user: dict = Depends(require_admin_role),
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
    current_user: dict = Depends(require_admin_role),
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
    current_user: dict = Depends(require_admin_role),
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
    current_user: dict = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Update user role"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_role = role_data.get('role')
        if new_role not in ['basic', 'pro', 'enterprise', 'admin', 'super_admin']:
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
    current_user: dict = Depends(require_admin_role),
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
    current_user: dict = Depends(require_admin_role),
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
    current_user: dict = Depends(require_admin_role),
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
    current_user: dict = Depends(require_admin_role),
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
    current_user: dict = Depends(require_super_admin_role),
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
    current_user: dict = Depends(require_admin_role),
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
