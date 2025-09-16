"""
Enhanced Valuation Algorithm with Comprehensive Data Integration
Incorporates buying trends, broker networks, performance comparisons, and market intelligence
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from logger import get_logger

logger = get_logger("enhanced_valuation")

class EnhancedValuationAlgorithm:
    """
    Enhanced valuation algorithm that incorporates:
    - MARCS depreciation curves
    - Market buying trends
    - Broker network intelligence
    - Performance comparison metrics
    - Regional market factors
    - Real transaction data
    """
    
    def __init__(self):
        self.logger = logger
        self.buying_trends = self._load_buying_trends()
        self.broker_networks = self._load_broker_networks()
        self.performance_metrics = self._load_performance_metrics()
        self.market_intelligence = self._load_market_intelligence()
        
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
            }
        }
        
        # Regional market multipliers
        self.regional_multipliers = {
            'northeast_us': 1.15,     # High demand, infrastructure projects
            'southeast_us': 1.05,     # Moderate demand
            'gulf_coast': 1.20,       # Energy sector premium
            'west_coast': 1.25,       # High cost of living, regulations
            'midwest': 0.95,          # Lower cost base
            'canada': 1.10            # Currency and import factors
        }
        
        logger.info("enhanced_valuation_init", "Enhanced valuation algorithm initialized")
    
    def _load_buying_trends(self) -> Dict[str, Any]:
        """Load and process buying trends data"""
        try:
            # Load buying trends from CSV
            trends_df = pd.read_csv('/home/ubuntu/upload/Valuation_Engine_-_Buying_Trends.csv')
            
            trends = {}
            for _, row in trends_df.iterrows():
                segment = row.get('Market Segment', '').lower().replace(' ', '_')
                trends[segment] = {
                    'growth_rate': self._parse_percentage(row.get('YoY Growth', '0%')),
                    'demand_drivers': row.get('Key Demand Drivers', '').split(', '),
                    'price_trend': row.get('Price Trend', 'stable').lower(),
                    'market_size': row.get('Market Size', 'medium').lower()
                }
            
            logger.info("_load_buying_trends", "Buying trends loaded", segments=len(trends))
            return trends
            
        except Exception as e:
            logger.error("_load_buying_trends", "Failed to load buying trends", error=e)
            return {}
    
    def _load_broker_networks(self) -> Dict[str, Any]:
        """Load and process broker network data"""
        try:
            broker_data = {}
            
            # Load LLoma broker list
            try:
                lloma_df = pd.read_excel('/home/ubuntu/upload/LLomaBrokerListFinal5-21.xlsx')
                broker_data['lloma'] = self._process_broker_data(lloma_df, 'LLoma')
            except Exception as e:
                logger.warning("_load_broker_networks", "Could not load LLoma data", error=e)
            
            # Load CPP broker list
            try:
                cpp_df = pd.read_excel('/home/ubuntu/upload/CPPBrokerList6-6-25.xlsx')
                broker_data['cpp'] = self._process_broker_data(cpp_df, 'CPP')
            except Exception as e:
                logger.warning("_load_broker_networks", "Could not load CPP data", error=e)
            
            logger.info("_load_broker_networks", "Broker networks loaded", networks=len(broker_data))
            return broker_data
            
        except Exception as e:
            logger.error("_load_broker_networks", "Failed to load broker networks", error=e)
            return {}
    
    def _process_broker_data(self, df: pd.DataFrame, source: str) -> Dict[str, Any]:
        """Process broker data into standardized format"""
        processed = {
            'source': source,
            'listings': [],
            'avg_price': 0,
            'price_range': {'min': 0, 'max': 0},
            'capacity_range': {'min': 0, 'max': 0}
        }
        
        prices = []
        capacities = []
        
        for _, row in df.iterrows():
            listing = {
                'manufacturer': row.get('Manufacturer', '').strip(),
                'model': row.get('Model', '').strip(),
                'year': self._parse_year(row.get('Year', 0)),
                'capacity': self._parse_capacity(row.get('Capacity', 0)),
                'price': self._parse_price(row.get('Price', 0)),
                'location': row.get('Location', '').strip(),
                'features': row.get('Key Features', '').strip()
            }
            
            if listing['price'] > 0:
                prices.append(listing['price'])
            if listing['capacity'] > 0:
                capacities.append(listing['capacity'])
            
            processed['listings'].append(listing)
        
        # Calculate statistics
        if prices:
            processed['avg_price'] = np.mean(prices)
            processed['price_range'] = {'min': min(prices), 'max': max(prices)}
        
        if capacities:
            processed['capacity_range'] = {'min': min(capacities), 'max': max(capacities)}
        
        return processed
    
    def _load_performance_metrics(self) -> Dict[str, Any]:
        """Load performance comparison metrics from charts"""
        # Based on the performance comparison charts provided
        performance_data = {
            'grove_gmk4100l': {
                'max_capacity': 100,
                'working_radius_40ft': 50,
                'working_radius_80ft': 18,
                'mobility_score': 0.9,
                'versatility_score': 0.8,
                'boom_utilization': 0.85
            },
            'liebherr_ltm1070_4_2': {
                'max_capacity': 70,
                'working_radius_40ft': 35,
                'working_radius_80ft': 12,
                'mobility_score': 0.85,
                'versatility_score': 0.7,
                'boom_utilization': 0.75
            },
            'tadano_ac4_080_1': {
                'max_capacity': 80,
                'working_radius_40ft': 40,
                'working_radius_80ft': 15,
                'mobility_score': 0.8,
                'versatility_score': 0.75,
                'boom_utilization': 0.8
            }
        }
        
        logger.info("_load_performance_metrics", "Performance metrics loaded", models=len(performance_data))
        return performance_data
    
    def _load_market_intelligence(self) -> Dict[str, Any]:
        """Load market intelligence from merged sales data"""
        try:
            sales_df = pd.read_csv('/home/ubuntu/upload/merged_crane_sales.csv')
            
            intelligence = {
                'total_transactions': len(sales_df),
                'avg_transaction_value': 0,
                'price_trends': {},
                'volume_trends': {},
                'seasonal_patterns': {}
            }
            
            # Calculate average transaction value
            if 'price' in sales_df.columns:
                prices = pd.to_numeric(sales_df['price'], errors='coerce').dropna()
                if len(prices) > 0:
                    intelligence['avg_transaction_value'] = prices.mean()
            
            # Analyze price trends by manufacturer
            if 'manufacturer' in sales_df.columns and 'price' in sales_df.columns:
                for manufacturer in sales_df['manufacturer'].unique():
                    if pd.notna(manufacturer):
                        mfg_data = sales_df[sales_df['manufacturer'] == manufacturer]
                        mfg_prices = pd.to_numeric(mfg_data['price'], errors='coerce').dropna()
                        if len(mfg_prices) > 0:
                            intelligence['price_trends'][manufacturer] = {
                                'avg_price': mfg_prices.mean(),
                                'price_range': {'min': mfg_prices.min(), 'max': mfg_prices.max()},
                                'transaction_count': len(mfg_prices)
                            }
            
            logger.info("_load_market_intelligence", "Market intelligence loaded", 
                       transactions=intelligence['total_transactions'])
            return intelligence
            
        except Exception as e:
            logger.error("_load_market_intelligence", "Failed to load market intelligence", error=e)
            return {}
    
    def calculate_enhanced_valuation(self, crane_specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate enhanced valuation using all available data sources
        """
        logger.info("calculate_enhanced_valuation", "Starting enhanced valuation", 
                   model=crane_specs.get('model', 'Unknown'))
        
        # Base MARCS depreciation calculation
        base_valuation = self._calculate_base_marcs_valuation(crane_specs)
        
        # Apply market trend adjustments
        trend_adjustment = self._calculate_trend_adjustment(crane_specs)
        
        # Apply broker network intelligence
        broker_adjustment = self._calculate_broker_adjustment(crane_specs)
        
        # Apply performance metrics
        performance_adjustment = self._calculate_performance_adjustment(crane_specs)
        
        # Apply regional factors
        regional_adjustment = self._calculate_regional_adjustment(crane_specs)
        
        # Apply market intelligence
        market_adjustment = self._calculate_market_intelligence_adjustment(crane_specs)
        
        # Calculate final valuation
        final_valuation = base_valuation * (1 + trend_adjustment + broker_adjustment + 
                                          performance_adjustment + regional_adjustment + 
                                          market_adjustment)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(crane_specs)
        
        # Generate valuation breakdown
        valuation_breakdown = {
            'base_marcs_valuation': base_valuation,
            'trend_adjustment': trend_adjustment,
            'broker_adjustment': broker_adjustment,
            'performance_adjustment': performance_adjustment,
            'regional_adjustment': regional_adjustment,
            'market_adjustment': market_adjustment,
            'final_valuation': final_valuation,
            'confidence_score': confidence_score
        }
        
        # Calculate multiple valuation types
        valuation_types = self._calculate_multiple_valuation_types(final_valuation)
        
        # Find enhanced comparables
        comparables = self._find_enhanced_comparables(crane_specs)
        
        result = {
            'estimated_value': final_valuation,
            'confidence_score': confidence_score,
            'valuation_breakdown': valuation_breakdown,
            'valuation_types': valuation_types,
            'comparables': comparables,
            'market_insights': self._generate_market_insights(crane_specs),
            'deal_score': self._calculate_deal_score(crane_specs, final_valuation),
            'wear_score': self._calculate_enhanced_wear_score(crane_specs)
        }
        
        logger.info("calculate_enhanced_valuation", "Enhanced valuation complete", 
                   final_value=final_valuation, confidence=confidence_score)
        
        return result
    
    def _calculate_base_marcs_valuation(self, crane_specs: Dict[str, Any]) -> float:
        """Calculate base MARCS depreciation valuation"""
        # Get new unit cost estimate
        new_unit_cost = self._estimate_new_unit_cost(crane_specs)
        
        # Calculate age-based depreciation
        age = 2025 - crane_specs.get('year', 2020)
        crane_type = crane_specs.get('crane_type', 'all_terrain').lower().replace(' ', '_')
        
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
        crane_type = crane_specs.get('crane_type', 'all_terrain').lower()
        manufacturer = crane_specs.get('manufacturer', '').lower()
        
        # Base cost per ton by type
        base_costs = {
            'all_terrain': 12000,  # $12k per ton
            'crawler': 15000,      # $15k per ton (more complex)
            'tower': 8000,         # $8k per ton
            'rough_terrain': 8000, # $8k per ton
            'carry_deck': 6000     # $6k per ton
        }
        
        base_cost_per_ton = base_costs.get(crane_type, 12000)
        
        # Manufacturer premium/discount
        manufacturer_multipliers = {
            'liebherr': 1.15,    # Premium brand
            'grove': 1.05,       # Solid brand
            'manitowoc': 1.10,   # Premium brand
            'terex': 0.95,       # Value brand
            'link-belt': 1.00,   # Standard
            'tadano': 1.08,      # Quality brand
            'national': 0.90     # Value brand
        }
        
        manufacturer_multiplier = manufacturer_multipliers.get(manufacturer, 1.0)
        
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
        capacity = crane_specs.get('capacity', 100)
        crane_type = crane_specs.get('crane_type', 'all_terrain').lower()
        
        # Map to trend segments
        if crane_type == 'crawler' and capacity >= 300:
            segment = '300t+_crawler_cranes'
        elif crane_type == 'all_terrain' and 70 <= capacity <= 120:
            segment = '70-120t_all-terrain'
        elif crane_type == 'tower':
            segment = 'refurbished_tower_cranes'
        elif crane_type == 'all_terrain' and 90 <= capacity <= 200:
            segment = 'used_90-200t_at'
        else:
            segment = 'general_market'
        
        # Get trend data
        trend_data = self.buying_trends.get(segment, {})
        growth_rate = trend_data.get('growth_rate', 0)
        
        # Convert growth rate to valuation adjustment
        # High growth = higher values
        if growth_rate > 0.15:      # >15% growth
            return 0.10             # 10% premium
        elif growth_rate > 0.10:    # >10% growth
            return 0.05             # 5% premium
        elif growth_rate > 0.05:    # >5% growth
            return 0.02             # 2% premium
        elif growth_rate < -0.05:   # Declining market
            return -0.05            # 5% discount
        else:
            return 0.0              # No adjustment
    
    def _calculate_broker_adjustment(self, crane_specs: Dict[str, Any]) -> float:
        """Calculate adjustment based on broker network data"""
        model = crane_specs.get('model', '').lower()
        manufacturer = crane_specs.get('manufacturer', '').lower()
        capacity = crane_specs.get('capacity', 100)
        
        # Find similar cranes in broker networks
        similar_listings = []
        
        for network_name, network_data in self.broker_networks.items():
            for listing in network_data.get('listings', []):
                # Check similarity
                if (listing.get('manufacturer', '').lower() == manufacturer or
                    listing.get('model', '').lower() == model or
                    abs(listing.get('capacity', 0) - capacity) <= capacity * 0.2):
                    similar_listings.append(listing)
        
        if not similar_listings:
            return 0.0  # No broker data available
        
        # Calculate average broker premium/discount
        broker_prices = [l['price'] for l in similar_listings if l['price'] > 0]
        
        if not broker_prices:
            return 0.0
        
        avg_broker_price = np.mean(broker_prices)
        
        # Compare to estimated market value (simplified)
        estimated_market_value = self._estimate_new_unit_cost(crane_specs) * 0.7  # Rough estimate
        
        if estimated_market_value > 0:
            broker_premium = (avg_broker_price - estimated_market_value) / estimated_market_value
            # Cap adjustment at ±10%
            return max(-0.10, min(0.10, broker_premium))
        
        return 0.0
    
    def _calculate_performance_adjustment(self, crane_specs: Dict[str, Any]) -> float:
        """Calculate adjustment based on performance metrics"""
        model = crane_specs.get('model', '').lower()
        manufacturer = crane_specs.get('manufacturer', '').lower()
        
        # Create model key
        model_key = f"{manufacturer}_{model}".replace(' ', '_').replace('-', '_')
        
        # Find performance data
        performance_data = None
        for key, data in self.performance_metrics.items():
            if key in model_key or model_key in key:
                performance_data = data
                break
        
        if not performance_data:
            return 0.0  # No performance data available
        
        # Calculate performance score
        mobility = performance_data.get('mobility_score', 0.5)
        versatility = performance_data.get('versatility_score', 0.5)
        boom_utilization = performance_data.get('boom_utilization', 0.5)
        
        # Weighted performance score
        performance_score = (mobility * 0.3 + versatility * 0.3 + boom_utilization * 0.4)
        
        # Convert to adjustment
        if performance_score > 0.85:
            return 0.08     # 8% premium for excellent performance
        elif performance_score > 0.75:
            return 0.04     # 4% premium for good performance
        elif performance_score < 0.60:
            return -0.04    # 4% discount for poor performance
        else:
            return 0.0      # No adjustment for average performance
    
    def _calculate_regional_adjustment(self, crane_specs: Dict[str, Any]) -> float:
        """Calculate adjustment based on regional factors"""
        location = crane_specs.get('location', '').lower()
        
        # Map location to region
        region = 'midwest'  # Default
        
        if any(state in location for state in ['ny', 'nj', 'pa', 'ct', 'ma', 'me', 'nh', 'vt', 'ri']):
            region = 'northeast_us'
        elif any(state in location for state in ['fl', 'ga', 'sc', 'nc', 'va', 'tn', 'ky', 'al', 'ms']):
            region = 'southeast_us'
        elif any(state in location for state in ['tx', 'la', 'ok', 'ar']):
            region = 'gulf_coast'
        elif any(state in location for state in ['ca', 'or', 'wa', 'nv', 'az']):
            region = 'west_coast'
        elif 'canada' in location or 'ca' in location:
            region = 'canada'
        
        # Get regional multiplier
        multiplier = self.regional_multipliers.get(region, 1.0)
        
        # Convert to adjustment (multiplier - 1)
        return multiplier - 1.0
    
    def _calculate_market_intelligence_adjustment(self, crane_specs: Dict[str, Any]) -> float:
        """Calculate adjustment based on market intelligence"""
        manufacturer = crane_specs.get('manufacturer', '').lower()
        
        # Get manufacturer price trends
        price_trends = self.market_intelligence.get('price_trends', {})
        manufacturer_data = price_trends.get(manufacturer, {})
        
        if not manufacturer_data:
            return 0.0
        
        # Compare to overall market average
        overall_avg = self.market_intelligence.get('avg_transaction_value', 0)
        manufacturer_avg = manufacturer_data.get('avg_price', 0)
        
        if overall_avg > 0 and manufacturer_avg > 0:
            price_premium = (manufacturer_avg - overall_avg) / overall_avg
            # Cap adjustment at ±5%
            return max(-0.05, min(0.05, price_premium))
        
        return 0.0
    
    def _calculate_confidence_score(self, crane_specs: Dict[str, Any]) -> int:
        """Calculate confidence score based on data availability"""
        confidence = 50  # Base confidence
        
        # Add confidence for each data source available
        if self.buying_trends:
            confidence += 10
        
        if self.broker_networks:
            confidence += 15
        
        if self.performance_metrics:
            confidence += 10
        
        if self.market_intelligence:
            confidence += 15
        
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
    
    def _calculate_multiple_valuation_types(self, base_value: float) -> Dict[str, float]:
        """Calculate multiple valuation types"""
        return {
            'fair_market_value': base_value,
            'orderly_liquidation_value': base_value * 0.65,
            'forced_liquidation_value': base_value * 0.45,
            'net_orderly_liquidation': base_value * 0.65 * 0.85,
            'net_forced_liquidation': base_value * 0.45 * 0.85,
            'insurance_replacement': base_value * 1.15
        }
    
    def _find_enhanced_comparables(self, crane_specs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find enhanced comparables using all data sources"""
        comparables = []
        
        # Search broker networks
        for network_name, network_data in self.broker_networks.items():
            for listing in network_data.get('listings', []):
                similarity = self._calculate_similarity(crane_specs, listing)
                if similarity > 0.6:  # 60% similarity threshold
                    comparable = listing.copy()
                    comparable['similarity_score'] = similarity * 100
                    comparable['data_source'] = f"broker_{network_name}"
                    comparables.append(comparable)
        
        # Sort by similarity
        comparables.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        return comparables[:10]  # Return top 10
    
    def _calculate_similarity(self, crane_specs: Dict[str, Any], listing: Dict[str, Any]) -> float:
        """Calculate similarity score between crane specs and listing"""
        score = 0.0
        
        # Manufacturer match (30%)
        if (crane_specs.get('manufacturer', '').lower() == 
            listing.get('manufacturer', '').lower()):
            score += 0.30
        
        # Model match (20%)
        if (crane_specs.get('model', '').lower() == 
            listing.get('model', '').lower()):
            score += 0.20
        
        # Capacity similarity (30%)
        crane_capacity = crane_specs.get('capacity', 0)
        listing_capacity = listing.get('capacity', 0)
        if crane_capacity > 0 and listing_capacity > 0:
            capacity_diff = abs(crane_capacity - listing_capacity) / crane_capacity
            if capacity_diff <= 0.2:  # Within 20%
                score += 0.30 * (1 - capacity_diff / 0.2)
        
        # Year similarity (20%)
        crane_year = crane_specs.get('year', 0)
        listing_year = listing.get('year', 0)
        if crane_year > 0 and listing_year > 0:
            year_diff = abs(crane_year - listing_year)
            if year_diff <= 5:  # Within 5 years
                score += 0.20 * (1 - year_diff / 5)
        
        return score
    
    def _generate_market_insights(self, crane_specs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate market insights based on all data"""
        insights = {
            'market_trend': 'stable',
            'demand_outlook': 'moderate',
            'price_direction': 'stable',
            'key_factors': []
        }
        
        # Analyze buying trends
        capacity = crane_specs.get('capacity', 100)
        crane_type = crane_specs.get('crane_type', 'all_terrain').lower()
        
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
        location = crane_specs.get('location', '').lower()
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
    
    def _calculate_enhanced_wear_score(self, crane_specs: Dict[str, Any]) -> float:
        """Calculate enhanced wear score"""
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
    
    # Utility methods
    def _parse_percentage(self, value: str) -> float:
        """Parse percentage string to float"""
        try:
            return float(value.replace('%', '')) / 100
        except:
            return 0.0
    
    def _parse_year(self, value) -> int:
        """Parse year value"""
        try:
            return int(value)
        except:
            return 0
    
    def _parse_capacity(self, value) -> float:
        """Parse capacity value"""
        try:
            if isinstance(value, str):
                # Remove 't', 'ton', 'tons' etc.
                value = value.lower().replace('t', '').replace('on', '').replace('s', '').strip()
            return float(value)
        except:
            return 0.0
    
    def _parse_price(self, value) -> float:
        """Parse price value"""
        try:
            if isinstance(value, str):
                # Remove currency symbols and commas
                value = value.replace('$', '').replace(',', '').strip()
            return float(value)
        except:
            return 0.0

# Global enhanced valuation algorithm instance
enhanced_valuation_algorithm = EnhancedValuationAlgorithm()

