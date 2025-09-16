"""
Core configuration for Crane Intelligence Platform
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App Settings
    app_name: str = "Crane Intelligence Platform"
    app_version: str = "2.0.0"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///./crane_intelligence.db"
    database_echo: bool = False
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # API
    api_prefix: str = "/api/v1"
    
    # External Services
    crane_data_api_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "development":
    settings.debug = True
    settings.database_echo = True
