"""
Main FastAPI application for Crane Intelligence Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys
import logging
from pathlib import Path

# Add config to path for cross-platform support
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'config'))

from .core.config import settings
from .core.database import init_db
from .api.v1 import auth, valuation, market_data, enhanced_data, subscription, enhanced_valuation, data_refresh, reports, admin, user_management, admin_comprehensive, equipment, database_management, analytics, ironplanet, realtime_feeds, api_status
# from .api.v1 import payment  # Payment integration for future use
from .core.admin_auth import admin_auth_router

# Security imports - temporarily disabled for basic functionality
# from .security.security_middleware import SecurityMiddleware
# from .security.security_config import get_security_config
# from .security.ssl_manager import SSLManager
# from .security.database_security import DatabaseSecurityManager
# from .security.rate_limiter import RateLimiter
# from .security.input_validator import InputValidator
# from .security.sql_injection_prevention import SQLInjectionPrevention
# from .security.xss_protection import XSSProtection
# from .security.csrf_protection import CSRFProtection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load security configuration - temporarily disabled
# security_config = get_security_config()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
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

# Add security middleware - temporarily disabled
# security_middleware = SecurityMiddleware(
#     app,
#     database_url=os.getenv("DATABASE_URL"),
#     redis_client=None,  # Will be initialized in the middleware
#     secret_key=security_config.csrf_secret_key
# )
# app.add_middleware(SecurityMiddleware, **{
#     "database_url": os.getenv("DATABASE_URL"),
#     "redis_client": None,
#     "secret_key": security_config.csrf_secret_key
# })

# Mount static files - use cross-platform path
try:
    from environment import env_config
    static_path = env_config.get_static_files_path()
except ImportError:
    # Fallback to relative path
    static_path = "frontend"

app.mount("/static", StaticFiles(directory=static_path), name="static")

# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(valuation.router, prefix="/api/v1")
app.include_router(market_data.router, prefix="/api/v1")
app.include_router(enhanced_data.router, prefix="/api/v1")
app.include_router(subscription.router, prefix="/api/v1")
app.include_router(enhanced_valuation.router, prefix="/api/v1")
app.include_router(data_refresh.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(user_management.router, prefix="/api/v1")
app.include_router(admin_comprehensive.router, prefix="/api/v1")
app.include_router(admin_auth_router, prefix="/api/v1")
app.include_router(equipment.router, prefix="/api/v1/equipment")
app.include_router(database_management.router, prefix="/api/v1")
# app.include_router(email.router, prefix="/api/v1/email")
# app.include_router(comprehensive_email.router, prefix="/api/v1/comprehensive")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(ironplanet.router, prefix="/api/v1")
app.include_router(realtime_feeds.router, prefix="/api/v1")
app.include_router(api_status.router, prefix="/api/v1")
# app.include_router(security.router, prefix="/api/v1")  # Temporarily disabled
# app.include_router(payment.router, prefix="/api/v1")  # Payment integration for future use

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")
        
        # Security middleware temporarily disabled
        # await security_middleware.initialize()
        # logger.info("Security middleware initialized successfully")
        
        # Log basic configuration
        logger.info("Basic configuration loaded")
        logger.info("Security features temporarily disabled for basic functionality")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }

# Security status endpoint - temporarily disabled
# @app.get("/security/status")
# async def security_status():
#     """Get comprehensive security status"""
#     try:
#         status = await security_middleware.get_security_status()
#         return {
#             "status": "success",
#             "security_status": status,
#             "timestamp": "2024-01-01T00:00:00Z"
#         }
#     except Exception as e:
#         logger.error(f"Error getting security status: {e}")
#         return {
#             "status": "error",
#             "error": str(e),
#             "timestamp": "2024-01-01T00:00:00Z"
#         }

# Serve frontend files - use cross-platform paths
@app.get("/{path:path}")
async def serve_frontend(path: str):
    try:
        from environment import env_config
        frontend_dir = env_config.frontend_dir
    except ImportError:
        frontend_dir = Path("frontend")
    
    frontend_path = frontend_dir / path
    if frontend_path.exists() and frontend_path.is_file():
        return FileResponse(str(frontend_path))
    else:
        # Serve homepage.html for root path
        homepage_path = frontend_dir / "homepage.html"
        return FileResponse(str(homepage_path))

# Root endpoint (fallback)
@app.get("/")
async def root():
    try:
        from environment import env_config
        frontend_dir = env_config.frontend_dir
    except ImportError:
        frontend_dir = Path("frontend")
    
    homepage_path = frontend_dir / "homepage.html"
    return FileResponse(str(homepage_path))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)