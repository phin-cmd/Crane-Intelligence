from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import math

from ..models.equipment import Equipment, MaintenanceRecord, InspectionRecord, ValuationRecord, Company
from ..schemas.equipment import (
    EquipmentCreate, EquipmentUpdate, EquipmentSearch,
    MaintenanceRecordCreate, MaintenanceRecordUpdate,
    InspectionRecordCreate, InspectionRecordUpdate,
    ValuationRecordCreate, ValuationRecordUpdate,
    CompanyCreate, CompanyUpdate,
    EquipmentStats
)


class EquipmentService:
    def __init__(self, db: Session):
        self.db = db

    # Equipment CRUD Operations
    def create_equipment(self, equipment_data: EquipmentCreate) -> Equipment:
        """Create new equipment record"""
        equipment = Equipment(**equipment_data.dict())
        self.db.add(equipment)
        self.db.commit()
        self.db.refresh(equipment)
        return equipment

    def get_equipment(self, equipment_id: int) -> Optional[Equipment]:
        """Get equipment by ID"""
        return self.db.query(Equipment).filter(Equipment.id == equipment_id).first()

    def get_equipment_by_serial(self, serial_number: str) -> Optional[Equipment]:
        """Get equipment by serial number"""
        return self.db.query(Equipment).filter(Equipment.serial_number == serial_number).first()

    def update_equipment(self, equipment_id: int, equipment_data: EquipmentUpdate) -> Optional[Equipment]:
        """Update equipment record"""
        equipment = self.get_equipment(equipment_id)
        if not equipment:
            return None
        
        update_data = equipment_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(equipment, field, value)
        
        equipment.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(equipment)
        return equipment

    def delete_equipment(self, equipment_id: int) -> bool:
        """Delete equipment record (soft delete)"""
        equipment = self.get_equipment(equipment_id)
        if not equipment:
            return False
        
        equipment.is_active = False
        equipment.status = "retired"
        equipment.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def list_equipment(self, search_params: EquipmentSearch) -> Dict[str, Any]:
        """List equipment with search and pagination"""
        query = self.db.query(Equipment)
        
        # Apply filters
        if search_params.query:
            search_term = f"%{search_params.query}%"
            query = query.filter(
                or_(
                    Equipment.manufacturer.ilike(search_term),
                    Equipment.model.ilike(search_term),
                    Equipment.serial_number.ilike(search_term),
                    Equipment.location.ilike(search_term),
                    Equipment.description.ilike(search_term)
                )
            )
        
        if search_params.manufacturer:
            query = query.filter(Equipment.manufacturer.ilike(f"%{search_params.manufacturer}%"))
        
        if search_params.model:
            query = query.filter(Equipment.model.ilike(f"%{search_params.model}%"))
        
        if search_params.year_min:
            query = query.filter(Equipment.year >= search_params.year_min)
        
        if search_params.year_max:
            query = query.filter(Equipment.year <= search_params.year_max)
        
        if search_params.capacity_min:
            query = query.filter(Equipment.capacity_tons >= search_params.capacity_min)
        
        if search_params.capacity_max:
            query = query.filter(Equipment.capacity_tons <= search_params.capacity_max)
        
        if search_params.condition_min:
            query = query.filter(Equipment.condition_score >= search_params.condition_min)
        
        if search_params.condition_max:
            query = query.filter(Equipment.condition_score <= search_params.condition_max)
        
        if search_params.status:
            query = query.filter(Equipment.status == search_params.status)
        
        if search_params.location:
            query = query.filter(Equipment.location.ilike(f"%{search_params.location}%"))
        
        if search_params.is_active is not None:
            query = query.filter(Equipment.is_active == search_params.is_active)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (search_params.page - 1) * search_params.size
        equipment = query.offset(offset).limit(search_params.size).all()
        
        # Calculate pagination info
        pages = math.ceil(total / search_params.size) if total > 0 else 1
        
        return {
            "equipment": equipment,
            "total": total,
            "page": search_params.page,
            "size": search_params.size,
            "pages": pages
        }

    def get_equipment_stats(self) -> EquipmentStats:
        """Get equipment statistics"""
        total_equipment = self.db.query(Equipment).count()
        active_equipment = self.db.query(Equipment).filter(Equipment.is_active == True).count()
        maintenance_equipment = self.db.query(Equipment).filter(Equipment.status == "maintenance").count()
        retired_equipment = self.db.query(Equipment).filter(Equipment.status == "retired").count()
        
        # Calculate total value
        total_value_result = self.db.query(func.sum(Equipment.current_value)).filter(
            Equipment.current_value.isnot(None)
        ).scalar()
        total_value = total_value_result or 0.0
        
        # Calculate average condition score
        avg_condition_result = self.db.query(func.avg(Equipment.condition_score)).scalar()
        average_condition_score = float(avg_condition_result) if avg_condition_result else 0.0
        
        # Equipment by manufacturer
        manufacturer_stats = self.db.query(
            Equipment.manufacturer,
            func.count(Equipment.id).label('count')
        ).group_by(Equipment.manufacturer).all()
        equipment_by_manufacturer = {stat.manufacturer: stat.count for stat in manufacturer_stats}
        
        # Equipment by status
        status_stats = self.db.query(
            Equipment.status,
            func.count(Equipment.id).label('count')
        ).group_by(Equipment.status).all()
        equipment_by_status = {stat.status: stat.count for stat in status_stats}
        
        # Equipment by year
        year_stats = self.db.query(
            Equipment.year,
            func.count(Equipment.id).label('count')
        ).group_by(Equipment.year).order_by(Equipment.year).all()
        equipment_by_year = {str(stat.year): stat.count for stat in year_stats}
        
        return EquipmentStats(
            total_equipment=total_equipment,
            active_equipment=active_equipment,
            maintenance_equipment=maintenance_equipment,
            retired_equipment=retired_equipment,
            total_value=total_value,
            average_condition_score=average_condition_score,
            equipment_by_manufacturer=equipment_by_manufacturer,
            equipment_by_status=equipment_by_status,
            equipment_by_year=equipment_by_year
        )

    # Maintenance Record Operations
    def create_maintenance_record(self, maintenance_data: MaintenanceRecordCreate) -> MaintenanceRecord:
        """Create maintenance record"""
        maintenance = MaintenanceRecord(**maintenance_data.dict())
        self.db.add(maintenance)
        
        # Update equipment last maintenance date
        equipment = self.get_equipment(maintenance_data.equipment_id)
        if equipment:
            equipment.last_maintenance_date = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(maintenance)
        return maintenance

    def get_maintenance_records(self, equipment_id: int) -> List[MaintenanceRecord]:
        """Get maintenance records for equipment"""
        return self.db.query(MaintenanceRecord).filter(
            MaintenanceRecord.equipment_id == equipment_id
        ).order_by(desc(MaintenanceRecord.performed_at)).all()

    def update_maintenance_record(self, record_id: int, maintenance_data: MaintenanceRecordUpdate) -> Optional[MaintenanceRecord]:
        """Update maintenance record"""
        maintenance = self.db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
        if not maintenance:
            return None
        
        update_data = maintenance_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(maintenance, field, value)
        
        self.db.commit()
        self.db.refresh(maintenance)
        return maintenance

    # Inspection Record Operations
    def create_inspection_record(self, inspection_data: InspectionRecordCreate) -> InspectionRecord:
        """Create inspection record"""
        inspection = InspectionRecord(**inspection_data.dict())
        self.db.add(inspection)
        
        # Update equipment inspection dates and condition score
        equipment = self.get_equipment(inspection_data.equipment_id)
        if equipment:
            equipment.last_inspection_date = datetime.utcnow()
            equipment.condition_score = inspection_data.overall_score
            
            # Set next inspection date (1 year from now)
            equipment.next_inspection_date = datetime.utcnow() + timedelta(days=365)
        
        self.db.commit()
        self.db.refresh(inspection)
        return inspection

    def get_inspection_records(self, equipment_id: int) -> List[InspectionRecord]:
        """Get inspection records for equipment"""
        return self.db.query(InspectionRecord).filter(
            InspectionRecord.equipment_id == equipment_id
        ).order_by(desc(InspectionRecord.inspected_at)).all()

    def update_inspection_record(self, record_id: int, inspection_data: InspectionRecordUpdate) -> Optional[InspectionRecord]:
        """Update inspection record"""
        inspection = self.db.query(InspectionRecord).filter(InspectionRecord.id == record_id).first()
        if not inspection:
            return None
        
        update_data = inspection_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(inspection, field, value)
        
        self.db.commit()
        self.db.refresh(inspection)
        return inspection

    # Valuation Record Operations
    def create_valuation_record(self, valuation_data: ValuationRecordCreate) -> ValuationRecord:
        """Create valuation record"""
        valuation = ValuationRecord(**valuation_data.dict())
        self.db.add(valuation)
        
        # Update equipment valuation data
        equipment = self.get_equipment(valuation_data.equipment_id)
        if equipment:
            equipment.estimated_value = valuation_data.estimated_value
            equipment.current_value = valuation_data.market_value or valuation_data.estimated_value
        
        self.db.commit()
        self.db.refresh(valuation)
        return valuation

    def get_valuation_records(self, equipment_id: int) -> List[ValuationRecord]:
        """Get valuation records for equipment"""
        return self.db.query(ValuationRecord).filter(
            ValuationRecord.equipment_id == equipment_id
        ).order_by(desc(ValuationRecord.valued_at)).all()

    def update_valuation_record(self, record_id: int, valuation_data: ValuationRecordUpdate) -> Optional[ValuationRecord]:
        """Update valuation record"""
        valuation = self.db.query(ValuationRecord).filter(ValuationRecord.id == record_id).first()
        if not valuation:
            return None
        
        update_data = valuation_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(valuation, field, value)
        
        self.db.commit()
        self.db.refresh(valuation)
        return valuation

    # Company Operations
    def create_company(self, company_data: CompanyCreate) -> Company:
        """Create new company"""
        company = Company(**company_data.dict())
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def get_company(self, company_id: int) -> Optional[Company]:
        """Get company by ID"""
        return self.db.query(Company).filter(Company.id == company_id).first()

    def update_company(self, company_id: int, company_data: CompanyUpdate) -> Optional[Company]:
        """Update company"""
        company = self.get_company(company_id)
        if not company:
            return None
        
        update_data = company_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(company, field, value)
        
        company.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(company)
        return company

    def list_companies(self, skip: int = 0, limit: int = 100) -> List[Company]:
        """List companies"""
        return self.db.query(Company).offset(skip).limit(limit).all()

    # Utility Methods
    def get_equipment_by_user(self, user_id: int) -> List[Equipment]:
        """Get equipment owned by user"""
        return self.db.query(Equipment).filter(
            Equipment.user_id == user_id,
            Equipment.is_active == True
        ).all()

    def get_equipment_by_company(self, company_id: int) -> List[Equipment]:
        """Get equipment owned by company"""
        return self.db.query(Equipment).filter(
            Equipment.company_id == company_id,
            Equipment.is_active == True
        ).all()

    def get_upcoming_maintenance(self, days_ahead: int = 30) -> List[Equipment]:
        """Get equipment with upcoming maintenance"""
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
        return self.db.query(Equipment).filter(
            Equipment.next_inspection_date <= cutoff_date,
            Equipment.is_active == True
        ).all()

    def get_overdue_maintenance(self) -> List[Equipment]:
        """Get equipment with overdue maintenance"""
        return self.db.query(Equipment).filter(
            Equipment.next_inspection_date < datetime.utcnow(),
            Equipment.is_active == True
        ).all()
