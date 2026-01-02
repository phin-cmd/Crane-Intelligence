"""
Visitor Tracking API Endpoints
Tracks website visitors, demographics, and behavior analytics
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from sqlalchemy.sql import case
import logging
import json
import hashlib
import uuid

from ...core.database import get_db
from ...models.visitor_tracking import VisitorTracking
from ...api.v1.admin_auth import get_current_admin_user, AdminUser
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/visitor-tracking", tags=["Visitor Tracking"])


# Request Models
class TrackVisitorRequest(BaseModel):
    page_url: str
    page_title: Optional[str] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class UpdateVisitorRequest(BaseModel):
    time_on_page: Optional[int] = None
    scroll_depth: Optional[int] = None
    exit_page: Optional[bool] = False


# Helper Functions
def parse_user_agent(user_agent: str) -> Dict[str, Optional[str]]:
    """Parse user agent string to extract browser, OS, device info"""
    result = {
        'browser': None,
        'browser_version': None,
        'os': None,
        'os_version': None,
        'device_type': None,
        'device_brand': None,
        'device_model': None
    }
    
    if not user_agent:
        return result
    
    user_agent_lower = user_agent.lower()
    
    # Detect browser
    if 'chrome' in user_agent_lower and 'edg' not in user_agent_lower:
        result['browser'] = 'Chrome'
        try:
            chrome_idx = user_agent_lower.find('chrome/')
            if chrome_idx != -1:
                version = user_agent[chrome_idx + 7:].split()[0].split('.')[0]
                result['browser_version'] = version
        except:
            pass
    elif 'firefox' in user_agent_lower:
        result['browser'] = 'Firefox'
        try:
            ff_idx = user_agent_lower.find('firefox/')
            if ff_idx != -1:
                version = user_agent[ff_idx + 8:].split()[0]
                result['browser_version'] = version
        except:
            pass
    elif 'safari' in user_agent_lower and 'chrome' not in user_agent_lower:
        result['browser'] = 'Safari'
    elif 'edg' in user_agent_lower:
        result['browser'] = 'Edge'
    elif 'opera' in user_agent_lower or 'opr' in user_agent_lower:
        result['browser'] = 'Opera'
    
    # Detect OS
    if 'windows' in user_agent_lower:
        result['os'] = 'Windows'
        if 'windows nt 10' in user_agent_lower:
            result['os_version'] = '10'
        elif 'windows nt 6.3' in user_agent_lower:
            result['os_version'] = '8.1'
        elif 'windows nt 6.2' in user_agent_lower:
            result['os_version'] = '8'
        elif 'windows nt 6.1' in user_agent_lower:
            result['os_version'] = '7'
    elif 'mac os x' in user_agent_lower or 'macintosh' in user_agent_lower:
        result['os'] = 'macOS'
        try:
            mac_idx = user_agent_lower.find('mac os x ')
            if mac_idx != -1:
                version = user_agent[mac_idx + 9:].split('_')[0]
                result['os_version'] = version.replace('_', '.')
        except:
            pass
    elif 'iphone' in user_agent_lower:
        result['os'] = 'iOS'
        result['device_type'] = 'mobile'
        result['device_brand'] = 'Apple'
        result['device_model'] = 'iPhone'
    elif 'ipad' in user_agent_lower:
        result['os'] = 'iOS'
        result['device_type'] = 'tablet'
        result['device_brand'] = 'Apple'
        result['device_model'] = 'iPad'
    elif 'android' in user_agent_lower:
        result['os'] = 'Android'
        try:
            android_idx = user_agent_lower.find('android ')
            if android_idx != -1:
                version = user_agent[android_idx + 8:].split(';')[0].strip()
                result['os_version'] = version
        except:
            pass
        
        # Detect Android device
        if 'mobile' in user_agent_lower:
            result['device_type'] = 'mobile'
        else:
            result['device_type'] = 'tablet'
        
        # Try to detect brand/model
        if 'samsung' in user_agent_lower:
            result['device_brand'] = 'Samsung'
        elif 'xiaomi' in user_agent_lower:
            result['device_brand'] = 'Xiaomi'
        elif 'huawei' in user_agent_lower:
            result['device_brand'] = 'Huawei'
    elif 'linux' in user_agent_lower:
        result['os'] = 'Linux'
    
    # Detect device type if not already set
    if not result['device_type']:
        if 'mobile' in user_agent_lower or 'iphone' in user_agent_lower or 'android' in user_agent_lower:
            result['device_type'] = 'mobile'
        elif 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
            result['device_type'] = 'tablet'
        else:
            result['device_type'] = 'desktop'
    
    return result


def get_visitor_id(request: Request) -> str:
    """Get or create visitor ID from cookie"""
    visitor_id = request.cookies.get('visitor_id')
    if not visitor_id:
        visitor_id = str(uuid.uuid4())
    return visitor_id


def get_session_id(request: Request) -> str:
    """Get or create session ID"""
    session_id = request.cookies.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    # Check for forwarded IP (from proxy/load balancer)
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    if request.client:
        return request.client.host
    
    return 'unknown'


def parse_referrer(referrer: Optional[str]) -> Dict[str, Optional[str]]:
    """Parse referrer to extract domain and traffic source"""
    result = {
        'referrer_domain': None,
        'traffic_source': 'direct',
        'source': None,
        'medium': None
    }
    
    if not referrer:
        return result
    
    try:
        from urllib.parse import urlparse
        parsed = urlparse(referrer)
        domain = parsed.netloc
        
        if domain:
            result['referrer_domain'] = domain
            
            # Determine traffic source
            if 'google' in domain.lower():
                result['traffic_source'] = 'organic'
                result['source'] = 'google'
                result['medium'] = 'organic'
            elif 'bing' in domain.lower() or 'yahoo' in domain.lower():
                result['traffic_source'] = 'organic'
                result['source'] = domain.split('.')[0]
                result['medium'] = 'organic'
            elif 'facebook' in domain.lower() or 'twitter' in domain.lower() or 'linkedin' in domain.lower() or 'instagram' in domain.lower():
                result['traffic_source'] = 'social'
                result['source'] = domain.split('.')[0]
                result['medium'] = 'social'
            elif 'mail' in domain.lower() or 'email' in domain.lower():
                result['traffic_source'] = 'email'
                result['source'] = domain
                result['medium'] = 'email'
            else:
                result['traffic_source'] = 'referral'
                result['source'] = domain
                result['medium'] = 'referral'
    except:
        pass
    
    return result


# Public Endpoints (No auth required for tracking)
@router.post("/track")
async def track_visitor(
    request: TrackVisitorRequest,
    http_request: Request,
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Track a visitor page view (public endpoint - no auth required)
    Only available in production environment
    """
    # Check if tracking is enabled (production only)
    environment = os.getenv("ENVIRONMENT", "prod").lower()
    if environment not in ["prod", "production"]:
        # Silently return success in dev/uat to avoid frontend errors
        return {
            "success": True,
            "message": "Tracking disabled in non-production environment",
            "tracked": False
        }
    
    try:
        visitor_id = get_visitor_id(http_request)
        session_id = get_session_id(http_request)
        ip_address = get_client_ip(http_request)
        
        # Parse user agent
        ua_info = parse_user_agent(request.user_agent or http_request.headers.get('user-agent', ''))
        
        # Parse referrer
        ref_info = parse_referrer(request.referrer)
        
        # Determine device flags
        device_type = ua_info.get('device_type', 'desktop')
        is_mobile = device_type == 'mobile'
        is_tablet = device_type == 'tablet'
        is_desktop = device_type == 'desktop'
        
        # Create visitor tracking record
        visitor = VisitorTracking(
            visitor_id=visitor_id,
            session_id=session_id,
            user_id=user_id,
            page_url=request.page_url,
            page_title=request.page_title,
            referrer=request.referrer,
            referrer_domain=ref_info.get('referrer_domain'),
            user_agent=request.user_agent or http_request.headers.get('user-agent'),
            browser=ua_info.get('browser'),
            browser_version=ua_info.get('browser_version'),
            device_type=device_type,
            device_brand=ua_info.get('device_brand'),
            device_model=ua_info.get('device_model'),
            os=ua_info.get('os'),
            os_version=ua_info.get('os_version'),
            screen_width=request.screen_width,
            screen_height=request.screen_height,
            screen_resolution=f"{request.screen_width}x{request.screen_height}" if request.screen_width and request.screen_height else None,
            ip_address=ip_address,
            language=request.language or http_request.headers.get('accept-language', '').split(',')[0].split(';')[0].strip(),
            timezone=request.timezone,
            traffic_source=ref_info.get('traffic_source'),
            source=ref_info.get('source'),
            medium=ref_info.get('medium'),
            is_mobile=is_mobile,
            is_tablet=is_tablet,
            is_desktop=is_desktop,
            additional_metadata=json.dumps(request.metadata) if request.metadata else None
        )
        
        db.add(visitor)
        db.commit()
        db.refresh(visitor)
        
        # Return response with cookies
        from fastapi.responses import JSONResponse
        response = JSONResponse({
            "success": True,
            "visitor_id": visitor_id,
            "session_id": session_id,
            "tracking_id": visitor.id
        })
        
        # Set cookies
        response.set_cookie(
            key="visitor_id",
            value=visitor_id,
            max_age=31536000,  # 1 year
            httponly=False,
            samesite="Lax"
        )
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=1800,  # 30 minutes
            httponly=False,
            samesite="Lax"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error tracking visitor: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to track visitor: {str(e)}")


@router.put("/update/{tracking_id}")
async def update_visitor(
    tracking_id: int,
    request: UpdateVisitorRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Update visitor tracking data (e.g., time on page, scroll depth)
    """
    try:
        visitor = db.query(VisitorTracking).filter(VisitorTracking.id == tracking_id).first()
        
        if not visitor:
            raise HTTPException(status_code=404, detail="Tracking record not found")
        
        if request.time_on_page is not None:
            visitor.time_on_page = request.time_on_page
        if request.scroll_depth is not None:
            visitor.scroll_depth = request.scroll_depth
        if request.exit_page is not None:
            visitor.exit_page = request.exit_page
        
        db.commit()
        
        return {"success": True, "message": "Visitor tracking updated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating visitor: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update visitor: {str(e)}")


# Admin Endpoints (Auth required)
@router.get("/stats", dependencies=[Depends(get_current_admin_user)])
async def get_visitor_stats(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get visitor statistics (admin only)
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Total visitors
        total_visitors = db.query(func.count(func.distinct(VisitorTracking.visitor_id))).filter(
            and_(
                VisitorTracking.visited_at >= start_date,
                VisitorTracking.visited_at <= end_date,
                VisitorTracking.is_bot == False
            )
        ).scalar() or 0
        
        # Total page views
        total_page_views = db.query(func.count(VisitorTracking.id)).filter(
            and_(
                VisitorTracking.visited_at >= start_date,
                VisitorTracking.visited_at <= end_date,
                VisitorTracking.is_bot == False
            )
        ).scalar() or 0
        
        # Unique sessions
        unique_sessions = db.query(func.count(func.distinct(VisitorTracking.session_id))).filter(
            and_(
                VisitorTracking.visited_at >= start_date,
                VisitorTracking.visited_at <= end_date,
                VisitorTracking.is_bot == False
            )
        ).scalar() or 0
        
        # Average time on page
        avg_time = db.query(func.avg(VisitorTracking.time_on_page)).filter(
            and_(
                VisitorTracking.visited_at >= start_date,
                VisitorTracking.visited_at <= end_date,
                VisitorTracking.is_bot == False,
                VisitorTracking.time_on_page.isnot(None)
            )
        ).scalar()
        avg_time_on_page = int(avg_time) if avg_time else 0
        
        # Bounce rate
        total_sessions = unique_sessions
        bounced_sessions = db.query(func.count(func.distinct(VisitorTracking.session_id))).filter(
            and_(
                VisitorTracking.visited_at >= start_date,
                VisitorTracking.visited_at <= end_date,
                VisitorTracking.is_bot == False,
                VisitorTracking.bounce == True
            )
        ).scalar() or 0
        bounce_rate = (bounced_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        return {
            "success": True,
            "stats": {
                "total_visitors": total_visitors,
                "total_page_views": total_page_views,
                "unique_sessions": unique_sessions,
                "avg_time_on_page": avg_time_on_page,
                "bounce_rate": round(bounce_rate, 2)
            },
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting visitor stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get visitor stats: {str(e)}")


@router.get("/demographics", dependencies=[Depends(get_current_admin_user)])
async def get_demographics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get visitor demographics (admin only)
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        date_filter = and_(
            VisitorTracking.visited_at >= start_date,
            VisitorTracking.visited_at <= end_date,
            VisitorTracking.is_bot == False
        )
        
        # Countries
        countries = db.query(
            VisitorTracking.country,
            func.count(func.distinct(VisitorTracking.visitor_id)).label('visitors')
        ).filter(date_filter).group_by(VisitorTracking.country).order_by(desc('visitors')).limit(10).all()
        
        # Devices
        devices = db.query(
            VisitorTracking.device_type,
            func.count(func.distinct(VisitorTracking.visitor_id)).label('visitors')
        ).filter(date_filter).group_by(VisitorTracking.device_type).all()
        
        # Browsers
        browsers = db.query(
            VisitorTracking.browser,
            func.count(func.distinct(VisitorTracking.visitor_id)).label('visitors')
        ).filter(
            and_(date_filter, VisitorTracking.browser.isnot(None))
        ).group_by(VisitorTracking.browser).order_by(desc('visitors')).limit(10).all()
        
        # Operating Systems
        os_list = db.query(
            VisitorTracking.os,
            func.count(func.distinct(VisitorTracking.visitor_id)).label('visitors')
        ).filter(
            and_(date_filter, VisitorTracking.os.isnot(None))
        ).group_by(VisitorTracking.os).order_by(desc('visitors')).limit(10).all()
        
        # Traffic Sources
        traffic_sources = db.query(
            VisitorTracking.traffic_source,
            func.count(func.distinct(VisitorTracking.visitor_id)).label('visitors')
        ).filter(
            and_(date_filter, VisitorTracking.traffic_source.isnot(None))
        ).group_by(VisitorTracking.traffic_source).all()
        
        return {
            "success": True,
            "demographics": {
                "countries": [{"country": c[0] or "Unknown", "visitors": c[1]} for c in countries],
                "devices": [{"device": d[0] or "Unknown", "visitors": d[1]} for d in devices],
                "browsers": [{"browser": b[0] or "Unknown", "visitors": b[1]} for b in browsers],
                "operating_systems": [{"os": o[0] or "Unknown", "visitors": o[1]} for o in os_list],
                "traffic_sources": [{"source": t[0] or "Unknown", "visitors": t[1]} for t in traffic_sources]
            },
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting demographics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get demographics: {str(e)}")


@router.get("/timeline", dependencies=[Depends(get_current_admin_user)])
async def get_visitor_timeline(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    group_by: str = Query("day", regex="^(hour|day|week|month)$"),
    db: Session = Depends(get_db)
):
    """
    Get visitor timeline data for charts (admin only)
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        date_filter = and_(
            VisitorTracking.visited_at >= start_date,
            VisitorTracking.visited_at <= end_date,
            VisitorTracking.is_bot == False
        )
        
        # Group by time period
        if group_by == "hour":
            time_format = func.date_trunc('hour', VisitorTracking.visited_at)
        elif group_by == "day":
            time_format = func.date_trunc('day', VisitorTracking.visited_at)
        elif group_by == "week":
            time_format = func.date_trunc('week', VisitorTracking.visited_at)
        else:  # month
            time_format = func.date_trunc('month', VisitorTracking.visited_at)
        
        # Get visitors per period
        visitors_timeline = db.query(
            time_format.label('period'),
            func.count(func.distinct(VisitorTracking.visitor_id)).label('visitors'),
            func.count(VisitorTracking.id).label('page_views')
        ).filter(date_filter).group_by('period').order_by('period').all()
        
        # Get sessions per period
        sessions_timeline = db.query(
            time_format.label('period'),
            func.count(func.distinct(VisitorTracking.session_id)).label('sessions')
        ).filter(date_filter).group_by('period').order_by('period').all()
        
        timeline_data = []
        for v in visitors_timeline:
            period_str = v.period.isoformat() if hasattr(v.period, 'isoformat') else str(v.period)
            timeline_data.append({
                "period": period_str,
                "visitors": v.visitors,
                "page_views": v.page_views,
                "sessions": 0
            })
        
        # Merge sessions data
        sessions_dict = {s.period.isoformat() if hasattr(s.period, 'isoformat') else str(s.period): s.sessions for s in sessions_timeline}
        for item in timeline_data:
            item["sessions"] = sessions_dict.get(item["period"], 0)
        
        return {
            "success": True,
            "timeline": timeline_data,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "group_by": group_by
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting visitor timeline: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get visitor timeline: {str(e)}")


@router.get("/pages", dependencies=[Depends(get_current_admin_user)])
async def get_top_pages(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get top pages by views (admin only)
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        top_pages = db.query(
            VisitorTracking.page_url,
            VisitorTracking.page_title,
            func.count(VisitorTracking.id).label('views'),
            func.count(func.distinct(VisitorTracking.visitor_id)).label('unique_visitors'),
            func.avg(VisitorTracking.time_on_page).label('avg_time')
        ).filter(
            and_(
                VisitorTracking.visited_at >= start_date,
                VisitorTracking.visited_at <= end_date,
                VisitorTracking.is_bot == False
            )
        ).group_by(VisitorTracking.page_url, VisitorTracking.page_title).order_by(desc('views')).limit(limit).all()
        
        return {
            "success": True,
            "pages": [
                {
                    "url": p.page_url,
                    "title": p.page_title,
                    "views": p.views,
                    "unique_visitors": p.unique_visitors,
                    "avg_time_on_page": int(p.avg_time) if p.avg_time else 0
                }
                for p in top_pages
            ],
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting top pages: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get top pages: {str(e)}")

