"""
Core configuration for Crane Intelligence Platform
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from pathlib import Path

# Get the project root directory (backend folder)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # App Settings
    app_name: str = "Crane Intelligence Platform"
    app_version: str = "2.0.0"
    debug: bool = False
    
    # Database
    # Default to localhost:5434 (Docker container) if DATABASE_URL not set
    # Docker container maps internal 5432 to host 5434
    database_url: str = os.getenv("DATABASE_URL", "postgresql://crane_user:crane_password@localhost:5434/crane_intelligence")
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
    
    # Email Settings - Brevo (formerly Sendinblue)
    # Note: Pydantic Settings will read from .env file automatically
    brevo_api_key: str = ""
    mail_server: str = "smtp-relay.brevo.com"
    mail_port: int = 587
    mail_username: str = "pgenerelly@craneintelligence.tech"
    mail_password: str = os.getenv("BREVO_SMTP_PASSWORD", "")  # Brevo SMTP password (different from API key)
    mail_use_tls: bool = True
    mail_use_ssl: bool = False
    mail_from_name: str = "Crane Intelligence Platform"
    mail_from_email: str = "pgenerelly@craneintelligence.tech"
    use_brevo_api: bool = True  # Use Brevo API instead of SMTP when True
    
    # Email Templates (use absolute path to avoid permission issues)
    # Try to detect the correct path based on where the code is running
    _default_template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates", "emails")
    if not os.path.exists(_default_template_dir):
        _default_template_dir = "/app/templates/emails"
    email_templates_dir: str = os.getenv("EMAIL_TEMPLATES_DIR", _default_template_dir)
    
    # Frontend URL for email links
    frontend_url: str = os.getenv("FRONTEND_URL", "https://craneintelligence.tech")
    admin_url: str = os.getenv("ADMIN_URL", "https://craneintelligence.tech")
    
    # Stripe Payment Settings
    stripe_publishable_key: str = ""
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    
    # GitHub Settings
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    github_repo: str = "phin-cmd/Crane-Intelligence"
    github_username: str = "phin@accranes.com"
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,  # Environment variables are case-insensitive
        extra="allow"  # Allow extra fields from .env that aren't in the model
    )

# Global settings instance
settings = Settings()

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "development":
    settings.debug = True
    settings.database_echo = True
