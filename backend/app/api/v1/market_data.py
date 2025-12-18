"""
Market Data API for Real-time Terminal Display
Provides live market data for the Bloomberg Terminal-style valuation interface
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from ...core.database import get_db
# from ...models.enhanced_crane import (
#     CraneListing, MarketTrend, RentalRates, PerformanceMetrics
# )  # Tables don't exist yet
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market-data", tags=["Market Data"])

@router.get("/live-stats")
async def get_live_market_stats(db: Session = Depends(get_db)):
    """Get live market statistics for terminal display"""
    try:
        # Use existing cranes table instead of non-existent crane_listings
        from ...models.crane import Crane
        
        # Get total listings count
        total_listings = db.query(Crane).count()
        
        # Get average price
        avg_price_result = db.query(func.avg(Crane.price)).filter(
            Crane.price.isnot(None)
        ).scalar()
        avg_price = float(avg_price_result) if avg_price_result else 0
        
        # Get total market value (sum of all prices)
        total_market_value = db.query(func.sum(Crane.price)).filter(
            Crane.price.isnot(None)
        ).scalar()
        total_market_value = float(total_market_value) if total_market_value else 0
        
        # Get recent listings (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_listings = db.query(Crane).filter(
            Crane.created_at >= recent_cutoff
        ).count()
        
        # Get price range
        min_price = db.query(func.min(Crane.price)).filter(
            Crane.price.isnot(None)
        ).scalar()
        max_price = db.query(func.max(Crane.price)).filter(
            Crane.price.isnot(None)
        ).scalar()
        
        # Get manufacturer distribution
        manufacturer_stats = db.query(
            Crane.manufacturer,
            func.count(Crane.id).label('count'),
            func.avg(Crane.price).label('avg_price')
        ).filter(
            Crane.manufacturer.isnot(None)
        ).group_by(Crane.manufacturer).order_by(desc('count')).limit(10).all()
        
        # Get regional distribution
        regional_stats = db.query(
            Crane.location,
            func.count(Crane.id).label('count'),
            func.avg(Crane.price).label('avg_price')
        ).filter(
            Crane.location.isnot(None)
        ).group_by(Crane.location).order_by(desc('count')).limit(10).all()
        
        # Get capacity distribution
        capacity_stats = db.query(
            func.case(
                (Crane.capacity_tons < 100, '<100T'),
                (Crane.capacity_tons < 200, '100-200T'),
                (Crane.capacity_tons < 300, '200-300T'),
                (Crane.capacity_tons < 400, '300-400T'),
                (Crane.capacity_tons < 500, '400-500T'),
                else_='>500T'
            ).label('capacity_range'),
            func.count(Crane.id).label('count')
        ).filter(
            Crane.capacity_tons.isnot(None)
        ).group_by('capacity_range').all()
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "market_stats": {
                "total_listings": total_listings,
                "average_price": round(avg_price, 2),
                "total_market_value": round(total_market_value, 2),
                "recent_listings_24h": recent_listings,
                "price_range": {
                    "min": float(min_price) if min_price else 0,
                    "max": float(max_price) if max_price else 0
                }
            },
            "manufacturer_distribution": [
                {
                    "manufacturer": stat.manufacturer,
                    "count": stat.count,
                    "avg_price": round(float(stat.avg_price), 2) if stat.avg_price else 0
                }
                for stat in manufacturer_stats
            ],
            "regional_distribution": [
                {
                    "region": stat.region,
                    "count": stat.count,
                    "avg_price": round(float(stat.avg_price), 2) if stat.avg_price else 0
                }
                for stat in regional_stats
            ],
            "capacity_distribution": [
                {
                    "capacity_range": stat.capacity_range,
                    "count": stat.count
                }
                for stat in capacity_stats
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting live market stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ticker-data")
async def get_ticker_data(db: Session = Depends(get_db)):
    """Get ticker-style market data for scrolling display"""
    try:
        # Get top manufacturers with their average prices and recent changes
        manufacturer_data = db.query(
            CraneListing.manufacturer,
            func.avg(CraneListing.price).label('avg_price'),
            func.count(CraneListing.id).label('count')
        ).filter(
            CraneListing.is_active == True,
            CraneListing.manufacturer.isnot(None),
            CraneListing.price.isnot(None)
        ).group_by(CraneListing.manufacturer).order_by(desc('count')).limit(8).all()
        
        # Get regional indices
        regional_data = db.query(
            CraneListing.region,
            func.avg(CraneListing.price).label('avg_price'),
            func.count(CraneListing.id).label('count')
        ).filter(
            CraneListing.is_active == True,
            CraneListing.region.isnot(None),
            CraneListing.price.isnot(None)
        ).group_by(CraneListing.region).order_by(desc('count')).limit(5).all()
        
        # Calculate market index (weighted average of all prices)
        market_index = db.query(func.avg(CraneListing.price)).filter(
            CraneListing.is_active == True,
            CraneListing.price.isnot(None)
        ).scalar()
        market_index = float(market_index) if market_index else 0
        
        # Generate ticker items
        ticker_items = []
        
        # Add market index
        ticker_items.append({
            "symbol": "CRI",
            "price": round(market_index / 1000, 1),  # Scale down for display
            "change": "+1.2%",  # Mock change for now
            "change_type": "up"
        })
        
        # Add manufacturer data
        for i, mfg in enumerate(manufacturer_data):
            if mfg.manufacturer:
                # Scale price for display
                display_price = round(float(mfg.avg_price) / 1000, 1)
                # Mock change percentage
                change = f"+{round((i + 1) * 0.3, 1)}%" if i % 2 == 0 else f"-{round((i + 1) * 0.2, 1)}%"
                change_type = "up" if i % 2 == 0 else "down"
                
                ticker_items.append({
                    "symbol": mfg.manufacturer.upper()[:8],  # Limit symbol length
                    "price": display_price,
                    "change": change,
                    "change_type": change_type
                })
        
        # Add regional data
        for i, region in enumerate(regional_data):
            if region.region:
                display_price = round(float(region.avg_price) / 1000, 1)
                change = f"+{round((i + 1) * 0.4, 1)}%"
                change_type = "up"
                
                ticker_items.append({
                    "symbol": f"{region.region[:2].upper()}-CRANE",
                    "price": display_price,
                    "change": change,
                    "change_type": change_type
                })
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "ticker_items": ticker_items
        }
        
    except Exception as e:
        logger.error(f"Error getting ticker data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/terminal-dashboard")
async def get_terminal_dashboard_data(db: Session = Depends(get_db)):
    """Get comprehensive dashboard data for terminal display"""
    try:
        # Get market index
        market_index = db.query(func.avg(CraneListing.price)).filter(
            CraneListing.is_active == True,
            CraneListing.price.isnot(None)
        ).scalar()
        market_index = float(market_index) if market_index else 0
        
        # Get average deal size
        avg_deal_size = db.query(func.avg(CraneListing.price)).filter(
            CraneListing.is_active == True,
            CraneListing.price.isnot(None)
        ).scalar()
        avg_deal_size = float(avg_deal_size) if avg_deal_size else 0
        
        # Get active listings count
        active_listings = db.query(CraneListing).filter(CraneListing.is_active == True).count()
        
        # Get 24h volume (sum of prices from recent listings)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        volume_24h = db.query(func.sum(CraneListing.price)).filter(
            CraneListing.is_active == True,
            CraneListing.scraped_at >= recent_cutoff,
            CraneListing.price.isnot(None)
        ).scalar()
        volume_24h = float(volume_24h) if volume_24h else 0
        
        # Get confidence score (based on data completeness)
        total_listings = db.query(CraneListing).filter(CraneListing.is_active == True).count()
        complete_listings = db.query(CraneListing).filter(
            CraneListing.is_active == True,
            CraneListing.price.isnot(None),
            CraneListing.capacity_tons.isnot(None),
            CraneListing.hours.isnot(None)
        ).count()
        confidence_score = round((complete_listings / total_listings * 100), 1) if total_listings > 0 else 0
        
        # Get risk level (based on price volatility)
        price_std = db.query(func.stddev(CraneListing.price)).filter(
            CraneListing.is_active == True,
            CraneListing.price.isnot(None)
        ).scalar()
        price_std = float(price_std) if price_std else 0
        risk_level = "LOW" if price_std < 500000 else "MEDIUM" if price_std < 1000000 else "HIGH"
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "dashboard_data": {
                "market_index": round(market_index / 1000, 1),
                "avg_deal_size": round(avg_deal_size / 1000000, 1),
                "active_listings": active_listings,
                "volume_24h": round(volume_24h / 1000000, 1),
                "confidence": confidence_score,
                "risk_level": risk_level
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting terminal dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comparable-sales")
async def get_comparable_sales(
    manufacturer: Optional[str] = Query(None, description="Manufacturer filter"),
    capacity_min: Optional[float] = Query(None, description="Minimum capacity"),
    capacity_max: Optional[float] = Query(None, description="Maximum capacity"),
    year_min: Optional[int] = Query(None, description="Minimum year"),
    year_max: Optional[int] = Query(None, description="Maximum year"),
    limit: int = Query(10, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get comparable sales for valuation analysis"""
    try:
        query = db.query(CraneListing).filter(
            CraneListing.is_active == True,
            CraneListing.price.isnot(None)
        )
        
        if manufacturer:
            query = query.filter(CraneListing.manufacturer.ilike(f"%{manufacturer}%"))
        
        if capacity_min:
            query = query.filter(CraneListing.capacity_tons >= capacity_min)
        
        if capacity_max:
            query = query.filter(CraneListing.capacity_tons <= capacity_max)
        
        if year_min:
            query = query.filter(CraneListing.year >= year_min)
        
        if year_max:
            query = query.filter(CraneListing.year <= year_max)
        
        # Order by most recent and limit results
        comparables = query.order_by(desc(CraneListing.scraped_at)).limit(limit).all()
        
        return {
            "success": True,
            "count": len(comparables),
            "comparables": [
                {
                    "id": str(comp.id),
                    "manufacturer": comp.manufacturer,
                    "model": comp.title.split(' ')[1] if len(comp.title.split(' ')) > 1 else "N/A",
                    "year": comp.year,
                    "capacity": comp.capacity_tons,
                    "hours": comp.hours,
                    "price": float(comp.price),
                    "price_per_ton": round(float(comp.price) / comp.capacity_tons, 0) if comp.capacity_tons else 0,
                    "location": comp.location,
                    "region": comp.region,
                    "source": comp.source,
                    "scraped_at": comp.scraped_at.isoformat() if comp.scraped_at else None
                }
                for comp in comparables
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting comparable sales: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-trends")
async def get_market_trends_data(db: Session = Depends(get_db)):
    """Get market trends for terminal display"""
    try:
        trends = db.query(MarketTrend).order_by(desc(MarketTrend.trend_date)).limit(10).all()
        
        return {
            "success": True,
            "count": len(trends),
            "trends": [
                {
                    "id": str(trend.id),
                    "segment": trend.segment,
                    "yoy_growth_percent": trend.yoy_growth_percent,
                    "key_drivers": trend.key_drivers,
                    "buyer_priorities": trend.buyer_priorities,
                    "market_size": trend.market_size,
                    "price_trend": trend.price_trend,
                    "demand_outlook": trend.demand_outlook,
                    "trend_date": trend.trend_date.isoformat() if trend.trend_date else None
                }
                for trend in trends
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting market trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))
