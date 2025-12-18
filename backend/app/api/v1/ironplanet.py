"""
IronPlanet API Integration Endpoints
Provides access to IronPlanet marketplace data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...services.ironplanet_service import IronPlanetService
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ironplanet", tags=["IronPlanet Integration"])

# Global service instance
ironplanet_service = None

async def get_ironplanet_service():
    """Get or create IronPlanet service instance"""
    global ironplanet_service
    if ironplanet_service is None:
        ironplanet_service = IronPlanetService()
        await ironplanet_service.initialize()
    return ironplanet_service

@router.get("/listings/active")
async def get_active_listings(
    make: str = Query(..., description="Equipment make"),
    model: str = Query(..., description="Equipment model"),
    category: str = Query("crane", description="Equipment category"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results")
):
    """Get active listings from IronPlanet marketplace"""
    try:
        service = await get_ironplanet_service()
        result = await service.get_active_listings(make, model, category)
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error getting IronPlanet active listings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auctions/recent")
async def get_recent_auctions(
    make: str = Query(..., description="Equipment make"),
    model: str = Query(..., description="Equipment model"),
    days_back: int = Query(30, ge=1, le=365, description="Days to look back"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of results")
):
    """Get recent auction results from IronPlanet"""
    try:
        service = await get_ironplanet_service()
        result = await service.get_recent_auctions(make, model, days_back)
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error getting IronPlanet recent auctions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends/market")
async def get_market_trends(
    make: str = Query(..., description="Equipment make"),
    model: str = Query(..., description="Equipment model")
):
    """Get market trends and analysis from IronPlanet data"""
    try:
        service = await get_ironplanet_service()
        result = await service.get_market_trends(make, model)
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error getting IronPlanet market trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_health_status():
    """Get IronPlanet service health status"""
    try:
        service = await get_ironplanet_service()
        result = await service.get_health_status()
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "health": result
        }
        
    except Exception as e:
        logger.error(f"Error getting IronPlanet health status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comprehensive")
async def get_comprehensive_data(
    make: str = Query(..., description="Equipment make"),
    model: str = Query(..., description="Equipment model"),
    include_listings: bool = Query(True, description="Include active listings"),
    include_auctions: bool = Query(True, description="Include recent auctions"),
    include_trends: bool = Query(True, description="Include market trends")
):
    """Get comprehensive IronPlanet data including listings, auctions, and trends"""
    try:
        service = await get_ironplanet_service()
        result = {
            "make": make,
            "model": model,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "IronPlanet"
        }
        
        if include_listings:
            result["active_listings"] = await service.get_active_listings(make, model)
        
        if include_auctions:
            result["recent_auctions"] = await service.get_recent_auctions(make, model)
        
        if include_trends:
            result["market_trends"] = await service.get_market_trends(make, model)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error getting comprehensive IronPlanet data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
