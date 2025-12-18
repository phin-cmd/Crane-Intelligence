from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CraneEquipment(Base):
    __tablename__ = "crane_equipment"
    
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    manufacturer = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    capacity = Column(Float, nullable=False)
    condition = Column(String, nullable=False)
    location = Column(String, nullable=False)
    purchase_price = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    depreciation_rate = Column(Float, nullable=True)
    maintenance_cost = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Valuation(Base):
    __tablename__ = "valuations"
    
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String, nullable=False)
    valuation_date = Column(DateTime(timezone=True), server_default=func.now())
    market_value = Column(Float, nullable=False)
    replacement_cost = Column(Float, nullable=True)
    depreciation = Column(Float, nullable=True)
    condition_factor = Column(Float, nullable=True)
    market_trends = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
