"""
Comprehensive Valuation Engine for Crane Intelligence Platform
Bloomberg-style analysis with all data sources integrated
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
from .data_loader import data_loader

logger = logging.getLogger(__name__)

class ComprehensiveValuationEngine:
    """
    Comprehensive Bloomberg-style valuation engine that delivers:
    - Fair market valuation with wholesale/retail ranges
    - Automatic comparable units from live listings and sales
    - Market context from weekly trend data
    - Financing scenarios by region
    - Professional deal scoring and wear analysis
    """
    
    def __init__(self):
        self.logger = logger
        self.data_loader = data_loader
        
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
        
        logger.info("Comprehensive valuation engine initialized")
    
    def calculate_valuation(self, crane_specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive Bloomberg-style valuation
        """
        logger.info(f"Starting valuation for {crane_specs.get('manufacturer', 'Unknown')} {crane_specs.get('model', 'Unknown')}")
        
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
            
            logger.info(f"Valuation completed: ${final_valuation:,.0f} (confidence: {confidence_score}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"Valuation calculation failed: {e}")
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
        year = crane_specs.get('year', 2020) or 2020  # Ensure year is not None
        age = 2025 - year
        if age is None or age < 0:
            age = 0  # Handle invalid age
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
        hours = crane_specs.get('hours', 0) or 0  # Ensure hours is not None
        hours_adjustment = self._calculate_hours_adjustment(hours, age)
        
        return base_value * (1 + hours_adjustment)
    
    def _estimate_new_unit_cost(self, crane_specs: Dict[str, Any]) -> float:
        """Estimate new unit cost based on capacity and type"""
        capacity = crane_specs.get('capacity', 100) or 100
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
        if any(indicator in model for indicator in ['ltm', 'at', 'all-terrain', 'gmk']):
            return 'all_terrain'
        
        # Crawler indicators
        if any(indicator in model for indicator in ['cc', 'crawler', 'lr', 'mlc']):
            return 'crawler'
        
        # Tower indicators
        if any(indicator in model for indicator in ['tower', 'tt', 'ct']):
            return 'tower'
        
        # Rough terrain indicators
        if any(indicator in model for indicator in ['rt', 'rough-terrain']):
            return 'rough_terrain'
        
        # Default based on capacity
        capacity = crane_specs.get('capacity', 100) or 100
        if capacity >= 200:
            return 'crawler'
        elif capacity >= 100:
            return 'all_terrain'
        else:
            return 'rough_terrain'
    
    def _calculate_hours_adjustment(self, hours: int, age: int) -> float:
        """Calculate adjustment based on operating hours"""
        # Handle None, invalid hours, or non-numeric values
        try:
            hours = int(hours) if hours is not None else 0
        except (ValueError, TypeError):
            hours = 0
            
        if hours <= 0:
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
        # For now, return a small positive adjustment
        # In production, this would use the buying trends data
        return 0.02  # 2% premium for current market trends
    
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
        # Use actual market data from listings
        crane_listings = self.data_loader.get_crane_listings()
        if crane_listings.empty:
            return 0.0
        
        manufacturer = crane_specs.get('manufacturer', '').lower()
        model = crane_specs.get('model', '').lower()
        
        # Find similar listings
        similar_listings = crane_listings[
            (crane_listings['manufacturer'].str.lower() == manufacturer) |
            (crane_listings['title'].str.lower().str.contains(model, na=False))
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
        manufacturer = crane_specs.get('manufacturer', '')
        model = crane_specs.get('model', '')
        capacity = crane_specs.get('capacity', 100) or 100
        year = crane_specs.get('year', 2020) or 2020
        
        return self.data_loader.find_comparables(manufacturer, model, capacity, year, limit=10)
    
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
        capacity = crane_specs.get('capacity', 100) or 100
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
        asking_price = crane_specs.get('asking_price', 0) or 0
        
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
        year = crane_specs.get('year', 2020) or 2020  # Ensure year is not None
        age = 2025 - year
        if age is None or age < 0:
            age = 0  # Handle invalid age
        hours = crane_specs.get('hours', 0) or 0  # Ensure hours is not None
        capacity = crane_specs.get('capacity', 100) or 100  # Ensure capacity is not None
        
        # Base wear score calculation
        age_factor = max(0, 100 - (age * 3))  # 3 points per year
        
        if hours and hours > 0:
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
        crane_type = self._determine_crane_type(crane_specs)
        capacity = crane_specs.get('capacity', 100) or 100
        
        # Get rental scenarios from data loader
        rental_scenarios = self.data_loader.get_rental_scenarios(crane_type, capacity)
        
        scenarios = {}
        for region, rental_data in rental_scenarios.items():
            monthly_rate = rental_data.get('monthly_rental_rate', 0)
            
            if monthly_rate > 0:
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
        if not self.data_loader.get_crane_listings().empty:
            confidence += 15
        
        if not self.data_loader.get_rental_rates().empty:
            confidence += 10
        
        if not self.data_loader.get_buying_trends().empty:
            confidence += 10
        
        # Add confidence for complete crane specs
        year = crane_specs.get('year', 0) or 0
        if year > 0:
            confidence += 5
        hours = crane_specs.get('hours', 0) or 0
        if hours > 0:
            confidence += 5
        capacity = crane_specs.get('capacity', 0) or 0
        if capacity > 0:
            confidence += 5
        if crane_specs.get('manufacturer', ''):
            confidence += 5
        
        return min(100, confidence)

# Global comprehensive valuation engine instance
comprehensive_valuation_engine = ComprehensiveValuationEngine()
