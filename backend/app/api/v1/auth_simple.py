"""
Crane Intelligence Platform - Simplified Authentication API
This is a simplified version to get login/signup working immediately
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime

from ...services.auth_service import auth_service
from ...models.user import User, UserRole, SubscriptionTier
from ...core.database import get_db

router = APIRouter()

class AuthRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any] = None
    error: str = None

@router.post("/login", response_model=AuthResponse)
async def login(request: AuthRequest, db: Session = Depends(get_db)):
    """User login endpoint"""
    try:
        print(f"Login attempt for: {request.email}")
        
        # Find user
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            print(f"User not found: {request.email}")
            return AuthResponse(
                success=False,
                message="Login failed",
                error="Invalid email or password"
            )
        
        print(f"User found: {user.email}, verified: {user.is_verified}, active: {user.is_active}")
        
        # Verify password
        if not auth_service.verify_password(request.password, user.hashed_password):
            print("Password verification failed")
            return AuthResponse(
                success=False,
                message="Login failed",
                error="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            print("User account is inactive")
            return AuthResponse(
                success=False,
                message="Login failed",
                error="Account is deactivated"
            )
        
        # Create session tokens
        tokens = auth_service.create_session_tokens(
            user_id=user.id,
            email=user.email,
            subscription_tier=user.subscription_tier.value,
            user_role=user.user_role.value
        )
        
        print(f"Tokens created successfully")
        
        return AuthResponse(
            success=True,
            message="Welcome back! You've successfully logged in.",
            data={
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "subscription_tier": user.subscription_tier.value,
                    "user_role": user.user_role.value
                },
                "tokens": tokens
            }
        )
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return AuthResponse(
            success=False,
            message="Login failed",
            error="An error occurred during login"
        )

@router.post("/signup", response_model=AuthResponse)
async def signup(request: AuthRequest, db: Session = Depends(get_db)):
    """User signup endpoint"""
    try:
        print(f"Signup attempt for: {request.email}")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            print(f"User already exists: {request.email}")
            return AuthResponse(
                success=False,
                message="Signup failed",
                error="Email already registered"
            )
        
        # Create new user with all required fields
        new_user = User(
            email=request.email,
            hashed_password=auth_service.get_password_hash(request.password),
            full_name="Test User",
            username=request.email.split('@')[0],
            company_name="Test Company",
            user_role=UserRole.USER,
            subscription_tier=SubscriptionTier.BASIC,
            is_active=True,
            is_verified=True,  # Bypass email verification
            monthly_valuations_used=0,
            monthly_api_calls_used=0,
            subscription_start_date=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"User created successfully: {new_user.email}")
        
        return AuthResponse(
            success=True,
            message="Account created successfully!",
            data={
                "user": {
                    "id": new_user.id,
                    "email": new_user.email,
                    "username": new_user.username,
                    "subscription_tier": new_user.subscription_tier.value
                }
            }
        )
        
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return AuthResponse(
            success=False,
            message="Signup failed",
            error=f"An error occurred during signup: {str(e)}"
        )

# Add the missing get_current_user function
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return {
            "id": int(user_id),
            "email": email,
            "subscription_tier": payload.get("subscription_tier"),
            "role": payload.get("role")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
