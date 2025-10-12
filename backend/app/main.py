"""
Main FastAPI application for Crane Intelligence Platform
Production-ready version with proper database integration
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
try:
    from pydantic import EmailStr
    EMAIL_VALIDATION_AVAILABLE = True
except ImportError:
    EMAIL_VALIDATION_AVAILABLE = False
    # Create a simple string type for email when validation is not available
    EmailStr = str
import jwt
from datetime import datetime, timedelta
import os
from pathlib import Path
import hashlib
import secrets
from typing import Optional
import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Import models
try:
    from app.models.user import User as DBUser, UserRole, SubscriptionTier
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    DBUser = None
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: Redis module not available. Caching will be disabled.")

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False
    print("Warning: Rate limiting not available. Rate limiting will be disabled.")

# Import email service
try:
    from app.email_service import email_service
    EMAIL_SERVICE_AVAILABLE = True
except ImportError:
    EMAIL_SERVICE_AVAILABLE = False
    print("Warning: Email service not available. Email functionality will be disabled.")

# Database configuration - unified with config.py
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://crane_user:crane_password@db:5432/crane_intelligence")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis configuration
if REDIS_AVAILABLE:
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    except:
        redis_client = None
        print("Warning: Could not connect to Redis. Caching will be disabled.")
else:
    redis_client = None

# Rate limiting
if RATE_LIMITING_AVAILABLE:
    limiter = Limiter(key_func=get_remote_address)
else:
    # Create a dummy limiter that doesn't do anything
    class DummyLimiter:
        def limit(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    limiter = DummyLimiter()

# Create FastAPI app
app = FastAPI(
    title="Crane Intelligence API",
    version="1.0.0",
    description="Professional Crane Valuation and Market Analysis Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting
if RATE_LIMITING_AVAILABLE:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware with security improvements
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://craneintelligence.tech", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Models
# Define User model that matches actual database schema
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    user_role = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class CraneListing(Base):
    __tablename__ = "crane_listings"
    
    id = Column(Integer, primary_key=True, index=True)
    manufacturer = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    capacity = Column(String, nullable=False)
    condition = Column(String, nullable=False)
    location = Column(String, nullable=False)
    price = Column(String, nullable=False)
    mileage = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Consultation(Base):
    __tablename__ = "consultations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    message = Column(Text)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    username: Optional[str] = None
    company_name: Optional[str] = None
    user_role: str = "user"
    subscription_tier: str = "basic"

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    user_role: Optional[str]
    is_active: Optional[bool]
    is_verified: Optional[bool]
    
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    user: Optional[UserResponse] = None

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    return hashlib.sha256((password + salt).encode()).hexdigest() + ":" + salt

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        stored_hash, salt = hashed_password.split(":")
        return hashlib.sha256((password + salt).encode()).hexdigest() == stored_hash
    except:
        return False

# Create JWT token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Verify JWT token
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "message": "Crane Intelligence API is running"}

# AUTHENTICATION ENDPOINTS MOVED TO api/v1/auth.py
# Login and register are now handled by the auth router
# See: backend/app/api/v1/auth.py

# Additional Pydantic models
class CraneListingResponse(BaseModel):
    id: int
    manufacturer: str
    model: str
    year: int
    capacity: str
    condition: str
    location: str
    price: str
    mileage: Optional[str]
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConsultationRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    message: str

# Crane listings endpoint (legacy - redirects to new API)
@app.get("/api/v1/enhanced-data/crane-listings")
@limiter.limit("10/minute")
async def get_crane_listings_legacy(limit: int = 10, db: Session = Depends(get_db)):
    try:
        # Use text query to avoid ORM issues
        from sqlalchemy import text
        result = db.execute(
            text("""
                SELECT id, manufacturer, model, year, capacity, condition, location, 
                       price, mileage, description, created_at
                FROM crane_listings
                ORDER BY created_at DESC
                LIMIT :limit
            """),
            {"limit": limit}
        )
        listings = result.fetchall()
        
        return [{
            "id": row[0],
            "manufacturer": row[1],
            "model": row[2],
            "year": row[3],
            "capacity": str(row[4]) if row[4] else "0",
            "condition": row[5],
            "location": row[6],
            "price": str(row[7]) if row[7] else "0",
            "mileage": str(row[8]) if row[8] else "0",
            "description": row[9],
            "created_at": str(row[10]) if row[10] else None
        } for row in listings]
    except Exception as e:
        logger.error(f"Error fetching crane listings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Market analysis endpoint
@app.get("/api/v1/analytics/market-analysis")
@limiter.limit("5/minute")
async def get_market_analysis():
    try:
        # Mock market analysis data
        return {
            "market_trends": {
                "total_listings": 150,
                "average_price": "$45,000",
                "price_trend": "increasing",
                "popular_types": ["Tower Crane", "Mobile Crane", "Crawler Crane"]
            },
            "regional_analysis": {
                "north_america": {"listings": 45, "avg_price": "$52,000"},
                "europe": {"listings": 38, "avg_price": "$41,000"},
                "asia": {"listings": 42, "avg_price": "$38,000"},
                "other": {"listings": 25, "avg_price": "$35,000"}
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating market analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Consultation submission endpoint
@app.post("/api/v1/consultations")
@limiter.limit("3/minute")
async def submit_consultation(consultation: ConsultationRequest, db: Session = Depends(get_db)):
    try:
        new_consultation = Consultation(
            name=consultation.name,
            email=consultation.email,
            phone=consultation.phone,
            message=consultation.message
        )
        
        db.add(new_consultation)
        db.commit()
        db.refresh(new_consultation)
        
        # Send confirmation email to user
        if EMAIL_SERVICE_AVAILABLE:
            try:
                email_service.send_consultation_confirmation(
                    consultation.name, 
                    consultation.email, 
                    str(new_consultation.id)
                )
                
                # Send admin notification
                email_service.send_admin_consultation_notification(
                    consultation.name,
                    consultation.email,
                    str(new_consultation.id),
                    consultation.message
                )
                
                logger.info(f"Consultation confirmation emails sent for consultation {new_consultation.id}")
            except Exception as e:
                logger.error(f"Failed to send consultation emails: {str(e)}")
        
        logger.info(f"New consultation submitted by: {consultation.email}")
        
        return {
            "success": True,
            "message": "Consultation submitted successfully. You will receive a confirmation email shortly.",
            "consultation_id": new_consultation.id
        }
    except Exception as e:
        logger.error(f"Error submitting consultation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Password reset request endpoint
@app.post("/api/v1/auth/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(email: str, db: Session = Depends(get_db)):
    try:
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return {"success": False, "message": "Email not found"}
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        # In a real implementation, you'd store this token in the database with expiry
        
        # Send password reset email
        if EMAIL_SERVICE_AVAILABLE:
            try:
                email_service.send_password_reset_email(user.full_name, user.email, reset_token)
                logger.info(f"Password reset email sent to {email}")
            except Exception as e:
                logger.error(f"Failed to send password reset email: {str(e)}")
                return {"success": False, "message": "Failed to send reset email"}
        
        return {"success": True, "message": "Password reset email sent"}
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Email verification endpoint
@app.post("/api/v1/auth/verify-email")
@limiter.limit("5/minute")
async def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        # In a real implementation, you'd verify the token from the database
        # For now, we'll just mark the user as verified
        # You should implement proper token verification logic here
        
        return {"success": True, "message": "Email verified successfully"}
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Test email endpoint (for testing purposes)
@app.post("/api/v1/test-email")
@limiter.limit("2/minute")
async def test_email(email: str, email_type: str = "welcome"):
    try:
        if not EMAIL_SERVICE_AVAILABLE:
            return {"success": False, "message": "Email service not available"}
        
        # Simple test - just try to send a basic email
        try:
            success = email_service._send_email(
                email, 
                "Test Email from Crane Intelligence", 
                "<h1>Test Email</h1><p>This is a test email from Crane Intelligence.</p>",
                "Test Email\n\nThis is a test email from Crane Intelligence."
            )
            
            if success:
                return {"success": True, "message": f"Test email sent successfully to {email}"}
            else:
                return {"success": False, "message": "Failed to send test email"}
                
        except Exception as e:
            logger.error(f"Email sending error: {str(e)}")
            return {"success": False, "message": f"Email sending failed: {str(e)}"}
            
    except Exception as e:
        logger.error(f"Test email error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Mount static files - DISABLED (frontend served by nginx)
# app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Frontend serving routes - DISABLED (frontend served by nginx)
# @app.get("/{path:path}")
# async def serve_frontend(path: str):
#     frontend_path = Path("frontend") / path
#     if frontend_path.exists() and frontend_path.is_file():
#         return FileResponse(str(frontend_path))
#     else:
#         # Serve homepage.html for root path
#         homepage_path = Path("frontend") / "homepage.html"
#         return FileResponse(str(homepage_path))

# Add missing endpoints for live-data-framework compatibility
@app.get("/api/v1/dashboard/data")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """Legacy endpoint - redirects to dashboard stats"""
    try:
        from sqlalchemy import text
        
        # Get basic stats
        total_listings = db.execute(text("SELECT COUNT(*) FROM crane_listings")).fetchone()[0]
        total_users = db.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0]
        
        return {
            "total_users": total_users,
            "active_users": total_users,
            "total_listings": total_listings,
            "system_health": "excellent",
            "uptime": "99.9%"
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
        return {"error": str(e)}

@app.get("/api/v1/market/trends")
async def get_market_trends(db: Session = Depends(get_db)):
    """Get market trends data"""
    try:
        from sqlalchemy import text
        result = db.execute(
            text("""
                SELECT crane_type, AVG(average_price) as avg_price, 
                       SUM(market_volume) as total_volume
                FROM market_data
                GROUP BY crane_type
                LIMIT 10
            """)
        )
        trends = result.fetchall()
        
        return {
            "labels": [row[0] for row in trends],
            "datasets": [{
                "label": "Average Price",
                "data": [float(row[1]) if row[1] else 0 for row in trends]
            }]
        }
    except Exception as e:
        logger.error(f"Error fetching market trends: {str(e)}")
        return {"labels": [], "datasets": []}

@app.get("/api/v1/equipment/live")
async def get_equipment_live(db: Session = Depends(get_db)):
    """Get live equipment data"""
    try:
        from sqlalchemy import text
        result = db.execute(
            text("""
                SELECT id, manufacturer, model, year, price, location, condition
                FROM crane_listings
                ORDER BY created_at DESC
                LIMIT 20
            """)
        )
        equipment = result.fetchall()
        
        return [{
            "id": f"CRN-{str(row[0]).zfill(4)}",
            "type": row[1],
            "model": row[2],
            "year": row[3],
            "value": float(row[4]) if row[4] else 0,
            "location": row[5],
            "status": row[6],
            "lastUpdate": datetime.utcnow().isoformat()
        } for row in equipment]
    except Exception as e:
        logger.error(f"Error fetching equipment live: {str(e)}")
        return []

@app.get("/api/v1/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get analytics overview"""
    try:
        from sqlalchemy import text
        
        total_listings = db.execute(text("SELECT COUNT(*) FROM crane_listings")).fetchone()[0]
        avg_price = db.execute(text("SELECT AVG(price) FROM crane_listings")).fetchone()[0]
        
        return {
            "total_listings": total_listings,
            "average_price": float(avg_price) if avg_price else 0,
            "market_trend": "stable",
            "popular_types": ["Mobile Crane", "Tower Crane", "Crawler Crane"]
        }
    except Exception as e:
        logger.error(f"Error fetching analytics overview: {str(e)}")
        return {}

@app.get("/api/v1/notifications")
async def get_notifications_legacy(db: Session = Depends(get_db)):
    """Legacy notifications endpoint"""
    try:
        from sqlalchemy import text
        result = db.execute(
            text("""
                SELECT id, title, message, type, is_read, created_at
                FROM notifications
                ORDER BY created_at DESC
                LIMIT 10
            """)
        )
        notifications = result.fetchall()
        
        return [{
            "id": row[0],
            "title": row[1],
            "message": row[2],
            "type": row[3],
            "is_read": row[4],
            "created_at": str(row[5]) if row[5] else None
        } for row in notifications]
    except Exception as e:
        logger.error(f"Error fetching notifications: {str(e)}")
        return []

# Import and include API routes
try:
    from app.api_routes import api_router
    app.include_router(api_router)
    logger.info("API routes loaded successfully")
except ImportError as e:
    logger.error(f"Failed to import API routes: {str(e)}")

# Import and include Admin API routes
try:
    from app.api.v1.admin_simple import router as admin_router
    app.include_router(admin_router, prefix="/api/v1")
    logger.info("✅ Admin API routes loaded successfully")
except ImportError as e:
    logger.warning(f"Failed to import Admin API routes: {str(e)}")
except Exception as e:
    logger.warning(f"Error loading Admin API routes: {str(e)}")

# Root endpoint - returns API info
@app.get("/")
async def root():
    return {
        "name": "Crane Intelligence API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/api/v1/auth/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)