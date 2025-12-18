"""
Unified Main FastAPI Application for Crane Intelligence Platform
Consolidates: main.py and main_simple.py
Production-ready with database initialization and all features
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from pathlib import Path
import os
import logging

# Try to import database components (optional - graceful fallback if not available)
try:
    from .config import get_db, engine, Base
    from .models.user import User  # Use new User model from models/user.py
    from .auth_endpoints import router as auth_router
    DATABASE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Database components not available: {e}")
    DATABASE_AVAILABLE = False
    auth_router = None

# Try to import simplified auth router as fallback
try:
    from .api.v1.auth_simple import router as auth_simple_router
    AUTH_SIMPLE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Simple auth router not available: {e}")
    AUTH_SIMPLE_AVAILABLE = False
    auth_simple_router = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Crane Intelligence API",
    version="1.0.0",
    description="Professional Crane Valuation and Market Analysis Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== PYDANTIC MODELS ====================

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    username: str = None
    company_name: str = None
    user_role: str = "user"

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    username: str
    user_role: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: str = None
    user: UserResponse = None

# ==================== JWT CONFIGURATION ====================

SECRET_KEY = os.getenv("SECRET_KEY", "crane-intelligence-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ==================== DATABASE INITIALIZATION ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database and create default users on startup"""
    if not DATABASE_AVAILABLE:
        logger.warning("Database not available, skipping initialization")
        return
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create default admin user if it doesn't exist
        # Temporarily disabled to avoid is_admin errors - users can sign up via API
        # db = next(get_db())
        # try:
        #     admin_user = db.query(User).filter(User.email == "admin@craneintelligence.com").first()
        #     if not admin_user:
        #         from .auth_utils import get_password_hash
        #         from .models.user import UserRole, SubscriptionTier
        #         admin_user = User(
        #             email="admin@craneintelligence.com",
        #             hashed_password=get_password_hash("admin123"),
        #             full_name="System Administrator",
        #             username="admin",
        #             company_name="Crane Intelligence",
        #             user_role=UserRole.OTHERS,
        #             subscription_tier=SubscriptionTier.FREE,
        #             is_active=True,
        #             is_verified=True,
        #             total_payments=0.0
        #         )
        #         db.add(admin_user)
        #         
        #         # Create a regular user for testing
        #         test_user = db.query(User).filter(User.email == "user@craneintelligence.com").first()
        #         if not test_user:
        #             test_user = User(
        #                 email="user@craneintelligence.com",
        #                 hashed_password=get_password_hash("user123"),
        #                 full_name="Test User",
        #                 username="testuser",
        #                 company_name="Test Company",
        #                 user_role=UserRole.OTHERS,
        #                 subscription_tier=SubscriptionTier.FREE,
        #                 is_active=True,
        #                 is_verified=True,
        #                 total_payments=0.0
        #             )
        #             db.add(test_user)
        #         
        #         db.commit()
        #         logger.info("Default users created successfully")
        # finally:
        #     db.close()
        logger.info("Default user creation skipped - use signup API instead")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # Don't raise - allow app to start even if database init fails
        logger.warning("Continuing without database initialization")

# ==================== API ROUTERS ====================

# Include authentication router (if available)
# Old auth router disabled - using auth_simple_router instead
# if DATABASE_AVAILABLE and auth_router:
#     try:
#         app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
#         logger.info("✓ Authentication router registered")
#     except Exception as e:
#         logger.warning(f"Could not load auth router: {e}")

# Include simplified auth router (for signup endpoint)
if AUTH_SIMPLE_AVAILABLE and auth_simple_router:
    try:
        app.include_router(auth_simple_router, prefix="/api/v1/auth", tags=["authentication"])
        logger.info("✓ Simple authentication router registered")
    except Exception as e:
        logger.warning(f"Could not load simple auth router: {e}")

# Include full auth router (with email verification, password reset, etc.)
try:
    from app.api.v1.auth import router as full_auth_router
    app.include_router(full_auth_router, prefix="/api/v1", tags=["authentication"])
    logger.info("✓ Full authentication router registered")
except Exception as e:
    logger.warning(f"Could not load full auth router: {e}")

# Include notifications router
try:
    from app.api.v1.notifications import router as notifications_router
    app.include_router(notifications_router, prefix="/api/v1", tags=["Notifications"])
    logger.info("✓ Notifications router registered")
except Exception as e:
    logger.warning(f"Could not load notifications router: {e}")

# Include draft reminders router
try:
    from app.api.v1.draft_reminders import router as draft_reminders_router
    app.include_router(draft_reminders_router, prefix="/api/v1", tags=["Draft Reminders"])
    logger.info("✓ Draft reminders router registered")
except Exception as e:
    logger.warning(f"Could not load draft reminders router: {e}")

# Include enhanced data router
try:
    from app.api.v1.enhanced_data import router as enhanced_data_router
    app.include_router(enhanced_data_router, prefix="/api/v1")
    logger.info("✓ Enhanced data router registered")
except Exception as e:
    logger.warning(f"Could not load enhanced_data router: {e}")
    import traceback
    traceback.print_exc()

# Include valuation router (if available)
try:
    from app.api.v1.valuation import router as valuation_router
    app.include_router(valuation_router, prefix="/api/v1", tags=["valuation"])
    logger.info("✓ Valuation router registered")
except Exception as e:
    logger.warning(f"Could not load valuation router: {e}")

# Include enhanced valuation router (if available)
try:
    from app.api.v1.enhanced_valuation import router as enhanced_valuation_router
    app.include_router(enhanced_valuation_router, prefix="/api/v1", tags=["enhanced-valuation"])
    logger.info("✓ Enhanced valuation router registered")
except Exception as e:
    logger.warning(f"Could not load enhanced_valuation router: {e}")

# Public configuration endpoint (always register, not dependent on enhanced_valuation)
try:
    from app.api.v1.config import router as config_router
    app.include_router(config_router, prefix="/api/v1/config", tags=["configuration"])
    logger.info("✓ Configuration router registered")
except Exception as e:
    logger.error(f"Could not load config router: {e}")

# Include email router
try:
    from app.api.v1.email import router as email_router
    app.include_router(email_router, prefix="/api/v1/email", tags=["email"])
    logger.info("✓ Email router registered")
except Exception as e:
    logger.warning(f"Could not load email router: {e}")

# Include comprehensive email router
try:
    from app.api.v1.comprehensive_email import router as comprehensive_email_router
    app.include_router(comprehensive_email_router, prefix="/api/v1/email", tags=["email"])
    logger.info("✓ Comprehensive email router registered")
except Exception as e:
    logger.warning(f"Could not load comprehensive email router: {e}")

# Subscription router removed - subscription logic removed from platform

# Include reports router
try:
    from app.api.v1.reports import router as reports_router
    app.include_router(reports_router, prefix="/api/v1", tags=["reports"])
    logger.info("✓ Reports router registered")
except Exception as e:
    logger.warning(f"Could not load reports router: {e}")

# Include FMV reports router
try:
    from app.api.v1.fmv_reports import router as fmv_reports_router
    app.include_router(fmv_reports_router, prefix="/api/v1", tags=["fmv-reports"])
    logger.info("✓ FMV Reports router registered")
except Exception as e:
    logger.warning(f"Could not load FMV reports router: {e}")

# Include Admin FMV reports router (matches frontend expectations)
try:
    from app.api.v1.admin_fmv_reports import router as admin_fmv_reports_router
    app.include_router(admin_fmv_reports_router, prefix="/api/v1", tags=["admin-fmv-reports"])
    logger.info("✓ Admin FMV Reports router registered")
except Exception as e:
    logger.warning(f"Could not load Admin FMV reports router: {e}")

# Include Admin Fallback Requests router
try:
    from app.api.v1.admin_fallback_requests import router as admin_fallback_requests_router
    app.include_router(admin_fallback_requests_router, prefix="/api/v1", tags=["admin-fallback-requests"])
    logger.info("✓ Admin Fallback Requests router registered")
except Exception as e:
    logger.warning(f"Could not load Admin Fallback Requests router: {e}")

# Include analytics router
try:
    from app.api.v1.analytics import router as analytics_router
    app.include_router(analytics_router, prefix="/api/v1", tags=["analytics"])
    logger.info("✓ Analytics router registered")
except Exception as e:
    logger.warning(f"Could not load analytics router: {e}")

# Include market data router
try:
    from app.api.v1.market_data import router as market_data_router
    app.include_router(market_data_router, prefix="/api/v1", tags=["market-data"])
    logger.info("✓ Market data router registered")
except Exception as e:
    logger.warning(f"Could not load market data router: {e}")

# Include equipment router
try:
    from app.api.v1.equipment import router as equipment_router
    app.include_router(equipment_router, prefix="/api/v1/equipment", tags=["equipment"])
    logger.info("✓ Equipment router registered")
except Exception as e:
    logger.warning(f"Could not load equipment router: {e}")

# Include admin authentication router
try:
    from app.api.v1.admin_auth import router as admin_auth_router
    app.include_router(admin_auth_router, prefix="/api/v1", tags=["admin-auth"])
    logger.info("✓ Admin authentication router registered")
except Exception as e:
    logger.warning(f"Could not load admin auth router: {e}")

# Include admin users management router
try:
    from app.api.v1.admin_users import router as admin_users_router
    app.include_router(admin_users_router, prefix="/api/v1", tags=["admin-users"])
    logger.info("✓ Admin users router registered")
except Exception as e:
    logger.warning(f"Could not load admin users router: {e}")

# Include admin router (existing admin endpoints)
try:
    from app.api.v1.admin import router as admin_router
    app.include_router(admin_router, prefix="/api/v1", tags=["admin"])
    logger.info("✓ Admin router registered")
except Exception as e:
    logger.warning(f"Could not load admin router: {e}")

# Include admin impersonation router
try:
    from app.api.v1.admin_impersonation import router as admin_impersonation_router
    app.include_router(admin_impersonation_router, prefix="/api/v1", tags=["admin-impersonation"])
    logger.info("✓ Admin impersonation router registered")
except Exception as e:
    logger.warning(f"Could not load admin impersonation router: {e}")

# Include notification preferences router
try:
    from app.api.v1.notification_preferences import router as notification_preferences_router
    app.include_router(notification_preferences_router, prefix="/api/v1", tags=["notifications"])
    logger.info("✓ Notification preferences router registered")
except Exception as e:
    logger.warning(f"Could not load notification preferences router: {e}")

# Include payment webhooks router
try:
    from app.api.v1.payment_webhooks import router as payment_webhooks_router
    app.include_router(payment_webhooks_router, prefix="/api/v1", tags=["webhooks"])
    logger.info("✓ Payment webhooks router registered")
except Exception as e:
    logger.warning(f"Could not load payment webhooks router: {e}")

# Include user-facing payments router
try:
    from app.api.v1.payments import router as payments_router
    app.include_router(payments_router, prefix="/api/v1", tags=["payments"])
    logger.info("✓ Payments router registered")
except Exception as e:
    logger.warning(f"Could not load payments router: {e}")

# Include admin cranes router
try:
    from app.api.v1.admin_cranes import router as admin_cranes_router
    app.include_router(admin_cranes_router, prefix="/api/v1", tags=["admin-cranes"])
    logger.info("✓ Admin cranes router registered")
except Exception as e:
    logger.warning(f"Could not load admin cranes router: {e}")

# Include admin valuations router
try:
    from app.api.v1.admin_valuations import router as admin_valuations_router
    app.include_router(admin_valuations_router, prefix="/api/v1", tags=["admin-valuations"])
    logger.info("✓ Admin valuations router registered")
except Exception as e:
    logger.warning(f"Could not load admin valuations router: {e}")

# Include admin payments router
try:
    from app.api.v1.admin_payments import router as admin_payments_router
    app.include_router(admin_payments_router, prefix="/api/v1", tags=["admin-payments"])
    logger.info("✓ Admin payments router registered")
except Exception as e:
    logger.warning(f"Could not load admin payments router: {e}")

# Admin subscriptions router removed - subscription logic removed from platform

# Include admin roles router
try:
    from app.api.v1.admin_roles import router as admin_roles_router
    app.include_router(admin_roles_router, prefix="/api/v1", tags=["admin-roles"])
    logger.info("✓ Admin roles router registered")
except Exception as e:
    logger.warning(f"Could not load admin roles router: {e}")

# Include admin algorithm router
try:
    from app.api.v1.admin_algorithm import router as admin_algorithm_router
    app.include_router(admin_algorithm_router, prefix="/api/v1", tags=["admin-algorithm"])
    logger.info("✓ Admin algorithm router registered")
except Exception as e:
    logger.warning(f"Could not load admin algorithm router: {e}")

# Include admin 2FA router
try:
    from app.api.v1.admin_2fa import router as admin_2fa_router
    app.include_router(admin_2fa_router, prefix="/api/v1", tags=["admin-2fa"])
    logger.info("✓ Admin 2FA router registered")
except Exception as e:
    logger.warning(f"Could not load admin 2FA router: {e}")

# Include admin audit router
try:
    from app.api.v1.admin_audit import router as admin_audit_router
    app.include_router(admin_audit_router, prefix="/api/v1", tags=["admin-audit"])
    logger.info("✓ Admin audit router registered")
except Exception as e:
    logger.warning(f"Could not load admin audit router: {e}")

# Include admin sessions router
try:
    from app.api.v1.admin_sessions import router as admin_sessions_router
    app.include_router(admin_sessions_router, prefix="/api/v1", tags=["admin-sessions"])
    logger.info("✓ Admin sessions router registered")
except Exception as e:
    logger.warning(f"Could not load admin sessions router: {e}")

# Include admin payment reconciliation router
try:
    from app.api.v1.admin_payment_reconciliation import router as admin_payment_reconciliation_router
    app.include_router(admin_payment_reconciliation_router, prefix="/api/v1", tags=["admin-payment-reconciliation"])
    logger.info("✓ Admin payment reconciliation router registered")
except Exception as e:
    logger.warning(f"Could not load admin payment reconciliation router: {e}")

# Include admin system health router
try:
    from app.api.v1.admin_system_health import router as admin_system_health_router
    app.include_router(admin_system_health_router, prefix="/api/v1", tags=["admin-system-health"])
    logger.info("✓ Admin system health router registered")
except Exception as e:
    logger.warning(f"Could not load admin system health router: {e}")

# Include admin email management router
try:
    from app.api.v1.admin_email_management import router as admin_email_management_router
    app.include_router(admin_email_management_router, prefix="/api/v1", tags=["admin-email-management"])
    logger.info("✓ Admin email management router registered")
except Exception as e:
    logger.warning(f"Could not load admin email management router: {e}")

# Include admin bulk operations router
try:
    from app.api.v1.admin_bulk_operations import router as admin_bulk_operations_router
    app.include_router(admin_bulk_operations_router, prefix="/api/v1", tags=["admin-bulk-operations"])
    logger.info("✓ Admin bulk operations router registered")
except Exception as e:
    logger.warning(f"Could not load admin bulk operations router: {e}")

# Include admin GDPR router
try:
    from app.api.v1.admin_gdpr import router as admin_gdpr_router
    app.include_router(admin_gdpr_router, prefix="/api/v1", tags=["admin-gdpr"])
    logger.info("✓ Admin GDPR router registered")
except Exception as e:
    logger.warning(f"Could not load admin GDPR router: {e}")

# ==================== HEALTH CHECK ENDPOINTS ====================

@app.get("/api/v1/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "message": "Crane Intelligence API is running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check_alt():
    """Alternative health check endpoint"""
    return {
        "status": "healthy",
        "app": "Crane Intelligence Platform",
        "version": "1.0.0"
    }

@app.get("/api/v1/database/health")
async def database_health(db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    """Database health check endpoint"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )

# Add stub endpoints for dashboard and notifications
@app.get("/api/v1/dashboard/data")
async def get_dashboard_data():
    """Get dashboard data"""
    return {
        "success": True,
        "data": {
            "stats": {},
            "recent_activity": [],
            "notifications": []
        }
    }

# Removed stub endpoint - using notifications router instead
# @app.get("/api/v1/notifications")
# async def get_notifications():
#     """Get user notifications"""
#     return {
#         "success": True,
#         "notifications": [],
#         "count": 0
#     }

@app.get("/api/v1/market/trends")
async def get_market_trends():
    """Get market trends"""
    return {
        "success": True,
        "trends": [],
        "data": []
    }

@app.get("/api/v1/equipment/live")
async def get_equipment_live():
    """Get live equipment data"""
    return {
        "success": True,
        "equipment": [],
        "count": 0
    }

@app.get("/api/v1/analytics/overview")
async def get_analytics_overview():
    """Get analytics overview"""
    return {
        "success": True,
        "analytics": {},
        "metrics": {}
    }

# ==================== AUTHENTICATION ENDPOINTS (Simple - for backward compatibility) ====================

@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(user_data: UserLogin):
    """
    Simple login endpoint for backward compatibility
    In production, use the full auth router at /api/v1/auth/login
    """
    try:
        # Simple demo authentication
        if user_data.email == "test@craneintelligence.com" and user_data.password == "password123":
            # Create demo user
            demo_user = UserResponse(
                id=1,
                email=user_data.email,
                full_name="Test User",
                username="testuser",
                user_role="admin"
            )
            
            # Create access token
            access_token = create_access_token(data={"sub": user_data.email, "user_id": 1})
            
            return LoginResponse(
                success=True,
                message="Login successful",
                access_token=access_token,
                user=demo_user
            )
        else:
            return LoginResponse(
                success=False,
                message="Invalid credentials"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/auth/register", response_model=LoginResponse)
async def register(user_data: UserRegister):
    """
    Simple registration endpoint for backward compatibility
    In production, use the full auth router at /api/v1/auth/register
    """
    try:
        # Create demo user for registration
        demo_user = UserResponse(
            id=2,
            email=user_data.email,
            full_name=user_data.full_name,
            username=user_data.username or user_data.email.split('@')[0],
            user_role=user_data.user_role
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": user_data.email, "user_id": 2})
        
        return LoginResponse(
            success=True,
            message="Registration successful",
            access_token=access_token,
            user=demo_user
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== STATIC FILES ====================

# Frontend is served separately by Nginx, so we don't mount it here
# app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve frontend files (fallback if Nginx is not available)
@app.get("/{path:path}")
async def serve_frontend(path: str):
    """Serve frontend files (fallback)"""
    frontend_path = Path("frontend") / path
    if frontend_path.exists() and frontend_path.is_file():
        return FileResponse(str(frontend_path))
    else:
        # Serve homepage.html for root path
        homepage_path = Path("frontend") / "homepage.html"
        if homepage_path.exists():
            return FileResponse(str(homepage_path))
        else:
            raise HTTPException(status_code=404, detail="File not found")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    homepage_path = Path("frontend") / "homepage.html"
    if homepage_path.exists():
        return FileResponse(str(homepage_path))
    else:
        return {
            "message": "Crane Intelligence Platform API",
            "version": "1.0.0",
            "docs": "/docs"
        }

# ==================== MAIN ENTRY POINT ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)