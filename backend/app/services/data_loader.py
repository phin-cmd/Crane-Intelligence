"""
Data Loader for Crane Intelligence Platform
Loads and processes all data sources for the valuation engine
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

class DataLoader:
    """Loads and processes all data sources for the platform"""
    
    def __init__(self):
        self.crane_listings = None
        self.rental_rates = None
        self.buying_trends = None
        self.load_all_data()
    
    def load_all_data(self):
        """Load all data sources"""
        try:
            self.load_crane_listings()
            self.load_rental_rates()
            self.load_buying_trends()
            logger.info("All data sources loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load data sources: {e}")
    
    def load_crane_listings(self):
        """Load crane listings data"""
        try:
            csv_path = Path("docs/requirements/crane_data_scoring_20250706_173618.csv")
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                # Clean and process the data
                df['price'] = pd.to_numeric(df['price'], errors='coerce')
                df['hours'] = pd.to_numeric(df['hours'], errors='coerce')
                df['year'] = pd.to_numeric(df['year'], errors='coerce')
                df['wear_score'] = pd.to_numeric(df['wear_score'], errors='coerce')
                df['value_score'] = pd.to_numeric(df['value_score'], errors='coerce')
                
                # Extract capacity from title - improved regex
                capacity_pattern = r'(\d+(?:\.\d+)?)\s*(?:t|ton|tons?)'
                df['capacity'] = df['title'].str.extract(capacity_pattern, flags=re.IGNORECASE)[0]
                df['capacity'] = pd.to_numeric(df['capacity'], errors='coerce')
                
                # If no capacity found, try to extract from model names
                df.loc[df['capacity'].isna(), 'capacity'] = df.loc[df['capacity'].isna(), 'title'].str.extract(r'(\d{3,4})', flags=re.IGNORECASE)[0]
                df['capacity'] = pd.to_numeric(df['capacity'], errors='coerce')
                
                self.crane_listings = df
                logger.info(f"Loaded {len(df)} crane listings")
            else:
                logger.warning("Crane listings CSV not found")
                self.crane_listings = pd.DataFrame()
        except Exception as e:
            logger.error(f"Failed to load crane listings: {e}")
            self.crane_listings = pd.DataFrame()
    
    def load_rental_rates(self):
        """Load rental rates by region"""
        try:
            csv_path = Path("docs/requirements/Crane_Rental_Rates_By_Region.csv")
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                df['Monthly Rate (USD)'] = pd.to_numeric(df['Monthly Rate (USD)'], errors='coerce')
                df['Tonnage'] = pd.to_numeric(df['Tonnage'], errors='coerce')
                self.rental_rates = df
                logger.info(f"Loaded {len(df)} rental rate records")
            else:
                logger.warning("Rental rates CSV not found")
                self.rental_rates = pd.DataFrame()
        except Exception as e:
            logger.error(f"Failed to load rental rates: {e}")
            self.rental_rates = pd.DataFrame()
    
    def load_buying_trends(self):
        """Load buying trends data"""
        try:
            csv_path = Path("docs/requirements/Valuation_Engine_-_Buying_Trends.csv")
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                self.buying_trends = df
                logger.info(f"Loaded {len(df)} buying trend records")
            else:
                logger.warning("Buying trends CSV not found")
                self.buying_trends = pd.DataFrame()
        except Exception as e:
            logger.error(f"Failed to load buying trends: {e}")
            self.buying_trends = pd.DataFrame()
    
    def get_crane_listings(self) -> pd.DataFrame:
        """Get crane listings data"""
        return self.crane_listings if self.crane_listings is not None else pd.DataFrame()
    
    def get_rental_rates(self) -> pd.DataFrame:
        """Get rental rates data"""
        return self.rental_rates if self.rental_rates is not None else pd.DataFrame()
    
    def get_buying_trends(self) -> pd.DataFrame:
        """Get buying trends data"""
        return self.buying_trends if self.buying_trends is not None else pd.DataFrame()
    
    def find_comparables(self, manufacturer: str, model: str, capacity: float, year: int, limit: int = 10) -> List[Dict]:
        """Find comparable crane listings"""
        if self.crane_listings.empty:
            return []
        
        # Filter by manufacturer and model similarity
        manufacturer_lower = manufacturer.lower()
        model_lower = model.lower()
        
        # Find similar listings - more flexible matching
        similar_listings = self.crane_listings[
            (self.crane_listings['manufacturer'].str.lower() == manufacturer_lower) |
            (self.crane_listings['title'].str.lower().str.contains(model_lower, na=False)) |
            (self.crane_listings['title'].str.lower().str.contains(manufacturer_lower, na=False))
        ].copy()
        
        if similar_listings.empty:
            # Fallback to capacity-based matching with wider range
            similar_listings = self.crane_listings[
                (self.crane_listings['capacity'] >= capacity * 0.5) &
                (self.crane_listings['capacity'] <= capacity * 1.5) &
                (self.crane_listings['capacity'].notna())
            ].copy()
        
        if similar_listings.empty:
            # Final fallback - any listings with similar year
            similar_listings = self.crane_listings[
                (self.crane_listings['year'] >= year - 3) &
                (self.crane_listings['year'] <= year + 3) &
                (self.crane_listings['year'].notna())
            ].copy()
        
        if similar_listings.empty:
            return []
        
        # Calculate similarity scores
        similar_listings['similarity_score'] = similar_listings.apply(
            lambda row: self._calculate_similarity_score(manufacturer, model, capacity, year, row), axis=1
        )
        
        # Sort by similarity and return top results
        top_comparables = similar_listings.nlargest(limit, 'similarity_score')
        
        comparables = []
        for _, row in top_comparables.iterrows():
            comparable = {
                'title': row.get('title', ''),
                'manufacturer': row.get('manufacturer', ''),
                'year': int(row.get('year', 0)) if pd.notna(row.get('year')) else 0,
                'price': float(row.get('price', 0)) if pd.notna(row.get('price')) else 0,
                'location': row.get('location', ''),
                'hours': int(row.get('hours', 0)) if pd.notna(row.get('hours')) else 0,
                'capacity': float(row.get('capacity', 0)) if pd.notna(row.get('capacity')) else 0,
                'similarity_score': float(row.get('similarity_score', 0)),
                'source': row.get('source', '')
            }
            comparables.append(comparable)
        
        return comparables
    
    def _calculate_similarity_score(self, manufacturer: str, model: str, capacity: float, year: int, row: pd.Series) -> float:
        """Calculate similarity score between crane specs and listing"""
        score = 0.0
        
        # Manufacturer match (30%)
        if row.get('manufacturer', '').lower() == manufacturer.lower():
            score += 0.30
        
        # Model match (20%)
        if model.lower() in row.get('title', '').lower():
            score += 0.20
        
        # Capacity similarity (30%)
        row_capacity = row.get('capacity', 0)
        if row_capacity > 0 and capacity > 0:
            capacity_diff = abs(row_capacity - capacity) / capacity
            if capacity_diff <= 0.2:  # Within 20%
                score += 0.30 * (1 - capacity_diff / 0.2)
        
        # Year similarity (20%)
        row_year = row.get('year', 0)
        if row_year > 0 and year > 0:
            year_diff = abs(row_year - year)
            if year_diff <= 5:  # Within 5 years
                score += 0.20 * (1 - year_diff / 5)
        
        return score
    
    def get_rental_scenarios(self, crane_type: str, capacity: float) -> Dict[str, Dict]:
        """Get financing scenarios by region"""
        if self.rental_rates.empty:
            return {}
        
        # Map crane type to rental data
        type_mapping = {
            'all_terrain': 'All Terrain (AT)',
            'crawler': 'Crawler Crane',
            'rough_terrain': 'Rough Terrain (RT)',
            'tower': 'Tower Crane',
            'truck': 'Truck Crane',
            'boom_truck': 'Boom Truck'
        }
        
        mapped_type = type_mapping.get(crane_type.lower(), crane_type)
        
        # Find matching rental rates
        matching_rates = self.rental_rates[
            (self.rental_rates['Crane Type'].str.contains(mapped_type, case=False, na=False)) |
            (self.rental_rates['Tonnage'] >= capacity * 0.8) & 
            (self.rental_rates['Tonnage'] <= capacity * 1.2)
        ]
        
        if matching_rates.empty:
            return {}
        
        scenarios = {}
        for _, row in matching_rates.iterrows():
            region = row.get('Region', '')
            monthly_rate = row.get('Monthly Rate (USD)', 0)
            
            if region and monthly_rate > 0:
                scenarios[region] = {
                    'monthly_rental_rate': monthly_rate,
                    'annual_rental_income': monthly_rate * 12,
                    'crane_type': row.get('Crane Type', ''),
                    'tonnage': row.get('Tonnage', 0)
                }
        
        return scenarios

# Global data loader instance
data_loader = DataLoader()
