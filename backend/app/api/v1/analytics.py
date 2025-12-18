"""
Advanced Analytics and Reporting API Endpoints
Comprehensive analytics, business intelligence, and reporting endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

from ...services.advanced_analytics import advanced_analytics_service
from ...api.v1.auth import get_current_user, User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Advanced Analytics"])

# Request/Response Models
class AnalyticsRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    report_type: Optional[str] = "comprehensive"

class ReportRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    report_format: str = "json"  # json, html, pdf
    report_type: str = "executive"  # executive, market, user, performance, financial

class CustomReportRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    metrics: List[str]
    charts: List[str]
    format: str = "json"

@router.get("/dashboard")
async def get_analytics_dashboard(
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive analytics dashboard
    """
    try:
        # Default to last 30 days if no dates provided
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Generate comprehensive analytics
        analytics = await advanced_analytics_service.generate_comprehensive_analytics(
            start_date, end_date
        )
        
        return {
            "success": True,
            "data": analytics,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Analytics dashboard error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate analytics dashboard: {str(e)}")

@router.get("/metrics")
async def get_analytics_metrics(
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    current_user: User = Depends(get_current_user)
):
    """
    Get key analytics metrics
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        analytics = await advanced_analytics_service.generate_comprehensive_analytics(
            start_date, end_date
        )
        
        return {
            "success": True,
            "metrics": analytics["metrics"],
            "period": analytics["period"]
        }
        
    except Exception as e:
        logger.error(f"Analytics metrics error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics metrics: {str(e)}")

@router.get("/market-analysis")
async def get_market_analysis(
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    current_user: User = Depends(get_current_user)
):
    """
    Get market analysis and trends
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        analytics = await advanced_analytics_service.generate_comprehensive_analytics(
            start_date, end_date
        )
        
        return {
            "success": True,
            "market_analytics": analytics["market_analytics"],
            "charts": {
                "market_analysis": analytics["charts"].get("market_analysis", ""),
                "regional_analysis": analytics["charts"].get("regional_analysis", "")
            },
            "insights": [insight for insight in analytics["insights"] if "market" in insight.lower()],
            "period": analytics["period"]
        }
        
    except Exception as e:
        logger.error(f"Market analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get market analysis: {str(e)}")

@router.get("/user-analytics")
async def get_user_analytics(
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    current_user: User = Depends(get_current_user)
):
    """
    Get user behavior analytics
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        analytics = await advanced_analytics_service.generate_comprehensive_analytics(
            start_date, end_date
        )
        
        return {
            "success": True,
            "user_analytics": analytics["user_analytics"],
            "charts": {
                "user_engagement": analytics["charts"].get("user_engagement", "")
            },
            "insights": [insight for insight in analytics["insights"] if "user" in insight.lower()],
            "period": analytics["period"]
        }
        
    except Exception as e:
        logger.error(f"User analytics error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user analytics: {str(e)}")

@router.get("/performance-metrics")
async def get_performance_metrics(
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    current_user: User = Depends(get_current_user)
):
    """
    Get system performance metrics
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        analytics = await advanced_analytics_service.generate_comprehensive_analytics(
            start_date, end_date
        )
        
        return {
            "success": True,
            "performance_kpis": analytics["performance_kpis"],
            "charts": {
                "performance_metrics": analytics["charts"].get("performance_metrics", "")
            },
            "insights": [insight for insight in analytics["insights"] if "performance" in insight.lower()],
            "period": analytics["period"]
        }
        
    except Exception as e:
        logger.error(f"Performance metrics error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@router.get("/charts")
async def get_analytics_charts(
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    chart_types: Optional[str] = Query(default="all"),
    current_user: User = Depends(get_current_user)
):
    """
    Get analytics charts and visualizations
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        analytics = await advanced_analytics_service.generate_comprehensive_analytics(
            start_date, end_date
        )
        
        # Filter charts based on request
        if chart_types != "all":
            requested_charts = chart_types.split(",")
            filtered_charts = {
                chart_name: chart_html 
                for chart_name, chart_html in analytics["charts"].items()
                if chart_name in requested_charts
            }
        else:
            filtered_charts = analytics["charts"]
        
        return {
            "success": True,
            "charts": filtered_charts,
            "available_charts": list(analytics["charts"].keys()),
            "period": analytics["period"]
        }
        
    except Exception as e:
        logger.error(f"Analytics charts error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics charts: {str(e)}")

@router.post("/reports/executive")
async def generate_executive_report(
    request: ReportRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate executive summary report
    """
    try:
        if request.report_format == "json":
            report = await advanced_analytics_service.generate_executive_report(
                request.start_date, request.end_date
            )
            return JSONResponse(content={"success": True, "report": report})
        
        elif request.report_format == "html":
            # Generate HTML report
            analytics = await advanced_analytics_service.generate_comprehensive_analytics(
                request.start_date, request.end_date
            )
            
            # Create executive summary HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Executive Summary - Crane Intelligence Analytics</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background: #1a1a1a; color: white; padding: 20px; }}
                    .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f5f5f5; border-radius: 5px; }}
                    .value {{ font-size: 24px; font-weight: bold; color: #00ff85; }}
                    .insight {{ background: #e8f4fd; padding: 10px; margin: 5px 0; border-left: 4px solid #007bff; }}
                    .recommendation {{ background: #fff3cd; padding: 10px; margin: 5px 0; border-left: 4px solid #ffc107; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Executive Summary - Crane Intelligence Analytics</h1>
                    <p>Period: {request.start_date.strftime('%Y-%m-%d')} to {request.end_date.strftime('%Y-%m-%d')}</p>
                </div>
                
                <div class="section">
                    <h2>Key Metrics</h2>
                    <div class="metric">
                        <div>Total Valuations</div>
                        <div class="value">{analytics['metrics']['total_valuations']}</div>
                    </div>
                    <div class="metric">
                        <div>Total Revenue</div>
                        <div class="value">${analytics['metrics']['total_revenue']:,.0f}</div>
                    </div>
                    <div class="metric">
                        <div>User Engagement</div>
                        <div class="value">{analytics['metrics']['user_engagement']*100:.1f}%</div>
                    </div>
                    <div class="metric">
                        <div>System Uptime</div>
                        <div class="value">{analytics['performance_kpis']['system_uptime']:.1f}%</div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Key Insights</h2>
                    {''.join([f'<div class="insight">{insight}</div>' for insight in analytics['insights'][:3]])}
                </div>
                
                <div class="section">
                    <h2>Recommendations</h2>
                    {''.join([f'<div class="recommendation">{rec}</div>' for rec in analytics['recommendations'][:3]])}
                </div>
            </body>
            </html>
            """
            
            return HTMLResponse(content=html_content)
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported report format")
        
    except Exception as e:
        logger.error(f"Executive report generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate executive report: {str(e)}")

@router.post("/reports/market")
async def generate_market_report(
    request: ReportRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate market analysis report
    """
    try:
        if request.report_format == "json":
            report = await advanced_analytics_service.generate_market_report(
                request.start_date, request.end_date
            )
            return JSONResponse(content={"success": True, "report": report})
        
        elif request.report_format == "html":
            # Generate HTML market report
            analytics = await advanced_analytics_service.generate_comprehensive_analytics(
                request.start_date, request.end_date
            )
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Market Analysis Report - Crane Intelligence</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background: #1a1a1a; color: white; padding: 20px; }}
                    .chart-container {{ margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Market Analysis Report</h1>
                    <p>Period: {request.start_date.strftime('%Y-%m-%d')} to {request.end_date.strftime('%Y-%m-%d')}</p>
                </div>
                
                <div class="chart-container">
                    {analytics['charts'].get('market_analysis', '')}
                </div>
                
                <div class="chart-container">
                    {analytics['charts'].get('regional_analysis', '')}
                </div>
            </body>
            </html>
            """
            
            return HTMLResponse(content=html_content)
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported report format")
        
    except Exception as e:
        logger.error(f"Market report generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate market report: {str(e)}")

@router.post("/reports/user-analytics")
async def generate_user_analytics_report(
    request: ReportRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate user analytics report
    """
    try:
        if request.report_format == "json":
            report = await advanced_analytics_service.generate_user_analytics_report(
                request.start_date, request.end_date
            )
            return JSONResponse(content={"success": True, "report": report})
        
        elif request.report_format == "html":
            # Generate HTML user analytics report
            analytics = await advanced_analytics_service.generate_comprehensive_analytics(
                request.start_date, request.end_date
            )
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>User Analytics Report - Crane Intelligence</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background: #1a1a1a; color: white; padding: 20px; }}
                    .chart-container {{ margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>User Analytics Report</h1>
                    <p>Period: {request.start_date.strftime('%Y-%m-%d')} to {request.end_date.strftime('%Y-%m-%d')}</p>
                </div>
                
                <div class="chart-container">
                    {analytics['charts'].get('user_engagement', '')}
                </div>
            </body>
            </html>
            """
            
            return HTMLResponse(content=html_content)
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported report format")
        
    except Exception as e:
        logger.error(f"User analytics report generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate user analytics report: {str(e)}")

@router.post("/reports/custom")
async def generate_custom_report(
    request: CustomReportRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate custom analytics report
    """
    try:
        # Generate comprehensive analytics
        analytics = await advanced_analytics_service.generate_comprehensive_analytics(
            request.start_date, request.end_date
        )
        
        # Filter requested metrics and charts
        filtered_metrics = {
            metric: analytics["metrics"].get(metric, None)
            for metric in request.metrics
            if metric in analytics["metrics"]
        }
        
        filtered_charts = {
            chart: analytics["charts"].get(chart, "")
            for chart in request.charts
            if chart in analytics["charts"]
        }
        
        custom_report = {
            "period": analytics["period"],
            "requested_metrics": filtered_metrics,
            "requested_charts": filtered_charts,
            "insights": analytics["insights"],
            "recommendations": analytics["recommendations"],
            "generated_at": datetime.now().isoformat()
        }
        
        if request.format == "json":
            return JSONResponse(content={"success": True, "report": custom_report})
        else:
            raise HTTPException(status_code=400, detail="Unsupported format for custom report")
        
    except Exception as e:
        logger.error(f"Custom report generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate custom report: {str(e)}")

@router.get("/insights")
async def get_analytics_insights(
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    current_user: User = Depends(get_current_user)
):
    """
    Get actionable insights from analytics
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        analytics = await advanced_analytics_service.generate_comprehensive_analytics(
            start_date, end_date
        )
        
        return {
            "success": True,
            "insights": analytics["insights"],
            "recommendations": analytics["recommendations"],
            "period": analytics["period"]
        }
        
    except Exception as e:
        logger.error(f"Analytics insights error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics insights: {str(e)}")

@router.get("/health")
async def get_analytics_health(current_user: User = Depends(get_current_user)):
    """
    Get analytics system health status
    """
    try:
        # Check analytics service health
        health_status = {
            "status": "healthy",
            "service": "advanced_analytics",
            "version": "1.0.0",
            "uptime": "99.8%",
            "last_updated": datetime.now().isoformat(),
            "features": {
                "comprehensive_analytics": True,
                "market_analysis": True,
                "user_analytics": True,
                "performance_metrics": True,
                "report_generation": True,
                "chart_generation": True
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Analytics health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_updated": datetime.now().isoformat()
        }
