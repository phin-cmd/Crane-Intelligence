"""
FMV Report Pydantic Schemas
Request and response models for FMV report API
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class FMVReportType(str, Enum):
    SPOT_CHECK = "spot_check"
    PROFESSIONAL = "professional"
    FLEET_VALUATION = "fleet_valuation"


class FMVReportStatus(str, Enum):
    DRAFT = "draft"  # Form filled, purchase clicked but payment not completed
    SUBMITTED = "submitted"  # Form filled, payment successful
    IN_PROGRESS = "in_progress"  # Admin views report and changes status to in_progress
    COMPLETED = "completed"  # Admin completes the FMV report
    DELIVERED = "delivered"  # Admin uploads PDF and clicks "Upload and send to customer"
    NEED_MORE_INFO = "need_more_info"  # Admin needs more information to complete report
    OVERDUE = "overdue"  # Admin didn't complete within 24 hours (calculated status)


class FleetPricingTier(str, Enum):
    TIER_1_5 = "1-5"
    TIER_6_10 = "6-10"
    TIER_11_25 = "11-25"
    TIER_26_50 = "26-50"


class CraneDetails(BaseModel):
    """Crane details for FMV report - supports both camelCase and snake_case"""
    manufacturer: str
    model: str
    year: int
    capacity: Optional[float] = None
    capacity_tons: Optional[float] = None
    hours: Optional[int] = None
    region: Optional[str] = None
    crane_type: Optional[str] = Field(None, alias='craneType')  # Accept camelCase from frontend
    operating_hours: Optional[int] = Field(None, alias='operatingHours')  # Accept camelCase from frontend
    mileage: Optional[int] = None
    boom_length: Optional[float] = Field(None, alias='boomLength')  # Accept camelCase from frontend
    jib_length: Optional[float] = Field(None, alias='jibLength')  # Accept camelCase from frontend
    max_hook_height: Optional[float] = Field(None, alias='maxHookHeight')  # Accept camelCase from frontend
    max_radius: Optional[float] = Field(None, alias='maxRadius')  # Accept camelCase from frontend
    serial_number: Optional[str] = Field(None, alias='serialNumber')  # Accept camelCase from frontend
    condition: Optional[str] = None
    additional_notes: Optional[str] = None
    additional_specs: Optional[str] = Field(None, alias='additionalSpecs')  # Accept camelCase from frontend
    special_features: Optional[str] = Field(None, alias='specialFeatures')  # Accept camelCase from frontend
    usage_history: Optional[str] = Field(None, alias='usageHistory')  # Accept camelCase from frontend
    is_manual_entry: Optional[bool] = False  # Flag to identify manual entries
    
    class Config:
        # Allow both camelCase and snake_case field names
        allow_population_by_field_name = True
        # Allow extra fields to be stored (for backward compatibility)
        extra = 'allow'


class ServiceRecord(BaseModel):
    """Service record entry"""
    date: str
    service_type: str
    description: str
    cost: Optional[float] = None
    performed_by: Optional[str] = None


class FMVReportCreate(BaseModel):
    """Request to create/submit an FMV report"""
    report_type: FMVReportType
    crane_details: CraneDetails
    service_records: Optional[List[ServiceRecord]] = None  # Structured service records
    service_record_files: Optional[List[str]] = None  # URLs of uploaded service record files
    fleet_pricing_tier: Optional[FleetPricingTier] = None
    unit_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None  # Optional metadata (e.g., user_email, payment_intent_id)
    
    @validator('unit_count')
    def validate_unit_count(cls, v, values):
        # Only validate if fleet_valuation is selected and unit_count is provided
        if values.get('report_type') == FMVReportType.FLEET_VALUATION and v is not None:
            if v < 2 or v > 50:
                raise ValueError('unit_count must be between 2 and 50 for fleet valuation')
        return v
    
    @validator('fleet_pricing_tier')
    def validate_fleet_tier(cls, v, values):
        # Only validate if fleet_valuation is selected and fleet_pricing_tier is provided
        # If not provided, it's OK - the service layer can handle defaults
        if values.get('report_type') == FMVReportType.FLEET_VALUATION and v is not None:
            # Validation passed - fleet_pricing_tier is provided
            pass
        return v


class StatusTransition(BaseModel):
    """Request to transition report status"""
    status: FMVReportStatus
    analyst_notes: Optional[str] = None
    rejection_reason: Optional[str] = None  # Used for need_more_info_reason (backward compatibility)
    need_more_info_reason: Optional[str] = None  # Reason why more info is needed
    assigned_analyst: Optional[str] = None


class FMVReportTimelineItem(BaseModel):
    """Single timeline entry"""
    status: str
    timestamp: datetime
    details: str


class FMVReportTimelineResponse(BaseModel):
    """Full timeline for a report"""
    report_id: int
    timeline: List[FMVReportTimelineItem]


class FMVReportResponse(BaseModel):
    """FMV Report response model"""
    id: int
    user_id: int
    report_type: str
    status: str
    crane_details: Dict[str, Any]
    service_records: Optional[List[Dict[str, Any]]] = None
    service_record_files: Optional[List[str]] = None  # URLs of uploaded service record files
    fleet_pricing_tier: Optional[str] = None
    unit_count: Optional[int] = None
    amount_paid: Optional[float] = None
    payment_intent_id: Optional[str] = None
    payment_status: Optional[str] = None
    created_at: datetime
    submitted_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    overdue_at: Optional[datetime] = None
    in_progress_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    need_more_info_at: Optional[datetime] = None
    turnaround_deadline: Optional[datetime] = None
    pdf_url: Optional[str] = None
    pdf_uploaded_at: Optional[datetime] = None
    analyst_notes: Optional[str] = None
    need_more_info_reason: Optional[str] = None
    assigned_analyst: Optional[str] = None
    # Legacy fields kept for backward compatibility
    # Legacy fields kept for backward compatibility
    paid_at: Optional[datetime] = None  # Deprecated - maps to submitted_at
    rejected_at: Optional[datetime] = None  # Deprecated
    cancelled_at: Optional[datetime] = None  # Deprecated
    rejection_reason: Optional[str] = None  # Deprecated - use need_more_info_reason
    metadata: Optional[Dict[str, Any]] = None
    updated_at: datetime
    
    class Config:
        orm_mode = True


class FMVReportUpdate(BaseModel):
    """Update FMV report fields"""
    analyst_notes: Optional[str] = None
    need_more_info_reason: Optional[str] = None
    rejection_reason: Optional[str] = None  # Backward compatibility - maps to need_more_info_reason
    assigned_analyst: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class FleetPricingRequest(BaseModel):
    """Fleet pricing tier selection"""
    tier: FleetPricingTier
    unit_count: int
    
    @validator('unit_count')
    def validate_units(cls, v, values):
        tier = values.get('tier')
        if tier == FleetPricingTier.TIER_1_5 and (v < 1 or v > 5):
            raise ValueError('Unit count must be 1-5 for tier 1-5')
        elif tier == FleetPricingTier.TIER_6_10 and (v < 6 or v > 10):
            raise ValueError('Unit count must be 6-10 for tier 6-10')
        elif tier == FleetPricingTier.TIER_11_25 and (v < 11 or v > 25):
            raise ValueError('Unit count must be 11-25 for tier 11-25')
        elif tier == FleetPricingTier.TIER_26_50 and (v < 26 or v > 50):
            raise ValueError('Unit count must be 26-50 for tier 26-50')
        return v

