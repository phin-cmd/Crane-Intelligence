"""
Public Configuration Endpoint
Returns public configuration values (like Stripe publishable key) to frontend
"""

from fastapi import APIRouter
from pydantic import BaseModel
from ...core.config import settings

router = APIRouter()


class PublicConfigResponse(BaseModel):
    """Public configuration response"""
    stripe_publishable_key: str
    frontend_url: str
    app_name: str
    app_version: str


@router.get("/public", response_model=PublicConfigResponse)
async def get_public_config():
    """
    Get public configuration values
    Returns configuration that can be safely exposed to frontend
    """
    return PublicConfigResponse(
        stripe_publishable_key=settings.stripe_publishable_key or "",
        frontend_url=getattr(settings, 'frontend_url', 'https://craneintelligence.tech'),
        app_name=settings.app_name,
        app_version=settings.app_version
    )

