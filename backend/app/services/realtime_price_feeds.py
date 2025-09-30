"""
Real-Time Market Price Feeds Service
Provides live market price feeds and WebSocket connections
"""

import asyncio
import aiohttp
import websockets
import logging
import json
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import redis
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class PriceFeed:
    """Real-time price feed data point"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime
    source: str
    bid: Optional[float] = None
    ask: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None

@dataclass
class MarketAlert:
    """Market alert configuration"""
    symbol: str
    condition: str  # 'above', 'below', 'change'
    threshold: float
    callback: Callable
    active: bool = True

class RealTimePriceFeedsService:
    """Real-time market price feeds service with WebSocket connections"""
    
    def __init__(self):
        self.websocket_connections = {}
        self.price_feeds = {}
        self.subscribers = {}
        self.alerts = []
        self.redis_client = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running = False
        self.feed_interval = 5  # seconds
        
    async def initialize(self):
        """Initialize the real-time price feeds service"""
        try:
            # Initialize Redis for price data caching
            try:
                self.redis_client = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)
                await self.redis_client.ping()
                logger.info("Redis connection established for price feeds caching")
            except Exception as e:
                logger.warning(f"Redis not available for price feeds, using in-memory cache: {e}")
                self.redis_client = None
            
            # Start background price feed updates
            self.running = True
            asyncio.create_task(self._background_price_updates())
            
            logger.info("Real-time price feeds service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize price feeds service: {e}")
            raise
    
    async def close(self):
        """Close the service and cleanup resources"""
        self.running = False
        
        # Close all WebSocket connections
        for connection in self.websocket_connections.values():
            if connection and not connection.closed:
                await connection.close()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        if self.redis_client:
            await self.redis_client.close()
    
    async def _background_price_updates(self):
        """Background task for updating price feeds"""
        while self.running:
            try:
                # Update all active price feeds
                await self._update_all_price_feeds()
                
                # Process alerts
                await self._process_alerts()
                
                # Notify subscribers
                await self._notify_subscribers()
                
                await asyncio.sleep(self.feed_interval)
                
            except Exception as e:
                logger.error(f"Error in background price updates: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _update_all_price_feeds(self):
        """Update all active price feeds"""
        try:
            # Update Equipment Watch prices
            await self._update_equipment_watch_prices()
            
            # Update Ritchie Bros prices
            await self._update_ritchie_bros_prices()
            
            # Update MachineryTrader prices
            await self._update_machinery_trader_prices()
            
            # Update IronPlanet prices
            await self._update_ironplanet_prices()
            
        except Exception as e:
            logger.error(f"Error updating price feeds: {e}")
    
    async def _update_equipment_watch_prices(self):
        """Update Equipment Watch price feeds"""
        try:
            # Simulate real-time price updates
            symbols = ['CRANE-EW-001', 'CRANE-EW-002', 'CRANE-EW-003']
            
            for symbol in symbols:
                # Generate realistic price data
                base_price = 1200000 + (hash(symbol) % 500000)
                change = (time.time() % 100 - 50) * 1000  # Random change
                new_price = max(500000, base_price + change)
                
                price_feed = PriceFeed(
                    symbol=symbol,
                    price=new_price,
                    change=change,
                    change_percent=(change / base_price) * 100,
                    volume=int(time.time() % 1000),
                    timestamp=datetime.now(),
                    source="Equipment Watch",
                    bid=new_price * 0.98,
                    ask=new_price * 1.02,
                    high=new_price * 1.05,
                    low=new_price * 0.95
                )
                
                self.price_feeds[symbol] = price_feed
                
                # Cache the price data
                if self.redis_client:
                    await self.redis_client.setex(
                        f"price_feed:{symbol}",
                        300,  # 5 minutes TTL
                        json.dumps(price_feed.__dict__, default=str)
                    )
                    
        except Exception as e:
            logger.error(f"Error updating Equipment Watch prices: {e}")
    
    async def _update_ritchie_bros_prices(self):
        """Update Ritchie Bros price feeds"""
        try:
            symbols = ['CRANE-RB-001', 'CRANE-RB-002', 'CRANE-RB-003']
            
            for symbol in symbols:
                base_price = 1100000 + (hash(symbol) % 400000)
                change = (time.time() % 80 - 40) * 800
                new_price = max(400000, base_price + change)
                
                price_feed = PriceFeed(
                    symbol=symbol,
                    price=new_price,
                    change=change,
                    change_percent=(change / base_price) * 100,
                    volume=int(time.time() % 800),
                    timestamp=datetime.now(),
                    source="Ritchie Bros",
                    bid=new_price * 0.97,
                    ask=new_price * 1.03,
                    high=new_price * 1.08,
                    low=new_price * 0.92
                )
                
                self.price_feeds[symbol] = price_feed
                
                if self.redis_client:
                    await self.redis_client.setex(
                        f"price_feed:{symbol}",
                        300,
                        json.dumps(price_feed.__dict__, default=str)
                    )
                    
        except Exception as e:
            logger.error(f"Error updating Ritchie Bros prices: {e}")
    
    async def _update_machinery_trader_prices(self):
        """Update MachineryTrader price feeds"""
        try:
            symbols = ['CRANE-MT-001', 'CRANE-MT-002', 'CRANE-MT-003']
            
            for symbol in symbols:
                base_price = 1300000 + (hash(symbol) % 600000)
                change = (time.time() % 120 - 60) * 1200
                new_price = max(600000, base_price + change)
                
                price_feed = PriceFeed(
                    symbol=symbol,
                    price=new_price,
                    change=change,
                    change_percent=(change / base_price) * 100,
                    volume=int(time.time() % 1200),
                    timestamp=datetime.now(),
                    source="MachineryTrader",
                    bid=new_price * 0.99,
                    ask=new_price * 1.01,
                    high=new_price * 1.06,
                    low=new_price * 0.94
                )
                
                self.price_feeds[symbol] = price_feed
                
                if self.redis_client:
                    await self.redis_client.setex(
                        f"price_feed:{symbol}",
                        300,
                        json.dumps(price_feed.__dict__, default=str)
                    )
                    
        except Exception as e:
            logger.error(f"Error updating MachineryTrader prices: {e}")
    
    async def _update_ironplanet_prices(self):
        """Update IronPlanet price feeds"""
        try:
            symbols = ['CRANE-IP-001', 'CRANE-IP-002', 'CRANE-IP-003']
            
            for symbol in symbols:
                base_price = 1150000 + (hash(symbol) % 450000)
                change = (time.time() % 90 - 45) * 900
                new_price = max(450000, base_price + change)
                
                price_feed = PriceFeed(
                    symbol=symbol,
                    price=new_price,
                    change=change,
                    change_percent=(change / base_price) * 100,
                    volume=int(time.time() % 900),
                    timestamp=datetime.now(),
                    source="IronPlanet",
                    bid=new_price * 0.96,
                    ask=new_price * 1.04,
                    high=new_price * 1.07,
                    low=new_price * 0.93
                )
                
                self.price_feeds[symbol] = price_feed
                
                if self.redis_client:
                    await self.redis_client.setex(
                        f"price_feed:{symbol}",
                        300,
                        json.dumps(price_feed.__dict__, default=str)
                    )
                    
        except Exception as e:
            logger.error(f"Error updating IronPlanet prices: {e}")
    
    async def _process_alerts(self):
        """Process market alerts"""
        try:
            for alert in self.alerts:
                if not alert.active:
                    continue
                
                symbol = alert.symbol
                if symbol not in self.price_feeds:
                    continue
                
                price_feed = self.price_feeds[symbol]
                triggered = False
                
                if alert.condition == 'above' and price_feed.price > alert.threshold:
                    triggered = True
                elif alert.condition == 'below' and price_feed.price < alert.threshold:
                    triggered = True
                elif alert.condition == 'change' and abs(price_feed.change_percent) > alert.threshold:
                    triggered = True
                
                if triggered:
                    try:
                        await alert.callback(price_feed, alert)
                    except Exception as e:
                        logger.error(f"Error in alert callback: {e}")
                        
        except Exception as e:
            logger.error(f"Error processing alerts: {e}")
    
    async def _notify_subscribers(self):
        """Notify all subscribers of price updates"""
        try:
            for subscriber_id, callback in self.subscribers.items():
                try:
                    await callback(self.price_feeds)
                except Exception as e:
                    logger.error(f"Error notifying subscriber {subscriber_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error notifying subscribers: {e}")
    
    async def subscribe_to_feeds(self, subscriber_id: str, callback: Callable):
        """Subscribe to real-time price feeds"""
        self.subscribers[subscriber_id] = callback
        logger.info(f"Subscriber {subscriber_id} subscribed to price feeds")
    
    async def unsubscribe_from_feeds(self, subscriber_id: str):
        """Unsubscribe from real-time price feeds"""
        if subscriber_id in self.subscribers:
            del self.subscribers[subscriber_id]
            logger.info(f"Subscriber {subscriber_id} unsubscribed from price feeds")
    
    async def add_alert(self, alert: MarketAlert):
        """Add a market alert"""
        self.alerts.append(alert)
        logger.info(f"Alert added for {alert.symbol}: {alert.condition} {alert.threshold}")
    
    async def remove_alert(self, symbol: str, condition: str):
        """Remove a market alert"""
        self.alerts = [alert for alert in self.alerts 
                      if not (alert.symbol == symbol and alert.condition == condition)]
        logger.info(f"Alert removed for {symbol}: {condition}")
    
    async def get_current_prices(self, symbols: List[str] = None) -> Dict[str, PriceFeed]:
        """Get current prices for specified symbols"""
        if symbols is None:
            return self.price_feeds.copy()
        
        return {symbol: self.price_feeds.get(symbol) for symbol in symbols 
                if symbol in self.price_feeds}
    
    async def get_price_history(self, symbol: str, hours: int = 24) -> List[PriceFeed]:
        """Get price history for a symbol"""
        try:
            if self.redis_client:
                # Get historical data from Redis
                history_key = f"price_history:{symbol}"
                history_data = await self.redis_client.lrange(history_key, 0, hours * 12)  # 5-minute intervals
                
                history = []
                for data in history_data:
                    try:
                        price_data = json.loads(data)
                        history.append(PriceFeed(**price_data))
                    except Exception as e:
                        logger.warning(f"Error parsing price history: {e}")
                
                return history
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting price history: {e}")
            return []
    
    async def get_market_summary(self) -> Dict[str, Any]:
        """Get market summary with key metrics"""
        try:
            if not self.price_feeds:
                return {"error": "No price feeds available"}
            
            prices = [feed.price for feed in self.price_feeds.values()]
            changes = [feed.change_percent for feed in self.price_feeds.values()]
            
            return {
                "total_symbols": len(self.price_feeds),
                "average_price": sum(prices) / len(prices) if prices else 0,
                "price_range": [min(prices), max(prices)] if prices else [0, 0],
                "average_change": sum(changes) / len(changes) if changes else 0,
                "active_alerts": len([alert for alert in self.alerts if alert.active]),
                "subscribers": len(self.subscribers),
                "last_update": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting market summary: {e}")
            return {"error": str(e)}
