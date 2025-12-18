"""
Audit Log API endpoints for Admin Panel
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from ...core.database import get_db
from ...models.admin import AdminUser, AuditLog
from ...core.admin_auth import get_current_admin_user, require_admin_or_super_admin
from ...services.audit_service import AuditService

router = APIRouter(prefix="/admin/audit", tags=["admin-audit"])


class AuditLogResponse(BaseModel):
    """Response model for audit log"""
    id: int
    timestamp: datetime
    admin_user_id: int
    admin_email: Optional[str]
    admin_name: Optional[str]
    action: str
    resource_type: str
    resource_id: str
    description: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Response model for audit log list"""
    logs: List[AuditLogResponse]
    total: int
    limit: int
    offset: int


class AuditLogStatsResponse(BaseModel):
    """Response model for audit log statistics"""
    total_logs: int
    logs_by_action: Dict[str, int]
    logs_by_resource_type: Dict[str, int]
    logs_by_admin: Dict[str, int]
    recent_activity: List[AuditLogResponse]


@router.get("", response_model=AuditLogListResponse)
async def get_audit_logs(
    admin_user_id: Optional[int] = Query(None, description="Filter by admin user ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Get audit logs with filters"""
    logs = AuditService.get_audit_logs(
        db=db,
        admin_user_id=admin_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    
    total = AuditService.get_audit_log_count(
        db=db,
        admin_user_id=admin_user_id,
        action=action,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date
    )
    
    log_responses = [
        AuditLogResponse(
            id=log.id,
            timestamp=log.timestamp,
            admin_user_id=log.admin_user_id,
            admin_email=log.admin_user.email if log.admin_user else None,
            admin_name=log.admin_user.full_name if log.admin_user else None,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            description=log.description,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            old_values=log.old_values,
            new_values=log.new_values
        )
        for log in logs
    ]
    
    return AuditLogListResponse(
        logs=log_responses,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: int,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Get a specific audit log by ID"""
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    
    return AuditLogResponse(
        id=log.id,
        timestamp=log.timestamp,
        admin_user_id=log.admin_user_id,
        admin_email=log.admin_user.email if log.admin_user else None,
        admin_name=log.admin_user.full_name if log.admin_user else None,
        action=log.action,
        resource_type=log.resource_type,
        resource_id=log.resource_id,
        description=log.description,
        ip_address=log.ip_address,
        user_agent=log.user_agent,
        old_values=log.old_values,
        new_values=log.new_values
    )


@router.get("/stats/summary", response_model=AuditLogStatsResponse)
async def get_audit_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Get audit log statistics"""
    from datetime import timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get all logs in the period
    all_logs = AuditService.get_audit_logs(
        db=db,
        start_date=start_date,
        limit=10000
    )
    
    # Calculate statistics
    total_logs = len(all_logs)
    logs_by_action = {}
    logs_by_resource_type = {}
    logs_by_admin = {}
    
    for log in all_logs:
        # By action
        logs_by_action[log.action] = logs_by_action.get(log.action, 0) + 1
        
        # By resource type
        logs_by_resource_type[log.resource_type] = logs_by_resource_type.get(log.resource_type, 0) + 1
        
        # By admin
        admin_name = log.admin_user.full_name if log.admin_user else f"User {log.admin_user_id}"
        logs_by_admin[admin_name] = logs_by_admin.get(admin_name, 0) + 1
    
    # Get recent activity (last 20)
    recent_logs = AuditService.get_audit_logs(db=db, limit=20)
    recent_activity = [
        AuditLogResponse(
            id=log.id,
            timestamp=log.timestamp,
            admin_user_id=log.admin_user_id,
            admin_email=log.admin_user.email if log.admin_user else None,
            admin_name=log.admin_user.full_name if log.admin_user else None,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            description=log.description,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            old_values=log.old_values,
            new_values=log.new_values
        )
        for log in recent_logs
    ]
    
    return AuditLogStatsResponse(
        total_logs=total_logs,
        logs_by_action=logs_by_action,
        logs_by_resource_type=logs_by_resource_type,
        logs_by_admin=logs_by_admin,
        recent_activity=recent_activity
    )


@router.get("/export/csv")
async def export_audit_logs_csv(
    admin_user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Export audit logs as CSV"""
    import csv
    from io import StringIO
    from fastapi.responses import Response
    
    logs = AuditService.export_audit_logs(
        db=db,
        admin_user_id=admin_user_id,
        action=action,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date
    )
    
    # Create CSV
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "id", "timestamp", "admin_user_id", "admin_email", "action",
        "resource_type", "resource_id", "description", "ip_address", "user_agent"
    ])
    writer.writeheader()
    
    for log in logs:
        writer.writerow({
            "id": log["id"],
            "timestamp": log["timestamp"],
            "admin_user_id": log["admin_user_id"],
            "admin_email": log["admin_email"],
            "action": log["action"],
            "resource_type": log["resource_type"],
            "resource_id": log["resource_id"],
            "description": log["description"],
            "ip_address": log["ip_address"],
            "user_agent": log["user_agent"]
        })
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"}
    )


@router.get("/export/json")
async def export_audit_logs_json(
    admin_user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Export audit logs as JSON"""
    from fastapi.responses import JSONResponse
    
    logs = AuditService.export_audit_logs(
        db=db,
        admin_user_id=admin_user_id,
        action=action,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date
    )
    
    return JSONResponse(content=logs)

