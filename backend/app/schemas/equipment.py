from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class EquipmentStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"
    SOLD = "sold"


class MaintenanceType(str, Enum):
    SCHEDULED = "scheduled"
    EMERGENCY = "emergency"
    REPAIR = "repair"
    INSPECTION = "inspection"


class InspectionType(str, Enum):
    ANNUAL = "annual"
    PRE_PURCHASE = "pre-purchase"
    SAFETY = "safety"
    COMPLIANCE = "compliance"


class ValuationType(str, Enum):
    MARKET = "market"
    INSURANCE = "insurance"
    BOOK = "book"
    AUCTION = "auction"


class ValuationMethod(str, Enum):
    COST_APPROACH = "cost_approach"
    MARKET_APPROACH = "market_approach"
    INCOME_APPROACH = "income_approach"


# Base Equipment Schemas
class EquipmentBase(BaseModel):
    manufacturer: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1990, le=2030)
    serial_number: str = Field(..., min_length=1, max_length=100)
    capacity_tons: float = Field(..., gt=0)
    condition_score: int = Field(..., ge=1, le=100)
    location: str = Field(..., min_length=1, max_length=200)
    purchase_date: date
    description: Optional[str] = None
    status: EquipmentStatus = EquipmentStatus.ACTIVE
    estimated_value: Optional[float] = Field(None, ge=0)
    current_value: Optional[float] = Field(None, ge=0)
    depreciation_rate: float = Field(0.15, ge=0, le=1)
    total_operating_hours: float = Field(0.0, ge=0)
    maintenance_interval_hours: float = Field(500.0, gt=0)


class EquipmentCreate(EquipmentBase):
    user_id: Optional[int] = None
    company_id: Optional[int] = None


class EquipmentUpdate(BaseModel):
    manufacturer: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1990, le=2030)
    serial_number: Optional[str] = Field(None, min_length=1, max_length=100)
    capacity_tons: Optional[float] = Field(None, gt=0)
    condition_score: Optional[int] = Field(None, ge=1, le=100)
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    purchase_date: Optional[date] = None
    description: Optional[str] = None
    status: Optional[EquipmentStatus] = None
    estimated_value: Optional[float] = Field(None, ge=0)
    current_value: Optional[float] = Field(None, ge=0)
    depreciation_rate: Optional[float] = Field(None, ge=0, le=1)
    total_operating_hours: Optional[float] = Field(None, ge=0)
    maintenance_interval_hours: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None


class EquipmentResponse(EquipmentBase):
    id: int
    user_id: Optional[int] = None
    company_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_inspection_date: Optional[datetime] = None
    next_inspection_date: Optional[datetime] = None
    last_maintenance_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class EquipmentListResponse(BaseModel):
    equipment: List[EquipmentResponse]
    total: int
    page: int
    size: int
    pages: int


# Maintenance Record Schemas
class MaintenanceRecordBase(BaseModel):
    maintenance_type: MaintenanceType
    description: str = Field(..., min_length=1)
    performed_by: Optional[str] = Field(None, max_length=100)
    cost: Optional[float] = Field(None, ge=0)
    next_due_date: Optional[datetime] = None


class MaintenanceRecordCreate(MaintenanceRecordBase):
    equipment_id: int


class MaintenanceRecordUpdate(BaseModel):
    maintenance_type: Optional[MaintenanceType] = None
    description: Optional[str] = Field(None, min_length=1)
    performed_by: Optional[str] = Field(None, max_length=100)
    cost: Optional[float] = Field(None, ge=0)
    next_due_date: Optional[datetime] = None
    status: Optional[str] = None


class MaintenanceRecordResponse(MaintenanceRecordBase):
    id: int
    equipment_id: int
    performed_at: datetime
    status: str

    class Config:
        from_attributes = True


# Inspection Record Schemas
class InspectionRecordBase(BaseModel):
    inspection_type: InspectionType
    inspector_name: str = Field(..., min_length=1, max_length=100)
    inspection_company: Optional[str] = Field(None, max_length=100)
    overall_score: int = Field(..., ge=1, le=100)
    passed: bool
    notes: Optional[str] = None
    recommendations: Optional[str] = None
    valid_until: Optional[datetime] = None


class InspectionRecordCreate(InspectionRecordBase):
    equipment_id: int


class InspectionRecordUpdate(BaseModel):
    inspection_type: Optional[InspectionType] = None
    inspector_name: Optional[str] = Field(None, min_length=1, max_length=100)
    inspection_company: Optional[str] = Field(None, max_length=100)
    overall_score: Optional[int] = Field(None, ge=1, le=100)
    passed: Optional[bool] = None
    notes: Optional[str] = None
    recommendations: Optional[str] = None
    valid_until: Optional[datetime] = None
    status: Optional[str] = None


class InspectionRecordResponse(InspectionRecordBase):
    id: int
    equipment_id: int
    inspected_at: datetime
    status: str

    class Config:
        from_attributes = True


# Valuation Record Schemas
class ValuationRecordBase(BaseModel):
    valuation_type: ValuationType
    valuation_method: ValuationMethod
    valuer_name: Optional[str] = Field(None, max_length=100)
    valuation_company: Optional[str] = Field(None, max_length=100)
    estimated_value: float = Field(..., gt=0)
    market_value: Optional[float] = Field(None, ge=0)
    replacement_cost: Optional[float] = Field(None, ge=0)
    salvage_value: Optional[float] = Field(None, ge=0)
    market_conditions: Optional[str] = Field(None, max_length=100)
    regional_demand: Optional[float] = Field(None, ge=0, le=100)
    price_trend: Optional[str] = Field(None, max_length=50)
    valid_until: Optional[datetime] = None


class ValuationRecordCreate(ValuationRecordBase):
    equipment_id: int


class ValuationRecordUpdate(BaseModel):
    valuation_type: Optional[ValuationType] = None
    valuation_method: Optional[ValuationMethod] = None
    valuer_name: Optional[str] = Field(None, max_length=100)
    valuation_company: Optional[str] = Field(None, max_length=100)
    estimated_value: Optional[float] = Field(None, gt=0)
    market_value: Optional[float] = Field(None, ge=0)
    replacement_cost: Optional[float] = Field(None, ge=0)
    salvage_value: Optional[float] = Field(None, ge=0)
    market_conditions: Optional[str] = Field(None, max_length=100)
    regional_demand: Optional[float] = Field(None, ge=0, le=100)
    price_trend: Optional[str] = Field(None, max_length=50)
    valid_until: Optional[datetime] = None
    status: Optional[str] = None


class ValuationRecordResponse(ValuationRecordBase):
    id: int
    equipment_id: int
    valued_at: datetime
    status: str

    class Config:
        from_attributes = True


# Company Schemas
class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    size: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=200)
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state_province: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    size: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=200)
    address_line1: Optional[str] = Field(None, max_length=100)
    address_line2: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    state_province: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class CompanyResponse(CompanyBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Equipment Statistics Schemas
class EquipmentStats(BaseModel):
    total_equipment: int
    active_equipment: int
    maintenance_equipment: int
    retired_equipment: int
    total_value: float
    average_condition_score: float
    equipment_by_manufacturer: dict
    equipment_by_status: dict
    equipment_by_year: dict


# Equipment Search and Filter Schemas
class EquipmentSearch(BaseModel):
    query: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    capacity_min: Optional[float] = None
    capacity_max: Optional[float] = None
    condition_min: Optional[int] = None
    condition_max: Optional[int] = None
    status: Optional[EquipmentStatus] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
