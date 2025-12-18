"""
Fallback Request Pydantic Schemas
Request and response models for fallback request API
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class FallbackRequestCreate(BaseModel):
    """Request to create a fallback valuation request"""
    manufacturer: str = Field(..., min_length=1, max_length=255)
    model: str = Field(..., min_length=1, max_length=255)
    year: int = Field(..., ge=1990, le=2025)
    serial_number: Optional[str] = None
    capacity_tons: float = Field(..., gt=0)
    crane_type: str = Field(..., min_length=1)
    operating_hours: int = Field(..., ge=0)
    mileage: Optional[int] = Field(None, ge=0)
    boom_length: Optional[float] = Field(None, ge=0)
    jib_length: Optional[float] = Field(None, ge=0)
    max_hook_height: Optional[float] = Field(None, ge=0)
    max_radius: Optional[float] = Field(None, ge=0)
    region: str = Field(..., min_length=1)
    condition: str = Field(..., min_length=1)
    additional_specs: Optional[str] = None
    special_features: Optional[str] = None
    usage_history: Optional[str] = None
    user_email: Optional[EmailStr] = None  # For unauthenticated users


class FallbackRequestResponse(BaseModel):
    """Fallback request response model"""
    id: int
    user_id: Optional[int] = None
    user_email: str
    manufacturer: str
    model: str
    year: int
    serial_number: Optional[str] = None
    capacity_tons: float
    crane_type: str
    operating_hours: int
    mileage: Optional[int] = None
    boom_length: Optional[float] = None
    jib_length: Optional[float] = None
    max_hook_height: Optional[float] = None
    max_radius: Optional[float] = None
    region: str
    condition: str
    additional_specs: Optional[str] = None
    special_features: Optional[str] = None
    usage_history: Optional[str] = None
    status: str
    assigned_analyst: Optional[str] = None
    analyst_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    linked_fmv_report_id: Optional[int] = None
    created_at: datetime
    in_review_at: Optional[datetime] = None
    valuation_started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    updated_at: datetime
    
    class Config:
        orm_mode = True


class FallbackRequestUpdate(BaseModel):
    """Update fallback request fields (admin only)"""
    status: Optional[str] = None
    assigned_analyst: Optional[str] = None
    analyst_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    linked_fmv_report_id: Optional[int] = None

