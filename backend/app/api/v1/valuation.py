"""
Crane Intelligence Platform - Valuation API Endpoints
Provides professional crane valuation services via REST API with subscription-based access control
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
from pydantic import BaseModel, Field
import sys
import os

# Add the app directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ...services.valuation_engine_unified import (
    UnifiedValuationEngine as CraneValuationEngine,
    CraneSpecs,
    ValuationResult
)
# Backward compatibility - use unified engine for both
from ...services.valuation_engine_unified import UnifiedValuationEngine
comprehensive_valuation_engine = UnifiedValuationEngine(use_real_time_data=True)
from ...services.auth_service import get_current_user, require_api_access, require_portfolio_analysis
from ...services.auth_service import subscription_service

router = APIRouter(prefix="/valuation", tags=["Crane Valuation"])

# Initialize the valuation engine
valuation_engine = CraneValuationEngine()


class CraneValuationRequest(BaseModel):
    """Request model for crane valuation"""
    manufacturer: str = Field(..., description="Crane manufacturer (e.g., Liebherr, Grove)")
    model: str = Field(..., description="Crane model (e.g., LTM1350-6.1)")
    year: int = Field(..., ge=1950, le=2030, description="Manufacturing year")
    capacity_tons: float = Field(..., gt=0, description="Lifting capacity in tons")
    hours: int = Field(..., ge=0, description="Total operating hours")
    condition_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Condition score (0.0-1.0)")
    region: str = Field(..., description="Geographic region (e.g., TX, CA, NY)")
    price: Optional[float] = Field(None, ge=0, description="Asking price (optional)")


class CraneValuationResponse(BaseModel):
    """Response model for crane valuation"""
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None


class MarketAnalysisRequest(BaseModel):
    """Request model for market analysis"""
    manufacturer: str
    model: str
    year: int
    capacity_tons: float
    region: str


class FleetOptimizationRequest(BaseModel):
    """Request model for fleet optimization analysis"""
    cranes: List[CraneValuationRequest]
    target_roi: float = Field(..., ge=0.05, le=0.25, description="Target ROI (5%-25%)")
    budget: Optional[float] = Field(None, ge=0, description="Total budget constraint")


@router.post("/value-crane-enhanced", response_model=CraneValuationResponse)
async def value_crane_enhanced(
    request: CraneValuationRequest,
    current_user: dict = Depends(get_current_user),
    http_request: Request = None
):
    """
    Perform Bloomberg-style enhanced crane valuation analysis
    
    This endpoint provides professional-grade Bloomberg-style valuation including:
    - Fair market value with wholesale/retail ranges
    - Automatic comparable units from live listings and sales
    - Market context from weekly trend data
    - Financing scenarios by region
    - Professional deal scoring and wear analysis
    
    Subscription Requirements:
    - Professional or Fleet Valuation subscription required for enhanced features
    - Basic tier gets standard valuation only
    """
    try:
        # Check subscription limits
        # Subscription tier logic removed - pay-per-use model
        
        if not subscription_plan:
            return CraneValuationResponse(
                success=False,
                message="Enhanced valuation failed",
                error="Invalid subscription tier"
            )
        
        # Convert request to enhanced format
        crane_specs = {
            'manufacturer': request.manufacturer,
            'model': request.model,
            'year': request.year,
            'capacity': request.capacity_tons,
            'hours': request.hours,
            'region': request.region,
            'asking_price': request.price
        }
        
        # Run comprehensive valuation
        result = comprehensive_valuation_engine.calculate_valuation(crane_specs)
        
        # Check if user can access enhanced features (Pro+ subscription)
        if not subscription_service.can_access_feature(user_tier, "deal_score"):
            # Remove enhanced features for Basic tier
            result['deal_score'] = None
            result['wear_score'] = None
            result['financing_scenarios'] = {}
            result['market_insights'] = {}
        
        return CraneValuationResponse(
            success=True,
            message="Enhanced Bloomberg-style valuation completed successfully",
            data=result
        )
        
    except Exception as e:
        return CraneValuationResponse(
            success=False,
            message="Enhanced valuation failed",
            error=str(e)
        )


@router.post("/value-crane", response_model=CraneValuationResponse)
async def value_crane(
    request: CraneValuationRequest,
    current_user: dict = Depends(get_current_user),
    http_request: Request = None
):
    """
    Perform comprehensive crane valuation analysis
    
    This endpoint provides professional-grade crane valuation including:
    - Fair market value calculation
    - Deal scoring (0-100) - Requires Professional or Fleet Valuation subscription
    - Risk assessment
    - Financial analysis
    - Comparable market analysis
    
    Subscription Requirements:
    - Spot Check: 1 valuation/month
    - Professional: 1 valuation/month
    - Fleet Valuation: 5 valuations/month
    """
    try:
        # Check subscription limits
        # Subscription tier logic removed - pay-per-use model
        
        if not subscription_plan:
            return CraneValuationResponse(
                success=False,
                message="Valuation failed",
                error="Invalid subscription tier"
            )
        
        # Check valuation limits
        monthly_limit = subscription_plan.get("monthly_valuations_limit", 0)
        if monthly_limit > 0:  # -1 means unlimited
            # In production, you would check actual usage from database
            # For demo, we'll assume user has used some valuations
            current_usage = 25  # Mock usage
            if current_usage >= monthly_limit:
                return CraneValuationResponse(
                    success=False,
                    message="Valuation failed",
                    error=f"Monthly valuation limit reached ({monthly_limit}). Please upgrade your subscription."
                )
        
        # Convert request to CraneSpecs
        specs = CraneSpecs(
            manufacturer=request.manufacturer,
            model=request.model,
            year=request.year,
            capacity_tons=request.capacity_tons,
            hours=request.hours,
            condition_score=request.condition_score,
            region=request.region,
            price=request.price
        )
        
        # Run valuation
        result = valuation_engine.value_crane(specs)
        
        # Check if user can access deal score (Pro+ subscription)
        if not subscription_service.can_access_feature(user_tier, "deal_score"):
            # Remove deal score and related features for Basic tier
            result.deal_score = None
            result.recommendations = []
            result.risk_factors = []
        
        # Convert result to dict for response
        result_dict = {
            "fair_market_value": result.fair_market_value,
            "deal_score": result.deal_score,
            "confidence_score": result.confidence_score,
            "risk_factors": result.risk_factors if subscription_service.can_access_feature(user_tier, "deal_score") else [],
            "recommendations": result.recommendations if subscription_service.can_access_feature(user_tier, "deal_score") else [],
            "market_position": result.market_position,
            "depreciation_rate": result.depreciation_rate,
            "hours_analysis": result.hours_analysis,
            "comparable_analysis": result.comparable_analysis,
            "financial_metrics": result.financial_metrics,
            "input_specs": {
                "manufacturer": specs.manufacturer,
                "model": specs.model,
                "year": specs.year,
                "capacity_tons": specs.capacity_tons,
                "hours": specs.hours,
                "condition_score": specs.condition_score,
                "region": specs.region,
                "price": specs.price
            },
            "subscription_info": {
                "tier": user_tier,
                "monthly_valuations_limit": monthly_limit,
                "deal_score_available": subscription_service.can_access_feature(user_tier, "deal_score")
            }
        }
        
        # Log usage (in production, this would update the database)
        # For demo purposes, we'll just note it
        
        return CraneValuationResponse(
            success=True,
            message="Crane valuation completed successfully",
            data=result_dict
        )
        
    except Exception as e:
        return CraneValuationResponse(
            success=False,
            message="Valuation failed",
            error=str(e)
        )


@router.post("/market-analysis", response_model=CraneValuationResponse)
async def analyze_market(
    request: MarketAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Perform market analysis for crane model
    
    Provides market intelligence including:
    - Regional pricing trends
    - Supply/demand analysis
    - Market positioning
    - Investment timing recommendations
    
    Available to all subscription tiers.
    """
    try:
        # Create dummy specs for market analysis (hours and condition not needed)
        specs = CraneSpecs(
            manufacturer=request.manufacturer,
            model=request.model,
            year=request.year,
            capacity_tons=request.capacity_tons,
            hours=request.year * 800,  # Estimate based on age
            condition_score=0.8,  # Assume average condition
            region=request.region
        )
        
        # Run valuation for market analysis
        result = valuation_engine.value_crane(specs)
        
        # Extract market-specific data
        market_data = {
            "base_value": specs.capacity_tons * 12000,
            "market_value": result.fair_market_value,
            "market_position": result.market_position,
            "comparable_analysis": result.comparable_analysis,
            "regional_adjustment": valuation_engine.regional_adjustments.get(
                request.region, 
                valuation_engine.regional_adjustments['default']
            ),
            "manufacturer_premium": valuation_engine.manufacturer_premiums.get(
                request.manufacturer,
                valuation_engine.manufacturer_premiums['default']
            )
        }
        
        return CraneValuationResponse(
            success=True,
            message="Market analysis completed successfully",
            data=market_data
        )
        
    except Exception as e:
        return CraneValuationResponse(
            success=False,
            message="Market analysis failed",
            error=str(e)
        )


@router.post("/fleet-optimization", response_model=CraneValuationResponse)
async def optimize_fleet(
    request: FleetOptimizationRequest,
    current_user: dict = Depends(require_portfolio_analysis)
):
    """
    Perform fleet optimization analysis
    
    Analyzes multiple cranes to optimize:
    - Portfolio composition
    - ROI optimization
    - Risk diversification
    - Budget allocation
    
    Subscription Requirements:
    - Fleet Valuation subscription required
    - Basic tier cannot access portfolio analysis
    """
    try:
        # Check if user can access portfolio analysis
        user_tier = current_user.get("subscription_tier", "basic")
        if not subscription_service.can_access_feature(user_tier, "portfolio_analysis"):
            return CraneValuationResponse(
                success=False,
                message="Fleet optimization failed",
                error="Portfolio analysis requires Fleet Valuation subscription"
            )
        
        fleet_analysis = []
        total_investment = 0
        weighted_roi = 0
        
        for crane_request in request.cranes:
            # Convert to specs
            specs = CraneSpecs(
                manufacturer=crane_request.manufacturer,
                model=crane_request.model,
                year=crane_request.year,
                capacity_tons=crane_request.capacity_tons,
                hours=crane_request.hours,
                condition_score=crane_request.condition_score,
                region=crane_request.region,
                price=crane_request.price
            )
            
            # Run valuation
            result = valuation_engine.value_crane(specs)
            
            # Calculate ROI (using medium scenario)
            roi = 0.12  # Default 12% ROI
            if result.financial_metrics and 'roi_scenarios' in result.financial_metrics:
                roi = result.financial_metrics['roi_scenarios']['medium']['annual_return'] / specs.price
            
            crane_analysis = {
                "crane_id": len(fleet_analysis) + 1,
                "specs": {
                    "manufacturer": specs.manufacturer,
                    "model": specs.model,
                    "year": specs.year,
                    "capacity_tons": specs.capacity_tons
                },
                "valuation": {
                    "fair_market_value": result.fair_market_value,
                    "deal_score": result.deal_score,
                    "market_position": result.market_position
                },
                "financial": {
                    "price": specs.price or result.fair_market_value,
                    "roi": roi,
                    "annual_return": (specs.price or result.fair_market_value) * roi
                }
            }
            
            fleet_analysis.append(crane_analysis)
            
            if specs.price:
                total_investment += specs.price
                weighted_roi += specs.price * roi
        
        # Calculate portfolio metrics
        portfolio_roi = weighted_roi / total_investment if total_investment > 0 else 0
        
        # Generate optimization recommendations
        recommendations = []
        if portfolio_roi < request.target_roi:
            recommendations.append("Consider higher-ROI equipment to meet target returns")
        
        if request.budget and total_investment > request.budget:
            recommendations.append("Fleet exceeds budget - prioritize highest-ROI equipment")
        
        # Sort by deal score for prioritization
        fleet_analysis.sort(key=lambda x: x['valuation']['deal_score'], reverse=True)
        
        portfolio_data = {
            "fleet_analysis": fleet_analysis,
            "portfolio_metrics": {
                "total_cranes": len(fleet_analysis),
                "total_investment": total_investment,
                "portfolio_roi": portfolio_roi,
                "target_roi": request.target_roi,
                "budget_utilization": (total_investment / request.budget * 100) if request.budget else None
            },
            "recommendations": recommendations,
            "top_picks": fleet_analysis[:3]  # Top 3 by deal score
        }
        
        return CraneValuationResponse(
            success=True,
            message="Fleet optimization analysis completed successfully",
            data=portfolio_data
        )
        
    except Exception as e:
        return CraneValuationResponse(
            success=False,
            message="Fleet optimization failed",
            error=str(e)
        )


@router.get("/manufacturers", response_model=CraneValuationResponse)
async def get_manufacturers():
    """Get list of supported manufacturers with premium factors"""
    try:
        manufacturers = {
            manufacturer: {
                "premium_factor": premium,
                "description": f"{manufacturer} crane premium"
            }
            for manufacturer, premium in valuation_engine.manufacturer_premiums.items()
            if manufacturer != 'default'
        }
        
        return CraneValuationResponse(
            success=True,
            message="Manufacturers retrieved successfully",
            data={"manufacturers": manufacturers}
        )
        
    except Exception as e:
        return CraneValuationResponse(
            success=False,
            message="Failed to retrieve manufacturers",
            error=str(e)
        )


@router.get("/regions", response_model=CraneValuationResponse)
async def get_regions():
    """Get list of supported regions with adjustment factors"""
    try:
        regions = {
            region: {
                "adjustment_factor": factor,
                "description": f"{region} regional adjustment"
            }
            for region, factor in valuation_engine.regional_adjustments.items()
            if region != 'default'
        }
        
        return CraneValuationResponse(
            success=True,
            message="Regions retrieved successfully",
            data={"regions": regions}
        )
        
    except Exception as e:
        return CraneValuationResponse(
            success=False,
            message="Failed to retrieve regions",
            error=str(e)
        )


@router.get("/subscription/limits", response_model=CraneValuationResponse)
async def get_subscription_limits(current_user: dict = Depends(get_current_user)):
    """Get current user's subscription limits and usage"""
    try:
        # Subscription tier logic removed - pay-per-use model
        
        if not subscription_plan:
            return CraneValuationResponse(
                success=False,
                message="Failed to retrieve subscription limits",
                error="Invalid subscription tier"
            )
        
        # In production, you would get actual usage from database
        # For demo purposes, we'll return mock usage
        mock_usage = {
            "basic": {"valuations": 25, "api_calls": 0},
            "pro": {"valuations": 75, "api_calls": 150},
            "fleet_valuation": {"valuations": 5, "api_calls": 0}
        }
        
        current_usage = mock_usage.get(user_tier, {"valuations": 0, "api_calls": 0})
        
        limits_data = {
            "subscription_tier": user_tier,
            "plan": subscription_plan,
            "current_usage": current_usage,
            "remaining": {
                "valuations": max(0, subscription_plan.get("monthly_valuations_limit", 0) - current_usage["valuations"]),
                "api_calls": max(0, subscription_plan.get("monthly_api_calls_limit", 0) - current_usage["api_calls"])
            }
        }
        
        return CraneValuationResponse(
            success=True,
            message="Subscription limits retrieved successfully",
            data=limits_data
        )
        
    except Exception as e:
        return CraneValuationResponse(
            success=False,
            message="Failed to retrieve subscription limits",
            error=str(e)
        )


@router.post("/value-crane-test", response_model=CraneValuationResponse)
async def value_crane_test(request: CraneValuationRequest):
    """
    Test endpoint for Bloomberg-style valuation without authentication
    """
    try:
        # Convert request to enhanced format
        crane_specs = {
            'manufacturer': request.manufacturer,
            'model': request.model,
            'year': request.year,
            'capacity': request.capacity_tons,
            'hours': request.hours,
            'region': request.region,
            'asking_price': request.price
        }
        
        # Run comprehensive valuation
        result = comprehensive_valuation_engine.calculate_valuation(crane_specs)
        
        return CraneValuationResponse(
            success=True,
            message="Bloomberg-style valuation completed successfully",
            data=result
        )
        
    except Exception as e:
        return CraneValuationResponse(
            success=False,
            message="Valuation failed",
            error=str(e)
        )


@router.get("/health", response_model=CraneValuationResponse)
async def valuation_health_check():
    """Health check for valuation service"""
    try:
        # Test valuation with sample data
        test_specs = CraneSpecs(
            manufacturer="Liebherr",
            model="LTM1350-6.1",
            year=2022,
            capacity_tons=350,
            hours=1200,
            condition_score=0.95,
            region="TX"
        )
        
        result = valuation_engine.value_crane(test_specs)
        
        return CraneValuationResponse(
            success=True,
            message="Valuation service is healthy",
            data={
                "status": "healthy",
                "test_valuation": {
                    "fair_market_value": result.fair_market_value,
                    "deal_score": result.deal_score,
                    "confidence_score": result.confidence_score
                },
                "subscription_plans": len(subscription_service.get_all_plans())
            }
        )
        
    except Exception as e:
        return CraneValuationResponse(
            success=False,
            message="Valuation service health check failed",
            error=str(e)
        )
