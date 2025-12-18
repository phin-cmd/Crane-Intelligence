"""
Database models for the Spec Catalog system
Handles crane specifications, scraping metadata, and normalization
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, Index
from sqlalchemy.orm import relationship
from ..core.database import Base
from datetime import datetime

class SpecCatalog(Base):
    """Canonical crane specifications catalog"""
    __tablename__ = "spec_catalog"
    
    spec_id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)  # bigge, liebherr_used, maxim, oem, other
    source_url = Column(Text, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Basic identification
    make = Column(String(100), nullable=False, index=True)
    model = Column(String(200), nullable=False, index=True)
    variant = Column(String(100))  # EU/US, etc.
    year_from = Column(Integer)
    year_to = Column(Integer)
    
    # Technical specifications
    capacity_tons = Column(Float)
    boom_length_ft = Column(Float)
    jib_options_ft = Column(JSON)  # Array of jib lengths
    winches = Column(Integer)
    counterweight_lbs = Column(Float)
    
    # Transport profile
    transport_profile = Column(JSON)  # carrier_only_lbs, boom_on_dolly_lbs, axle_layout, tire_size
    
    # Features and equipment
    features = Column(JSON)  # Array of features like ["aux nose", "rooster sheave", "hyd outriggers"]
    engine = Column(String(200))
    dimensions = Column(JSON)  # length_ft, width_ft, height_ft
    
    # Documentation
    pdf_specs = Column(JSON)  # Array of PDF URLs
    raw = Column(JSON)  # html_hash, pdf_text_hash
    
    # Normalization
    spec_hash = Column(String(40), unique=True, index=True)  # SHA1 hash for deduplication
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_spec_catalog_make_model', 'make', 'model'),
        Index('idx_spec_catalog_capacity', 'capacity_tons'),
        Index('idx_spec_catalog_source_last_seen', 'source', 'last_seen'),
    )

class ScrapingJob(Base):
    """Tracks scraping jobs and their status"""
    __tablename__ = "scraping_jobs"
    
    job_id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)
    job_type = Column(String(50), nullable=False)  # full_scrape, incremental, spec_extraction
    
    # Job status
    status = Column(String(20), nullable=False, default='pending')  # pending, running, completed, failed
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Job metrics
    pages_scraped = Column(Integer, default=0)
    specs_extracted = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    
    # Job configuration
    config = Column(JSON)  # Job-specific configuration
    error_log = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ScrapingCache(Base):
    """Caches scraped content for efficiency"""
    __tablename__ = "scraping_cache"
    
    cache_id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, nullable=False, unique=True, index=True)
    content_hash = Column(String(40), nullable=False, index=True)  # SHA1 of content
    
    # Content
    content_type = Column(String(20), nullable=False)  # html, pdf, json
    content = Column(Text)  # For HTML/JSON
    file_path = Column(String(500))  # For PDFs and large files
    
    # Metadata
    source = Column(String(50), nullable=False, index=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_valid = Column(Boolean, default=True)
    
    # Headers and metadata
    headers = Column(JSON)
    file_size = Column(Integer)
    
    # Indexes
    __table_args__ = (
        Index('idx_scraping_cache_source_scraped', 'source', 'scraped_at'),
        Index('idx_scraping_cache_expires', 'expires_at'),
    )

class SpecCompleteness(Base):
    """Tracks completeness of specifications by make/model"""
    __tablename__ = "spec_completeness"
    
    id = Column(Integer, primary_key=True, index=True)
    make = Column(String(100), nullable=False, index=True)
    model = Column(String(200), nullable=False, index=True)
    
    # Completeness scores (0-100)
    capacity_completeness = Column(Float, default=0)
    boom_completeness = Column(Float, default=0)
    jib_completeness = Column(Float, default=0)
    counterweight_completeness = Column(Float, default=0)
    features_completeness = Column(Float, default=0)
    transport_completeness = Column(Float, default=0)
    
    # Overall completeness
    overall_completeness = Column(Float, default=0)
    
    # Counts
    total_specs = Column(Integer, default=0)
    unique_sources = Column(Integer, default=0)
    
    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_spec_completeness_make_model', 'make', 'model'),
        Index('idx_spec_completeness_overall', 'overall_completeness'),
    )

class DataRefreshLog(Base):
    """Logs data refresh operations"""
    __tablename__ = "data_refresh_log"
    
    log_id = Column(Integer, primary_key=True, index=True)
    refresh_type = Column(String(50), nullable=False)  # full_refresh, incremental, csv_import
    
    # Status
    status = Column(String(20), nullable=False, default='started')  # started, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Metrics
    records_processed = Column(Integer, default=0)
    records_added = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)
    
    # Configuration
    config = Column(JSON)
    error_message = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
