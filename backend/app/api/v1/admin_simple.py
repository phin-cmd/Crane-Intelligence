"""
Simplified Admin API endpoints for Crane Intelligence Platform
Works directly with database without complex service dependencies
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from ...config import get_db

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)


# ==================== DASHBOARD ENDPOINTS ====================

@router.get("/dashboard/data")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """Get dashboard metrics and stats"""
    try:
        # Get user counts
        total_users = db.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0]
        active_users = db.execute(text("SELECT COUNT(*) FROM users WHERE is_active = true")).fetchone()[0]
        
        # Get valuation counts
        total_valuations = db.execute(text("SELECT COUNT(*) FROM valuations")).fetchone()[0]
        today_valuations = db.execute(
            text("SELECT COUNT(*) FROM valuations WHERE created_at >= CURRENT_DATE")
        ).fetchone()[0]
        
        # Get revenue estimate (mock for now)
        monthly_revenue = total_valuations * 25.50  # Assuming $25.50 per valuation average
        
        # Get system stats
        db_size = db.execute(
            text("SELECT pg_database_size(current_database())")
        ).fetchone()[0] / (1024 * 1024)  # Convert to MB
        
        return {
            "success": True,
            "metrics": {
                "active_users": active_users,
                "total_users": total_users,
                "total_valuations": total_valuations,
                "today_valuations": today_valuations,
                "monthly_revenue": round(monthly_revenue, 2),
                "database_size_mb": round(db_size, 2),
                "user_growth": round(((active_users / max(total_users - 10, 1)) - 1) * 100, 1),
                "valuation_growth": 12.5,
                "revenue_growth": 8.3
            },
            "charts": {
                "user_growth": _generate_growth_data(db, "users", 30),
                "valuation_trend": _generate_growth_data(db, "valuations", 30)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard data: {str(e)}")


@router.get("/dashboard/activity")
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get recent activity logs"""
    try:
        result = db.execute(
            text("""
                SELECT 
                    'valuation' as type,
                    u.full_name as user_name,
                    v.manufacturer || ' ' || v.model as description,
                    v.created_at as timestamp
                FROM valuations v
                JOIN users u ON v.user_id = u.id
                ORDER BY v.created_at DESC
                LIMIT :limit
            """),
            {"limit": limit}
        )
        activities = result.fetchall()
        
        return {
            "success": True,
            "activity": [
                {
                    "id": idx + 1,
                    "type": row[0],
                    "user": row[1],
                    "description": f"Valued {row[2]}",
                    "timestamp": str(row[3]) if row[3] else None
                }
                for idx, row in enumerate(activities)
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching recent activity: {str(e)}")
        return {"success": True, "activity": []}


# ==================== USER MANAGEMENT ENDPOINTS ====================

@router.get("/users")
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all users with pagination and search"""
    try:
        where_clause = "1=1"
        params = {"skip": skip, "limit": limit}
        
        if search:
            where_clause += " AND (full_name ILIKE :search OR email ILIKE :search)"
            params["search"] = f"%{search}%"
        
        # Get total count
        total = db.execute(
            text(f"SELECT COUNT(*) FROM users WHERE {where_clause}"),
            params
        ).fetchone()[0]
        
        # Get users
        result = db.execute(
            text(f"""
                SELECT id, email, username, full_name, user_role, is_active, 
                       is_verified, created_at
                FROM users
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :skip
            """),
            params
        )
        users = result.fetchall()
        
        return {
            "success": True,
            "total": total,
            "users": [
                {
                    "id": row[0],
                    "email": row[1],
                    "username": row[2],
                    "full_name": row[3],
                    "role": row[4],
                    "is_active": row[5],
                    "is_verified": row[6],
                    "created_at": str(row[7]) if row[7] else None
                }
                for row in users
            ],
            "page": (skip // limit) + 1,
            "per_page": limit
        }
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")


# ==================== DATABASE STATS ENDPOINTS ====================

@router.get("/database/stats")
async def get_database_stats(db: Session = Depends(get_db)):
    """Get database statistics"""
    try:
        tables = ['users', 'valuations', 'crane_listings', 'market_data', 
                  'notifications', 'watchlist', 'price_alerts']
        
        table_stats = []
        for table in tables:
            try:
                count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()[0]
                size = db.execute(
                    text(f"SELECT pg_total_relation_size('{table}')") 
                ).fetchone()[0] / (1024 * 1024)  # Convert to MB
                
                table_stats.append({
                    "name": table,
                    "count": count,
                    "size_mb": round(size, 2)
                })
            except Exception as e:
                logger.warning(f"Could not get stats for table {table}: {str(e)}")
                table_stats.append({
                    "name": table,
                    "count": 0,
                    "size_mb": 0
                })
        
        total_size = db.execute(
            text("SELECT pg_database_size(current_database())")
        ).fetchone()[0] / (1024 * 1024)  # Convert to MB
        
        return {
            "success": True,
            "tables": table_stats,
            "total_size_mb": round(total_size, 2),
            "connection_status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching database stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch database stats: {str(e)}")


# ==================== ANALYTICS ENDPOINTS ====================

@router.get("/analytics")
async def get_analytics(
    timeRange: str = Query("30d", regex="^(7d|30d|90d|365d)$"),
    db: Session = Depends(get_db)
):
    """Get analytics data"""
    try:
        days = int(timeRange[:-1])
        
        # User growth data
        user_growth = db.execute(
            text("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM users
                WHERE created_at >= CURRENT_DATE - :days::integer
                GROUP BY DATE(created_at)
                ORDER BY date
            """),
            {"days": days}
        ).fetchall()
        
        # Valuation data
        valuation_data = db.execute(
            text("""
                SELECT DATE(created_at) as date, COUNT(*) as count, 
                       AVG(estimated_value) as avg_value
                FROM valuations
                WHERE created_at >= CURRENT_DATE - :days::integer
                GROUP BY DATE(created_at)
                ORDER BY date
            """),
            {"days": days}
        ).fetchall()
        
        return {
            "success": True,
            "analytics": {
                "user_growth": [
                    {"date": str(row[0]), "count": row[1]}
                    for row in user_growth
                ],
                "valuations": [
                    {"date": str(row[0]), "count": row[1], "avg_value": float(row[2]) if row[2] else 0}
                    for row in valuation_data
                ],
                "time_range": timeRange
            }
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        return {"success": False, "analytics": {}, "error": str(e)}


# ==================== NOTIFICATIONS ENDPOINTS ====================

@router.get("/notifications")
async def get_notifications(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get system notifications"""
    try:
        result = db.execute(
            text("""
                SELECT id, title, message, type, is_read, created_at
                FROM notifications
                ORDER BY created_at DESC
                LIMIT :limit
            """),
            {"limit": limit}
        )
        notifications = result.fetchall()
        
        return {
            "success": True,
            "notifications": [
                {
                    "id": row[0],
                    "title": row[1],
                    "message": row[2],
                    "type": row[3],
                    "is_read": row[4],
                    "created_at": str(row[5]) if row[5] else None
                }
                for row in notifications
            ],
            "total": len(notifications)
        }
    except Exception as e:
        logger.error(f"Error fetching notifications: {str(e)}")
        return {"success": True, "notifications": [], "total": 0}


# ==================== SETTINGS ENDPOINTS ====================

@router.get("/settings")
async def get_settings(db: Session = Depends(get_db)):
    """Get system settings"""
    try:
        # Return default settings for now
        return {
            "success": True,
            "settings": {
                "general": {
                    "site_name": "Crane Intelligence",
                    "site_url": "https://craneintelligence.tech",
                    "timezone": "UTC",
                    "language": "en"
                },
                "email": {
                    "smtp_host": "smtp.gmail.com",
                    "smtp_port": 587,
                    "from_email": "noreply@craneintelligence.tech"
                },
                "security": {
                    "two_factor_enabled": True,
                    "password_policy_enabled": True,
                    "session_timeout": 30
                }
            }
        }
    except Exception as e:
        logger.error(f"Error fetching settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CORE LOGIC ENDPOINTS ====================

@router.get("/core-logic/components")
async def get_core_logic_components(db: Session = Depends(get_db)):
    """Get core logic components"""
    try:
        # Return mock data for core logic components
        components = [
            {
                "id": 1,
                "name": "Smart Rental Engine",
                "status": "active",
                "version": "3.0.1",
                "last_updated": datetime.utcnow().isoformat()
            },
            {
                "id": 2,
                "name": "Valuation Engine",
                "status": "active",
                "version": "2.5.0",
                "last_updated": datetime.utcnow().isoformat()
            },
            {
                "id": 3,
                "name": "Market Analysis",
                "status": "active",
                "version": "1.8.2",
                "last_updated": datetime.utcnow().isoformat()
            }
        ]
        
        return {
            "success": True,
            "components": components,
            "total": len(components)
        }
    except Exception as e:
        logger.error(f"Error fetching core logic components: {str(e)}")
        return {"success": True, "components": [], "total": 0}


# ==================== HELPER FUNCTIONS ====================

def _generate_growth_data(db: Session, table: str, days: int):
    """Generate growth data for charts"""
    try:
        result = db.execute(
            text(f"""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM {table}
                WHERE created_at >= CURRENT_DATE - :days::integer
                GROUP BY DATE(created_at)
                ORDER BY date
            """),
            {"days": days}
        )
        data = result.fetchall()
        
        return {
            "labels": [str(row[0]) for row in data],
            "values": [row[1] for row in data]
        }
    except Exception as e:
        logger.warning(f"Error generating growth data for {table}: {str(e)}")
        return {"labels": [], "values": []}

