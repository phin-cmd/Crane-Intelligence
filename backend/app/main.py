"""
Main FastAPI application for Crane Intelligence Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.database import init_db
from .api.v1 import auth, valuation, market_data, enhanced_data, subscription, enhanced_valuation, data_refresh, reports

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
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(valuation.router, prefix="/api/v1")
app.include_router(market_data.router, prefix="/api/v1")
app.include_router(enhanced_data.router, prefix="/api/v1")
app.include_router(subscription.router, prefix="/api/v1")
app.include_router(enhanced_valuation.router, prefix="/api/v1")
app.include_router(data_refresh.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Crane Intelligence Platform",
        "version": settings.app_version,
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
