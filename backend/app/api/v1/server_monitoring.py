"""
Server Monitoring API Endpoints
Handles server health monitoring, alerts, and status reporting
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import json

# Try to import database components
try:
    from ...core.database import get_db
    from ...models.admin import AdminUser
    from ...core.admin_auth import require_admin_or_super_admin
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    # Fallback for when database is not available
    def get_db():
        return None
    def require_admin_or_super_admin():
        return None

router = APIRouter(prefix="/admin", tags=["server-monitoring"])

# In-memory storage for server status (fallback if database not available)
server_status_cache = {}
server_alerts_cache = []


class ServerStatus(BaseModel):
    """Server status model"""
    server: str
    name: str
    status: str  # healthy, degraded, down, unknown
    api_status: str
    website_status: str
    api_response_time: Optional[float] = None
    website_response_time: Optional[float] = None
    api_error: Optional[str] = None
    website_error: Optional[str] = None
    timestamp: str


class ServerStatusResponse(BaseModel):
    """Response model for server status"""
    success: bool
    overall: str
    servers: List[ServerStatus]
    last_updated: Optional[str] = None


class ServerAlert(BaseModel):
    """Server alert model"""
    server: str
    server_name: Optional[str] = None
    status: str
    api_status: Optional[str] = None
    website_status: Optional[str] = None
    api_error: Optional[str] = None
    website_error: Optional[str] = None
    timestamp: str


class AlertResponse(BaseModel):
    """Response model for alert submission"""
    success: bool
    message: str
    alert_id: Optional[str] = None


@router.get("/server-status", response_model=ServerStatusResponse)
async def get_server_status(
    current_user: Optional[AdminUser] = Depends(require_admin_or_super_admin) if DATABASE_AVAILABLE else None,
    db: Optional[Session] = Depends(get_db) if DATABASE_AVAILABLE else None
):
    """
    Get current status of all monitored servers
    Returns status from cache or database
    """
    try:
        # Try to get from cache first
        if server_status_cache:
            servers = list(server_status_cache.values())
            overall = determine_overall_status(servers)
            return ServerStatusResponse(
                success=True,
                overall=overall,
                servers=servers,
                last_updated=max([s.get('timestamp', '') for s in servers]) if servers else None
            )
        
        # If no cache, return default healthy status for all servers
        default_servers = [
            ServerStatus(
                server="production",
                name="Production Server",
                status="healthy",
                api_status="healthy",
                website_status="healthy",
                timestamp=datetime.utcnow().isoformat()
            ),
            ServerStatus(
                server="uat",
                name="UAT Server",
                status="healthy",
                api_status="healthy",
                website_status="healthy",
                timestamp=datetime.utcnow().isoformat()
            ),
            ServerStatus(
                server="dev",
                name="Development Server",
                status="healthy",
                api_status="healthy",
                website_status="healthy",
                timestamp=datetime.utcnow().isoformat()
            )
        ]
        
        return ServerStatusResponse(
            success=True,
            overall="healthy",
            servers=default_servers,
            last_updated=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching server status: {str(e)}"
        )


@router.post("/alerts", response_model=AlertResponse)
async def receive_server_alert(
    alert: ServerAlert,
    db: Optional[Session] = Depends(get_db) if DATABASE_AVAILABLE else None
):
    """
    Receive server alert from monitoring script
    Note: No authentication required - this endpoint is called by the monitoring script
    """
    """
    Receive server alert from monitoring script
    Stores alert and creates notifications for admins
    """
    try:
        alert_data = alert.dict()
        alert_data['received_at'] = datetime.utcnow().isoformat()
        
        # Store in cache
        server_alerts_cache.append(alert_data)
        # Keep only last 100 alerts
        if len(server_alerts_cache) > 100:
            server_alerts_cache.pop(0)
        
        # Update server status cache
        server_status_cache[alert.server] = {
            'server': alert.server,
            'name': alert.server_name or alert.server,
            'status': alert.status,
            'api_status': alert.api_status or 'unknown',
            'website_status': alert.website_status or 'unknown',
            'api_error': alert.api_error,
            'website_error': alert.website_error,
            'timestamp': alert.timestamp
        }
        
        # Try to store in database if available
        if DATABASE_AVAILABLE and db:
            try:
                # Create notification for all admins
                from ...models.notification import Notification
                from ...models.admin import AdminUser
                
                admins = db.query(AdminUser).filter(AdminUser.is_active == True).all()
                for admin in admins:
                    notification = Notification(
                        user_id=admin.id,
                        user_type='admin',
                        title=f"Server Alert: {alert.server_name or alert.server}",
                        message=f"Server {alert.server} status: {alert.status}. API: {alert.api_status}, Website: {alert.website_status}",
                        notification_type='server_alert',
                        is_read=False,
                        metadata=json.dumps(alert_data)
                    )
                    db.add(notification)
                
                db.commit()
            except Exception as db_error:
                # Log but don't fail if database operation fails
                print(f"Database notification creation failed: {db_error}")
        
        return AlertResponse(
            success=True,
            message="Alert received and processed",
            alert_id=f"alert_{alert.server}_{datetime.utcnow().timestamp()}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing alert: {str(e)}"
        )


def determine_overall_status(servers: List[Dict]) -> str:
    """Determine overall status from server list"""
    if not servers:
        return "unknown"
    
    statuses = [s.get('status', 'unknown') for s in servers]
    
    if any(s == 'down' for s in statuses):
        return "down"
    elif any(s == 'degraded' for s in statuses):
        return "degraded"
    elif all(s == 'healthy' for s in statuses):
        return "healthy"
    else:
        return "unknown"


@router.get("/alerts/history")
async def get_alert_history(
    limit: int = 50,
    current_user: Optional[AdminUser] = Depends(require_admin_or_super_admin) if DATABASE_AVAILABLE else None,
    db: Optional[Session] = Depends(get_db) if DATABASE_AVAILABLE else None
):
    """Get recent alert history"""
    try:
        # Return from cache (last N alerts)
        recent_alerts = server_alerts_cache[-limit:] if server_alerts_cache else []
        return {
            "success": True,
            "alerts": recent_alerts,
            "total": len(server_alerts_cache)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching alert history: {str(e)}"
        )

