"""
Specification Catalog Service
Manages crane specifications from Bigge and other sources for accurate comparisons
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import hashlib
import sqlite3
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# from ..models.enhanced_crane import CraneListing  # Table doesn't exist yet
from ..core.database import get_db

logger = logging.getLogger(__name__)

class SpecsCatalogService:
    """
    Service for managing crane specifications catalog
    Provides CRUD operations and search functionality
    """
    
    def __init__(self, db_path: str = None):
        # Use PostgreSQL from environment, fallback to SQLite for development
        database_url = os.getenv("DATABASE_URL", None)
        if database_url:
            self.engine = create_engine(database_url, pool_pre_ping=True)
        else:
            db_path = db_path or "crane_intelligence.db"
            self.engine = create_engine(f"sqlite:///{db_path}")
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Initialize specification catalog table
        self._init_specs_catalog_table()
    
    def _init_specs_catalog_table(self):
        """Initialize the specification catalog table"""
        try:
            with self.engine.connect() as conn:
                # Check if using PostgreSQL or SQLite
                is_postgres = 'postgresql' in str(self.engine.url) or 'postgres' in str(self.engine.url)
                
                # Drop table if it exists to recreate with correct schema
                conn.execute(text("DROP TABLE IF EXISTS spec_catalog"))
                
                if is_postgres:
                    # PostgreSQL syntax
                    conn.execute(text("""
                        CREATE TABLE spec_catalog (
                            id SERIAL PRIMARY KEY,
                            spec_id VARCHAR(50) UNIQUE NOT NULL,
                            source VARCHAR(50) NOT NULL,
                            source_url TEXT,
                            last_seen TIMESTAMP,
                            make VARCHAR(100) NOT NULL,
                            model VARCHAR(100) NOT NULL,
                            variant VARCHAR(50),
                            year_from INTEGER,
                            year_to INTEGER,
                            capacity_tons REAL,
                            boom_length_ft REAL,
                            jib_options_ft TEXT,
                            counterweight_lbs INTEGER,
                            engine VARCHAR(200),
                            dimensions TEXT,
                            features TEXT,
                            pdf_specs TEXT,
                            raw_data TEXT,
                            spec_hash VARCHAR(32) UNIQUE NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                else:
                    # SQLite syntax
                    conn.execute(text("""
                        CREATE TABLE spec_catalog (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            spec_id VARCHAR(50) UNIQUE NOT NULL,
                            source VARCHAR(50) NOT NULL,
                            source_url TEXT,
                            last_seen DATETIME,
                            make VARCHAR(100) NOT NULL,
                            model VARCHAR(100) NOT NULL,
                            variant VARCHAR(50),
                            year_from INTEGER,
                            year_to INTEGER,
                            capacity_tons REAL,
                            boom_length_ft REAL,
                            jib_options_ft TEXT,
                            counterweight_lbs INTEGER,
                            engine VARCHAR(200),
                            dimensions TEXT,
                            features TEXT,
                            pdf_specs TEXT,
                            raw_data TEXT,
                            spec_hash VARCHAR(32) UNIQUE NOT NULL,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                
                # Create indexes
                conn.execute(text("CREATE INDEX idx_spec_catalog_make_model ON spec_catalog(make, model)"))
                conn.execute(text("CREATE INDEX idx_spec_catalog_capacity ON spec_catalog(capacity_tons)"))
                conn.execute(text("CREATE INDEX idx_spec_catalog_source ON spec_catalog(source)"))
                conn.execute(text("CREATE INDEX idx_spec_catalog_spec_hash ON spec_catalog(spec_hash)"))
                
                conn.commit()
                logger.info("Specification catalog table initialized")
                
        except Exception as e:
            logger.error(f"Error initializing spec catalog table: {e}")
            raise
    
    def upsert_spec(self, spec_data: Dict[str, Any]) -> bool:
        """Insert or update specification in catalog"""
        try:
            # Convert complex data types to JSON strings
            processed_data = spec_data.copy()
            
            # Convert lists and dicts to JSON strings
            for field in ['jib_options_ft', 'dimensions', 'features', 'pdf_specs', 'raw_data']:
                if field in processed_data and processed_data[field] is not None:
                    if isinstance(processed_data[field], (list, dict)):
                        processed_data[field] = json.dumps(processed_data[field])
                    elif not isinstance(processed_data[field], str):
                        processed_data[field] = json.dumps(processed_data[field])
            
            with self.engine.connect() as conn:
                # Check if spec exists
                existing = conn.execute(
                    text("SELECT id FROM spec_catalog WHERE spec_hash = :spec_hash"),
                    {"spec_hash": processed_data.get('spec_hash')}
                ).fetchone()
                
                if existing:
                    # Update existing spec
                    conn.execute(text("""
                        UPDATE spec_catalog SET
                            source = :source,
                            source_url = :source_url,
                            last_seen = :last_seen,
                            make = :make,
                            model = :model,
                            variant = :variant,
                            year_from = :year_from,
                            year_to = :year_to,
                            capacity_tons = :capacity_tons,
                            boom_length_ft = :boom_length_ft,
                            jib_options_ft = :jib_options_ft,
                            counterweight_lbs = :counterweight_lbs,
                            engine = :engine,
                            dimensions = :dimensions,
                            features = :features,
                            pdf_specs = :pdf_specs,
                            raw_data = :raw_data,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE spec_hash = :spec_hash
                    """), processed_data)
                else:
                    # Insert new spec
                    conn.execute(text("""
                        INSERT INTO spec_catalog (
                            spec_id, source, source_url, last_seen, make, model, variant,
                            year_from, year_to, capacity_tons, boom_length_ft, jib_options_ft,
                            counterweight_lbs, engine, dimensions, features, pdf_specs,
                            raw_data, spec_hash
                        ) VALUES (
                            :spec_id, :source, :source_url, :last_seen, :make, :model, :variant,
                            :year_from, :year_to, :capacity_tons, :boom_length_ft, :jib_options_ft,
                            :counterweight_lbs, :engine, :dimensions, :features, :pdf_specs,
                            :raw_data, :spec_hash
                        )
                    """), processed_data)
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error upserting spec: {e}")
            return False
    
    def get_specs_by_make_model(self, make: str, model: str) -> List[Dict[str, Any]]:
        """Get specifications by make and model"""
        try:
            with self.engine.connect() as conn:
                result =                 conn.execute(text("""
                    SELECT * FROM spec_catalog 
                    WHERE LOWER(make) LIKE LOWER(:make) AND LOWER(model) LIKE LOWER(:model)
                    ORDER BY capacity_tons DESC
                """), {"make": f"%{make}%", "model": f"%{model}%"})
                
                specs = []
                for row in result:
                    spec = dict(row._mapping)
                    # Parse JSON fields
                    spec['jib_options_ft'] = json.loads(spec['jib_options_ft']) if spec['jib_options_ft'] else []
                    spec['dimensions'] = json.loads(spec['dimensions']) if spec['dimensions'] else {}
                    spec['features'] = json.loads(spec['features']) if spec['features'] else []
                    spec['pdf_specs'] = json.loads(spec['pdf_specs']) if spec['pdf_specs'] else []
                    spec['raw_data'] = json.loads(spec['raw_data']) if spec['raw_data'] else {}
                    specs.append(spec)
                
                return specs
                
        except Exception as e:
            logger.error(f"Error getting specs by make/model: {e}")
            return []
    
    def get_specs_by_capacity_range(self, min_capacity: float, max_capacity: float) -> List[Dict[str, Any]]:
        """Get specifications by capacity range"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM spec_catalog 
                    WHERE capacity_tons BETWEEN :min_capacity AND :max_capacity
                    ORDER BY capacity_tons ASC
                """), {"min_capacity": min_capacity, "max_capacity": max_capacity})
                
                specs = []
                for row in result:
                    spec = dict(row._mapping)
                    # Parse JSON fields
                    spec['jib_options_ft'] = json.loads(spec['jib_options_ft']) if spec['jib_options_ft'] else []
                    spec['dimensions'] = json.loads(spec['dimensions']) if spec['dimensions'] else {}
                    spec['features'] = json.loads(spec['features']) if spec['features'] else []
                    spec['pdf_specs'] = json.loads(spec['pdf_specs']) if spec['pdf_specs'] else []
                    spec['raw_data'] = json.loads(spec['raw_data']) if spec['raw_data'] else {}
                    specs.append(spec)
                
                return specs
                
        except Exception as e:
            logger.error(f"Error getting specs by capacity range: {e}")
            return []
    
    def search_specs(self, query: str) -> List[Dict[str, Any]]:
        """Search specifications by query"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM spec_catalog 
                    WHERE LOWER(make) LIKE LOWER(:query) OR LOWER(model) LIKE LOWER(:query) OR LOWER(features) LIKE LOWER(:query)
                    ORDER BY capacity_tons DESC
                    LIMIT 100
                """), {"query": f"%{query}%"})
                
                specs = []
                for row in result:
                    spec = dict(row._mapping)
                    # Parse JSON fields
                    spec['jib_options_ft'] = json.loads(spec['jib_options_ft']) if spec['jib_options_ft'] else []
                    spec['dimensions'] = json.loads(spec['dimensions']) if spec['dimensions'] else {}
                    spec['features'] = json.loads(spec['features']) if spec['features'] else []
                    spec['pdf_specs'] = json.loads(spec['pdf_specs']) if spec['pdf_specs'] else []
                    spec['raw_data'] = json.loads(spec['raw_data']) if spec['raw_data'] else {}
                    specs.append(spec)
                
                return specs
                
        except Exception as e:
            logger.error(f"Error searching specs: {e}")
            return []
    
    def get_spec_stats(self) -> Dict[str, Any]:
        """Get specification catalog statistics"""
        try:
            with self.engine.connect() as conn:
                # Total specs
                total_specs = conn.execute(text("SELECT COUNT(*) FROM spec_catalog")).fetchone()[0]
                
                # Specs by source
                sources = conn.execute(text("""
                    SELECT source, COUNT(*) as count 
                    FROM spec_catalog 
                    GROUP BY source 
                    ORDER BY count DESC
                """)).fetchall()
                
                # Specs by make
                makes = conn.execute(text("""
                    SELECT make, COUNT(*) as count 
                    FROM spec_catalog 
                    GROUP BY make 
                    ORDER BY count DESC 
                    LIMIT 10
                """)).fetchall()
                
                # Capacity distribution
                capacity_ranges = conn.execute(text("""
                    SELECT 
                        CASE 
                            WHEN capacity_tons < 50 THEN '0-50'
                            WHEN capacity_tons < 100 THEN '50-100'
                            WHEN capacity_tons < 200 THEN '100-200'
                            WHEN capacity_tons < 500 THEN '200-500'
                            ELSE '500+'
                        END as range,
                        COUNT(*) as count,
                        AVG(capacity_tons) as avg_capacity
                    FROM spec_catalog 
                    WHERE capacity_tons IS NOT NULL
                    GROUP BY range
                    ORDER BY avg_capacity
                """)).fetchall()
                
                # Field completeness
                completeness = conn.execute(text("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(capacity_tons) as capacity_count,
                        COUNT(boom_length_ft) as boom_count,
                        COUNT(jib_options_ft) as jib_count,
                        COUNT(counterweight_lbs) as counterweight_count,
                        COUNT(engine) as engine_count
                    FROM spec_catalog
                """)).fetchone()
                
                return {
                    'total_specs': total_specs,
                    'by_source': [{'source': row[0], 'count': row[1]} for row in sources],
                    'by_make': [{'make': row[0], 'count': row[1]} for row in makes],
                    'by_capacity_range': [
                        {
                            'range': row[0],
                            'count': row[1],
                            'avg_capacity': round(row[2], 2) if row[2] else 0
                        }
                        for row in capacity_ranges
                    ],
                    'field_completeness': {
                        'total': completeness[0],
                        'capacity': round(completeness[1] / completeness[0] * 100, 1) if completeness[0] > 0 else 0,
                        'boom_length': round(completeness[2] / completeness[0] * 100, 1) if completeness[0] > 0 else 0,
                        'jib_options': round(completeness[3] / completeness[0] * 100, 1) if completeness[0] > 0 else 0,
                        'counterweight': round(completeness[4] / completeness[0] * 100, 1) if completeness[0] > 0 else 0,
                        'engine': round(completeness[5] / completeness[0] * 100, 1) if completeness[0] > 0 else 0
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting spec stats: {e}")
            return {}
    
    def find_matching_specs(self, crane_listing: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find matching specifications for a crane listing"""
        try:
            make = crane_listing.get('manufacturer', '')
            model = crane_listing.get('title', '')
            capacity = crane_listing.get('capacity_tons')
            
            if not make and not model:
                return []
            
            with self.engine.connect() as conn:
                # Build query based on available data
                query_parts = []
                params = {}
                
                if make:
                    query_parts.append("LOWER(make) LIKE LOWER(:make)")
                    params['make'] = f"%{make}%"
                
                if model:
                    query_parts.append("LOWER(model) LIKE LOWER(:model)")
                    params['model'] = f"%{model}%"
                
                if capacity:
                    # Look for specs within 20% of the capacity
                    tolerance = capacity * 0.2
                    query_parts.append("capacity_tons BETWEEN :min_capacity AND :max_capacity")
                    params['min_capacity'] = capacity - tolerance
                    params['max_capacity'] = capacity + tolerance
                
                if not query_parts:
                    return []
                
                query = f"""
                    SELECT * FROM spec_catalog 
                    WHERE {' AND '.join(query_parts)}
                    ORDER BY 
                        CASE WHEN capacity_tons IS NOT NULL THEN ABS(capacity_tons - :target_capacity) ELSE 999999 END,
                        make, model
                    LIMIT 10
                """
                params['target_capacity'] = capacity or 0
                
                result = conn.execute(text(query), params)
                
                specs = []
                for row in result:
                    spec = dict(row._mapping)
                    # Parse JSON fields
                    spec['jib_options_ft'] = json.loads(spec['jib_options_ft']) if spec['jib_options_ft'] else []
                    spec['dimensions'] = json.loads(spec['dimensions']) if spec['dimensions'] else {}
                    spec['features'] = json.loads(spec['features']) if spec['features'] else []
                    spec['pdf_specs'] = json.loads(spec['pdf_specs']) if spec['pdf_specs'] else []
                    spec['raw_data'] = json.loads(spec['raw_data']) if spec['raw_data'] else {}
                    specs.append(spec)
                
                return specs
                
        except Exception as e:
            logger.error(f"Error finding matching specs: {e}")
            return []
    
    def enrich_crane_listing(self, crane_listing: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich crane listing with specification data"""
        try:
            # Find matching specifications
            matching_specs = self.find_matching_specs(crane_listing)
            
            if not matching_specs:
                return crane_listing
            
            # Use the best match (first one)
            best_match = matching_specs[0]
            
            # Enrich the listing
            enriched_listing = crane_listing.copy()
            
            # Add specification data
            enriched_listing['spec_data'] = {
                'spec_id': best_match.get('spec_id'),
                'source': best_match.get('source'),
                'capacity_tons': best_match.get('capacity_tons'),
                'boom_length_ft': best_match.get('boom_length_ft'),
                'jib_options_ft': best_match.get('jib_options_ft', []),
                'counterweight_lbs': best_match.get('counterweight_lbs'),
                'engine': best_match.get('engine'),
                'dimensions': best_match.get('dimensions', {}),
                'features': best_match.get('features', []),
                'confidence_score': self._calculate_match_confidence(crane_listing, best_match)
            }
            
            # Update listing fields if missing
            if not enriched_listing.get('capacity_tons') and best_match.get('capacity_tons'):
                enriched_listing['capacity_tons'] = best_match['capacity_tons']
            
            if not enriched_listing.get('crane_type') and best_match.get('features'):
                enriched_listing['crane_type'] = self._infer_crane_type_from_features(best_match['features'])
            
            return enriched_listing
            
        except Exception as e:
            logger.error(f"Error enriching crane listing: {e}")
            return crane_listing
    
    def _calculate_match_confidence(self, listing: Dict[str, Any], spec: Dict[str, Any]) -> float:
        """Calculate confidence score for spec match"""
        try:
            confidence = 0.0
            
            # Make match
            if listing.get('manufacturer', '').lower() in spec.get('make', '').lower():
                confidence += 0.3
            
            # Model match
            if any(word in spec.get('model', '').lower() for word in listing.get('title', '').lower().split()):
                confidence += 0.3
            
            # Capacity match
            listing_capacity = listing.get('capacity_tons')
            spec_capacity = spec.get('capacity_tons')
            if listing_capacity and spec_capacity:
                capacity_diff = abs(listing_capacity - spec_capacity) / max(listing_capacity, spec_capacity)
                if capacity_diff < 0.1:  # Within 10%
                    confidence += 0.4
                elif capacity_diff < 0.2:  # Within 20%
                    confidence += 0.2
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.warning(f"Error calculating match confidence: {e}")
            return 0.0
    
    def _infer_crane_type_from_features(self, features: List[str]) -> str:
        """Infer crane type from features"""
        if not features:
            return 'unknown'
        
        features_text = ' '.join(features).lower()
        
        if any(word in features_text for word in ['all terrain', 'at', 'gmk', 'ltm', 'ac']):
            return 'all_terrain'
        elif any(word in features_text for word in ['crawler', 'cc', 'ltc']):
            return 'crawler'
        elif any(word in features_text for word in ['rough terrain', 'rt', 'rtc']):
            return 'rough_terrain'
        elif any(word in features_text for word in ['truck', 'boom truck', 'tm']):
            return 'truck_mounted'
        elif any(word in features_text for word in ['tower', 'tt', 'ct']):
            return 'tower'
        
        return 'unknown'
    
    def load_specs_from_file(self, file_path: Path) -> int:
        """Load specifications from JSONL file"""
        try:
            loaded_count = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        spec_data = json.loads(line.strip())
                        
                        # Ensure required fields
                        if not spec_data.get('spec_id') or not spec_data.get('spec_hash'):
                            continue
                        
                        # Convert lists to JSON strings
                        if 'jib_options_ft' in spec_data and isinstance(spec_data['jib_options_ft'], list):
                            spec_data['jib_options_ft'] = json.dumps(spec_data['jib_options_ft'])
                        
                        if 'dimensions' in spec_data and isinstance(spec_data['dimensions'], dict):
                            spec_data['dimensions'] = json.dumps(spec_data['dimensions'])
                        
                        if 'features' in spec_data and isinstance(spec_data['features'], list):
                            spec_data['features'] = json.dumps(spec_data['features'])
                        
                        if 'pdf_specs' in spec_data and isinstance(spec_data['pdf_specs'], list):
                            spec_data['pdf_specs'] = json.dumps(spec_data['pdf_specs'])
                        
                        if 'raw_data' in spec_data and isinstance(spec_data['raw_data'], dict):
                            spec_data['raw_data'] = json.dumps(spec_data['raw_data'])
                        
                        if self.upsert_spec(spec_data):
                            loaded_count += 1
                            
                    except Exception as e:
                        logger.warning(f"Error loading spec from line: {e}")
                        continue
            
            logger.info(f"Loaded {loaded_count} specifications from {file_path}")
            return loaded_count
            
        except Exception as e:
            logger.error(f"Error loading specs from file: {e}")
            return 0