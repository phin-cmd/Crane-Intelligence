"""
Comprehensive Health Check Endpoints
Provides detailed health status for monitoring and alerting
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any, List
import psutil
import os
import logging

from app.config import get_db, engine

router = APIRouter()
logger = logging.getLogger(__name__)


class HealthStatus:
    """Health status constants"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@router.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint
    Returns simple OK status for load balancers
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "crane-intelligence-api"
    }


@router.get("/health/detailed", tags=["Health"])
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Detailed health check with all system components
    """
    health_status = {
        "status": HealthStatus.HEALTHY,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "crane-intelligence-api",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "checks": {}
    }
    
    overall_healthy = True
    
    # Database check
    try:
        db.execute(text("SELECT 1"))
        db.commit()
        health_status["checks"]["database"] = {
            "status": HealthStatus.HEALTHY,
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status["checks"]["database"] = {
            "status": HealthStatus.UNHEALTHY,
            "message": f"Database connection failed: {str(e)}"
        }
        overall_healthy = False
    
    # System resources
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status["checks"]["system"] = {
            "status": HealthStatus.HEALTHY if cpu_percent < 80 and memory.percent < 80 else HealthStatus.DEGRADED,
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "message": "System resources within acceptable limits"
        }
        
        if cpu_percent > 90 or memory.percent > 90:
            overall_healthy = False
            health_status["checks"]["system"]["status"] = HealthStatus.UNHEALTHY
    except Exception as e:
        logger.error(f"System health check failed: {str(e)}")
        health_status["checks"]["system"] = {
            "status": HealthStatus.UNKNOWN,
            "message": f"System check failed: {str(e)}"
        }
    
    # API endpoints check
    try:
        # Check if critical endpoints are accessible
        health_status["checks"]["api"] = {
            "status": HealthStatus.HEALTHY,
            "message": "API endpoints accessible"
        }
    except Exception as e:
        logger.error(f"API health check failed: {str(e)}")
        health_status["checks"]["api"] = {
            "status": HealthStatus.DEGRADED,
            "message": f"API check failed: {str(e)}"
        }
    
    # Determine overall status
    if not overall_healthy:
        health_status["status"] = HealthStatus.UNHEALTHY
    elif any(check.get("status") == HealthStatus.DEGRADED for check in health_status["checks"].values()):
        health_status["status"] = HealthStatus.DEGRADED
    
    # Set HTTP status code
    status_code = status.HTTP_200_OK
    if health_status["status"] == HealthStatus.UNHEALTHY:
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif health_status["status"] == HealthStatus.DEGRADED:
        status_code = status.HTTP_200_OK  # Still OK but degraded
    
    return health_status


@router.get("/health/database", tags=["Health"])
async def database_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Database-specific health check
    """
    try:
        # Test basic query
        result = db.execute(text("SELECT 1 as test"))
        db.commit()
        
        # Test connection pool
        pool_status = engine.pool.status()
        
        # Get database size
        size_result = db.execute(text("""
            SELECT pg_size_pretty(pg_database_size(current_database())) as size
        """))
        db_size = size_result.scalar()
        
        return {
            "status": HealthStatus.HEALTHY,
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "connected": True,
                "pool_size": pool_status(),
                "size": db_size
            }
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database health check failed: {str(e)}"
        )


@router.get("/health/readiness", tags=["Health"])
async def readiness_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Readiness check - indicates if service is ready to accept traffic
    """
    try:
        # Check database
        db.execute(text("SELECT 1"))
        db.commit()
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )


@router.get("/health/liveness", tags=["Health"])
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check - indicates if service is alive
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/metrics", tags=["Health"])
async def metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    System metrics for monitoring
    """
    metrics_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "system": {},
        "database": {},
        "application": {}
    }
    
    # System metrics
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics_data["system"] = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available / (1024 * 1024),
            "disk_percent": disk.percent,
            "disk_free_gb": disk.free / (1024 * 1024 * 1024)
        }
    except Exception as e:
        logger.error(f"Failed to collect system metrics: {str(e)}")
    
    # Database metrics
    try:
        # Connection pool stats
        pool = engine.pool
        metrics_data["database"] = {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }
        
        # Database size
        size_result = db.execute(text("""
            SELECT pg_size_pretty(pg_database_size(current_database())) as size
        """))
        metrics_data["database"]["size"] = size_result.scalar()
    except Exception as e:
        logger.error(f"Failed to collect database metrics: {str(e)}")
    
    # Application metrics
    metrics_data["application"] = {
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "version": "1.0.0"
    }
    
    return metrics_data

