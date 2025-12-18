"""
System Health Monitoring API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import psutil
import os

from ...core.database import get_db, engine
from ...models.admin import AdminUser
from ...core.admin_auth import require_admin_or_super_admin

router = APIRouter(prefix="/admin/system", tags=["admin-system-health"])


class SystemHealthResponse(BaseModel):
    """System health status"""
    status: str  # healthy, degraded, down
    timestamp: datetime
    api_status: Dict[str, Any]
    database_status: Dict[str, Any]
    server_resources: Dict[str, Any]
    uptime: float
    version: str


class PerformanceMetricsResponse(BaseModel):
    """Performance metrics"""
    response_times: Dict[str, float]
    error_rates: Dict[str, float]
    request_counts: Dict[str, int]
    database_query_times: Dict[str, float]


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Get overall system health status"""
    health_status = "healthy"
    issues = []
    
    # Check database
    db_status = {"status": "healthy", "response_time_ms": 0}
    try:
        start = datetime.utcnow()
        db.execute(text("SELECT 1"))
        response_time = (datetime.utcnow() - start).total_seconds() * 1000
        db_status["response_time_ms"] = round(response_time, 2)
        if response_time > 1000:
            db_status["status"] = "degraded"
            issues.append("Database response time is high")
    except Exception as e:
        db_status["status"] = "down"
        db_status["error"] = str(e)
        health_status = "down"
        issues.append(f"Database error: {str(e)}")
    
    # Check API status
    api_status = {"status": "healthy", "endpoints": []}
    # In a real implementation, you'd check actual API endpoints
    
    # Check server resources
    server_resources = {}
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        server_resources = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2)
        }
        
        if cpu_percent > 90:
            issues.append("High CPU usage")
            health_status = "degraded"
        if memory.percent > 90:
            issues.append("High memory usage")
            health_status = "degraded"
        if disk.percent > 90:
            issues.append("Low disk space")
            health_status = "degraded"
    except Exception as e:
        server_resources = {"error": str(e)}
    
    # Calculate uptime (simplified - in production, track from server start)
    uptime_seconds = 0
    try:
        import time
        # This is a placeholder - in production, track actual server start time
        uptime_seconds = time.time()  # Placeholder
    except:
        pass
    
    return SystemHealthResponse(
        status=health_status,
        timestamp=datetime.utcnow(),
        api_status=api_status,
        database_status=db_status,
        server_resources=server_resources,
        uptime=uptime_seconds,
        version="1.0.0"
    )


@router.get("/database/status")
async def get_database_status(
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Get detailed database status"""
    try:
        # Test connection
        start = datetime.utcnow()
        db.execute(text("SELECT 1"))
        response_time = (datetime.utcnow() - start).total_seconds() * 1000
        
        # Get connection pool info
        pool = engine.pool
        pool_status = {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }
        
        # Get database size (PostgreSQL specific)
        db_size = None
        try:
            result = db.execute(text("SELECT pg_database_size(current_database())"))
            db_size_bytes = result.scalar()
            db_size = round(db_size_bytes / (1024**3), 2)  # Convert to GB
        except:
            pass
        
        return {
            "status": "healthy",
            "response_time_ms": round(response_time, 2),
            "connection_pool": pool_status,
            "database_size_gb": db_size,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/performance/metrics", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Get performance metrics"""
    # In a real implementation, you'd track these metrics over time
    # This is a placeholder structure
    
    return PerformanceMetricsResponse(
        response_times={
            "average": 150.0,
            "p95": 300.0,
            "p99": 500.0
        },
        error_rates={
            "total": 0.01,
            "4xx": 0.005,
            "5xx": 0.001
        },
        request_counts={
            "total": 1000,
            "last_hour": 100,
            "last_day": 5000
        },
        database_query_times={
            "average": 50.0,
            "slowest": 200.0
        }
    )


@router.get("/errors/recent")
async def get_recent_errors(
    limit: int = 50,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Get recent system errors"""
    from ...models.admin import SystemLog
    
    errors = db.query(SystemLog).filter(
        SystemLog.level.in_(["error", "critical"])
    ).order_by(SystemLog.timestamp.desc()).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "level": log.level,
            "message": log.message,
            "module": log.module,
            "timestamp": log.timestamp.isoformat(),
            "user_id": log.user_id,
            "ip_address": log.ip_address
        }
        for log in errors
    ]

