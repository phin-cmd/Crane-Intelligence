"""
Main FastAPI application for Crane Intelligence Platform
Production-ready simplified version
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
import os
from pathlib import Path

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

# Pydantic models
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
    subscription_tier: str = "basic"

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    username: str
    user_role: str
    subscription_tier: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    access_token: str = None
    user: UserResponse = None

# JWT configuration
SECRET_KEY = "crane-intelligence-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create JWT token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "message": "Crane Intelligence API is running"}

# Login endpoint
@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(user_data: UserLogin):
    try:
        # Simple demo authentication
        if user_data.email == "test@craneintelligence.com" and user_data.password == "password123":
            # Create demo user
            demo_user = UserResponse(
                id=1,
                email=user_data.email,
                full_name="Test User",
                username="testuser",
                user_role="admin",
                subscription_tier="premium"
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

# Register endpoint
@app.post("/api/v1/auth/register", response_model=LoginResponse)
async def register(user_data: UserRegister):
    try:
        # Create demo user for registration
        demo_user = UserResponse(
            id=2,
            email=user_data.email,
            full_name=user_data.full_name,
            username=user_data.username or user_data.email.split('@')[0],
            user_role=user_data.user_role,
            subscription_tier=user_data.subscription_tier
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

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve frontend files
@app.get("/{path:path}")
async def serve_frontend(path: str):
    frontend_path = Path("frontend") / path
    if frontend_path.exists() and frontend_path.is_file():
        return FileResponse(str(frontend_path))
    else:
        # Serve homepage.html for root path
        homepage_path = Path("frontend") / "homepage.html"
        return FileResponse(str(homepage_path))

# Root endpoint
@app.get("/")
async def root():
    homepage_path = Path("frontend") / "homepage.html"
    return FileResponse(str(homepage_path))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)