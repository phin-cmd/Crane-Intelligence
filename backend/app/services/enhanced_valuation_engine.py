"""
Enhanced Valuation Engine for Crane Intelligence Platform
Incorporates Bloomberg-style analysis with comprehensive data integration
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from logger import get_logger

logger = get_logger("enhanced_valuation")

class EnhancedValuationEngine:
    """
    Bloomberg-style valuation engine that delivers:
    - Fair market valuation with wholesale/retail ranges
    - Automatic comparable units from live listings and sales
    - Market context from weekly trend data
    - Financing scenarios by region
    - Professional PDF reports ready for clients
    """
    
    def __init__(self):
        self.logger = logger
        
        # Load data sources
        self.crane_listings = self._load_crane_listings()
        self.rental_rates = self._load_rental_rates()
        self.buying_trends = self._load_buying_trends()
        self.spec_catalog = self._load_spec_catalog()
        
        # Enhanced depreciation curves by crane type
        self.depreciation_curves = {
            'all_terrain': {
                'years_0_3': 0.08,    # 8% annual (premium equipment)
                'years_4_7': 0.12,    # 12% annual (standard)
                'years_8_15': 0.15,   # 15% annual (aging)
                'years_15_plus': 0.05 # 5% annual (stabilized)
            },
            'crawler': {
                'years_0_3': 0.06,    # 6% annual (heavy duty, slower depreciation)
                'years_4_7': 0.10,    # 10% annual
                'years_8_15': 0.12,   # 12% annual
                'years_15_plus': 0.04 # 4% annual
            },
            'tower': {
                'years_0_3': 0.10,    # 10% annual (technology dependent)
                'years_4_7': 0.15,    # 15% annual
                'years_8_15': 0.18,   # 18% annual
                'years_15_plus': 0.08 # 8% annual
            },
            'rough_terrain': {
                'years_0_3': 0.10,    # 10% annual
                'years_4_7': 0.14,    # 14% annual
                'years_8_15': 0.16,   # 16% annual
                'years_15_plus': 0.06 # 6% annual
            }
        }
        
        # Regional market multipliers
        self.regional_multipliers = {
            'northeast': 1.15,     # High demand, infrastructure projects
            'southeast': 1.05,     # Moderate demand
            'gulf_coast': 1.20,    # Energy sector premium
            'west_coast': 1.25,    # High cost of living, regulations
            'midwest': 0.95,       # Lower cost base
            'canada': 1.10         # Currency and import factors
        }
        
        # Manufacturer premium/discount factors
        self.manufacturer_factors = {
            'liebherr': 1.15,    # Premium brand
            'grove': 1.05,       # Solid brand
            'manitowoc': 1.10,   # Premium brand
            'terex': 0.95,       # Value brand
            'link-belt': 1.00,   # Standard
            'tadano': 1.08,      # Quality brand
            'national': 0.90,    # Value brand
            'demag': 1.12,       # Premium brand
            'kato': 1.03         # Quality brand
        }
        
        logger.info("enhanced_valuation_init", "Enhanced valuation engine initialized")
    
    def _load_crane_listings(self) -> pd.DataFrame:
        """Load crane listings data"""
        try:
            # Load from the CSV file in requirements
            csv_path = Path("Requirements/crane_data_scoring_20250706_173618.csv")
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                logger.info("_load_crane_listings", "Crane listings loaded", count=len(df))
                return df
            else:
                logger.warning("_load_crane_listings", "Crane listings CSV not found")
                return pd.DataFrame()
        except Exception as e:
            logger.error("_load_crane_listings", "Failed to load crane listings", error=str(e))
            return pd.DataFrame()
    
    def _load_rental_rates(self) -> pd.DataFrame:
        """Load rental rates by region"""
        try:
            csv_path = Path("Requirements/Crane_Rental_Rates_By_Region.csv")
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                logger.info("_load_rental_rates", "Rental rates loaded", count=len(df))
                return df
            else:
                logger.warning("_load_rental_rates", "Rental rates CSV not found")
                return pd.DataFrame()
        except Exception as e:
            logger.error("_load_rental_rates", "Failed to load rental rates", error=str(e))
            return pd.DataFrame()
    
    def _load_buying_trends(self) -> pd.DataFrame:
        """Load buying trends data"""
        try:
            csv_path = Path("Requirements/Valuation_Engine_-_Buying_Trends.csv")
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                logger.info("_load_buying_trends", "Buying trends loaded", count=len(df))
                return df
            else:
                logger.warning("_load_buying_trends", "Buying trends CSV not found")
                return pd.DataFrame()
        except Exception as e:
            logger.error("_load_buying_trends", "Failed to load buying trends", error=str(e))
            return pd.DataFrame()
    
    def _load_spec_catalog(self) -> Dict[str, Any]:
        """Load specification catalog"""
        try:
            # This would load from the normalized specs database
            # For now, return empty dict
            return {}
        except Exception as e:
            logger.error("_load_spec_catalog", "Failed to load spec catalog", error=str(e))
            return {}
    
    def calculate_valuation(self, crane_specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive Bloomberg-style valuation
        """
        logger.info("calculate_valuation", "Starting valuation calculation", 
                   model=crane_specs.get('model', 'Unknown'))
        
        try:
            # 1. Base MARCS depreciation calculation
            base_valuation = self._calculate_base_valuation(crane_specs)
            
            # 2. Apply market trend adjustments
            trend_adjustment = self._calculate_trend_adjustment(crane_specs)
            
            # 3. Apply regional factors
            regional_adjustment = self._calculate_regional_adjustment(crane_specs)
            
            # 4. Apply manufacturer factors
            manufacturer_adjustment = self._calculate_manufacturer_adjustment(crane_specs)
            
            # 5. Apply market intelligence
            market_adjustment = self._calculate_market_intelligence_adjustment(crane_specs)
            
            # 6. Calculate final valuation
            final_valuation = base_valuation * (1 + trend_adjustment + regional_adjustment + 
                                              manufacturer_adjustment + market_adjustment)
            
            # 7. Calculate valuation ranges
            valuation_ranges = self._calculate_valuation_ranges(final_valuation)
            
            # 8. Find comparables
            comparables = self._find_comparables(crane_specs)
            
            # 9. Generate market insights
            market_insights = self._generate_market_insights(crane_specs)
            
            # 10. Calculate deal score
            deal_score = self._calculate_deal_score(crane_specs, final_valuation)
            
            # 11. Calculate wear score
            wear_score = self._calculate_wear_score(crane_specs)
            
            # 12. Generate financing scenarios
            financing_scenarios = self._generate_financing_scenarios(crane_specs, final_valuation)
            
            # 13. Calculate confidence score
            confidence_score = self._calculate_confidence_score(crane_specs)
            
            result = {
                'estimated_value': final_valuation,
                'valuation_ranges': valuation_ranges,
                'confidence_score': confidence_score,
                'deal_score': deal_score,
                'wear_score': wear_score,
                'comparables': comparables,
                'market_insights': market_insights,
                'financing_scenarios': financing_scenarios,
                'valuation_breakdown': {
                    'base_valuation': base_valuation,
                    'trend_adjustment': trend_adjustment,
                    'regional_adjustment': regional_adjustment,
                    'manufacturer_adjustment': manufacturer_adjustment,
                    'market_adjustment': market_adjustment,
                    'final_valuation': final_valuation
                },
                'generated_at': datetime.now().isoformat(),
                'crane_specs': crane_specs
            }
            
            logger.info("calculate_valuation", "Valuation calculation completed", 
                       final_value=final_valuation, confidence=confidence_score)
            
            return result
            
        except Exception as e:
            logger.error("calculate_valuation", "Valuation calculation failed", error=str(e))
            return {
                'error': str(e),
                'estimated_value': 0,
                'confidence_score': 0
            }
    
    def _calculate_base_valuation(self, crane_specs: Dict[str, Any]) -> float:
        """Calculate base valuation using MARCS depreciation"""
        # Get new unit cost estimate
        new_unit_cost = self._estimate_new_unit_cost(crane_specs)
        
        # Calculate age-based depreciation
        age = 2025 - crane_specs.get('year', 2020)
        crane_type = self._determine_crane_type(crane_specs)
        
        # Get depreciation curve
        curve = self.depreciation_curves.get(crane_type, self.depreciation_curves['all_terrain'])
        
        # Apply depreciation based on age
        if age <= 3:
            annual_rate = curve['years_0_3']
        elif age <= 7:
            annual_rate = curve['years_4_7']
        elif age <= 15:
            annual_rate = curve['years_8_15']
        else:
            annual_rate = curve['years_15_plus']
        
        # Calculate depreciated value
        depreciation_factor = (1 - annual_rate) ** age
        base_value = new_unit_cost * depreciation_factor
        
        # Apply hours adjustment
        hours = crane_specs.get('hours', 0)
        hours_adjustment = self._calculate_hours_adjustment(hours, age)
        
        return base_value * (1 + hours_adjustment)
    
    def _estimate_new_unit_cost(self, crane_specs: Dict[str, Any]) -> float:
        """Estimate new unit cost based on capacity and type"""
        capacity = crane_specs.get('capacity', 100)
        crane_type = self._determine_crane_type(crane_specs)
        manufacturer = crane_specs.get('manufacturer', '').lower()
        
        # Base cost per ton by type
        base_costs = {
            'all_terrain': 12000,  # $12k per ton
            'crawler': 15000,      # $15k per ton (more complex)
            'tower': 8000,         # $8k per ton
            'rough_terrain': 8000, # $8k per ton
        }
        
        base_cost_per_ton = base_costs.get(crane_type, 12000)
        
        # Manufacturer premium/discount
        manufacturer_multiplier = self.manufacturer_factors.get(manufacturer, 1.0)
        
        # Calculate estimated new cost
        estimated_cost = capacity * base_cost_per_ton * manufacturer_multiplier
        
        # Apply capacity scaling (economies/diseconomies of scale)
        if capacity > 500:
            estimated_cost *= 1.2  # Large crane premium
        elif capacity > 300:
            estimated_cost *= 1.1  # Medium-large premium
        elif capacity < 50:
            estimated_cost *= 0.9  # Small crane discount
        
        return estimated_cost
    
    def _determine_crane_type(self, crane_specs: Dict[str, Any]) -> str:
        """Determine crane type from specifications"""
        model = crane_specs.get('model', '').lower()
        manufacturer = crane_specs.get('manufacturer', '').lower()
        
        # All-terrain indicators
        if any(indicator in model for indicator in ['ltm', 'at', 'all-terrain']):
            return 'all_terrain'
        
        # Crawler indicators
        if any(indicator in model for indicator in ['cc', 'crawler', 'lr']):
            return 'crawler'
        
        # Tower indicators
        if any(indicator in model for indicator in ['tower', 'tt', 'ct']):
            return 'tower'
        
        # Rough terrain indicators
        if any(indicator in model for indicator in ['rt', 'rough-terrain']):
            return 'rough_terrain'
        
        # Default based on capacity
        capacity = crane_specs.get('capacity', 100)
        if capacity >= 200:
            return 'crawler'
        elif capacity >= 100:
            return 'all_terrain'
        else:
            return 'rough_terrain'
    
    def _calculate_hours_adjustment(self, hours: int, age: int) -> float:
        """Calculate adjustment based on operating hours"""
        if hours == 0:
            return 0.0  # No adjustment for unknown hours
        
        # Expected hours per year by age
        expected_annual_hours = 800  # Industry average
        expected_total_hours = age * expected_annual_hours
        
        if expected_total_hours == 0:
            return 0.0
        
        # Calculate hours ratio
        hours_ratio = hours / expected_total_hours
        
        # Apply adjustment
        if hours_ratio < 0.5:
            return 0.15  # Low hours premium (15%)
        elif hours_ratio < 0.8:
            return 0.05  # Moderate hours premium (5%)
        elif hours_ratio < 1.2:
            return 0.0   # Normal hours (no adjustment)
        elif hours_ratio < 1.5:
            return -0.05 # High hours discount (-5%)
        else:
            return -0.15 # Very high hours discount (-15%)
    
    def _calculate_trend_adjustment(self, crane_specs: Dict[str, Any]) -> float:
        """Calculate adjustment based on buying trends"""
        if self.buying_trends.empty:
            return 0.0
        
        capacity = crane_specs.get('capacity', 100)
        crane_type = self._determine_crane_type(crane_specs)
        
        # Map to trend segments
        if crane_type == 'crawler' and capacity >= 300:
            segment = '300t+ Crawler Cranes'
        elif crane_type == 'all_terrain' and 70 <= capacity <= 120:
            segment = '70-120t All-Terrain'
        elif crane_type == 'tower':
            segment = 'Refurbished Tower Cranes'
        elif crane_type == 'all_terrain' and 90 <= capacity <= 200:
            segment = 'Used 90-200t AT'
        else:
            segment = 'General Market'
        
        # Get trend data
        trend_data = self.buying_trends[self.buying_trends['Market Segment'] == segment]
        if trend_data.empty:
            return 0.0
        
        growth_rate = trend_data.iloc[0].get('YoY Growth', '0%')
        growth_value = self._parse_percentage(growth_rate)
        
        # Convert growth rate to valuation adjustment
        if growth_value > 0.15:      # >15% growth
            return 0.10             # 10% premium
        elif growth_value > 0.10:    # >10% growth
            return 0.05             # 5% premium
        elif growth_value > 0.05:    # >5% growth
            return 0.02             # 2% premium
        elif growth_value < -0.05:   # Declining market
            return -0.05            # 5% discount
        else:
            return 0.0              # No adjustment
    
    def _calculate_regional_adjustment(self, crane_specs: Dict[str, Any]) -> float:
        """Calculate adjustment based on regional factors"""
        location = crane_specs.get('region', '').lower()
        
        # Map location to region
        region = 'midwest'  # Default
        
        if any(state in location for state in ['northeast', 'ny', 'nj', 'pa', 'ct', 'ma']):
            region = 'northeast'
        elif any(state in location for state in ['southeast', 'fl', 'ga', 'sc', 'nc', 'va']):
            region = 'southeast'
        elif any(state in location for state in ['gulf', 'tx', 'la', 'ok', 'ar']):
            region = 'gulf_coast'
        elif any(state in location for state in ['west', 'ca', 'or', 'wa', 'nv', 'az']):
            region = 'west_coast'
        elif 'canada' in location or 'ca' in location:
            region = 'canada'
        
        # Get regional multiplier
        multiplier = self.regional_multipliers.get(region, 1.0)
        
        # Convert to adjustment (multiplier - 1)
        return multiplier - 1.0
    
    def _calculate_manufacturer_adjustment(self, crane_specs: Dict[str, Any]) -> float:
        """Calculate adjustment based on manufacturer"""
        manufacturer = crane_specs.get('manufacturer', '').lower()
        multiplier = self.manufacturer_factors.get(manufacturer, 1.0)
        return multiplier - 1.0
    
    def _calculate_market_intelligence_adjustment(self, crane_specs: Dict[str, Any]) -> float:
        """Calculate adjustment based on market intelligence"""
        if self.crane_listings.empty:
            return 0.0
        
        manufacturer = crane_specs.get('manufacturer', '').lower()
        model = crane_specs.get('model', '').lower()
        
        # Find similar listings
        similar_listings = self.crane_listings[
            (self.crane_listings['manufacturer'].str.lower() == manufacturer) |
            (self.crane_listings['title'].str.lower().str.contains(model, na=False))
        ]
        
        if similar_listings.empty:
            return 0.0
        
        # Calculate average price premium/discount
        avg_listing_price = similar_listings['price'].mean()
        estimated_market_value = self._estimate_new_unit_cost(crane_specs) * 0.7
        
        if estimated_market_value > 0:
            market_premium = (avg_listing_price - estimated_market_value) / estimated_market_value
            # Cap adjustment at ±10%
            return max(-0.10, min(0.10, market_premium))
        
        return 0.0
    
    def _calculate_valuation_ranges(self, base_value: float) -> Dict[str, float]:
        """Calculate multiple valuation types"""
        return {
            'wholesale_value': base_value * 0.75,      # 75% of FMV
            'fair_market_value': base_value,           # 100% of FMV
            'retail_value': base_value * 1.15,         # 115% of FMV
            'orderly_liquidation_value': base_value * 0.65,
            'forced_liquidation_value': base_value * 0.45,
            'insurance_replacement_value': base_value * 1.25
        }
    
    def _find_comparables(self, crane_specs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find comparable units from listings"""
        if self.crane_listings.empty:
            return []
        
        manufacturer = crane_specs.get('manufacturer', '').lower()
        model = crane_specs.get('model', '').lower()
        capacity = crane_specs.get('capacity', 100)
        year = crane_specs.get('year', 2020)
        
        # Find similar listings
        similar_listings = self.crane_listings[
            (self.crane_listings['manufacturer'].str.lower() == manufacturer) |
            (self.crane_listings['title'].str.lower().str.contains(model, na=False))
        ].copy()
        
        if similar_listings.empty:
            return []
        
        # Calculate similarity scores
        similar_listings['similarity_score'] = similar_listings.apply(
            lambda row: self._calculate_similarity_score(crane_specs, row), axis=1
        )
        
        # Sort by similarity and return top 10
        top_comparables = similar_listings.nlargest(10, 'similarity_score')
        
        comparables = []
        for _, row in top_comparables.iterrows():
            comparable = {
                'title': row.get('title', ''),
                'manufacturer': row.get('manufacturer', ''),
                'year': row.get('year', ''),
                'price': row.get('price', 0),
                'location': row.get('location', ''),
                'hours': row.get('hours', 0),
                'similarity_score': row.get('similarity_score', 0),
                'source': row.get('source', '')
            }
            comparables.append(comparable)
        
        return comparables
    
    def _calculate_similarity_score(self, crane_specs: Dict[str, Any], listing: pd.Series) -> float:
        """Calculate similarity score between crane specs and listing"""
        score = 0.0
        
        # Manufacturer match (30%)
        if (crane_specs.get('manufacturer', '').lower() == 
            listing.get('manufacturer', '').lower()):
            score += 0.30
        
        # Model match (20%)
        if (crane_specs.get('model', '').lower() in 
            listing.get('title', '').lower()):
            score += 0.20
        
        # Year similarity (20%)
        crane_year = crane_specs.get('year', 0)
        listing_year = listing.get('year', 0)
        if crane_year > 0 and listing_year > 0:
            year_diff = abs(crane_year - listing_year)
            if year_diff <= 5:  # Within 5 years
                score += 0.20 * (1 - year_diff / 5)
        
        # Price reasonableness (30%)
        crane_capacity = crane_specs.get('capacity', 100)
        listing_price = listing.get('price', 0)
        if listing_price > 0 and crane_capacity > 0:
            price_per_ton = listing_price / crane_capacity
            expected_price_per_ton = 8000  # Rough estimate
            price_ratio = price_per_ton / expected_price_per_ton
            if 0.5 <= price_ratio <= 2.0:  # Reasonable range
                score += 0.30 * (1 - abs(price_ratio - 1.0))
        
        return score
    
    def _generate_market_insights(self, crane_specs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate market insights based on all data"""
        insights = {
            'market_trend': 'stable',
            'demand_outlook': 'moderate',
            'price_direction': 'stable',
            'key_factors': [],
            'regional_analysis': {},
            'competitive_landscape': {}
        }
        
        # Analyze buying trends
        capacity = crane_specs.get('capacity', 100)
        crane_type = self._determine_crane_type(crane_specs)
        
        # Determine market trend
        if crane_type == 'crawler' and capacity >= 300:
            insights['market_trend'] = 'strong_growth'
            insights['demand_outlook'] = 'high'
            insights['price_direction'] = 'increasing'
            insights['key_factors'].append('Infrastructure and offshore wind projects driving demand')
        
        elif crane_type == 'all_terrain' and 70 <= capacity <= 120:
            insights['market_trend'] = 'moderate_growth'
            insights['demand_outlook'] = 'moderate'
            insights['price_direction'] = 'stable_to_increasing'
            insights['key_factors'].append('Urban construction and utilities demand')
        
        # Add regional factors
        location = crane_specs.get('region', '').lower()
        if any(region in location for region in ['gulf', 'texas', 'louisiana']):
            insights['key_factors'].append('Energy sector activity in Gulf Coast region')
        
        return insights
    
    def _calculate_deal_score(self, crane_specs: Dict[str, Any], estimated_value: float) -> int:
        """Calculate deal score (0-100)"""
        asking_price = crane_specs.get('asking_price', 0)
        
        if asking_price <= 0:
            return 85  # No asking price, assume good deal for FMV
        
        # Calculate value ratio
        value_ratio = estimated_value / asking_price
        
        # Convert to deal score
        if value_ratio >= 1.3:      # 30%+ undervalued
            return 100
        elif value_ratio >= 1.2:    # 20%+ undervalued
            return 95
        elif value_ratio >= 1.1:    # 10%+ undervalued
            return 85
        elif value_ratio >= 1.0:    # Fair value
            return 75
        elif value_ratio >= 0.9:    # 10% overvalued
            return 60
        elif value_ratio >= 0.8:    # 20% overvalued
            return 40
        else:                       # 20%+ overvalued
            return 20
    
    def _calculate_wear_score(self, crane_specs: Dict[str, Any]) -> float:
        """Calculate wear score (0-100)"""
        age = 2025 - crane_specs.get('year', 2020)
        hours = crane_specs.get('hours', 0)
        capacity = crane_specs.get('capacity', 100)
        
        # Base wear score calculation
        age_factor = max(0, 100 - (age * 3))  # 3 points per year
        
        if hours > 0:
            # Expected hours per year
            expected_hours = age * 800
            if expected_hours > 0:
                hours_factor = max(0, 100 - ((hours / expected_hours - 1) * 50))
            else:
                hours_factor = 95  # New crane with low hours
        else:
            hours_factor = 80  # Unknown hours penalty
        
        # Capacity factor (larger cranes typically better maintained)
        if capacity >= 300:
            capacity_factor = 5
        elif capacity >= 150:
            capacity_factor = 3
        else:
            capacity_factor = 0
        
        wear_score = (age_factor * 0.6 + hours_factor * 0.4) + capacity_factor
        
        return min(100, max(0, wear_score))
    
    def _generate_financing_scenarios(self, crane_specs: Dict[str, Any], estimated_value: float) -> Dict[str, Any]:
        """Generate financing scenarios by region"""
        scenarios = {}
        
        if self.rental_rates.empty:
            return scenarios
        
        crane_type = self._determine_crane_type(crane_specs)
        capacity = crane_specs.get('capacity', 100)
        
        # Find matching rental rates
        matching_rates = self.rental_rates[
            (self.rental_rates['Crane Type'].str.contains(crane_type.replace('_', ' '), case=False, na=False)) |
            (self.rental_rates['Tonnage'] >= capacity * 0.8) & 
            (self.rental_rates['Tonnage'] <= capacity * 1.2)
        ]
        
        if matching_rates.empty:
            return scenarios
        
        # Generate scenarios by region
        for region in matching_rates['Region'].unique():
            region_rates = matching_rates[matching_rates['Region'] == region]
            if not region_rates.empty:
                monthly_rate = region_rates['Monthly Rate (USD)'].mean()
                
                scenarios[region] = {
                    'monthly_rental_rate': monthly_rate,
                    'annual_rental_income': monthly_rate * 12,
                    'purchase_price': estimated_value,
                    'payback_period_years': estimated_value / (monthly_rate * 12) if monthly_rate > 0 else 0,
                    'roi_percentage': ((monthly_rate * 12) / estimated_value * 100) if estimated_value > 0 else 0
                }
        
        return scenarios
    
    def _calculate_confidence_score(self, crane_specs: Dict[str, Any]) -> int:
        """Calculate confidence score based on data availability"""
        confidence = 50  # Base confidence
        
        # Add confidence for each data source available
        if not self.crane_listings.empty:
            confidence += 15
        
        if not self.rental_rates.empty:
            confidence += 10
        
        if not self.buying_trends.empty:
            confidence += 10
        
        if self.spec_catalog:
            confidence += 10
        
        # Add confidence for complete crane specs
        if crane_specs.get('year', 0) > 0:
            confidence += 5
        if crane_specs.get('hours', 0) > 0:
            confidence += 5
        if crane_specs.get('capacity', 0) > 0:
            confidence += 5
        if crane_specs.get('manufacturer', ''):
            confidence += 5
        
        return min(100, confidence)
    
    def _parse_percentage(self, value: str) -> float:
        """Parse percentage string to float"""
        try:
            return float(value.replace('%', '')) / 100
        except:
            return 0.0

# Global enhanced valuation engine instance
enhanced_valuation_engine = EnhancedValuationEngine()
