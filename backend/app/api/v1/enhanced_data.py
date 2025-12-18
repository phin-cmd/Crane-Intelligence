"""
Enhanced Data Management API
Handles spec catalog, market intelligence, and data refresh operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
try:
    from ...core.database import get_db
except ImportError:
    try:
        from ...config import SessionLocal
        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
    except ImportError:
        # Fallback if database module not available
        def get_db():
            yield None
# from ...models.enhanced_crane import (
#     CraneListing, MarketTrend, BrokerNetwork, PerformanceMetrics,
#     CraneValuationAnalysis, MarketIntelligence, RentalRates, DataRefreshLog
# )  # Tables don't exist yet
from ...models.spec_catalog import SpecCatalog, ScrapingJob, ScrapingCache, SpecCompleteness, DataRefreshLog
from ...models.crane import Crane, MarketData
from ...services.specs_catalog_service import SpecsCatalogService
from ...services.data_migration_service import data_migration_service

# Create service instance
specs_catalog_service = SpecsCatalogService()
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/enhanced-data", tags=["Enhanced Data Management"])

# Pydantic models for API requests/responses
class SpecCatalogRequest(BaseModel):
    make: str
    model: str
    capacity_min: Optional[float] = None
    capacity_max: Optional[float] = None
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    limit: int = 100

class DataRefreshRequest(BaseModel):
    refresh_type: str  # full_refresh, incremental, csv_import
    data_source: str   # crane_listings, market_trends, etc.

class ScrapingJobRequest(BaseModel):
    source: str
    job_type: str
    config: Dict[str, Any]

@router.get("/spec-catalog/search")
async def search_spec_catalog(
    make: Optional[str] = Query(None, description="Manufacturer name"),
    model: Optional[str] = Query(None, description="Model name"),
    capacity_min: Optional[float] = Query(None, description="Minimum capacity in tons"),
    capacity_max: Optional[float] = Query(None, description="Maximum capacity in tons"),
    year_min: Optional[int] = Query(None, description="Minimum year"),
    year_max: Optional[int] = Query(None, description="Maximum year"),
    limit: int = Query(100, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Search the spec catalog by various criteria"""
    try:
        specs = specs_catalog_service.find_specs_by_criteria(
            make=make,
            model=model,
            capacity_min=capacity_min,
            capacity_max=capacity_max,
            year_min=year_min,
            year_max=year_max,
            limit=limit,
            db=db
        )
        
        return {
            "success": True,
            "count": len(specs),
            "specs": [
                {
                    "spec_id": str(spec.spec_id),
                    "make": spec.make,
                    "model": spec.model,
                    "variant": spec.variant,
                    "capacity_tons": spec.capacity_tons,
                    "boom_length_ft": spec.boom_length_ft,
                    "jib_options_ft": spec.jib_options_ft,
                    "counterweight_lbs": spec.counterweight_lbs,
                    "features": spec.features,
                    "source": spec.source,
                    "last_seen": spec.last_seen.isoformat() if spec.last_seen else None
                }
                for spec in specs
            ]
        }
        
    except Exception as e:
        logger.error(f"Error searching spec catalog: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/spec-catalog/stats")
async def get_spec_catalog_stats(db: Session = Depends(get_db)):
    """Get spec catalog completeness statistics"""
    try:
        stats = specs_catalog_service.get_spec_completeness_stats(db)
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting spec catalog stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crane-listings")
async def get_crane_listings(
    manufacturer: Optional[str] = Query(None, description="Manufacturer filter"),
    crane_type: Optional[str] = Query(None, description="Crane type filter"),
    region: Optional[str] = Query(None, description="Region filter"),
    limit: int = Query(100, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get crane listings with filters"""
    try:
        # Handle case where db might be None
        if db is None:
            return {
                "success": False,
                "count": 0,
                "data": [],
                "message": "Database not available"
            }
        
        # Use existing cranes table instead of non-existent crane_listings
        try:
            from ...models.crane import Crane
        except ImportError:
            return {
                "success": False,
                "count": 0,
                "data": [],
                "message": "Database models not available"
            }
        
        query = db.query(Crane)
        
        if manufacturer:
            query = query.filter(Crane.manufacturer.ilike(f"%{manufacturer}%"))
        
        if crane_type:
            query = query.filter(Crane.condition.ilike(f"%{crane_type}%"))
        
        if region:
            query = query.filter(Crane.location.ilike(f"%{region}%"))
        
        listings = query.limit(limit).all()
        
        return {
            "success": True,
            "count": len(listings),
            "data": [
                {
                    "id": str(listing.id),
                    "title": f"{listing.manufacturer} {listing.model}",
                    "manufacturer": listing.manufacturer,
                    "year": listing.year,
                    "price": float(listing.price) if listing.price else 0,
                    "location": listing.location,
                    "hours": listing.hours,
                    "capacity_tons": float(listing.capacity_tons) if listing.capacity_tons else 0,
                    "crane_type": listing.condition,
                    "region": listing.location,
                    "wear_score": None,
                    "value_score": None,
                    "source": "Database",
                    "scraped_at": listing.created_at.isoformat() if listing.created_at else None
                }
                for listing in listings
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting crane listings: {e}", exc_info=True)
        # Return empty data instead of raising error to prevent frontend crashes
        return {
            "success": False,
            "count": 0,
            "data": [],
            "error": str(e),
            "message": "Unable to load crane listings at this time"
        }

@router.get("/market-trends")
async def get_market_trends(db: Session = Depends(get_db)):
    """Get market trends data"""
    try:
        # Use existing market_data table instead of non-existent market_trends
        from ...models.crane import MarketData
        
        trends = db.query(MarketData).all()
        
        return {
            "success": True,
            "count": len(trends),
            "trends": [
                {
                    "id": str(trend.id),
                    "segment": trend.data_type,
                    "yoy_growth_percent": 0,  # Not available in current schema
                    "key_drivers": "Market analysis based on current data",
                    "buyer_priorities": "Price and condition",
                    "market_size": trend.total_cranes,
                    "price_trend": "Stable",
                    "demand_outlook": "Positive",
                    "trend_date": trend.data_date.isoformat() if trend.data_date else None
                }
                for trend in trends
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting market trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rental-rates")
async def get_rental_rates(
    crane_type: Optional[str] = Query(None, description="Crane type filter"),
    region: Optional[str] = Query(None, description="Region filter"),
    db: Session = Depends(get_db)
):
    """Get rental rates by crane type and region"""
    try:
        query = db.query(RentalRates)
        
        if crane_type:
            query = query.filter(RentalRates.crane_type.ilike(f"%{crane_type}%"))
        
        if region:
            query = query.filter(RentalRates.region == region)
        
        rates = query.all()
        
        return {
            "success": True,
            "count": len(rates),
            "rates": [
                {
                    "id": str(rate.id),
                    "crane_type": rate.crane_type,
                    "tonnage": rate.tonnage,
                    "region": rate.region,
                    "monthly_rate_usd": float(rate.monthly_rate_usd),
                    "annual_rate_usd": float(rate.annual_rate_usd),
                    "daily_rate_usd": float(rate.daily_rate_usd),
                    "rate_date": rate.rate_date.isoformat() if rate.rate_date else None
                }
                for rate in rates
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting rental rates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance-metrics")
async def get_performance_metrics(
    manufacturer: Optional[str] = Query(None, description="Manufacturer filter"),
    model: Optional[str] = Query(None, description="Model filter"),
    db: Session = Depends(get_db)
):
    """Get performance metrics for crane models"""
    try:
        query = db.query(PerformanceMetrics)
        
        if manufacturer:
            query = query.filter(PerformanceMetrics.manufacturer.ilike(f"%{manufacturer}%"))
        
        if model:
            query = query.filter(PerformanceMetrics.model.ilike(f"%{model}%"))
        
        metrics = query.all()
        
        return {
            "success": True,
            "count": len(metrics),
            "metrics": [
                {
                    "id": str(metric.id),
                    "manufacturer": metric.manufacturer,
                    "model": metric.model,
                    "model_key": metric.model_key,
                    "max_capacity_tons": metric.max_capacity_tons,
                    "working_radius_40ft": metric.working_radius_40ft,
                    "working_radius_80ft": metric.working_radius_80ft,
                    "mobility_score": metric.mobility_score,
                    "versatility_score": metric.versatility_score,
                    "boom_utilization": metric.boom_utilization,
                    "fuel_efficiency": metric.fuel_efficiency,
                    "maintenance_cost": metric.maintenance_cost,
                    "reliability_score": metric.reliability_score
                }
                for metric in metrics
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data-refresh")
async def trigger_data_refresh(
    request: DataRefreshRequest,
    db: Session = Depends(get_db)
):
    """Trigger data refresh operation"""
    try:
        # Log the refresh start
        log_entry = DataRefreshLog(
            refresh_type=request.refresh_type,
            data_source=request.data_source,
            status='started',
            created_at=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        
        # Perform the refresh based on type
        if request.refresh_type == 'csv_import':
            results = data_migration_service.migrate_all_data(db)
            
            # Update log entry
            log_entry.status = 'completed'
            log_entry.completed_at = datetime.utcnow()
            log_entry.records_processed = results.get('total_processed', 0)
            log_entry.records_added = results.get('total_added', 0)
            log_entry.records_updated = results.get('total_updated', 0)
            db.commit()
            
            return {
                "success": True,
                "message": "Data refresh completed successfully",
                "log_id": str(log_entry.id),
                "results": results
            }
        else:
            return {
                "success": False,
                "message": f"Refresh type '{request.refresh_type}' not implemented yet"
            }
        
    except Exception as e:
        logger.error(f"Error triggering data refresh: {e}")
        
        # Update log entry with error
        if 'log_entry' in locals():
            log_entry.status = 'failed'
            log_entry.error_message = str(e)
            db.commit()
        
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data-refresh-logs")
async def get_data_refresh_logs(
    limit: int = Query(50, description="Maximum number of logs"),
    db: Session = Depends(get_db)
):
    """Get data refresh operation logs"""
    try:
        logs = db.query(DataRefreshLog).order_by(DataRefreshLog.created_at.desc()).limit(limit).all()
        
        return {
            "success": True,
            "count": len(logs),
            "logs": [
                {
                    "id": str(log.id),
                    "refresh_type": log.refresh_type,
                    "data_source": log.data_source,
                    "status": log.status,
                    "started_at": log.started_at.isoformat() if log.started_at else None,
                    "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                    "records_processed": log.records_processed,
                    "records_added": log.records_added,
                    "records_updated": log.records_updated,
                    "error_message": log.error_message,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                }
                for log in logs
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting data refresh logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def enhanced_data_health_check(db: Session = Depends(get_db)):
    """Health check for enhanced data services"""
    try:
        # Check table counts using existing tables
        from ...models.crane import Crane, MarketData
        from ...models.spec_catalog import SpecCatalog
        
        crane_listings_count = db.query(Crane).count()
        market_trends_count = db.query(MarketData).count()
        spec_catalog_count = db.query(SpecCatalog).count()
        
        return {
            "success": True,
            "message": "Enhanced data services are healthy",
            "data_counts": {
                "crane_listings": crane_listings_count,
                "market_trends": market_trends_count,
                "rental_rates": 0,  # Not available yet
                "performance_metrics": 0,  # Not available yet
                "spec_catalog": spec_catalog_count
            }
        }
        
    except Exception as e:
        logger.error(f"Enhanced data health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
