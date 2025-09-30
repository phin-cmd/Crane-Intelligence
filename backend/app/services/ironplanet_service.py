"""
IronPlanet Marketplace Data Integration Service
Provides real-time auction and listing data from IronPlanet marketplace
"""

import asyncio
import aiohttp
import logging
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import hashlib
import redis
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

@dataclass
class IronPlanetListing:
    """IronPlanet marketplace listing"""
    listing_id: str
    title: str
    price: float
    year: int
    hours: int
    location: str
    condition: str
    listing_date: datetime
    auction_end_date: Optional[datetime] = None
    current_bid: Optional[float] = None
    reserve_met: bool = False
    url: Optional[str] = None
    seller: Optional[str] = None
    features: List[str] = None
    images: List[str] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []
        if self.images is None:
            self.images = []

@dataclass
class IronPlanetAuction:
    """IronPlanet auction data"""
    auction_id: str
    title: str
    final_price: float
    year: int
    hours: int
    location: str
    condition: str
    auction_date: datetime
    bid_count: int
    reserve_met: bool
    url: Optional[str] = None
    seller: Optional[str] = None
    features: List[str] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []

class IronPlanetService:
    """IronPlanet marketplace data service with real API integration"""
    
    def __init__(self):
        self.session = None
        self.redis_client = None
        self.cache_duration = 1800  # 30 minutes cache
        self.rate_limits = {
            'ironplanet': {'requests': 0, 'last_reset': time.time()}
        }
        self.api_key = None
        self.base_url = "https://api.ironplanet.com/v1"
        
    async def initialize(self, api_key: str = None):
        """Initialize the service with API key"""
        try:
            self.api_key = api_key or "demo_key_ironplanet_2024"
            
            # Initialize aiohttp session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'Crane Intelligence Platform/1.0',
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip, deflate',
                    'Authorization': f'Bearer {self.api_key}',
                    'X-API-Version': '1.0'
                }
            )
            
            # Initialize Redis for caching (optional)
            try:
                self.redis_client = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
                await self.redis_client.ping()
                logger.info("Redis connection established for IronPlanet data caching")
            except Exception as e:
                logger.warning(f"Redis not available for IronPlanet, using in-memory cache: {e}")
                self.redis_client = None
                
        except Exception as e:
            logger.error(f"Failed to initialize IronPlanet service: {e}")
            raise
    
    async def close(self):
        """Close the service and cleanup resources"""
        if self.session:
            await self.session.close()
        if self.redis_client:
            await self.redis_client.close()
    
    async def _check_rate_limit(self, service: str, max_requests: int = 100, window: int = 3600) -> bool:
        """Check if we're within rate limits"""
        current_time = time.time()
        rate_limit = self.rate_limits[service]
        
        # Reset counter if window has passed
        if current_time - rate_limit['last_reset'] > window:
            rate_limit['requests'] = 0
            rate_limit['last_reset'] = current_time
        
        return rate_limit['requests'] < max_requests
    
    async def _increment_rate_limit(self, service: str):
        """Increment rate limit counter"""
        self.rate_limits[service]['requests'] += 1
    
    async def _cache_data(self, key: str, data: Any):
        """Cache data with TTL"""
        try:
            if self.redis_client:
                cache_key = f"ironplanet:{key}"
                await self.redis_client.setex(
                    cache_key, 
                    self.cache_duration, 
                    json.dumps(data, default=str)
                )
        except Exception as e:
            logger.warning(f"Failed to cache IronPlanet data: {e}")
    
    async def _get_cached_data(self, key: str) -> Optional[Any]:
        """Get cached data"""
        try:
            if self.redis_client:
                cache_key = f"ironplanet:{key}"
                cached = await self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
        except Exception as e:
            logger.warning(f"Failed to get cached IronPlanet data: {e}")
        return None
    
    async def get_active_listings(self, make: str, model: str, category: str = "crane") -> Dict[str, Any]:
        """Fetch active listings from IronPlanet marketplace"""
        try:
            # Check rate limits
            if not await self._check_rate_limit('ironplanet', max_requests=200, window=3600):
                logger.warning("IronPlanet rate limit exceeded, using cached data")
                return await self._get_cached_data(f"listings_{make}_{model}")
            
            # IronPlanet API endpoint for active listings
            api_url = f"{self.base_url}/listings/active"
            params = {
                'make': make,
                'model': model,
                'category': category,
                'status': 'active',
                'limit': 50,
                'sort': 'price_asc'
            }
            
            # Make API call
            async with self.session.get(api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    await self._increment_rate_limit('ironplanet')
                    
                    # Process listings
                    listings = []
                    for item in data.get('listings', []):
                        listing = IronPlanetListing(
                            listing_id=item.get('id', ''),
                            title=item.get('title', ''),
                            price=float(item.get('price', 0)),
                            year=int(item.get('year', 0)),
                            hours=int(item.get('hours', 0)),
                            location=item.get('location', ''),
                            condition=item.get('condition', ''),
                            listing_date=datetime.fromisoformat(item.get('listing_date', datetime.now().isoformat())),
                            auction_end_date=datetime.fromisoformat(item.get('auction_end_date', '')) if item.get('auction_end_date') else None,
                            current_bid=float(item.get('current_bid', 0)) if item.get('current_bid') else None,
                            reserve_met=item.get('reserve_met', False),
                            url=item.get('url', ''),
                            seller=item.get('seller', ''),
                            features=item.get('features', []),
                            images=item.get('images', [])
                        )
                        listings.append(listing)
                    
                    # Cache the data
                    await self._cache_data(f"listings_{make}_{model}", {
                        "listings": [listing.__dict__ for listing in listings],
                        "total_count": len(listings),
                        "last_updated": datetime.now().isoformat()
                    })
                    
                    return {
                        "listings": [listing.__dict__ for listing in listings],
                        "total_count": len(listings),
                        "average_price": sum(l.price for l in listings) / len(listings) if listings else 0,
                        "price_range": [min(l.price for l in listings), max(l.price for l in listings)] if listings else [0, 0],
                        "market_activity": "high" if len(listings) > 20 else "medium" if len(listings) > 10 else "low",
                        "source": "IronPlanet",
                        "last_updated": datetime.now().isoformat()
                    }
                else:
                    logger.error(f"IronPlanet API error: {response.status}")
                    return await self._get_cached_data(f"listings_{make}_{model}")
            
        except Exception as e:
            logger.error(f"IronPlanet API error: {e}")
            # Return cached data if available
            cached_data = await self._get_cached_data(f"listings_{make}_{model}")
            if cached_data:
                return cached_data
            return {"listings": [], "total_count": 0, "average_price": 0, "price_range": [0, 0], "market_activity": "low", "source": "IronPlanet", "error": str(e)}
    
    async def get_recent_auctions(self, make: str, model: str, days_back: int = 30) -> Dict[str, Any]:
        """Fetch recent auction results from IronPlanet"""
        try:
            # Check rate limits
            if not await self._check_rate_limit('ironplanet', max_requests=150, window=3600):
                logger.warning("IronPlanet rate limit exceeded, using cached data")
                return await self._get_cached_data(f"auctions_{make}_{model}")
            
            # IronPlanet API endpoint for recent auctions
            api_url = f"{self.base_url}/auctions/completed"
            params = {
                'make': make,
                'model': model,
                'days_back': days_back,
                'limit': 100,
                'sort': 'auction_date_desc'
            }
            
            # Make API call
            async with self.session.get(api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    await self._increment_rate_limit('ironplanet')
                    
                    # Process auctions
                    auctions = []
                    for item in data.get('auctions', []):
                        auction = IronPlanetAuction(
                            auction_id=item.get('id', ''),
                            title=item.get('title', ''),
                            final_price=float(item.get('final_price', 0)),
                            year=int(item.get('year', 0)),
                            hours=int(item.get('hours', 0)),
                            location=item.get('location', ''),
                            condition=item.get('condition', ''),
                            auction_date=datetime.fromisoformat(item.get('auction_date', datetime.now().isoformat())),
                            bid_count=int(item.get('bid_count', 0)),
                            reserve_met=item.get('reserve_met', False),
                            url=item.get('url', ''),
                            seller=item.get('seller', ''),
                            features=item.get('features', [])
                        )
                        auctions.append(auction)
                    
                    # Cache the data
                    await self._cache_data(f"auctions_{make}_{model}", {
                        "auctions": [auction.__dict__ for auction in auctions],
                        "total_count": len(auctions),
                        "last_updated": datetime.now().isoformat()
                    })
                    
                    return {
                        "auctions": [auction.__dict__ for auction in auctions],
                        "total_count": len(auctions),
                        "average_price": sum(a.final_price for a in auctions) / len(auctions) if auctions else 0,
                        "price_range": [min(a.final_price for a in auctions), max(a.final_price for a in auctions)] if auctions else [0, 0],
                        "reserve_met_rate": sum(1 for a in auctions if a.reserve_met) / len(auctions) if auctions else 0,
                        "source": "IronPlanet",
                        "last_updated": datetime.now().isoformat()
                    }
                else:
                    logger.error(f"IronPlanet API error: {response.status}")
                    return await self._get_cached_data(f"auctions_{make}_{model}")
            
        except Exception as e:
            logger.error(f"IronPlanet API error: {e}")
            # Return cached data if available
            cached_data = await self._get_cached_data(f"auctions_{make}_{model}")
            if cached_data:
                return cached_data
            return {"auctions": [], "total_count": 0, "average_price": 0, "price_range": [0, 0], "reserve_met_rate": 0, "source": "IronPlanet", "error": str(e)}
    
    async def get_market_trends(self, make: str, model: str) -> Dict[str, Any]:
        """Get market trends and analysis from IronPlanet data"""
        try:
            # Get both active listings and recent auctions
            listings_data = await self.get_active_listings(make, model)
            auctions_data = await self.get_recent_auctions(make, model)
            
            # Analyze trends
            all_prices = []
            all_prices.extend([l.get('price', 0) for l in listings_data.get('listings', [])])
            all_prices.extend([a.get('final_price', 0) for a in auctions_data.get('auctions', [])])
            
            if all_prices:
                avg_price = sum(all_prices) / len(all_prices)
                price_std = (sum((p - avg_price) ** 2 for p in all_prices) / len(all_prices)) ** 0.5
                
                # Determine trend
                if len(auctions_data.get('auctions', [])) > 1:
                    recent_auctions = sorted(auctions_data.get('auctions', []), 
                                           key=lambda x: x.get('auction_date', ''), reverse=True)[:5]
                    if len(recent_auctions) >= 2:
                        recent_avg = sum(a.get('final_price', 0) for a in recent_auctions) / len(recent_auctions)
                        older_auctions = sorted(auctions_data.get('auctions', []), 
                                              key=lambda x: x.get('auction_date', ''), reverse=True)[5:10]
                        if len(older_auctions) >= 2:
                            older_avg = sum(a.get('final_price', 0) for a in older_auctions) / len(older_auctions)
                            trend = "rising" if recent_avg > older_avg * 1.05 else "falling" if recent_avg < older_avg * 0.95 else "stable"
                        else:
                            trend = "stable"
                    else:
                        trend = "stable"
                else:
                    trend = "stable"
                
                return {
                    "trend": trend,
                    "average_price": avg_price,
                    "price_volatility": price_std / avg_price if avg_price > 0 else 0,
                    "market_activity": "high" if len(all_prices) > 30 else "medium" if len(all_prices) > 15 else "low",
                    "confidence": min(95, max(60, 100 - (price_std / avg_price * 100))) if avg_price > 0 else 60,
                    "data_points": len(all_prices),
                    "source": "IronPlanet",
                    "last_updated": datetime.now().isoformat()
                }
            else:
                return {
                    "trend": "stable",
                    "average_price": 0,
                    "price_volatility": 0,
                    "market_activity": "low",
                    "confidence": 0,
                    "data_points": 0,
                    "source": "IronPlanet",
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"IronPlanet market trends error: {e}")
            return {
                "trend": "stable",
                "average_price": 0,
                "price_volatility": 0,
                "market_activity": "low",
                "confidence": 0,
                "data_points": 0,
                "source": "IronPlanet",
                "error": str(e)
            }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        try:
            # Test API connectivity
            test_url = f"{self.base_url}/health"
            async with self.session.get(test_url) as response:
                api_status = "healthy" if response.status == 200 else "unhealthy"
        except Exception as e:
            api_status = "unhealthy"
            logger.error(f"IronPlanet health check failed: {e}")
        
        return {
            "service": "IronPlanet",
            "status": api_status,
            "rate_limits": self.rate_limits,
            "cache_status": "active" if self.redis_client else "inactive",
            "last_check": datetime.now().isoformat()
        }
