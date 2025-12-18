"""
Data Refresh Service
Orchestrates data normalization and scraping for continuous data refresh
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import sqlite3
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .data_normalization import DataNormalizationService
from .scraping_service import ScrapingService
# from ..models.enhanced_crane import CraneListing  # Table doesn't exist yet
from ..core.database import get_db

logger = logging.getLogger(__name__)

class DataRefreshService:
    """
    Service for refreshing crane data through normalization and scraping
    Handles both batch processing and incremental updates
    """
    
    def __init__(self, data_path: Path = Path("Requirements"), output_path: Path = Path("data/processed")):
        self.data_path = data_path
        self.output_path = output_path
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize services
        self.normalization_service = DataNormalizationService(data_path)
        self.scraping_service = ScrapingService()
        
        # Database connection
        # Use PostgreSQL from environment, fallback to SQLite for development
        database_url = os.getenv("DATABASE_URL", None)
        if database_url:
            self.engine = create_engine(database_url, pool_pre_ping=True)
        else:
            self.engine = create_engine("sqlite:///./crane_intelligence.db")
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    async def full_data_refresh(self) -> Dict[str, Any]:
        """
        Perform a full data refresh including normalization and scraping
        """
        try:
            logger.info("Starting full data refresh...")
            start_time = datetime.utcnow()
            
            results = {
                'refresh_type': 'full',
                'start_time': start_time.isoformat(),
                'steps_completed': [],
                'total_records': 0,
                'errors': []
            }
            
            # Step 1: Normalize existing CSV data
            logger.info("Step 1: Normalizing existing CSV data...")
            try:
                normalization_result = self.normalization_service.normalize_all_data()
                results['steps_completed'].append({
                    'step': 'normalization',
                    'status': 'completed',
                    'records_processed': normalization_result.get('total_records', 0),
                    'sources': normalization_result.get('sources_processed', [])
                })
                results['total_records'] += normalization_result.get('total_records', 0)
            except Exception as e:
                error_msg = f"Error in normalization: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                results['steps_completed'].append({
                    'step': 'normalization',
                    'status': 'failed',
                    'error': error_msg
                })
            
            # Step 2: Scrape fresh data from marketplaces
            logger.info("Step 2: Scraping fresh data from marketplaces...")
            try:
                scraping_result = await self.scraping_service.scrape_all_marketplaces()
                results['steps_completed'].append({
                    'step': 'scraping',
                    'status': 'completed',
                    'listings_found': scraping_result.get('total_listings', 0),
                    'marketplaces': scraping_result.get('marketplaces_scraped', [])
                })
                results['total_records'] += scraping_result.get('total_listings', 0)
            except Exception as e:
                error_msg = f"Error in scraping: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                results['steps_completed'].append({
                    'step': 'scraping',
                    'status': 'failed',
                    'error': error_msg
                })
            
            # Step 3: Merge and deduplicate data
            logger.info("Step 3: Merging and deduplicating data...")
            try:
                merge_result = await self._merge_and_deduplicate_data()
                results['steps_completed'].append({
                    'step': 'merge_deduplicate',
                    'status': 'completed',
                    'records_merged': merge_result.get('records_merged', 0),
                    'duplicates_removed': merge_result.get('duplicates_removed', 0)
                })
            except Exception as e:
                error_msg = f"Error in merge/deduplication: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                results['steps_completed'].append({
                    'step': 'merge_deduplicate',
                    'status': 'failed',
                    'error': error_msg
                })
            
            # Step 4: Update database
            logger.info("Step 4: Updating database...")
            try:
                db_result = await self._update_database()
                results['steps_completed'].append({
                    'step': 'database_update',
                    'status': 'completed',
                    'records_inserted': db_result.get('records_inserted', 0),
                    'records_updated': db_result.get('records_updated', 0)
                })
            except Exception as e:
                error_msg = f"Error updating database: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                results['steps_completed'].append({
                    'step': 'database_update',
                    'status': 'failed',
                    'error': error_msg
                })
            
            # Step 5: Generate summary report
            logger.info("Step 5: Generating summary report...")
            try:
                report_result = self._generate_summary_report(results)
                results['steps_completed'].append({
                    'step': 'summary_report',
                    'status': 'completed',
                    'report_path': str(report_result.get('report_path', ''))
                })
            except Exception as e:
                error_msg = f"Error generating summary report: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                results['steps_completed'].append({
                    'step': 'summary_report',
                    'status': 'failed',
                    'error': error_msg
                })
            
            end_time = datetime.utcnow()
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = (end_time - start_time).total_seconds()
            
            logger.info(f"Full data refresh completed in {results['duration_seconds']:.2f} seconds")
            return results
            
        except Exception as e:
            logger.error(f"Error in full data refresh: {e}")
            raise
    
    async def incremental_refresh(self) -> Dict[str, Any]:
        """
        Perform an incremental data refresh (scraping only)
        """
        try:
            logger.info("Starting incremental data refresh...")
            start_time = datetime.utcnow()
            
            results = {
                'refresh_type': 'incremental',
                'start_time': start_time.isoformat(),
                'steps_completed': [],
                'total_records': 0,
                'errors': []
            }
            
            # Step 1: Scrape fresh data
            logger.info("Step 1: Scraping fresh data...")
            try:
                scraping_result = await self.scraping_service.scrape_all_marketplaces()
                results['steps_completed'].append({
                    'step': 'scraping',
                    'status': 'completed',
                    'listings_found': scraping_result.get('total_listings', 0),
                    'marketplaces': scraping_result.get('marketplaces_scraped', [])
                })
                results['total_records'] = scraping_result.get('total_listings', 0)
            except Exception as e:
                error_msg = f"Error in scraping: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                results['steps_completed'].append({
                    'step': 'scraping',
                    'status': 'failed',
                    'error': error_msg
                })
            
            # Step 2: Update database with new data
            logger.info("Step 2: Updating database...")
            try:
                db_result = await self._update_database_incremental()
                results['steps_completed'].append({
                    'step': 'database_update',
                    'status': 'completed',
                    'records_inserted': db_result.get('records_inserted', 0),
                    'records_updated': db_result.get('records_updated', 0)
                })
            except Exception as e:
                error_msg = f"Error updating database: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                results['steps_completed'].append({
                    'step': 'database_update',
                    'status': 'failed',
                    'error': error_msg
                })
            
            end_time = datetime.utcnow()
            results['end_time'] = end_time.isoformat()
            results['duration_seconds'] = (end_time - start_time).total_seconds()
            
            logger.info(f"Incremental data refresh completed in {results['duration_seconds']:.2f} seconds")
            return results
            
        except Exception as e:
            logger.error(f"Error in incremental data refresh: {e}")
            raise
    
    async def _merge_and_deduplicate_data(self) -> Dict[str, Any]:
        """Merge normalized and scraped data, removing duplicates"""
        try:
            # Get normalized data
            normalized_data = self.normalization_service.get_normalized_data()
            
            # Get scraped data
            scraped_data = []
            for marketplace_result in self.scraping_service.marketplaces:
                # This would be populated from scraping results
                pass
            
            # Merge data
            all_data = normalized_data + scraped_data
            
            # Deduplicate based on record hash
            seen_hashes = set()
            unique_data = []
            duplicates_removed = 0
            
            for record in all_data:
                record_hash = record.get('record_hash', '')
                if record_hash and record_hash not in seen_hashes:
                    seen_hashes.add(record_hash)
                    unique_data.append(record)
                else:
                    duplicates_removed += 1
            
            # Save merged data
            merged_file = self.output_path / f"merged_data_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jsonl"
            with open(merged_file, 'w', encoding='utf-8') as f:
                for record in unique_data:
                    f.write(json.dumps(record) + '\n')
            
            return {
                'records_merged': len(all_data),
                'duplicates_removed': duplicates_removed,
                'unique_records': len(unique_data),
                'merged_file': str(merged_file)
            }
            
        except Exception as e:
            logger.error(f"Error merging data: {e}")
            raise
    
    async def _update_database(self) -> Dict[str, Any]:
        """Update database with processed data"""
        try:
            db = self.SessionLocal()
            records_inserted = 0
            records_updated = 0
            
            try:
                # Get merged data
                merged_file = max(self.output_path.glob("merged_data_*.jsonl"), key=lambda x: x.stat().st_mtime)
                
                with open(merged_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            record = json.loads(line.strip())
                            
                            # Check if record exists
                            existing = db.query(CraneListing).filter(
                                CraneListing.title == record.get('title', ''),
                                CraneListing.manufacturer == record.get('manufacturer', ''),
                                CraneListing.year == record.get('year', 0)
                            ).first()
                            
                            if existing:
                                # Update existing record
                                existing.price = record.get('price', 0)
                                existing.location = record.get('location', '')
                                existing.hours = record.get('hours', 0)
                                existing.capacity_tons = record.get('capacity_tons', 0)
                                existing.crane_type = record.get('crane_type', '')
                                existing.region = record.get('region', '')
                                existing.wear_score = record.get('wear_score', 0)
                                existing.value_score = record.get('value_score', 0)
                                existing.source = record.get('source', '')
                                existing.last_updated = datetime.utcnow()
                                records_updated += 1
                            else:
                                # Insert new record
                                new_listing = CraneListing(
                                    title=record.get('title', ''),
                                    manufacturer=record.get('manufacturer', ''),
                                    year=record.get('year', 0),
                                    price=record.get('price', 0),
                                    location=record.get('location', ''),
                                    hours=record.get('hours', 0),
                                    capacity_tons=record.get('capacity_tons', 0),
                                    crane_type=record.get('crane_type', ''),
                                    region=record.get('region', ''),
                                    wear_score=record.get('wear_score', 0),
                                    value_score=record.get('value_score', 0),
                                    source=record.get('source', ''),
                                    scraped_at=datetime.utcnow()
                                )
                                db.add(new_listing)
                                records_inserted += 1
                                
                        except Exception as e:
                            logger.warning(f"Error processing record: {e}")
                            continue
                
                db.commit()
                
            finally:
                db.close()
            
            return {
                'records_inserted': records_inserted,
                'records_updated': records_updated
            }
            
        except Exception as e:
            logger.error(f"Error updating database: {e}")
            raise
    
    async def _update_database_incremental(self) -> Dict[str, Any]:
        """Update database with incremental data"""
        # Similar to _update_database but only processes new scraped data
        return await self._update_database()
    
    def _generate_summary_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary report of the data refresh"""
        try:
            report = {
                'refresh_summary': {
                    'type': results.get('refresh_type', 'unknown'),
                    'start_time': results.get('start_time', ''),
                    'end_time': results.get('end_time', ''),
                    'duration_seconds': results.get('duration_seconds', 0),
                    'total_records': results.get('total_records', 0),
                    'errors_count': len(results.get('errors', []))
                },
                'steps_summary': results.get('steps_completed', []),
                'errors': results.get('errors', []),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            # Save report
            report_file = self.output_path / f"refresh_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            return {
                'report_path': str(report_file),
                'report': report
            }
            
        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
            raise
    
    def get_data_statistics(self) -> Dict[str, Any]:
        """Get current data statistics"""
        try:
            db = self.SessionLocal()
            
            try:
                # Get total listings count
                total_listings = db.query(CraneListing).count()
                
                # Get listings by source
                sources = db.query(CraneListing.source, db.func.count(CraneListing.id)).group_by(CraneListing.source).all()
                
                # Get listings by manufacturer
                manufacturers = db.query(CraneListing.manufacturer, db.func.count(CraneListing.id)).group_by(CraneListing.manufacturer).all()
                
                # Get listings by crane type
                crane_types = db.query(CraneListing.crane_type, db.func.count(CraneListing.id)).group_by(CraneListing.crane_type).all()
                
                # Get listings by region
                regions = db.query(CraneListing.region, db.func.count(CraneListing.id)).group_by(CraneListing.region).all()
                
                # Get average price by capacity range
                capacity_ranges = db.query(
                    db.func.case(
                        (CraneListing.capacity_tons < 50, '0-50'),
                        (CraneListing.capacity_tons < 100, '50-100'),
                        (CraneListing.capacity_tons < 200, '100-200'),
                        (CraneListing.capacity_tons < 500, '200-500'),
                        else_='500+'
                    ).label('capacity_range'),
                    db.func.avg(CraneListing.price).label('avg_price'),
                    db.func.count(CraneListing.id).label('count')
                ).group_by('capacity_range').all()
                
                return {
                    'total_listings': total_listings,
                    'by_source': dict(sources),
                    'by_manufacturer': dict(manufacturers),
                    'by_crane_type': dict(crane_types),
                    'by_region': dict(regions),
                    'by_capacity_range': [
                        {
                            'range': row.capacity_range,
                            'avg_price': float(row.avg_price) if row.avg_price else 0,
                            'count': row.count
                        }
                        for row in capacity_ranges
                    ],
                    'last_updated': datetime.utcnow().isoformat()
                }
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting data statistics: {e}")
            return {'error': str(e)}
