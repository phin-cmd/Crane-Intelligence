"""
Pydantic schemas for Crane data validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class CraneBase(BaseModel):
    """Base crane schema"""
    manufacturer: str = Field(..., description="Crane manufacturer")
    model: str = Field(..., description="Crane model")
    year: int = Field(..., ge=1900, le=2030, description="Manufacturing year")
    capacity_tons: Decimal = Field(..., gt=0, description="Lifting capacity in tons")
    hours: int = Field(..., ge=0, description="Operating hours")
    price: Decimal = Field(..., gt=0, description="Price in USD")
    location: Optional[str] = Field(None, description="Geographic location")
    condition: Optional[str] = Field(None, description="Equipment condition")

class CraneCreate(CraneBase):
    """Schema for creating a new crane"""
    pass

class CraneUpdate(BaseModel):
    """Schema for updating crane information"""
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = Field(None, ge=1900, le=2030)
    capacity_tons: Optional[Decimal] = Field(None, gt=0)
    hours: Optional[int] = Field(None, ge=0)
    price: Optional[Decimal] = Field(None, gt=0)
    location: Optional[str] = None
    condition: Optional[str] = None

class CraneResponse(CraneBase):
    """Schema for crane response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CraneAnalysis(BaseModel):
    """Schema for crane analysis results"""
    crane_id: int
    deal_score: int = Field(..., ge=0, le=100, description="Deal score (0-100)")
    estimated_value: Decimal = Field(..., gt=0, description="Estimated market value")
    confidence_score: Decimal = Field(..., ge=0, le=1, description="Confidence in analysis (0-1)")
    comparable_count: int = Field(..., ge=0, description="Number of comparable cranes")
    market_position: str = Field(..., description="Market positioning")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    recommendations: List[str] = Field(default_factory=list, description="Investment recommendations")
    analysis_date: datetime = Field(default_factory=datetime.utcnow)

class CraneListResponse(BaseModel):
    """Schema for paginated crane list response"""
    cranes: List[CraneResponse]
    total: int
    page: int
    size: int
    pages: int

class MarketStatistics(BaseModel):
    """Schema for market statistics"""
    total_cranes: int
    average_price: Decimal
    price_range: dict
    capacity_distribution: dict
    manufacturer_distribution: dict
    location_distribution: dict
    year_distribution: dict
