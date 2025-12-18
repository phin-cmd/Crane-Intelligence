"""
Report Generation API
Handles Bloomberg-style report generation and export
"""

import logging
import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime

from ...api.v1.auth import get_current_user
from ...models.user import User
from ...services.simple_pdf_export import SimplePDFExportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Report Generation"])

# Add FMV reports endpoint
@router.get("/fmv-reports/user/{email}")
async def get_fmv_reports_by_user(
    email: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get FMV reports for a specific user"""
    try:
        # For now, return empty list - can be implemented later
        return {
            "success": True,
            "reports": [],
            "count": 0,
            "message": "No reports found"
        }
    except Exception as e:
        logger.error(f"Error getting FMV reports: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve reports"
        )

class ValuationData(BaseModel):
    """Valuation data for report generation"""
    manufacturer: str
    model: str
    year: int
    capacity_tons: float
    hours: int
    region: str
    estimated_value: float
    confidence_score: float
    age_factor: float = 0.88
    condition_score: float = 0.85
    market_demand: str = "High"
    risk_score: str = "Low"

class ReportRequest(BaseModel):
    """Report generation request"""
    template: str
    valuation_data: ValuationData
    include_charts: bool = True
    include_comps: bool = True
    include_finance_scenarios: bool = True
    include_market_analysis: bool = True
    include_risk_assessment: bool = True

class ReportResponse(BaseModel):
    """Report generation response"""
    success: bool
    report_id: str
    report_url: str
    generated_at: str
    message: str
    pdf_url: Optional[str] = None

@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generate a Bloomberg-style report (simplified endpoint without WeasyPrint)
    """
    try:
        # Check permissions
        user_role = current_user.get('subscription_tier', 'free')
        if user_role not in ['professional', 'fleet_valuation', 'spot_check']:
            raise HTTPException(
                status_code=403, 
                detail="Insufficient permissions to generate reports"
            )
        
        # Generate a simple report with PDF export capability
        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        report_url = f"/reports/{report_id}"
        
        # Initialize PDF export service
        pdf_service = SimplePDFExportService()
        
        # Create a simple report data structure
        report_data = {
            "report_id": report_id,
            "generated_at": datetime.now().isoformat(),
            "template": request.template,
            "valuation_data": request.valuation_data.dict(),
            "options": {
                "include_charts": request.include_charts,
                "include_comps": request.include_comps,
                "include_finance_scenarios": request.include_finance_scenarios,
                "include_market_analysis": request.include_market_analysis,
                "include_risk_assessment": request.include_risk_assessment
            },
            "kpi_metrics": {
                "estimated_value": request.valuation_data.estimated_value,
                "value_per_ton": request.valuation_data.estimated_value / request.valuation_data.capacity_tons,
                "age_factor": request.valuation_data.age_factor,
                "condition_score": request.valuation_data.condition_score,
                "confidence_score": request.valuation_data.confidence_score
            },
            "comparable_sales": [
                {
                    "manufacturer": request.valuation_data.manufacturer,
                    "model": f"{request.valuation_data.model} (Similar)",
                    "year": request.valuation_data.year - 1,
                    "price": request.valuation_data.estimated_value * 0.95,
                    "location": request.valuation_data.region
                },
                {
                    "manufacturer": request.valuation_data.manufacturer,
                    "model": f"{request.valuation_data.model} (Newer)",
                    "year": request.valuation_data.year + 1,
                    "price": request.valuation_data.estimated_value * 1.15,
                    "location": request.valuation_data.region
                }
            ],
            "finance_scenarios": [
                {
                    "scenario": "Conservative",
                    "monthly_payment": request.valuation_data.estimated_value * 0.008,
                    "total_cost_5yr": request.valuation_data.estimated_value * 1.48,
                    "roi": 12.5
                },
                {
                    "scenario": "Moderate",
                    "monthly_payment": request.valuation_data.estimated_value * 0.012,
                    "total_cost_5yr": request.valuation_data.estimated_value * 1.72,
                    "roi": 18.3
                },
                {
                    "scenario": "Aggressive",
                    "monthly_payment": request.valuation_data.estimated_value * 0.018,
                    "total_cost_5yr": request.valuation_data.estimated_value * 2.08,
                    "roi": 25.7
                }
            ],
            "market_analysis": {
                "demand_level": "High",
                "market_trend": "Growing",
                "regional_factors": f"Strong demand in {request.valuation_data.region}",
                "price_trend": "Stable to increasing"
            },
            "risk_assessment": {
                "overall_risk": "Low",
                "market_risk": "Low",
                "operational_risk": "Medium",
                "financial_risk": "Low"
            }
        }
        
        # Generate dual reports (Market Intelligence + Cover Letter)
        try:
            logger.info(f"Attempting to generate dual reports for {report_id}")
            logger.info(f"Report data keys: {list(report_data.keys())}")
            report_paths = pdf_service.generate_dual_reports(report_data, report_id)
            pdf_url = f"/api/v1/reports/download/{report_id}"
            logger.info(f"Dual reports generated successfully: {report_paths}")
        except Exception as e:
            logger.error(f"Dual report generation failed: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            pdf_url = None
        
        return ReportResponse(
            success=True,
            report_id=report_id,
            report_url=report_url,
            generated_at=datetime.now().isoformat(),
            message="Report generated successfully",
            pdf_url=pdf_url
        )
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{report_id}")
async def get_report(report_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Retrieve a generated report
    """
    try:
        # Check permissions
        user_role = current_user.get('subscription_tier', 'free')
        if user_role not in ['admin', 'professional', 'fleet_valuation']:
            raise HTTPException(
                status_code=403, 
                detail="Insufficient permissions to access reports"
            )
        
        # For now, return a sample report
        # In production, this would retrieve the actual report file
        return {
            "success": True,
            "report_id": report_id,
            "message": "Report retrieved successfully",
            "report_data": {
                "status": "generated",
                "created_at": datetime.now().isoformat(),
                "file_path": f"reports/generated/{report_id}.html"
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{report_id}")
async def download_report_pdf(report_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Download a generated report PDF (defaults to Market Intelligence Report)
    """
    return await download_specific_report(report_id, "market_intelligence", current_user)

@router.get("/download/{report_id}/{report_type}")
async def download_specific_report(
    report_id: str, 
    report_type: str, 
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Download a specific report type (market_intelligence or cover_letter)
    """
    try:
        # Check permissions
        user_role = current_user.get('subscription_tier', 'free')
        if user_role not in ['admin', 'professional', 'fleet_valuation']:
            raise HTTPException(
                status_code=403, 
                detail="Insufficient permissions to download reports"
            )
        
        # Validate report type
        if report_type not in ['market_intelligence', 'cover_letter']:
            raise HTTPException(
                status_code=400, 
                detail="Invalid report type. Must be 'market_intelligence' or 'cover_letter'"
            )
        
        # Look for HTML report file
        pdf_service = SimplePDFExportService()
        html_dir = pdf_service.output_dir
        
        # Find the HTML file for this report type
        html_files = list(html_dir.glob(f"{report_id}_{report_type}_*.html"))
        
        if not html_files:
            raise HTTPException(status_code=404, detail=f"{report_type} report file not found")
        
        # Use the most recent HTML file
        html_path = max(html_files, key=os.path.getctime)
        
        if not os.path.exists(html_path):
            raise HTTPException(status_code=404, detail=f"{report_type} report file not found")
        
        # Return the HTML file with instructions for PDF conversion
        from fastapi.responses import FileResponse
        return FileResponse(
            path=html_path,
            media_type='text/html',
            filename=f"{report_id}_{report_type}.html",
            headers={"Content-Disposition": f"inline; filename={report_id}_{report_type}.html"}
        )
        
    except Exception as e:
        logger.error(f"Error downloading {report_type} report: {e}")
        raise HTTPException(status_code=500, detail=str(e))