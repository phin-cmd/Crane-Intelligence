"""
Data Migration Service for Crane Intelligence Platform
Handles migration of CSV data to enhanced database models
"""

import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from ..core.database import get_db
# from ..models.enhanced_crane import (
#     CraneListing, MarketTrend, BrokerNetwork, PerformanceMetrics,
#     CraneValuationAnalysis, MarketIntelligence, RentalRates, DataRefreshLog
# )  # Tables don't exist yet
from ..models.spec_catalog import SpecCatalog, ScrapingJob, ScrapingCache, SpecCompleteness
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import re
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class DataMigrationService:
    """Service for migrating CSV data to enhanced database models"""
    
    def __init__(self):
        self.logger = logger
        self.data_path = Path("Requirements")
    
    def migrate_all_data(self, db: Session) -> Dict[str, Any]:
        """Migrate all CSV data to enhanced database models"""
        results = {}
        
        try:
            # 1. Migrate crane listings
            results['crane_listings'] = self.migrate_crane_listings(db)
            
            # 2. Migrate market trends
            results['market_trends'] = self.migrate_market_trends(db)
            
            # 3. Migrate rental rates
            results['rental_rates'] = self.migrate_rental_rates(db)
            
            # 4. Create performance metrics
            results['performance_metrics'] = self.create_performance_metrics(db)
            
            # 5. Log the migration
            self.log_data_refresh(db, 'full_migration', 'completed', {
                'records_processed': sum(r.get('records_processed', 0) for r in results.values()),
                'records_added': sum(r.get('records_added', 0) for r in results.values()),
                'records_updated': sum(r.get('records_updated', 0) for r in results.values()),
            })
            
            self.logger.info("Data migration completed successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"Data migration failed: {e}")
            self.log_data_refresh(db, 'full_migration', 'failed', error_message=str(e))
            raise
    
    def migrate_crane_listings(self, db: Session) -> Dict[str, Any]:
        """Migrate crane listings from CSV to enhanced model"""
        try:
            csv_path = self.data_path / "crane_data_scoring_20250706_173618.csv"
            if not csv_path.exists():
                raise FileNotFoundError(f"Crane listings CSV not found: {csv_path}")
            
            df = pd.read_csv(csv_path)
            records_processed = 0
            records_added = 0
            records_updated = 0
            
            for _, row in df.iterrows():
                try:
                    # Extract capacity from title
                    capacity = self._extract_capacity_from_title(row.get('title', ''))
                    
                    # Determine crane type
                    crane_type = self._determine_crane_type(row.get('title', ''), capacity)
                    
                    # Extract region from location
                    region = self._extract_region_from_location(row.get('location', ''))
                    
                    # Check if listing already exists
                    existing = db.query(CraneListing).filter(
                        CraneListing.title == row.get('title', ''),
                        CraneListing.manufacturer == row.get('manufacturer', ''),
                        CraneListing.year == row.get('year', 0)
                    ).first()
                    
                    listing_data = {
                        'title': row.get('title', ''),
                        'manufacturer': row.get('manufacturer', ''),
                        'year': int(row.get('year', 0)) if pd.notna(row.get('year')) else 0,
                        'price': float(row.get('price', 0)) if pd.notna(row.get('price')) else 0,
                        'location': row.get('location', ''),
                        'hours': int(row.get('hours', 0)) if pd.notna(row.get('hours')) else None,
                        'wear_score': float(row.get('wear_score', 0)) if pd.notna(row.get('wear_score')) else None,
                        'value_score': float(row.get('value_score', 0)) if pd.notna(row.get('value_score')) else None,
                        'source': row.get('source', 'Live Scraper'),
                        'capacity_tons': capacity,
                        'crane_type': crane_type,
                        'region': region,
                        'scraped_at': datetime.utcnow(),
                        'last_updated': datetime.utcnow()
                    }
                    
                    if existing:
                        # Update existing listing
                        for key, value in listing_data.items():
                            if hasattr(existing, key):
                                setattr(existing, key, value)
                        existing.last_updated = datetime.utcnow()
                        records_updated += 1
                    else:
                        # Create new listing
                        new_listing = CraneListing(**listing_data)
                        db.add(new_listing)
                        records_added += 1
                    
                    records_processed += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing listing row: {e}")
                    continue
            
            db.commit()
            self.logger.info(f"Crane listings migration completed: {records_processed} processed, {records_added} added, {records_updated} updated")
            
            return {
                'records_processed': records_processed,
                'records_added': records_added,
                'records_updated': records_updated
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Crane listings migration failed: {e}")
            raise
    
    def migrate_market_trends(self, db: Session) -> Dict[str, Any]:
        """Migrate market trends from CSV to enhanced model"""
        try:
            csv_path = self.data_path / "Valuation_Engine_-_Buying_Trends.csv"
            if not csv_path.exists():
                self.logger.warning(f"Market trends CSV not found: {csv_path}")
                return {'records_processed': 0, 'records_added': 0, 'records_updated': 0}
            
            df = pd.read_csv(csv_path)
            records_processed = 0
            records_added = 0
            
            for _, row in df.iterrows():
                try:
                    # Parse YoY growth percentage
                    yoy_growth = self._parse_percentage(row.get('YoY Growth (%)', '0%'))
                    
                    trend_data = {
                        'segment': row.get('Segment', ''),
                        'yoy_growth_percent': yoy_growth,
                        'key_drivers': row.get('Key Drivers', ''),
                        'buyer_priorities': row.get('Buyer Priorities', ''),
                        'market_size': self._determine_market_size(yoy_growth),
                        'price_trend': self._determine_price_trend(yoy_growth),
                        'demand_outlook': self._determine_demand_outlook(yoy_growth),
                        'trend_date': datetime.utcnow()
                    }
                    
                    # Check if trend already exists
                    existing = db.query(MarketTrend).filter(
                        MarketTrend.segment == trend_data['segment']
                    ).first()
                    
                    if existing:
                        # Update existing trend
                        for key, value in trend_data.items():
                            if hasattr(existing, key):
                                setattr(existing, key, value)
                        existing.updated_at = datetime.utcnow()
                    else:
                        # Create new trend
                        new_trend = MarketTrend(**trend_data)
                        db.add(new_trend)
                        records_added += 1
                    
                    records_processed += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing trend row: {e}")
                    continue
            
            db.commit()
            self.logger.info(f"Market trends migration completed: {records_processed} processed, {records_added} added")
            
            return {
                'records_processed': records_processed,
                'records_added': records_added,
                'records_updated': 0
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Market trends migration failed: {e}")
            raise
    
    def migrate_rental_rates(self, db: Session) -> Dict[str, Any]:
        """Migrate rental rates from CSV to enhanced model"""
        try:
            csv_path = self.data_path / "Crane_Rental_Rates_By_Region.csv"
            if not csv_path.exists():
                self.logger.warning(f"Rental rates CSV not found: {csv_path}")
                return {'records_processed': 0, 'records_added': 0, 'records_updated': 0}
            
            df = pd.read_csv(csv_path)
            records_processed = 0
            records_added = 0
            
            for _, row in df.iterrows():
                try:
                    rate_data = {
                        'crane_type': row.get('Crane Type', ''),
                        'tonnage': float(row.get('Tonnage', 0)) if pd.notna(row.get('Tonnage')) else None,
                        'region': row.get('Region', ''),
                        'monthly_rate_usd': float(row.get('Monthly Rate (USD)', 0)) if pd.notna(row.get('Monthly Rate (USD)')) else 0,
                        'annual_rate_usd': float(row.get('Monthly Rate (USD)', 0)) * 12 if pd.notna(row.get('Monthly Rate (USD)')) else 0,
                        'daily_rate_usd': float(row.get('Monthly Rate (USD)', 0)) / 30 if pd.notna(row.get('Monthly Rate (USD)')) else 0,
                        'rate_date': datetime.utcnow()
                    }
                    
                    # Check if rate already exists
                    existing = db.query(RentalRates).filter(
                        RentalRates.crane_type == rate_data['crane_type'],
                        RentalRates.region == rate_data['region'],
                        RentalRates.tonnage == rate_data['tonnage']
                    ).first()
                    
                    if existing:
                        # Update existing rate
                        for key, value in rate_data.items():
                            if hasattr(existing, key):
                                setattr(existing, key, value)
                        existing.updated_at = datetime.utcnow()
                    else:
                        # Create new rate
                        new_rate = RentalRates(**rate_data)
                        db.add(new_rate)
                        records_added += 1
                    
                    records_processed += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing rental rate row: {e}")
                    continue
            
            db.commit()
            self.logger.info(f"Rental rates migration completed: {records_processed} processed, {records_added} added")
            
            return {
                'records_processed': records_processed,
                'records_added': records_added,
                'records_updated': 0
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Rental rates migration failed: {e}")
            raise
    
    def create_performance_metrics(self, db: Session) -> Dict[str, Any]:
        """Create performance metrics based on enhanced valuation algorithm"""
        try:
            # Performance data from enhanced valuation algorithm
            performance_data = [
                {
                    'manufacturer': 'Grove',
                    'model': 'GMK4100L',
                    'model_key': 'grove_gmk4100l',
                    'max_capacity_tons': 100,
                    'working_radius_40ft': 50,
                    'working_radius_80ft': 18,
                    'mobility_score': 0.9,
                    'versatility_score': 0.8,
                    'boom_utilization': 0.85
                },
                {
                    'manufacturer': 'Liebherr',
                    'model': 'LTM1070-4.2',
                    'model_key': 'liebherr_ltm1070_4_2',
                    'max_capacity_tons': 70,
                    'working_radius_40ft': 35,
                    'working_radius_80ft': 12,
                    'mobility_score': 0.85,
                    'versatility_score': 0.7,
                    'boom_utilization': 0.75
                },
                {
                    'manufacturer': 'Tadano',
                    'model': 'AC4-080-1',
                    'model_key': 'tadano_ac4_080_1',
                    'max_capacity_tons': 80,
                    'working_radius_40ft': 40,
                    'working_radius_80ft': 15,
                    'mobility_score': 0.8,
                    'versatility_score': 0.75,
                    'boom_utilization': 0.8
                }
            ]
            
            records_added = 0
            
            for data in performance_data:
                # Check if metrics already exist
                existing = db.query(PerformanceMetrics).filter(
                    PerformanceMetrics.model_key == data['model_key']
                ).first()
                
                if not existing:
                    new_metrics = PerformanceMetrics(**data)
                    db.add(new_metrics)
                    records_added += 1
            
            db.commit()
            self.logger.info(f"Performance metrics creation completed: {records_added} added")
            
            return {
                'records_processed': len(performance_data),
                'records_added': records_added,
                'records_updated': 0
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Performance metrics creation failed: {e}")
            raise
    
    def _extract_capacity_from_title(self, title: str) -> Optional[float]:
        """Extract capacity from crane title"""
        if not title:
            return None
        
        # Try various capacity patterns
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:t|ton|tons?)',  # 350t, 350 ton, 350 tons
            r'(\d{3,4})',  # 3-4 digit numbers (likely capacity)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                try:
                    capacity = float(match.group(1))
                    # Sanity check - capacity should be reasonable
                    if 10 <= capacity <= 2000:
                        return capacity
                except ValueError:
                    continue
        
        return None
    
    def _determine_crane_type(self, title: str, capacity: Optional[float]) -> Optional[str]:
        """Determine crane type from title and capacity"""
        if not title:
            return None
        
        title_lower = title.lower()
        
        # All-terrain indicators
        if any(indicator in title_lower for indicator in ['ltm', 'at', 'all-terrain', 'gmk']):
            return 'all_terrain'
        
        # Crawler indicators
        if any(indicator in title_lower for indicator in ['cc', 'crawler', 'lr', 'mlc']):
            return 'crawler'
        
        # Tower indicators
        if any(indicator in title_lower for indicator in ['tower', 'tt', 'ct']):
            return 'tower'
        
        # Rough terrain indicators
        if any(indicator in title_lower for indicator in ['rt', 'rough-terrain']):
            return 'rough_terrain'
        
        # Default based on capacity
        if capacity:
            if capacity >= 200:
                return 'crawler'
            elif capacity >= 100:
                return 'all_terrain'
            else:
                return 'rough_terrain'
        
        return None
    
    def _extract_region_from_location(self, location: str) -> Optional[str]:
        """Extract region from location string"""
        if not location:
            return None
        
        location_lower = location.lower()
        
        # Map states/areas to regions
        region_mapping = {
            'northeast': ['ny', 'nj', 'pa', 'ct', 'ma', 'ri', 'vt', 'nh', 'me'],
            'southeast': ['fl', 'ga', 'sc', 'nc', 'va', 'wv', 'ky', 'tn', 'al', 'ms'],
            'gulf_coast': ['tx', 'la', 'ok', 'ar', 'gulf'],
            'west_coast': ['ca', 'or', 'wa', 'nv', 'az'],
            'midwest': ['il', 'in', 'oh', 'mi', 'wi', 'mn', 'ia', 'mo', 'nd', 'sd', 'ne', 'ks']
        }
        
        for region, states in region_mapping.items():
            if any(state in location_lower for state in states):
                return region
        
        return None
    
    def _parse_percentage(self, percentage_str: str) -> float:
        """Parse percentage string to float"""
        if not percentage_str:
            return 0.0
        
        # Remove % and convert to float
        try:
            return float(str(percentage_str).replace('%', ''))
        except ValueError:
            return 0.0
    
    def _determine_market_size(self, yoy_growth: float) -> str:
        """Determine market size based on YoY growth"""
        if yoy_growth >= 20:
            return 'large'
        elif yoy_growth >= 10:
            return 'medium'
        else:
            return 'small'
    
    def _determine_price_trend(self, yoy_growth: float) -> str:
        """Determine price trend based on YoY growth"""
        if yoy_growth >= 15:
            return 'increasing'
        elif yoy_growth >= 5:
            return 'stable'
        else:
            return 'decreasing'
    
    def _determine_demand_outlook(self, yoy_growth: float) -> str:
        """Determine demand outlook based on YoY growth"""
        if yoy_growth >= 15:
            return 'high'
        elif yoy_growth >= 5:
            return 'moderate'
        else:
            return 'low'
    
    def log_data_refresh(self, db: Session, refresh_type: str, status: str, 
                        metrics: Dict[str, Any] = None, error_message: str = None) -> Dict[str, Any]:
        """Log data refresh operation"""
        try:
            # Create a simple log entry since DataRefreshLog table doesn't exist yet
            log_entry = {
                'refresh_type': refresh_type,
                'data_source': 'csv_migration',
                'status': status,
                'config': {'migration_service': 'DataMigrationService'},
                'error_message': error_message,
                'created_at': datetime.utcnow()
            }
            
            if status == 'completed':
                log_entry['completed_at'] = datetime.utcnow()
            
            if metrics:
                log_entry['records_processed'] = metrics.get('records_processed', 0)
                log_entry['records_added'] = metrics.get('records_added', 0)
                log_entry['records_updated'] = metrics.get('records_updated', 0)
            
            # For now, just return the log entry as a dictionary
            # In the future, this could be saved to a database table
            return log_entry
            
        except Exception as e:
            self.logger.error(f"Error logging data refresh: {e}")
            raise

# Global service instance
data_migration_service = DataMigrationService()
