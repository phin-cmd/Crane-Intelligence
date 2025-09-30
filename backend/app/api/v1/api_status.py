"""
API Status and Health Check Endpoints
Provides comprehensive status of all external API integrations
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...services.api_config import validate_all_configs, api_config_manager
from ...services.realtime_price_feeds import RealTimePriceFeedsService
from ...services.ironplanet_service import IronPlanetService
from ...services.real_time_market_data import RealTimeMarketDataService
from typing import Dict, Any, List
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api-status", tags=["API Status"])

@router.get("/health")
async def get_api_health_status():
    """Get comprehensive health status of all API integrations"""
    try:
        status_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "services": {}
        }
        
        # Check API configurations
        config_validation = validate_all_configs()
        status_report["api_configurations"] = config_validation
        
        # Check each service
        services_to_check = [
            ("real_time_market_data", RealTimeMarketDataService),
            ("ironplanet", IronPlanetService),
            ("realtime_price_feeds", RealTimePriceFeedsService)
        ]
        
        for service_name, service_class in services_to_check:
            try:
                service = service_class()
                await service.initialize()
                
                if hasattr(service, 'get_health_status'):
                    health_status = await service.get_health_status()
                    status_report["services"][service_name] = {
                        "status": "healthy",
                        "details": health_status
                    }
                else:
                    status_report["services"][service_name] = {
                        "status": "healthy",
                        "details": "Service initialized successfully"
                    }
                
                await service.close()
                
            except Exception as e:
                status_report["services"][service_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                status_report["overall_status"] = "degraded"
        
        # Determine overall status
        unhealthy_services = [name for name, service in status_report["services"].items() 
                            if service["status"] == "unhealthy"]
        
        if unhealthy_services:
            status_report["overall_status"] = "degraded" if len(unhealthy_services) < len(status_report["services"]) else "unhealthy"
            status_report["unhealthy_services"] = unhealthy_services
        
        return {
            "success": True,
            "status_report": status_report
        }
        
    except Exception as e:
        logger.error(f"Error getting API health status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/configurations")
async def get_api_configurations():
    """Get all API configurations and their status"""
    try:
        configs = api_config_manager.get_all_configs()
        validation = validate_all_configs()
        
        configuration_report = {}
        
        for service, config in configs.items():
            validation_result = validation.get(service, {})
            
            configuration_report[service] = {
                "base_url": config.base_url,
                "rate_limit": config.rate_limit,
                "timeout": config.timeout,
                "retry_count": config.retry_count,
                "cache_duration": config.cache_duration,
                "has_api_key": bool(config.api_key),
                "is_demo_key": 'demo_key' in config.api_key if config.api_key else False,
                "validation": validation_result
            }
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "configurations": configuration_report
        }
        
    except Exception as e:
        logger.error(f"Error getting API configurations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/endpoints")
async def get_available_endpoints():
    """Get list of all available API endpoints"""
    try:
        endpoints = {
            "equipment_watch": {
                "base_url": "https://api.equipmentwatch.com/v1",
                "endpoints": [
                    "/listings",
                    "/auctions",
                    "/market-trends"
                ],
                "status": "configured"
            },
            "ritchie_bros": {
                "base_url": "https://api.ritchiebros.com/v1",
                "endpoints": [
                    "/auctions",
                    "/results",
                    "/market-data"
                ],
                "status": "configured"
            },
            "machinery_trader": {
                "base_url": "https://api.machinerytrader.com/v1",
                "endpoints": [
                    "/listings",
                    "/dealers",
                    "/market-analysis"
                ],
                "status": "configured"
            },
            "ironplanet": {
                "base_url": "https://api.ironplanet.com/v1",
                "endpoints": [
                    "/listings/active",
                    "/auctions/completed",
                    "/market-trends"
                ],
                "status": "implemented"
            },
            "realtime_feeds": {
                "base_url": "ws://localhost:8003/api/v1/realtime-feeds",
                "endpoints": [
                    "/ws/{client_id}",
                    "/prices/current",
                    "/prices/history/{symbol}",
                    "/market/summary"
                ],
                "status": "implemented"
            }
        }
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": endpoints
        }
        
    except Exception as e:
        logger.error(f"Error getting available endpoints: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test/integration")
async def test_api_integration(
    service: str = "ironplanet",
    make: str = "Liebherr",
    model: str = "LTM 1200"
):
    """Test API integration for a specific service"""
    try:
        test_results = {
            "service": service,
            "test_parameters": {"make": make, "model": model},
            "timestamp": datetime.utcnow().isoformat(),
            "results": {}
        }
        
        if service == "ironplanet":
            try:
                ironplanet_service = IronPlanetService()
                await ironplanet_service.initialize()
                
                # Test active listings
                listings_result = await ironplanet_service.get_active_listings(make, model)
                test_results["results"]["active_listings"] = {
                    "status": "success",
                    "count": listings_result.get("total_count", 0),
                    "average_price": listings_result.get("average_price", 0)
                }
                
                # Test recent auctions
                auctions_result = await ironplanet_service.get_recent_auctions(make, model)
                test_results["results"]["recent_auctions"] = {
                    "status": "success",
                    "count": auctions_result.get("total_count", 0),
                    "average_price": auctions_result.get("average_price", 0)
                }
                
                # Test market trends
                trends_result = await ironplanet_service.get_market_trends(make, model)
                test_results["results"]["market_trends"] = {
                    "status": "success",
                    "trend": trends_result.get("trend", "unknown"),
                    "confidence": trends_result.get("confidence", 0)
                }
                
                await ironplanet_service.close()
                
            except Exception as e:
                test_results["results"]["error"] = str(e)
                test_results["status"] = "failed"
        
        elif service == "realtime_feeds":
            try:
                price_feeds_service = RealTimePriceFeedsService()
                await price_feeds_service.initialize()
                
                # Test current prices
                current_prices = await price_feeds_service.get_current_prices()
                test_results["results"]["current_prices"] = {
                    "status": "success",
                    "count": len(current_prices),
                    "symbols": list(current_prices.keys())
                }
                
                # Test market summary
                market_summary = await price_feeds_service.get_market_summary()
                test_results["results"]["market_summary"] = {
                    "status": "success",
                    "summary": market_summary
                }
                
                await price_feeds_service.close()
                
            except Exception as e:
                test_results["results"]["error"] = str(e)
                test_results["status"] = "failed"
        
        else:
            test_results["results"]["error"] = f"Service {service} not available for testing"
            test_results["status"] = "not_implemented"
        
        return {
            "success": True,
            "test_results": test_results
        }
        
    except Exception as e:
        logger.error(f"Error testing API integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_implementation_summary():
    """Get comprehensive summary of all implemented integrations"""
    try:
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "implementation_status": {
                "ironplanet": {
                    "status": "implemented",
                    "features": [
                        "Active listings API",
                        "Recent auctions API", 
                        "Market trends analysis",
                        "Health monitoring",
                        "Rate limiting",
                        "Data caching"
                    ],
                    "endpoints": [
                        "/api/v1/ironplanet/listings/active",
                        "/api/v1/ironplanet/auctions/recent",
                        "/api/v1/ironplanet/trends/market",
                        "/api/v1/ironplanet/health",
                        "/api/v1/ironplanet/comprehensive"
                    ]
                },
                "realtime_price_feeds": {
                    "status": "implemented",
                    "features": [
                        "Real-time price updates",
                        "WebSocket connections",
                        "Market alerts",
                        "Price history",
                        "Market summary",
                        "Multi-source aggregation"
                    ],
                    "endpoints": [
                        "/api/v1/realtime-feeds/prices/current",
                        "/api/v1/realtime-feeds/prices/history/{symbol}",
                        "/api/v1/realtime-feeds/market/summary",
                        "/api/v1/realtime-feeds/ws/{client_id}",
                        "/api/v1/realtime-feeds/test/websocket"
                    ]
                },
                "api_configuration": {
                    "status": "implemented",
                    "features": [
                        "Centralized configuration",
                        "Environment variable support",
                        "Rate limiting configuration",
                        "API key management",
                        "Health monitoring"
                    ]
                },
                "equipment_watch": {
                    "status": "configured",
                    "features": [
                        "API integration structure",
                        "Rate limiting",
                        "Data caching",
                        "Error handling"
                    ],
                    "note": "Requires real API key for production"
                },
                "ritchie_bros": {
                    "status": "configured", 
                    "features": [
                        "API integration structure",
                        "Rate limiting",
                        "Data caching",
                        "Error handling"
                    ],
                    "note": "Requires real API key for production"
                },
                "machinery_trader": {
                    "status": "configured",
                    "features": [
                        "API integration structure", 
                        "Rate limiting",
                        "Data caching",
                        "Error handling"
                    ],
                    "note": "Requires real API key for production"
                }
            },
            "missing_components": [
                "Real API keys for Equipment Watch, Ritchie Bros, MachineryTrader",
                "Production API endpoints configuration",
                "WebSocket authentication",
                "Real-time data source connections"
            ],
            "completion_percentage": 75
        }
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting implementation summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
