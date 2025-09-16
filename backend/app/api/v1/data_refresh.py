"""
Data Refresh API Endpoints
Handles data normalization and scraping operations
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path

from ...services.data_refresh_service import DataRefreshService
from ...services.bigge_specs_scraper import BiggeSpecsScraper
from ...services.specs_catalog_service import SpecsCatalogService
from ...api.v1.auth import get_current_user
from ...models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data-refresh", tags=["Data Refresh"])

# Initialize services
data_refresh_service = DataRefreshService()
bigge_scraper = BiggeSpecsScraper()
specs_catalog_service = SpecsCatalogService()

class DataRefreshRequest(BaseModel):
    """Request model for data refresh operations"""
    refresh_type: str = "incremental"  # "full" or "incremental"
    force_refresh: bool = False

class DataRefreshResponse(BaseModel):
    """Response model for data refresh operations"""
    success: bool
    message: str
    refresh_id: Optional[str] = None
    estimated_duration: Optional[int] = None  # seconds
    data: Optional[Dict[str, Any]] = None

@router.post("/start", response_model=DataRefreshResponse)
async def start_data_refresh(
    request: DataRefreshRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Start a data refresh operation
    Requires authentication and appropriate permissions
    """
    try:
        # Check if user has permission to trigger data refresh
        if current_user.user_role.value not in ['admin', 'crane_rental_company']:
            raise HTTPException(
                status_code=403, 
                detail="Insufficient permissions to trigger data refresh"
            )
        
        # Start background task
        if request.refresh_type == "full":
            background_tasks.add_task(run_full_refresh)
            estimated_duration = 300  # 5 minutes
            message = "Full data refresh started. This will normalize CSV data and scrape fresh listings."
        else:
            background_tasks.add_task(run_incremental_refresh)
            estimated_duration = 120  # 2 minutes
            message = "Incremental data refresh started. This will scrape fresh listings only."
        
        refresh_id = f"refresh_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return DataRefreshResponse(
            success=True,
            message=message,
            refresh_id=refresh_id,
            estimated_duration=estimated_duration
        )
        
    except Exception as e:
        logger.error(f"Error starting data refresh: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=Dict[str, Any])
async def get_refresh_status(current_user: User = Depends(get_current_user)):
    """
    Get current data refresh status and statistics
    """
    try:
        # Get data statistics
        stats = data_refresh_service.get_data_statistics()
        
        # Get recent refresh reports
        recent_reports = get_recent_refresh_reports()
        
        return {
            "success": True,
            "data_statistics": stats,
            "recent_refreshes": recent_reports,
            "last_checked": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting refresh status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics", response_model=Dict[str, Any])
async def get_data_statistics(current_user: User = Depends(get_current_user)):
    """
    Get detailed data statistics
    """
    try:
        stats = data_refresh_service.get_data_statistics()
        
        return {
            "success": True,
            "statistics": stats,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting data statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/normalize", response_model=DataRefreshResponse)
async def normalize_existing_data(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Normalize existing CSV data without scraping
    """
    try:
        # Check permissions
        if current_user.user_role.value not in ['admin', 'crane_rental_company']:
            raise HTTPException(
                status_code=403, 
                detail="Insufficient permissions to normalize data"
            )
        
        # Start background task
        background_tasks.add_task(run_normalization_only)
        
        return DataRefreshResponse(
            success=True,
            message="Data normalization started. This will process existing CSV files.",
            estimated_duration=180  # 3 minutes
        )
        
    except Exception as e:
        logger.error(f"Error starting data normalization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scrape", response_model=DataRefreshResponse)
async def scrape_fresh_data(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Scrape fresh data from marketplaces without normalizing CSV data
    """
    try:
        # Check permissions
        if current_user.user_role.value not in ['admin', 'crane_rental_company']:
            raise HTTPException(
                status_code=403, 
                detail="Insufficient permissions to scrape data"
            )
        
        # Start background task
        background_tasks.add_task(run_scraping_only)
        
        return DataRefreshResponse(
            success=True,
            message="Data scraping started. This will fetch fresh listings from marketplaces.",
            estimated_duration=120  # 2 minutes
        )
        
    except Exception as e:
        logger.error(f"Error starting data scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scrape-bigge", response_model=DataRefreshResponse)
async def scrape_bigge_specifications(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Scrape Bigge Equipment specifications for detailed crane data
    """
    try:
        # Check permissions
        if current_user.user_role.value not in ['admin', 'crane_rental_company']:
            raise HTTPException(
                status_code=403, 
                detail="Insufficient permissions to scrape Bigge specifications"
            )
        
        # Start background task
        background_tasks.add_task(run_bigge_scraping)
        
        return DataRefreshResponse(
            success=True,
            message="Bigge specifications scraping started. This will extract detailed crane specifications.",
            estimated_duration=300  # 5 minutes
        )
        
    except Exception as e:
        logger.error(f"Error starting Bigge scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/specs-catalog/stats", response_model=Dict[str, Any])
async def get_specs_catalog_stats(current_user: User = Depends(get_current_user)):
    """
    Get specification catalog statistics
    """
    try:
        stats = specs_catalog_service.get_spec_stats()
        
        return {
            "success": True,
            "statistics": stats,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting specs catalog stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/specs-catalog/search", response_model=Dict[str, Any])
async def search_specifications(
    make: Optional[str] = None,
    model: Optional[str] = None,
    capacity_min: Optional[float] = None,
    capacity_max: Optional[float] = None,
    query: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Search specifications in the catalog
    """
    try:
        if make and model:
            specs = specs_catalog_service.get_specs_by_make_model(make, model)
        elif capacity_min is not None and capacity_max is not None:
            specs = specs_catalog_service.get_specs_by_capacity_range(capacity_min, capacity_max)
        elif query:
            specs = specs_catalog_service.search_specs(query)
        else:
            raise HTTPException(status_code=400, detail="Must provide make/model, capacity range, or query")
        
        return {
            "success": True,
            "count": len(specs),
            "specifications": specs,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error searching specifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/specs-catalog/enrich", response_model=Dict[str, Any])
async def enrich_crane_listing(
    listing: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Enrich a crane listing with specification data
    """
    try:
        enriched_listing = specs_catalog_service.enrich_crane_listing(listing)
        
        return {
            "success": True,
            "enriched_listing": enriched_listing,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error enriching crane listing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task functions
async def run_full_refresh():
    """Run full data refresh in background"""
    try:
        logger.info("Starting full data refresh background task")
        result = await data_refresh_service.full_data_refresh()
        logger.info(f"Full data refresh completed: {result}")
    except Exception as e:
        logger.error(f"Error in full data refresh background task: {e}")

async def run_incremental_refresh():
    """Run incremental data refresh in background"""
    try:
        logger.info("Starting incremental data refresh background task")
        result = await data_refresh_service.incremental_refresh()
        logger.info(f"Incremental data refresh completed: {result}")
    except Exception as e:
        logger.error(f"Error in incremental data refresh background task: {e}")

async def run_normalization_only():
    """Run data normalization only in background"""
    try:
        logger.info("Starting data normalization background task")
        result = data_refresh_service.normalization_service.normalize_all_data()
        logger.info(f"Data normalization completed: {result}")
    except Exception as e:
        logger.error(f"Error in data normalization background task: {e}")

async def run_scraping_only():
    """Run data scraping only in background"""
    try:
        logger.info("Starting data scraping background task")
        result = await data_refresh_service.scraping_service.scrape_all_marketplaces()
        logger.info(f"Data scraping completed: {result}")
    except Exception as e:
        logger.error(f"Error in data scraping background task: {e}")

async def run_bigge_scraping():
    """Run Bigge specifications scraping in background"""
    try:
        logger.info("Starting Bigge specifications scraping background task")
        result = await bigge_scraper.scrape_all_specifications()
        logger.info(f"Bigge specifications scraping completed: {result}")
        
        # Load scraped specifications into catalog
        if result.get('output_file'):
            output_file = Path(result['output_file'])
            if output_file.exists():
                loaded_count = specs_catalog_service.load_specs_from_file(output_file)
                logger.info(f"Loaded {loaded_count} specifications into catalog")
    except Exception as e:
        logger.error(f"Error in Bigge scraping background task: {e}")

def get_recent_refresh_reports() -> list:
    """Get recent refresh reports"""
    try:
        from pathlib import Path
        import json
        
        reports_dir = Path("data/processed")
        if not reports_dir.exists():
            return []
        
        # Find recent report files
        report_files = list(reports_dir.glob("refresh_report_*.json"))
        report_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        recent_reports = []
        for report_file in report_files[:5]:  # Last 5 reports
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                    recent_reports.append({
                        'file': report_file.name,
                        'refresh_type': report_data.get('refresh_summary', {}).get('type', 'unknown'),
                        'start_time': report_data.get('refresh_summary', {}).get('start_time', ''),
                        'duration_seconds': report_data.get('refresh_summary', {}).get('duration_seconds', 0),
                        'total_records': report_data.get('refresh_summary', {}).get('total_records', 0),
                        'errors_count': report_data.get('refresh_summary', {}).get('errors_count', 0)
                    })
            except Exception as e:
                logger.warning(f"Error reading report file {report_file}: {e}")
                continue
        
        return recent_reports
        
    except Exception as e:
        logger.error(f"Error getting recent refresh reports: {e}")
        return []
