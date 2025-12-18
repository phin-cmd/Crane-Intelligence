from sqlalchemy import Column, Integer, String, Float, Date, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Equipment(Base):
    """Equipment model for crane and heavy machinery tracking"""
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    manufacturer = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    serial_number = Column(String(100), unique=True, nullable=False, index=True)
    
    # Specifications
    capacity_tons = Column(Float, nullable=False)
    condition_score = Column(Integer, nullable=False)  # 1-100 scale
    
    # Location and Ownership
    location = Column(String(200), nullable=False)
    purchase_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    
    # Status and Tracking
    status = Column(String(50), default="active", index=True)  # active, maintenance, retired, sold
    is_active = Column(Boolean, default=True, index=True)
    
    # User and Company Association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_inspection_date = Column(DateTime(timezone=True), nullable=True)
    next_inspection_date = Column(DateTime(timezone=True), nullable=True)
    
    # Valuation Data
    estimated_value = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    depreciation_rate = Column(Float, default=0.15)  # Annual depreciation rate
    
    # Maintenance Tracking
    total_operating_hours = Column(Float, default=0.0)
    last_maintenance_date = Column(DateTime(timezone=True), nullable=True)
    maintenance_interval_hours = Column(Float, default=500.0)
    
    # Relationships
    # Note: Using backref instead of back_populates to avoid requiring User.equipment relationship
    user = relationship("User", backref="equipment", lazy="select")
    company = relationship("Company", back_populates="equipment")
    maintenance_records = relationship("MaintenanceRecord", back_populates="equipment")
    inspection_records = relationship("InspectionRecord", back_populates="equipment")
    valuation_records = relationship("ValuationRecord", back_populates="equipment")


class MaintenanceRecord(Base):
    """Maintenance records for equipment"""
    __tablename__ = "maintenance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    
    # Maintenance Details
    maintenance_type = Column(String(50), nullable=False)  # scheduled, emergency, repair, inspection
    description = Column(Text, nullable=False)
    performed_by = Column(String(100), nullable=True)
    cost = Column(Float, nullable=True)
    
    # Timing
    performed_at = Column(DateTime(timezone=True), server_default=func.now())
    next_due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(String(50), default="completed")  # completed, pending, cancelled
    
    # Relationships
    equipment = relationship("Equipment", back_populates="maintenance_records")


class InspectionRecord(Base):
    """Inspection records for equipment"""
    __tablename__ = "inspection_records"
    
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    
    # Inspection Details
    inspection_type = Column(String(50), nullable=False)  # annual, pre-purchase, safety, compliance
    inspector_name = Column(String(100), nullable=False)
    inspection_company = Column(String(100), nullable=True)
    
    # Results
    overall_score = Column(Integer, nullable=False)  # 1-100
    passed = Column(Boolean, nullable=False)
    notes = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    
    # Timing
    inspected_at = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(String(50), default="completed")  # completed, pending, failed
    
    # Relationships
    equipment = relationship("Equipment", back_populates="inspection_records")


class ValuationRecord(Base):
    """Valuation records for equipment"""
    __tablename__ = "valuation_records"
    
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    
    # Valuation Details
    valuation_type = Column(String(50), nullable=False)  # market, insurance, book, auction
    valuation_method = Column(String(50), nullable=False)  # cost_approach, market_approach, income_approach
    valuer_name = Column(String(100), nullable=True)
    valuation_company = Column(String(100), nullable=True)
    
    # Values
    estimated_value = Column(Float, nullable=False)
    market_value = Column(Float, nullable=True)
    replacement_cost = Column(Float, nullable=True)
    salvage_value = Column(Float, nullable=True)
    
    # Market Data
    market_conditions = Column(String(100), nullable=True)
    regional_demand = Column(Float, nullable=True)  # 0-100 percentage
    price_trend = Column(String(50), nullable=True)  # rising, stable, falling
    
    # Timing
    valued_at = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(String(50), default="completed")  # completed, pending, expired
    
    # Relationships
    equipment = relationship("Equipment", back_populates="valuation_records")


class Company(Base):
    """Company model for equipment ownership"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Company Information
    name = Column(String(200), nullable=False, unique=True, index=True)
    industry = Column(String(100), nullable=True)
    size = Column(String(50), nullable=True)  # small, medium, large, enterprise
    
    # Contact Information
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(200), nullable=True)
    
    # Address
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state_province = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    equipment = relationship("Equipment", back_populates="company")
    # Note: User-Company relationship removed to avoid circular dependency
    # If needed, add company_id to User model first
