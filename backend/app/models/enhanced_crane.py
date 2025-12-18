"""
Enhanced Crane Models based on actual requirements data
Handles comprehensive crane data, market intelligence, and broker networks
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, Index, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from ..core.database import Base
from datetime import datetime

class CraneListing(Base):
    """Enhanced crane listing model based on actual CSV data structure"""
    __tablename__ = "crane_listings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Core listing data (from CSV)
    title = Column(String(500), nullable=False, index=True)
    manufacturer = Column(String(100), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    price = Column(Numeric(12, 2), nullable=False, index=True)
    location = Column(String(200), nullable=True, index=True)
    hours = Column(Integer, nullable=True, index=True)
    wear_score = Column(Float, nullable=True)
    value_score = Column(Float, nullable=True)
    source = Column(String(100), nullable=False, index=True)  # Live Scraper, etc.
    
    # Extracted/calculated fields
    capacity_tons = Column(Float, nullable=True, index=True)
    crane_type = Column(String(50), nullable=True, index=True)  # all_terrain, crawler, etc.
    region = Column(String(100), nullable=True, index=True)
    
    # Market intelligence
    market_position = Column(String(50), nullable=True)  # premium, standard, value
    deal_score = Column(Integer, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Metadata
    scraped_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    analyses = relationship("CraneValuationAnalysis", back_populates="listing")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_crane_listings_manufacturer_model', 'manufacturer', 'year'),
        Index('idx_crane_listings_capacity_price', 'capacity_tons', 'price'),
        Index('idx_crane_listings_source_scraped', 'source', 'scraped_at'),
        Index('idx_crane_listings_location_region', 'location', 'region'),
    )

class MarketTrend(Base):
    """Market trends data from buying trends CSV"""
    __tablename__ = "market_trends"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Trend data (from CSV)
    segment = Column(String(200), nullable=False, index=True)  # 300t+ Crawler Cranes, etc.
    yoy_growth_percent = Column(Float, nullable=False)
    key_drivers = Column(Text, nullable=True)  # Infrastructure, offshore wind, LNG projects
    buyer_priorities = Column(Text, nullable=True)  # Early ordering due to 9–12 month lead times
    
    # Calculated fields
    market_size = Column(String(50), nullable=True)  # small, medium, large
    price_trend = Column(String(50), nullable=True)  # increasing, stable, decreasing
    demand_outlook = Column(String(50), nullable=True)  # high, moderate, low
    
    # Metadata
    trend_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_market_trends_segment_date', 'segment', 'trend_date'),
        Index('idx_market_trends_growth', 'yoy_growth_percent'),
    )

class BrokerNetwork(Base):
    """Broker network data (LLoma, CPP, etc.)"""
    __tablename__ = "broker_networks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Broker identification
    broker_name = Column(String(200), nullable=False, index=True)
    broker_type = Column(String(50), nullable=False, index=True)  # LLoma, CPP, etc.
    contact_info = Column(JSON, nullable=True)
    
    # Listing data
    manufacturer = Column(String(100), nullable=False, index=True)
    model = Column(String(200), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    capacity_tons = Column(Float, nullable=True, index=True)
    price = Column(Numeric(12, 2), nullable=False, index=True)
    location = Column(String(200), nullable=True, index=True)
    key_features = Column(Text, nullable=True)
    
    # Broker metrics
    avg_price = Column(Numeric(12, 2), nullable=True)
    price_range_min = Column(Numeric(12, 2), nullable=True)
    price_range_max = Column(Numeric(12, 2), nullable=True)
    capacity_range_min = Column(Float, nullable=True)
    capacity_range_max = Column(Float, nullable=True)
    
    # Metadata
    scraped_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_broker_networks_broker_type', 'broker_type', 'broker_name'),
        Index('idx_broker_networks_manufacturer_model', 'manufacturer', 'model'),
        Index('idx_broker_networks_capacity_price', 'capacity_tons', 'price'),
    )

class PerformanceMetrics(Base):
    """Performance comparison metrics for crane models"""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Model identification
    manufacturer = Column(String(100), nullable=False, index=True)
    model = Column(String(200), nullable=False, index=True)
    model_key = Column(String(200), nullable=False, unique=True, index=True)  # grove_gmk4100l
    
    # Performance specifications
    max_capacity_tons = Column(Float, nullable=False)
    working_radius_40ft = Column(Float, nullable=True)
    working_radius_80ft = Column(Float, nullable=True)
    
    # Performance scores (0-1)
    mobility_score = Column(Float, nullable=True)
    versatility_score = Column(Float, nullable=True)
    boom_utilization = Column(Float, nullable=True)
    
    # Additional metrics
    fuel_efficiency = Column(Float, nullable=True)
    maintenance_cost = Column(Float, nullable=True)
    reliability_score = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_performance_metrics_manufacturer_model', 'manufacturer', 'model'),
        Index('idx_performance_metrics_capacity', 'max_capacity_tons'),
    )

class CraneValuationAnalysis(Base):
    """Enhanced crane valuation analysis results"""
    __tablename__ = "crane_valuation_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey('crane_listings.id'), nullable=False, index=True)
    
    # Valuation results
    estimated_value = Column(Numeric(12, 2), nullable=False)
    confidence_score = Column(Float, nullable=False)
    deal_score = Column(Integer, nullable=False)
    wear_score = Column(Float, nullable=True)
    
    # Valuation ranges
    wholesale_value = Column(Numeric(12, 2), nullable=True)
    retail_value = Column(Numeric(12, 2), nullable=True)
    insurance_replacement_value = Column(Numeric(12, 2), nullable=True)
    orderly_liquidation_value = Column(Numeric(12, 2), nullable=True)
    forced_liquidation_value = Column(Numeric(12, 2), nullable=True)
    
    # Market analysis
    market_trend = Column(String(50), nullable=True)
    demand_outlook = Column(String(50), nullable=True)
    price_direction = Column(String(50), nullable=True)
    key_factors = Column(JSON, nullable=True)
    
    # Financing scenarios
    financing_scenarios = Column(JSON, nullable=True)  # Regional ROI data
    
    # Comparables
    comparable_count = Column(Integer, nullable=False, default=0)
    comparable_data = Column(JSON, nullable=True)
    
    # Analysis metadata
    analysis_engine_version = Column(String(50), nullable=True)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    listing = relationship("CraneListing", back_populates="analyses")
    
    # Indexes
    __table_args__ = (
        Index('idx_crane_valuation_analyses_listing_date', 'listing_id', 'analysis_date'),
        Index('idx_crane_valuation_analyses_deal_score', 'deal_score'),
        Index('idx_crane_valuation_analyses_confidence', 'confidence_score'),
    )

class MarketIntelligence(Base):
    """Market intelligence and sales data"""
    __tablename__ = "market_intelligence"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Intelligence data
    data_type = Column(String(50), nullable=False, index=True)  # sales_data, price_trends, volume_trends
    segment = Column(String(200), nullable=True, index=True)
    region = Column(String(100), nullable=True, index=True)
    
    # Metrics
    total_transactions = Column(Integer, nullable=True)
    avg_transaction_value = Column(Numeric(12, 2), nullable=True)
    price_trend_percent = Column(Float, nullable=True)
    volume_trend_percent = Column(Float, nullable=True)
    
    # Data
    intelligence_data = Column(JSON, nullable=True)
    
    # Metadata
    intelligence_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_market_intelligence_type_date', 'data_type', 'intelligence_date'),
        Index('idx_market_intelligence_segment_region', 'segment', 'region'),
    )

class RentalRates(Base):
    """Crane rental rates by region and type"""
    __tablename__ = "rental_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Rate data (from CSV)
    crane_type = Column(String(100), nullable=False, index=True)  # All Terrain (AT), Crawler Crane, etc.
    tonnage = Column(Float, nullable=True, index=True)
    region = Column(String(100), nullable=False, index=True)  # Northeast, Southeast, etc.
    monthly_rate_usd = Column(Numeric(10, 2), nullable=False, index=True)
    
    # Calculated fields
    annual_rate_usd = Column(Numeric(12, 2), nullable=True)
    daily_rate_usd = Column(Numeric(8, 2), nullable=True)
    
    # Metadata
    rate_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_rental_rates_type_region', 'crane_type', 'region'),
        Index('idx_rental_rates_tonnage', 'tonnage'),
        Index('idx_rental_rates_monthly_rate', 'monthly_rate_usd'),
    )

class DataRefreshLog(Base):
    """Logs data refresh operations for all data sources"""
    __tablename__ = "data_refresh_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Refresh metadata
    refresh_type = Column(String(50), nullable=False, index=True)  # full_refresh, incremental, csv_import
    data_source = Column(String(100), nullable=False, index=True)  # crane_listings, market_trends, etc.
    
    # Status
    status = Column(String(20), nullable=False, default='started', index=True)  # started, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Metrics
    records_processed = Column(Integer, default=0)
    records_added = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Configuration and errors
    config = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_data_refresh_logs_source_status', 'data_source', 'status'),
        Index('idx_data_refresh_logs_type_date', 'refresh_type', 'started_at'),
    )
