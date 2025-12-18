"""
Enhanced Valuation API Endpoints
Bloomberg-style valuation with comprehensive market analysis
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime
import json

from ...services.valuation_engine_unified import (
    UnifiedValuationEngine as EnhancedValuationEngine,
    ValuationResult,
    CraneSpecs
)
# Backward compatibility aliases
BloombergReportGenerator = None  # Will be implemented in unified engine if needed
SpecsCatalogService = None  # Will be implemented in unified engine if needed
from ...api.v1.auth import get_current_user
from ...models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()

class CraneValuationRequest(BaseModel):
    """Request model for crane valuation"""
    manufacturer: str = Field(..., description="Crane manufacturer")
    model: str = Field(..., description="Crane model")
    year: int = Field(..., description="Manufacturing year")
    capacity_tons: float = Field(..., description="Lifting capacity in tons")
    hours: int = Field(..., description="Operating hours")
    location: str = Field(..., description="Current location")
    condition_score: float = Field(..., ge=0, le=1, description="Condition score (0-1)")
    boom_length_ft: Optional[float] = Field(None, description="Main boom length in feet")
    jib_length_ft: Optional[float] = Field(None, description="Jib length in feet")
    counterweight_lbs: Optional[float] = Field(None, description="Counterweight in pounds")
    features: Optional[List[str]] = Field(None, description="Crane features")
    description: Optional[str] = Field(None, description="Additional description")

class ValuationResponse(BaseModel):
    """Response model for valuation results"""
    fair_market_value: float
    wholesale_value: float
    retail_value: float
    confidence_score: float
    deal_score: int
    market_position: str
    comparable_count: int
    market_trends: Dict[str, Any]
    financing_scenarios: List[Dict[str, Any]]
    risk_factors: List[str]
    recommendations: List[str]
    comparable_sales: List[Dict[str, Any]]
    spec_analysis: Dict[str, Any]
    report_url: Optional[str] = None

class SpecsCatalogResponse(BaseModel):
    """Response model for specs catalog"""
    spec_id: str
    source: str
    make: str
    model: str
    variant: str
    capacity_tons: Optional[float]
    boom_length_ft: Optional[float]
    jib_options_ft: List[float]
    counterweight_lbs: Optional[float]
    features: List[str]
    engine: Optional[str]
    dimensions: Dict[str, float]
    pdf_specs: List[str]

@router.post("/value-crane", response_model=ValuationResponse)
async def value_crane(
    request: CraneValuationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Perform comprehensive crane valuation with Bloomberg-style analysis
    """
    try:
        # Initialize the enhanced valuation engine
        engine = EnhancedValuationEngine()
        
        # Convert request to dictionary
        request_data = request.dict()
        
        # Perform Bloomberg-style valuation
        valuation_result = await engine.value_crane(request_data)
        
        # Generate report in background
        if valuation_result:
            background_tasks.add_task(
                engine.report_generator.generate_valuation_report,
                valuation_result,
                request_data
            )
        
        # Convert to response model
        return ValuationResponse(
            fair_market_value=valuation_result.fair_market_value,
            wholesale_value=valuation_result.wholesale_value,
            retail_value=valuation_result.retail_value,
            confidence_score=valuation_result.confidence_score,
            deal_score=valuation_result.deal_score,
            market_position=valuation_result.market_position,
            comparable_count=valuation_result.comparable_count,
            market_trends=valuation_result.market_trends,
            financing_scenarios=valuation_result.financing_scenarios,
            risk_factors=valuation_result.risk_factors,
            recommendations=valuation_result.recommendations,
            comparable_sales=valuation_result.comparable_sales,
            spec_analysis=valuation_result.spec_analysis,
            report_url=valuation_result.report_url
        )
        
    except Exception as e:
        logger.error(f"Valuation error: {e}")
        raise HTTPException(status_code=500, detail=f"Valuation failed: {str(e)}")

@router.get("/specs-catalog", response_model=List[SpecsCatalogResponse])
async def get_specs_catalog(
    make: Optional[str] = None,
    model: Optional[str] = None,
    capacity_min: Optional[float] = None,
    capacity_max: Optional[float] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get crane specifications from catalog
    """
    try:
        # Initialize the specs service
        specs_service = SpecsCatalogService()
        
        # Get filtered catalog
        catalog_data = await specs_service.get_specs_catalog(
            make=make,
            model=model,
            capacity_min=capacity_min,
            capacity_max=capacity_max
        )
        
        # Convert to response models
        return [
            SpecsCatalogResponse(
                spec_id=item["spec_id"],
                source=item["source"],
                make=item["make"],
                model=item["model"],
                variant=item["variant"],
                capacity_tons=item["capacity_tons"],
                boom_length_ft=item["boom_length_ft"],
                jib_options_ft=item["jib_options_ft"],
                counterweight_lbs=item["counterweight_lbs"],
                features=item["features"],
                engine=item["engine"],
                dimensions=item["dimensions"],
                pdf_specs=item["pdf_specs"]
            )
            for item in catalog_data
        ]
        
    except Exception as e:
        logger.error(f"Specs catalog error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch specs catalog: {str(e)}")

@router.get("/specs-catalog/stats")
async def get_specs_stats(current_user: User = Depends(get_current_user)):
    """
    Get specifications catalog statistics
    """
    try:
        # Initialize the specs service
        specs_service = SpecsCatalogService()
        
        # Get all catalog data for stats
        all_catalog = await specs_service.get_specs_catalog()
        
        # Calculate statistics
        stats = {
            "total_specs": len(all_catalog),
            "manufacturers": len(set(item["make"] for item in all_catalog)),
            "models": len(set(item["model"] for item in all_catalog)),
            "capacity_range": {
                "min": min(item["capacity_tons"] for item in all_catalog if item["capacity_tons"]),
                "max": max(item["capacity_tons"] for item in all_catalog if item["capacity_tons"])
            },
            "last_updated": datetime.now().isoformat()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Specs stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch specs statistics: {str(e)}")

@router.get("/market-trends")
async def get_market_trends(
    make: Optional[str] = None,
    model: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get real-time market trend data
    """
    try:
        # Initialize the market data service
        from ...services.enhanced_valuation_engine import MarketDataService
        market_service = MarketDataService()
        
        # Fetch comprehensive market data
        if make and model:
            market_data = await market_service.get_comprehensive_market_data(make, model)
            
            # Extract trends from the comprehensive data
            trends = {
                "equipment_watch": market_data.get("equipment_watch", {}).get("market_trends", {}),
                "ritchie_bros": {
                    "average_price": market_data.get("ritchie_bros", {}).get("average_price", 0),
                    "price_range": market_data.get("ritchie_bros", {}).get("price_range", [0, 0])
                },
                "machinery_trader": {
                    "average_listing_price": market_data.get("machinery_trader", {}).get("average_listing_price", 0),
                    "market_activity": market_data.get("machinery_trader", {}).get("market_activity", "unknown")
                },
                "comprehensive": market_data.get("market_trends", {}),
                "total_listings": market_data.get("total_listings", 0),
                "last_updated": market_data.get("last_updated", datetime.now().isoformat())
            }
        else:
            # General market trends
            trends = {
                "general": {
                    "price_trend": "stable",
                    "demand_level": "high",
                    "supply_level": "medium",
                    "market_activity": "active"
                }
            }
        
        return trends
        
    except Exception as e:
        logger.error(f"Market trends error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch market trends: {str(e)}")

@router.get("/market-data/health")
async def get_market_data_health(current_user: User = Depends(get_current_user)):
    """
    Get health status of all market data sources
    """
    try:
        from ...services.real_time_market_data import real_time_market_data_service
        
        # Initialize service if needed
        if not hasattr(real_time_market_data_service, '_initialized') or not real_time_market_data_service._initialized:
            await real_time_market_data_service.initialize()
        
        # Get health status
        health_status = await real_time_market_data_service.get_market_health_status()
        
        return health_status
        
    except Exception as e:
        logger.error(f"Market data health check error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check market data health: {str(e)}")

@router.get("/market-data/live")
async def get_live_market_data(
    make: str,
    model: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get live market data from all sources
    """
    try:
        from ...services.enhanced_valuation_engine import MarketDataService
        market_service = MarketDataService()
        
        # Fetch comprehensive live market data
        market_data = await market_service.get_comprehensive_market_data(make, model)
        
        return {
            "make": make,
            "model": model,
            "data": market_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Live market data error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch live market data: {str(e)}")

@router.post("/scrape-specs")
async def trigger_specs_scraping(
    source: str = "bigge",
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user)
):
    """
    Trigger specifications scraping (admin only)
    """
    try:
        # Check if user is admin
        if current_user.role not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Initialize specs service
        specs_service = SpecsCatalogService()
        
        # Trigger background scraping task
        if background_tasks:
            background_tasks.add_task(
                specs_service.scrape_specifications,
                source
            )
        
        return {
            "message": f"Specifications scraping initiated for source: {source}",
            "status": "started",
            "source": source
        }
        
    except Exception as e:
        logger.error(f"Specs scraping error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger specs scraping: {str(e)}")

@router.get("/reports/{report_name}")
async def get_report(report_name: str, current_user: User = Depends(get_current_user)):
    """
    Download generated report
    """
    try:
        import os
        from fastapi.responses import FileResponse
        
        # Construct report path
        report_path = f"backend/generated_reports/{report_name}"
        
        # Check if report exists
        if not os.path.exists(report_path):
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Return file response
        return FileResponse(
            path=report_path,
            filename=report_name,
            media_type="text/html"
        )
        
    except Exception as e:
        logger.error(f"Report download error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download report: {str(e)}")
