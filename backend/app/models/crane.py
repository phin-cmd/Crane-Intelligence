"""
SQLAlchemy models for Crane data
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
from decimal import Decimal

class Crane(Base):
    """Crane model for database storage"""
    __tablename__ = "cranes"
    
    id = Column(Integer, primary_key=True, index=True)
    manufacturer = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    capacity_tons = Column(Numeric(8, 2), nullable=False, index=True)
    hours = Column(Integer, nullable=False, index=True)
    price = Column(Numeric(12, 2), nullable=False, index=True)
    location = Column(String(100), nullable=True, index=True)
    condition = Column(String(50), nullable=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    analyses = relationship("CraneAnalysis", back_populates="crane")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_manufacturer_model', 'manufacturer', 'model'),
        Index('idx_capacity_year', 'capacity_tons', 'year'),
        Index('idx_price_range', 'price'),
        Index('idx_location_condition', 'location', 'condition'),
    )
    
    def __repr__(self):
        return f"<Crane(id={self.id}, {self.manufacturer} {self.model}, {self.year})>"

class CraneAnalysis(Base):
    """Crane analysis results model"""
    __tablename__ = "crane_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    crane_id = Column(Integer, ForeignKey('cranes.id'), nullable=False, index=True)
    deal_score = Column(Integer, nullable=False)
    estimated_value = Column(Numeric(12, 2), nullable=False)
    confidence_score = Column(Numeric(3, 2), nullable=False)
    comparable_count = Column(Integer, nullable=False)
    market_position = Column(String(100), nullable=False)
    risk_factors = Column(Text, nullable=True)  # JSON string
    recommendations = Column(Text, nullable=True)  # JSON string
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    crane = relationship("Crane", back_populates="analyses")
    
    def __repr__(self):
        return f"<CraneAnalysis(id={self.id}, crane_id={self.crane_id}, score={self.deal_score})>"

class MarketData(Base):
    """Market data and statistics model"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String(50), nullable=False, index=True)  # 'daily', 'weekly', 'monthly'
    data_date = Column(DateTime(timezone=True), nullable=False, index=True)
    total_cranes = Column(Integer, nullable=False)
    average_price = Column(Numeric(12, 2), nullable=False)
    price_range_min = Column(Numeric(12, 2), nullable=False)
    price_range_max = Column(Numeric(12, 2), nullable=False)
    capacity_distribution = Column(Text, nullable=True)  # JSON string
    manufacturer_distribution = Column(Text, nullable=True)  # JSON string
    location_distribution = Column(Text, nullable=True)  # JSON string
    year_distribution = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<MarketData(id={self.id}, type={self.data_type}, date={self.data_date})>"
