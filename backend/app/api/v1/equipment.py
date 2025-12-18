from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ...core.database import get_db
from ...services.equipment_service import EquipmentService
from ...schemas.equipment import (
    EquipmentCreate, EquipmentUpdate, EquipmentResponse, EquipmentListResponse,
    MaintenanceRecordCreate, MaintenanceRecordUpdate, MaintenanceRecordResponse,
    InspectionRecordCreate, InspectionRecordUpdate, InspectionRecordResponse,
    ValuationRecordCreate, ValuationRecordUpdate, ValuationRecordResponse,
    CompanyCreate, CompanyUpdate, CompanyResponse,
    EquipmentSearch, EquipmentStats
)
from ...core.auth import get_current_user
from ...models.user import User

router = APIRouter()


# Equipment CRUD Endpoints
@router.post("/", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_equipment(
    equipment_data: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new equipment"""
    service = EquipmentService(db)
    
    # Check if serial number already exists
    existing_equipment = service.get_equipment_by_serial(equipment_data.serial_number)
    if existing_equipment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Equipment with this serial number already exists"
        )
    
    # Set user_id if not provided
    if not equipment_data.user_id:
        equipment_data.user_id = current_user.id
    
    equipment = service.create_equipment(equipment_data)
    return equipment


@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get equipment by ID"""
    service = EquipmentService(db)
    equipment = service.get_equipment(equipment_id)
    
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    return equipment


@router.put("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: int,
    equipment_data: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update equipment"""
    service = EquipmentService(db)
    equipment = service.update_equipment(equipment_id, equipment_data)
    
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    return equipment


@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete equipment (soft delete)"""
    service = EquipmentService(db)
    success = service.delete_equipment(equipment_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )


@router.get("/", response_model=EquipmentListResponse)
async def list_equipment(
    query: Optional[str] = Query(None, description="Search query"),
    manufacturer: Optional[str] = Query(None, description="Filter by manufacturer"),
    model: Optional[str] = Query(None, description="Filter by model"),
    year_min: Optional[int] = Query(None, description="Minimum year"),
    year_max: Optional[int] = Query(None, description="Maximum year"),
    capacity_min: Optional[float] = Query(None, description="Minimum capacity"),
    capacity_max: Optional[float] = Query(None, description="Maximum capacity"),
    condition_min: Optional[int] = Query(None, description="Minimum condition score"),
    condition_max: Optional[int] = Query(None, description="Maximum condition score"),
    status: Optional[str] = Query(None, description="Filter by status"),
    location: Optional[str] = Query(None, description="Filter by location"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List equipment with search and pagination"""
    service = EquipmentService(db)
    
    search_params = EquipmentSearch(
        query=query,
        manufacturer=manufacturer,
        model=model,
        year_min=year_min,
        year_max=year_max,
        capacity_min=capacity_min,
        capacity_max=capacity_max,
        condition_min=condition_min,
        condition_max=condition_max,
        status=status,
        location=location,
        is_active=is_active,
        page=page,
        size=size
    )
    
    result = service.list_equipment(search_params)
    return result


@router.get("/stats/overview", response_model=EquipmentStats)
async def get_equipment_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get equipment statistics"""
    service = EquipmentService(db)
    return service.get_equipment_stats()


# Maintenance Record Endpoints
@router.post("/{equipment_id}/maintenance", response_model=MaintenanceRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance_record(
    equipment_id: int,
    maintenance_data: MaintenanceRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create maintenance record for equipment"""
    service = EquipmentService(db)
    
    # Verify equipment exists
    equipment = service.get_equipment(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    maintenance_data.equipment_id = equipment_id
    maintenance = service.create_maintenance_record(maintenance_data)
    return maintenance


@router.get("/{equipment_id}/maintenance", response_model=List[MaintenanceRecordResponse])
async def get_maintenance_records(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get maintenance records for equipment"""
    service = EquipmentService(db)
    
    # Verify equipment exists
    equipment = service.get_equipment(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    records = service.get_maintenance_records(equipment_id)
    return records


@router.put("/maintenance/{record_id}", response_model=MaintenanceRecordResponse)
async def update_maintenance_record(
    record_id: int,
    maintenance_data: MaintenanceRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update maintenance record"""
    service = EquipmentService(db)
    maintenance = service.update_maintenance_record(record_id, maintenance_data)
    
    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found"
        )
    
    return maintenance


# Inspection Record Endpoints
@router.post("/{equipment_id}/inspections", response_model=InspectionRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_inspection_record(
    equipment_id: int,
    inspection_data: InspectionRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create inspection record for equipment"""
    service = EquipmentService(db)
    
    # Verify equipment exists
    equipment = service.get_equipment(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    inspection_data.equipment_id = equipment_id
    inspection = service.create_inspection_record(inspection_data)
    return inspection


@router.get("/{equipment_id}/inspections", response_model=List[InspectionRecordResponse])
async def get_inspection_records(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get inspection records for equipment"""
    service = EquipmentService(db)
    
    # Verify equipment exists
    equipment = service.get_equipment(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    records = service.get_inspection_records(equipment_id)
    return records


@router.put("/inspections/{record_id}", response_model=InspectionRecordResponse)
async def update_inspection_record(
    record_id: int,
    inspection_data: InspectionRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update inspection record"""
    service = EquipmentService(db)
    inspection = service.update_inspection_record(record_id, inspection_data)
    
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection record not found"
        )
    
    return inspection


# Valuation Record Endpoints
@router.post("/{equipment_id}/valuations", response_model=ValuationRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_valuation_record(
    equipment_id: int,
    valuation_data: ValuationRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create valuation record for equipment"""
    service = EquipmentService(db)
    
    # Verify equipment exists
    equipment = service.get_equipment(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    valuation_data.equipment_id = equipment_id
    valuation = service.create_valuation_record(valuation_data)
    return valuation


@router.get("/{equipment_id}/valuations", response_model=List[ValuationRecordResponse])
async def get_valuation_records(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get valuation records for equipment"""
    service = EquipmentService(db)
    
    # Verify equipment exists
    equipment = service.get_equipment(equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found"
        )
    
    records = service.get_valuation_records(equipment_id)
    return records


@router.put("/valuations/{record_id}", response_model=ValuationRecordResponse)
async def update_valuation_record(
    record_id: int,
    valuation_data: ValuationRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update valuation record"""
    service = EquipmentService(db)
    valuation = service.update_valuation_record(record_id, valuation_data)
    
    if not valuation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Valuation record not found"
        )
    
    return valuation


# Company Endpoints
@router.post("/companies", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new company"""
    service = EquipmentService(db)
    company = service.create_company(company_data)
    return company


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get company by ID"""
    service = EquipmentService(db)
    company = service.get_company(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company


@router.put("/companies/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update company"""
    service = EquipmentService(db)
    company = service.update_company(company_id, company_data)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company


@router.get("/companies", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List companies"""
    service = EquipmentService(db)
    companies = service.list_companies(skip=skip, limit=limit)
    return companies


# Utility Endpoints
@router.get("/user/{user_id}/equipment", response_model=List[EquipmentResponse])
async def get_user_equipment(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get equipment owned by user"""
    service = EquipmentService(db)
    equipment = service.get_equipment_by_user(user_id)
    return equipment


@router.get("/company/{company_id}/equipment", response_model=List[EquipmentResponse])
async def get_company_equipment(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get equipment owned by company"""
    service = EquipmentService(db)
    equipment = service.get_equipment_by_company(company_id)
    return equipment


@router.get("/maintenance/upcoming", response_model=List[EquipmentResponse])
async def get_upcoming_maintenance(
    days_ahead: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get equipment with upcoming maintenance"""
    service = EquipmentService(db)
    equipment = service.get_upcoming_maintenance(days_ahead)
    return equipment


@router.get("/maintenance/overdue", response_model=List[EquipmentResponse])
async def get_overdue_maintenance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get equipment with overdue maintenance"""
    service = EquipmentService(db)
    equipment = service.get_overdue_maintenance()
    return equipment


@router.get("/live")
async def get_live_equipment_data(
    db: Session = Depends(get_db)
):
    """Get live equipment data for real-time dashboard (public endpoint, no auth required)"""
    # Return empty data structure to prevent frontend errors
    # This endpoint can be enhanced later to return actual equipment data
    return {
        "success": True,
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "total_equipment": 0,
            "active_equipment": 0,
            "equipment": []
        }
    }
