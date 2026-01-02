"""
Public Configuration Endpoint
Returns public configuration values (like Stripe publishable key) to frontend
"""

import os
from fastapi import APIRouter
from pydantic import BaseModel
from ...core.config import settings

router = APIRouter()


class PublicConfigResponse(BaseModel):
    """Public configuration response"""
    stripe_publishable_key: str
    stripe_mode: str  # "test" or "live" - indicates which Stripe mode is active
    environment: str  # "dev", "uat", or "prod" - indicates current environment
    frontend_url: str
    app_name: str
    app_version: str


def _detect_stripe_mode() -> str:
    """
    Detect Stripe mode based on publishable key prefix.
    Returns "test" for test keys, "live" for live keys, or "unknown" if not configured.
    """
    publishable_key = settings.stripe_publishable_key or ""
    if publishable_key.startswith("pk_test_"):
        return "test"
    elif publishable_key.startswith("pk_live_"):
        return "live"
    else:
        return "unknown"


@router.get("/public", response_model=PublicConfigResponse)
async def get_public_config():
    """
    Get public configuration values
    Returns configuration that can be safely exposed to frontend
    """
    environment = os.getenv("ENVIRONMENT", "prod").lower()
    stripe_mode = _detect_stripe_mode()
    
    return PublicConfigResponse(
        stripe_publishable_key=settings.stripe_publishable_key or "",
        stripe_mode=stripe_mode,
        environment=environment,
        frontend_url=getattr(settings, 'frontend_url', 'https://craneintelligence.tech'),
        app_name=settings.app_name,
        app_version=settings.app_version
    )

