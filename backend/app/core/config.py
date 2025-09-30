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
    
    # Email Settings
    mail_server: str = "smtp.gmail.com"
    mail_port: int = 587
    mail_username: str = "pgenerelly@craneintelligence.tech"
    mail_password: str = ""  # Will be set via environment variable
    mail_use_tls: bool = True
    mail_use_ssl: bool = False
    mail_from_name: str = "Crane Intelligence Platform"
    mail_from_email: str = "pgenerelly@craneintelligence.tech"
    
    # Email Templates
    email_templates_dir: str = "backend/templates/emails"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "development":
    settings.debug = True
    settings.database_echo = True
