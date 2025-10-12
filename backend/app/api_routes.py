"""
Comprehensive API Routes for Crane Intelligence Platform
Complete CRUD operations for all database tables
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging

from app.config import get_db

logger = logging.getLogger(__name__)

# Create API router
api_router = APIRouter(prefix="/api/v1")

# ==================== PYDANTIC MODELS ====================

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    user_role: Optional[str] = None

class CraneListingCreate(BaseModel):
    manufacturer: str
    model: str
    year: int
    capacity: float
    condition: str
    location: str
    price: float
    mileage: Optional[float] = 0
    description: Optional[str] = None

class CraneListingUpdate(BaseModel):
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    capacity: Optional[float] = None
    condition: Optional[str] = None
    location: Optional[str] = None
    price: Optional[float] = None
    mileage: Optional[float] = None
    description: Optional[str] = None

class ValuationCreate(BaseModel):
    crane_make: str
    crane_model: str
    crane_year: int
    crane_hours: Optional[int] = None
    crane_condition: str
    boom_length: Optional[float] = None  # Boom length in meters or feet

class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    type: str = "info"

class WatchlistCreate(BaseModel):
    crane_listing_id: int

class PriceAlertCreate(BaseModel):
    crane_make: str
    crane_model: str
    target_price: float
    condition: str  # 'above' or 'below'

class MarketDataCreate(BaseModel):
    crane_type: str
    make: str
    model: str
    year: int
    average_price: float
    price_trend: str
    market_volume: int
    region: str

# ==================== AUTHENTICATION DEPENDENCY ====================

def get_current_user(db: Session = Depends(get_db)):
    """Get current authenticated user - simplified version"""
    # In production, implement proper JWT token verification
    # For now, return a mock user for testing
    from sqlalchemy import text
    result = db.execute(text("SELECT id, email, username, full_name, user_role FROM users LIMIT 1"))
    user = result.fetchone()
    if user:
        return {
            "id": user[0],
            "email": user[1],
            "username": user[2],
            "full_name": user[3],
            "user_role": user[4]
        }
    return None

# ==================== USER ENDPOINTS ====================

@api_router.get("/users/me")
async def get_current_user_profile(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        from sqlalchemy import text
        result = db.execute(
            text("SELECT id, email, username, full_name, user_role, is_active, is_verified, created_at FROM users WHERE id = :user_id"),
            {"user_id": current_user["id"]}
        )
        user = result.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user[0],
            "email": user[1],
            "username": user[2],
            "full_name": user[3],
            "user_role": user[4],
            "is_active": user[5],
            "is_verified": user[6],
            "created_at": user[7]
        }
    except Exception as e:
        logger.error(f"Error fetching user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.put("/users/me")
async def update_user_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        updates = []
        params = {"user_id": current_user["id"]}
        
        if profile_data.full_name:
            updates.append("full_name = :full_name")
            params["full_name"] = profile_data.full_name
        
        if profile_data.email:
            updates.append("email = :email")
            params["email"] = profile_data.email
        
        if profile_data.user_role:
            updates.append("user_role = :user_role")
            params["user_role"] = profile_data.user_role
        
        if updates:
            from sqlalchemy import text
            query = f"UPDATE users SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = :user_id"
            db.execute(text(query), params)
            db.commit()
        
        return {"success": True, "message": "Profile updated successfully"}
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ==================== CRANE LISTINGS ENDPOINTS ====================

@api_router.get("/crane-listings")
async def get_crane_listings(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    manufacturer: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    condition: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all crane listings with filters"""
    try:
        from sqlalchemy import text
        
        # Build query with filters
        where_clauses = []
        params = {"limit": limit, "offset": offset}
        
        if manufacturer:
            where_clauses.append("manufacturer ILIKE :manufacturer")
            params["manufacturer"] = f"%{manufacturer}%"
        
        if min_price:
            where_clauses.append("price >= :min_price")
            params["min_price"] = min_price
        
        if max_price:
            where_clauses.append("price <= :max_price")
            params["max_price"] = max_price
        
        if condition:
            where_clauses.append("condition = :condition")
            params["condition"] = condition
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        query = f"""
            SELECT id, manufacturer, model, year, capacity, condition, location, 
                   price, mileage, description, created_at
            FROM crane_listings
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """
        
        result = db.execute(text(query), params)
        listings = result.fetchall()
        
        return {
            "success": True,
            "count": len(listings),
            "listings": [
                {
                    "id": row[0],
                    "manufacturer": row[1],
                    "model": row[2],
                    "year": row[3],
                    "capacity": float(row[4]) if row[4] else 0,
                    "condition": row[5],
                    "location": row[6],
                    "price": float(row[7]) if row[7] else 0,
                    "mileage": float(row[8]) if row[8] else 0,
                    "description": row[9],
                    "created_at": str(row[10]) if row[10] else None
                }
                for row in listings
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching crane listings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/crane-listings/{listing_id}")
async def get_crane_listing(listing_id: int, db: Session = Depends(get_db)):
    """Get a specific crane listing by ID"""
    try:
        from sqlalchemy import text
        result = db.execute(
            text("""
                SELECT id, manufacturer, model, year, capacity, condition, location, 
                       price, mileage, description, created_at
                FROM crane_listings
                WHERE id = :listing_id
            """),
            {"listing_id": listing_id}
        )
        listing = result.fetchone()
        
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")
        
        return {
            "id": listing[0],
            "manufacturer": listing[1],
            "model": listing[2],
            "year": listing[3],
            "capacity": float(listing[4]) if listing[4] else 0,
            "condition": listing[5],
            "location": listing[6],
            "price": float(listing[7]) if listing[7] else 0,
            "mileage": float(listing[8]) if listing[8] else 0,
            "description": listing[9],
            "created_at": str(listing[10]) if listing[10] else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching crane listing: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/crane-listings")
async def create_crane_listing(
    listing_data: CraneListingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new crane listing"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        from sqlalchemy import text
        result = db.execute(
            text("""
                INSERT INTO crane_listings 
                (manufacturer, model, year, capacity, condition, location, price, mileage, description)
                VALUES (:manufacturer, :model, :year, :capacity, :condition, :location, :price, :mileage, :description)
                RETURNING id
            """),
            {
                "manufacturer": listing_data.manufacturer,
                "model": listing_data.model,
                "year": listing_data.year,
                "capacity": listing_data.capacity,
                "condition": listing_data.condition,
                "location": listing_data.location,
                "price": listing_data.price,
                "mileage": listing_data.mileage or 0,
                "description": listing_data.description
            }
        )
        listing_id = result.fetchone()[0]
        db.commit()
        
        return {"success": True, "message": "Listing created successfully", "listing_id": listing_id}
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating crane listing: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.put("/crane-listings/{listing_id}")
async def update_crane_listing(
    listing_id: int,
    listing_data: CraneListingUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a crane listing"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        updates = []
        params = {"listing_id": listing_id}
        
        if listing_data.manufacturer:
            updates.append("manufacturer = :manufacturer")
            params["manufacturer"] = listing_data.manufacturer
        
        if listing_data.model:
            updates.append("model = :model")
            params["model"] = listing_data.model
        
        if listing_data.year:
            updates.append("year = :year")
            params["year"] = listing_data.year
        
        if listing_data.capacity:
            updates.append("capacity = :capacity")
            params["capacity"] = listing_data.capacity
        
        if listing_data.condition:
            updates.append("condition = :condition")
            params["condition"] = listing_data.condition
        
        if listing_data.location:
            updates.append("location = :location")
            params["location"] = listing_data.location
        
        if listing_data.price:
            updates.append("price = :price")
            params["price"] = listing_data.price
        
        if listing_data.mileage is not None:
            updates.append("mileage = :mileage")
            params["mileage"] = listing_data.mileage
        
        if listing_data.description:
            updates.append("description = :description")
            params["description"] = listing_data.description
        
        if updates:
            from sqlalchemy import text
            query = f"UPDATE crane_listings SET {', '.join(updates)} WHERE id = :listing_id"
            db.execute(text(query), params)
            db.commit()
        
        return {"success": True, "message": "Listing updated successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating crane listing: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.delete("/crane-listings/{listing_id}")
async def delete_crane_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a crane listing"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        from sqlalchemy import text
        db.execute(text("DELETE FROM crane_listings WHERE id = :listing_id"), {"listing_id": listing_id})
        db.commit()
        
        return {"success": True, "message": "Listing deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting crane listing: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ==================== VALUATIONS ENDPOINTS ====================

@api_router.get("/valuations")
async def get_valuations(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all valuations for current user"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        from sqlalchemy import text
        result = db.execute(
            text("""
                SELECT id, manufacturer, model, year, capacity, condition, location,
                       mileage, boom_length, estimated_value, confidence_score, created_at
                FROM valuations
                WHERE user_id = :user_id
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """),
            {"user_id": current_user["id"], "limit": limit, "offset": offset}
        )
        valuations = result.fetchall()
        
        return {
            "success": True,
            "count": len(valuations),
            "valuations": [
                {
                    "id": row[0],
                    "crane_make": row[1],  # manufacturer
                    "crane_model": row[2],  # model
                    "crane_year": row[3],  # year
                    "capacity": float(row[4]) if row[4] else 0,
                    "crane_condition": row[5],  # condition
                    "location": row[6],
                    "crane_hours": float(row[7]) if row[7] else 0,  # mileage
                    "boom_length": float(row[8]) if row[8] else None,
                    "estimated_value": float(row[9]) if row[9] else 0,
                    "confidence_score": float(row[10]) if row[10] else 0,
                    "created_at": str(row[11]) if row[11] else None
                }
                for row in valuations
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching valuations: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/valuations")
async def create_valuation(
    valuation_data: ValuationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new valuation request"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Calculate estimated value based on market data
        from sqlalchemy import text
        market_result = db.execute(
            text("""
                SELECT AVG(average_price) as avg_price
                FROM market_data
                WHERE make = :make AND model = :model AND year = :year
            """),
            {
                "make": valuation_data.crane_make,
                "model": valuation_data.crane_model,
                "year": valuation_data.crane_year
            }
        )
        market_price = market_result.fetchone()
        estimated_value = float(market_price[0]) if market_price and market_price[0] else 500000.0
        
        # Adjust for condition
        condition_multipliers = {
            "excellent": 1.15,
            "good": 1.0,
            "fair": 0.85,
            "poor": 0.70
        }
        multiplier = condition_multipliers.get(valuation_data.crane_condition.lower(), 1.0)
        estimated_value *= multiplier
        
        # Adjust for boom length (longer boom = higher value)
        # Typical boom lengths: 20-80 meters for mobile cranes
        # Add 2% value for every 10 meters above baseline (40m)
        if valuation_data.boom_length:
            baseline_boom = 40.0  # meters
            if valuation_data.boom_length > baseline_boom:
                boom_premium = (valuation_data.boom_length - baseline_boom) / 10.0 * 0.02
                estimated_value *= (1 + boom_premium)
            elif valuation_data.boom_length < baseline_boom:
                boom_discount = (baseline_boom - valuation_data.boom_length) / 10.0 * 0.015
                estimated_value *= (1 - boom_discount)
        
        # Insert valuation (using actual database column names)
        result = db.execute(
            text("""
                INSERT INTO valuations 
                (user_id, manufacturer, model, year, capacity, condition, location,
                 mileage, boom_length, estimated_value, confidence_score)
                VALUES (:user_id, :manufacturer, :model, :year, :capacity, :condition, :location,
                        :mileage, :boom_length, :estimated_value, :confidence_score)
                RETURNING id
            """),
            {
                "user_id": current_user["id"],
                "manufacturer": valuation_data.crane_make,
                "model": valuation_data.crane_model,
                "year": valuation_data.crane_year,
                "capacity": 0,  # Default capacity, can be enhanced later
                "condition": valuation_data.crane_condition,
                "location": "Not specified",  # Default location
                "mileage": valuation_data.crane_hours or 0,  # Use hours as mileage for now
                "boom_length": valuation_data.boom_length,
                "estimated_value": estimated_value,
                "confidence_score": 0.85
            }
        )
        valuation_id = result.fetchone()[0]
        db.commit()
        
        return {
            "success": True,
            "message": "Valuation completed successfully",
            "valuation_id": valuation_id,
            "estimated_value": estimated_value,
            "confidence_score": 0.85
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating valuation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ==================== MARKET DATA ENDPOINTS ====================

@api_router.get("/market-data")
async def get_market_data(
    crane_type: Optional[str] = None,
    make: Optional[str] = None,
    region: Optional[str] = None,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """Get market data with filters"""
    try:
        from sqlalchemy import text
        
        where_clauses = []
        params = {"limit": limit}
        
        if crane_type:
            where_clauses.append("crane_type = :crane_type")
            params["crane_type"] = crane_type
        
        if make:
            where_clauses.append("make ILIKE :make")
            params["make"] = f"%{make}%"
        
        if region:
            where_clauses.append("region = :region")
            params["region"] = region
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        query = f"""
            SELECT id, crane_type, make, model, year, average_price, 
                   price_trend, market_volume, data_date, region, created_at
            FROM market_data
            WHERE {where_clause}
            ORDER BY data_date DESC
            LIMIT :limit
        """
        
        result = db.execute(text(query), params)
        data = result.fetchall()
        
        return {
            "success": True,
            "count": len(data),
            "market_data": [
                {
                    "id": row[0],
                    "crane_type": row[1],
                    "make": row[2],
                    "model": row[3],
                    "year": row[4],
                    "average_price": float(row[5]) if row[5] else 0,
                    "price_trend": row[6],
                    "market_volume": row[7],
                    "data_date": str(row[8]) if row[8] else None,
                    "region": row[9],
                    "created_at": str(row[10]) if row[10] else None
                }
                for row in data
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ==================== NOTIFICATIONS ENDPOINTS ====================

@api_router.get("/notifications")
async def get_notifications(
    limit: int = Query(20, le=100),
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user notifications"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        from sqlalchemy import text
        
        where_clause = "user_id = :user_id"
        if unread_only:
            where_clause += " AND is_read = false"
        
        result = db.execute(
            text(f"""
                SELECT id, title, message, type, is_read, created_at, read_at
                FROM notifications
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT :limit
            """),
            {"user_id": current_user["id"], "limit": limit}
        )
        notifications = result.fetchall()
        
        return {
            "success": True,
            "count": len(notifications),
            "notifications": [
                {
                    "id": row[0],
                    "title": row[1],
                    "message": row[2],
                    "type": row[3],
                    "is_read": row[4],
                    "created_at": str(row[5]) if row[5] else None,
                    "read_at": str(row[6]) if row[6] else None
                }
                for row in notifications
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching notifications: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mark a notification as read"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        from sqlalchemy import text
        db.execute(
            text("""
                UPDATE notifications
                SET is_read = true, read_at = CURRENT_TIMESTAMP
                WHERE id = :notification_id AND user_id = :user_id
            """),
            {"notification_id": notification_id, "user_id": current_user["id"]}
        )
        db.commit()
        
        return {"success": True, "message": "Notification marked as read"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ==================== WATCHLIST ENDPOINTS ====================

@api_router.get("/watchlist")
async def get_watchlist(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user's watchlist"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        from sqlalchemy import text
        result = db.execute(
            text("""
                SELECT w.id, w.crane_listing_id, w.created_at,
                       c.manufacturer, c.model, c.year, c.price, c.location
                FROM watchlist w
                JOIN crane_listings c ON w.crane_listing_id = c.id
                WHERE w.user_id = :user_id
                ORDER BY w.created_at DESC
            """),
            {"user_id": current_user["id"]}
        )
        watchlist = result.fetchall()
        
        return {
            "success": True,
            "count": len(watchlist),
            "watchlist": [
                {
                    "id": row[0],
                    "crane_listing_id": row[1],
                    "created_at": str(row[2]) if row[2] else None,
                    "manufacturer": row[3],
                    "model": row[4],
                    "year": row[5],
                    "price": float(row[6]) if row[6] else 0,
                    "location": row[7]
                }
                for row in watchlist
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/watchlist")
async def add_to_watchlist(
    watchlist_data: WatchlistCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add a crane listing to watchlist"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        from sqlalchemy import text
        result = db.execute(
            text("""
                INSERT INTO watchlist (user_id, crane_listing_id)
                VALUES (:user_id, :crane_listing_id)
                ON CONFLICT (user_id, crane_listing_id) DO NOTHING
                RETURNING id
            """),
            {"user_id": current_user["id"], "crane_listing_id": watchlist_data.crane_listing_id}
        )
        
        if result.rowcount > 0:
            watchlist_id = result.fetchone()[0]
            db.commit()
            return {"success": True, "message": "Added to watchlist", "watchlist_id": watchlist_id}
        else:
            return {"success": True, "message": "Already in watchlist"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding to watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.delete("/watchlist/{watchlist_id}")
async def remove_from_watchlist(
    watchlist_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Remove a crane listing from watchlist"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        from sqlalchemy import text
        db.execute(
            text("DELETE FROM watchlist WHERE id = :watchlist_id AND user_id = :user_id"),
            {"watchlist_id": watchlist_id, "user_id": current_user["id"]}
        )
        db.commit()
        
        return {"success": True, "message": "Removed from watchlist"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error removing from watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ==================== PRICE ALERTS ENDPOINTS ====================

@api_router.get("/price-alerts")
async def get_price_alerts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user's price alerts"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        from sqlalchemy import text
        result = db.execute(
            text("""
                SELECT id, crane_make, crane_model, target_price, condition, 
                       is_active, created_at, triggered_at
                FROM price_alerts
                WHERE user_id = :user_id
                ORDER BY created_at DESC
            """),
            {"user_id": current_user["id"]}
        )
        alerts = result.fetchall()
        
        return {
            "success": True,
            "count": len(alerts),
            "price_alerts": [
                {
                    "id": row[0],
                    "crane_make": row[1],
                    "crane_model": row[2],
                    "target_price": float(row[3]) if row[3] else 0,
                    "condition": row[4],
                    "is_active": row[5],
                    "created_at": str(row[6]) if row[6] else None,
                    "triggered_at": str(row[7]) if row[7] else None
                }
                for row in alerts
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching price alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/price-alerts")
async def create_price_alert(
    alert_data: PriceAlertCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new price alert"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        from sqlalchemy import text
        result = db.execute(
            text("""
                INSERT INTO price_alerts (user_id, crane_make, crane_model, target_price, condition)
                VALUES (:user_id, :crane_make, :crane_model, :target_price, :condition)
                RETURNING id
            """),
            {
                "user_id": current_user["id"],
                "crane_make": alert_data.crane_make,
                "crane_model": alert_data.crane_model,
                "target_price": alert_data.target_price,
                "condition": alert_data.condition
            }
        )
        alert_id = result.fetchone()[0]
        db.commit()
        
        return {"success": True, "message": "Price alert created successfully", "alert_id": alert_id}
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating price alert: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ==================== ACTIVITY LOGS ENDPOINTS ====================

@api_router.get("/activity-logs")
async def get_activity_logs(
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user's activity logs"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        from sqlalchemy import text
        result = db.execute(
            text("""
                SELECT id, action, resource, resource_id, details, 
                       ip_address, user_agent, created_at
                FROM activity_logs
                WHERE user_id = :user_id
                ORDER BY created_at DESC
                LIMIT :limit
            """),
            {"user_id": current_user["id"], "limit": limit}
        )
        logs = result.fetchall()
        
        return {
            "success": True,
            "count": len(logs),
            "activity_logs": [
                {
                    "id": row[0],
                    "action": row[1],
                    "resource": row[2],
                    "resource_id": row[3],
                    "details": row[4],
                    "ip_address": str(row[5]) if row[5] else None,
                    "user_agent": row[6],
                    "created_at": str(row[7]) if row[7] else None
                }
                for row in logs
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching activity logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ==================== DASHBOARD STATS ENDPOINTS ====================

@api_router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard statistics"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        from sqlalchemy import text
        
        # Get total listings
        total_listings = db.execute(text("SELECT COUNT(*) FROM crane_listings")).fetchone()[0]
        
        # Get user's valuations
        user_valuations = db.execute(
            text("SELECT COUNT(*) FROM valuations WHERE user_id = :user_id"),
            {"user_id": current_user["id"]}
        ).fetchone()[0]
        
        # Get watchlist count
        watchlist_count = db.execute(
            text("SELECT COUNT(*) FROM watchlist WHERE user_id = :user_id"),
            {"user_id": current_user["id"]}
        ).fetchone()[0]
        
        # Get unread notifications
        unread_notifications = db.execute(
            text("SELECT COUNT(*) FROM notifications WHERE user_id = :user_id AND is_read = false"),
            {"user_id": current_user["id"]}
        ).fetchone()[0]
        
        # Get average market price
        avg_market_price = db.execute(
            text("SELECT AVG(price) FROM crane_listings")
        ).fetchone()[0]
        
        return {
            "success": True,
            "stats": {
                "total_listings": total_listings,
                "user_valuations": user_valuations,
                "watchlist_count": watchlist_count,
                "unread_notifications": unread_notifications,
                "average_market_price": float(avg_market_price) if avg_market_price else 0
            }
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

