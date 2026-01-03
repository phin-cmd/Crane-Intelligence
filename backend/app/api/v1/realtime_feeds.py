"""
Real-Time Market Price Feeds API Endpoints
Provides WebSocket and REST access to real-time price feeds
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...services.realtime_price_feeds import RealTimePriceFeedsService, MarketAlert
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/realtime-feeds", tags=["Real-Time Price Feeds"])

# Separate router for /ws endpoint at root level
ws_router = APIRouter(tags=["WebSocket"])

# Global service instance
price_feeds_service = None

async def get_price_feeds_service():
    """Get or create price feeds service instance"""
    global price_feeds_service
    if price_feeds_service is None:
        price_feeds_service = RealTimePriceFeedsService()
        await price_feeds_service.initialize()
    return price_feeds_service

@router.get("/prices/current")
async def get_current_prices(
    symbols: Optional[str] = Query(None, description="Comma-separated list of symbols"),
    source: Optional[str] = Query(None, description="Filter by data source")
):
    """Get current prices for specified symbols"""
    try:
        service = await get_price_feeds_service()
        
        symbol_list = symbols.split(',') if symbols else None
        prices = await service.get_current_prices(symbol_list)
        
        # Filter by source if specified
        if source:
            prices = {symbol: feed for symbol, feed in prices.items() 
                     if feed and feed.source == source}
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "prices": {symbol: feed.__dict__ for symbol, feed in prices.items() if feed},
            "count": len(prices)
        }
        
    except Exception as e:
        logger.error(f"Error getting current prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prices/history/{symbol}")
async def get_price_history(
    symbol: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of history to retrieve")
):
    """Get price history for a specific symbol"""
    try:
        service = await get_price_feeds_service()
        history = await service.get_price_history(symbol, hours)
        
        return {
            "success": True,
            "symbol": symbol,
            "hours": hours,
            "timestamp": datetime.utcnow().isoformat(),
            "history": [feed.__dict__ for feed in history],
            "count": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting price history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/summary")
async def get_market_summary():
    """Get market summary with key metrics"""
    try:
        service = await get_price_feeds_service()
        summary = await service.get_market_summary()
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting market summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/add")
async def add_market_alert(
    symbol: str,
    condition: str,
    threshold: float,
    callback_url: Optional[str] = None
):
    """Add a market alert"""
    try:
        service = await get_price_feeds_service()
        
        # Create alert callback
        async def alert_callback(price_feed, alert):
            logger.info(f"Alert triggered: {alert.symbol} {alert.condition} {alert.threshold}")
            # In production, you would send notifications here
        
        alert = MarketAlert(
            symbol=symbol,
            condition=condition,
            threshold=threshold,
            callback=alert_callback
        )
        
        await service.add_alert(alert)
        
        return {
            "success": True,
            "message": f"Alert added for {symbol}: {condition} {threshold}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error adding market alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/alerts/remove")
async def remove_market_alert(
    symbol: str,
    condition: str
):
    """Remove a market alert"""
    try:
        service = await get_price_feeds_service()
        await service.remove_alert(symbol, condition)
        
        return {
            "success": True,
            "message": f"Alert removed for {symbol}: {condition}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error removing market alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@ws_router.websocket("/ws")
async def websocket_simple(websocket: WebSocket):
    """Simple WebSocket endpoint at /ws for frontend compatibility"""
    await websocket.accept()
    
    # Extract token from query string
    query_params = dict(websocket.query_params)
    token = query_params.get('token')
    
    # Extract client_id from token if provided
    client_id = f"client_{id(websocket)}"
    if token:
        try:
            from jose import jwt
            from ...core.config import settings
            payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
            client_id = f"user_{payload.get('sub', client_id)}"
        except:
            pass
    
    # Use the same logic as the main websocket endpoint
    try:
        service = await get_price_feeds_service()
        
        # Subscribe to price feeds
        async def price_callback(prices):
            try:
                await websocket.send_text(json.dumps({
                    "type": "price_update",
                    "timestamp": datetime.utcnow().isoformat(),
                    "prices": {symbol: feed.__dict__ for symbol, feed in prices.items() if feed}
                }, default=str))
            except Exception as e:
                logger.error(f"Error sending price update to {client_id}: {e}")
        
        await service.subscribe_to_feeds(client_id, price_callback)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                elif message.get("type") == "subscribe":
                    # Handle subscription requests
                    symbols = message.get("symbols", [])
                    if symbols:
                        prices = await service.get_current_prices(symbols)
                        await websocket.send_text(json.dumps({
                            "type": "subscription_confirmed",
                            "symbols": symbols,
                            "prices": {symbol: feed.__dict__ for symbol, feed in prices.items() if feed}
                        }, default=str))
                        
            except WebSocketDisconnect:
                logger.info(f"WebSocket client {client_id} disconnected")
                break
            except Exception as e:
                logger.error(f"Error handling WebSocket message from {client_id}: {e}")
                break
                
    except Exception as e:
        logger.error(f"Error in WebSocket connection for {client_id}: {e}")
    finally:
        # Unsubscribe from price feeds
        try:
            await service.unsubscribe_from_feeds(client_id)
        except:
            pass

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time price feeds"""
    await websocket.accept()
    
    try:
        service = await get_price_feeds_service()
        
        # Subscribe to price feeds
        async def price_callback(prices):
            try:
                await websocket.send_text(json.dumps({
                    "type": "price_update",
                    "timestamp": datetime.utcnow().isoformat(),
                    "prices": {symbol: feed.__dict__ for symbol, feed in prices.items() if feed}
                }, default=str))
            except Exception as e:
                logger.error(f"Error sending price update to {client_id}: {e}")
        
        await service.subscribe_to_feeds(client_id, price_callback)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                elif message.get("type") == "subscribe":
                    # Handle subscription requests
                    symbols = message.get("symbols", [])
                    if symbols:
                        prices = await service.get_current_prices(symbols)
                        await websocket.send_text(json.dumps({
                            "type": "subscription_confirmed",
                            "symbols": symbols,
                            "prices": {symbol: feed.__dict__ for symbol, feed in prices.items() if feed}
                        }, default=str))
                        
            except WebSocketDisconnect:
                logger.info(f"WebSocket client {client_id} disconnected")
                break
            except Exception as e:
                logger.error(f"Error handling WebSocket message from {client_id}: {e}")
                break
                
    except Exception as e:
        logger.error(f"Error in WebSocket connection for {client_id}: {e}")
    finally:
        # Unsubscribe from price feeds
        try:
            await service.unsubscribe_from_feeds(client_id)
        except Exception as e:
            logger.error(f"Error unsubscribing {client_id}: {e}")

@router.get("/test/websocket")
async def test_websocket():
    """Test WebSocket connection (returns HTML page)"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Real-Time Price Feeds Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .price-feed { border: 1px solid #ccc; margin: 10px 0; padding: 10px; }
            .symbol { font-weight: bold; color: #333; }
            .price { font-size: 18px; color: #0066cc; }
            .change { font-size: 14px; }
            .positive { color: #00aa00; }
            .negative { color: #aa0000; }
        </style>
    </head>
    <body>
        <h1>Real-Time Price Feeds Test</h1>
        <div id="status">Connecting...</div>
        <div id="prices"></div>
        
        <script>
            const clientId = 'test_' + Math.random().toString(36).substr(2, 9);
            const ws = new WebSocket(`ws://localhost:8003/api/v1/realtime-feeds/ws/${clientId}`);
            
            ws.onopen = function(event) {
                document.getElementById('status').innerHTML = 'Connected to real-time feeds';
                
                // Subscribe to all symbols
                ws.send(JSON.stringify({
                    type: 'subscribe',
                    symbols: ['CRANE-EW-001', 'CRANE-EW-002', 'CRANE-EW-003', 'CRANE-RB-001', 'CRANE-RB-002', 'CRANE-MT-001', 'CRANE-IP-001']
                }));
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                if (data.type === 'price_update') {
                    updatePrices(data.prices);
                }
            };
            
            ws.onclose = function(event) {
                document.getElementById('status').innerHTML = 'Connection closed';
            };
            
            ws.onerror = function(error) {
                document.getElementById('status').innerHTML = 'Connection error: ' + error;
            };
            
            function updatePrices(prices) {
                const container = document.getElementById('prices');
                container.innerHTML = '';
                
                for (const [symbol, feed] of Object.entries(prices)) {
                    const div = document.createElement('div');
                    div.className = 'price-feed';
                    
                    const changeClass = feed.change_percent >= 0 ? 'positive' : 'negative';
                    const changeSign = feed.change_percent >= 0 ? '+' : '';
                    
                    div.innerHTML = `
                        <div class="symbol">${symbol} (${feed.source})</div>
                        <div class="price">$${feed.price.toLocaleString()}</div>
                        <div class="change ${changeClass}">
                            ${changeSign}${feed.change_percent.toFixed(2)}% (${changeSign}$${feed.change.toLocaleString()})
                        </div>
                        <div>Volume: ${feed.volume.toLocaleString()}</div>
                        <div>Updated: ${new Date(feed.timestamp).toLocaleTimeString()}</div>
                    `;
                    
                    container.appendChild(div);
                }
            }
            
            // Send ping every 30 seconds to keep connection alive
            setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({type: 'ping'}));
                }
            }, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
