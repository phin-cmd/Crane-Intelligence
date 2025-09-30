"""
Simple FastAPI application for Crane Intelligence Platform
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from .config import get_db, engine, Base
from .models import User
from .auth_endpoints import router as auth_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Crane Intelligence Platform",
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

# Include authentication router
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create default admin user if it doesn't exist
        db = next(get_db())
        admin_user = db.query(User).filter(User.email == "admin@craneintelligence.com").first()
        if not admin_user:
            from .auth_utils import get_password_hash
            admin_user = User(
                email="admin@craneintelligence.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                is_active=True,
                is_admin=True
            )
            db.add(admin_user)
            
            # Create a regular user for testing
            test_user = User(
                email="user@craneintelligence.com",
                hashed_password=get_password_hash("user123"),
                full_name="Test User",
                is_active=True,
                is_admin=False
            )
            db.add(test_user)
            
            db.commit()
            logger.info("Default users created successfully")
        
        db.close()
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": "Crane Intelligence Platform",
        "version": "1.0.0"
    }

# Database health check
@app.get("/api/v1/database/health")
async def database_health(db: Session = Depends(get_db)):
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

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Crane Intelligence Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
