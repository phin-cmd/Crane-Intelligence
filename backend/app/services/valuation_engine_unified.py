"""
Unified Valuation Engine for Crane Intelligence Platform
Consolidates: valuation_engine.py, comprehensive_valuation_engine.py, enhanced_valuation_engine.py
Provides all valuation capabilities in a single, maintainable module
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import math
import logging
import asyncio
import numpy as np
from .data_loader import data_loader
from .real_time_market_data import RealTimeMarketDataService

logger = logging.getLogger(__name__)

# ==================== DATA CLASSES ====================

@dataclass
class CraneSpecs:
    """Crane specifications for valuation"""
    manufacturer: str
    model: str
    year: int
    capacity_tons: float
    hours: int
    condition_score: float  # 0.0 to 1.0
    region: str
    price: Optional[float] = None
    location: Optional[str] = None
    boom_length_ft: Optional[float] = None
    jib_length_ft: Optional[float] = None
    counterweight_lbs: Optional[float] = None
    features: Optional[List[str]] = None


@dataclass
class ValuationResult:
    """Complete valuation result - unified format"""
    fair_market_value: float
    wholesale_value: Optional[float] = None
    retail_value: Optional[float] = None
    deal_score: int = 0  # 0-100
    confidence_score: float = 0.0  # 0.0-1.0
    risk_factors: List[str] = None
    recommendations: List[str] = None
    market_position: str = ""
    depreciation_rate: float = 0.0
    hours_analysis: Dict[str, Any] = None
    comparable_analysis: Dict[str, Any] = None
    financial_metrics: Dict[str, Any] = None
    market_trends: Dict[str, Any] = None
    financing_scenarios: List[Dict[str, Any]] = None
    comparable_sales: List[Dict[str, Any]] = None
    wear_score: Optional[float] = None
    valuation_ranges: Dict[str, float] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.risk_factors is None:
            self.risk_factors = []
        if self.recommendations is None:
            self.recommendations = []
        if self.hours_analysis is None:
            self.hours_analysis = {}
        if self.comparable_analysis is None:
            self.comparable_analysis = {}
        if self.financial_metrics is None:
            self.financial_metrics = {}
        if self.market_trends is None:
            self.market_trends = {}
        if self.financing_scenarios is None:
            self.financing_scenarios = []
        if self.comparable_sales is None:
            self.comparable_sales = []
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.wholesale_value is None:
            self.wholesale_value = self.fair_market_value * 0.75
        if self.retail_value is None:
            self.retail_value = self.fair_market_value * 1.15
        if self.valuation_ranges is None:
            self.valuation_ranges = {
                'wholesale_value': self.wholesale_value,
                'fair_market_value': self.fair_market_value,
                'retail_value': self.retail_value,
                'orderly_liquidation_value': self.fair_market_value * 0.65,
                'forced_liquidation_value': self.fair_market_value * 0.45,
                'insurance_replacement_value': self.fair_market_value * 1.25
            }


# ==================== UNIFIED VALUATION ENGINE ====================

class UnifiedValuationEngine:
    """
    Unified professional-grade crane valuation engine
    Combines features from all three previous engines:
    - Core valuation algorithms
    - Bloomberg-style comprehensive analysis
    - Real-time market data integration
    """
    
    def __init__(self, use_real_time_data: bool = True):
        self.use_real_time_data = use_real_time_data
        self.real_time_service = None
        
        if use_real_time_data:
            try:
                self.real_time_service = RealTimeMarketDataService()
            except Exception as e:
                logger.warning(f"Real-time market data service not available: {e}")
                self.use_real_time_data = False
        
        # Manufacturer premium factors (from core engine)
        self.manufacturer_premiums = {
            'Liebherr': 1.15, 'liebherr': 1.15,
            'Grove': 1.10, 'grove': 1.10,
            'Tadano': 1.08, 'tadano': 1.08,
            'Manitowoc': 1.05, 'manitowoc': 1.05,
            'Terex': 1.02, 'terex': 1.02,
            'Link-Belt': 1.00, 'link-belt': 1.00,
            'Demag': 1.12, 'demag': 1.12,
            'Kato': 1.03, 'kato': 1.03,
            'National': 0.90, 'national': 0.90,
            'default': 1.00
        }
        
        # Regional market adjustments (combined from all engines)
        self.regional_adjustments = {
            'TX': 1.05, 'CA': 1.08, 'NY': 1.06, 'FL': 1.03,
            'northeast': 1.15, 'southeast': 1.05, 'gulf_coast': 1.20,
            'west_coast': 1.25, 'midwest': 0.95, 'canada': 1.10,
            'default': 1.00
        }
        
        # Base capacity pricing (per ton)
        self.base_capacity_price = 12000
        
        # Depreciation curves by age (from core engine)
        self.depreciation_curves = {
            'new': 1.00,      # 0-2 years
            'young': 0.85,    # 3-5 years
            'mid': 0.70,      # 6-10 years
            'mature': 0.50,   # 11-15 years
            'old': 0.35,      # 16-20 years
            'vintage': 0.25   # 20+ years
        }
        
        # Enhanced depreciation curves by crane type (from comprehensive engine)
        self.type_depreciation_curves = {
            'all_terrain': {
                'years_0_3': 0.08, 'years_4_7': 0.12,
                'years_8_15': 0.15, 'years_15_plus': 0.05
            },
            'crawler': {
                'years_0_3': 0.06, 'years_4_7': 0.10,
                'years_8_15': 0.12, 'years_15_plus': 0.04
            },
            'tower': {
                'years_0_3': 0.10, 'years_4_7': 0.15,
                'years_8_15': 0.18, 'years_15_plus': 0.08
            },
            'rough_terrain': {
                'years_0_3': 0.10, 'years_4_7': 0.14,
                'years_8_15': 0.16, 'years_15_plus': 0.06
            }
        }
        
        logger.info("Unified valuation engine initialized")
    
    # ==================== MAIN VALUATION METHODS ====================
    
    def value_crane(self, specs: CraneSpecs) -> ValuationResult:
        """
        Main synchronous valuation method - comprehensive analysis
        Maintains backward compatibility with existing code
        """
        return self._value_crane_sync(specs)
    
    async def value_crane_async(self, specs: CraneSpecs) -> ValuationResult:
        """
        Async valuation method with real-time market data integration
        """
        # 1. Calculate base value
        base_value = self._calculate_base_value(specs)
        
        # 2. Apply depreciation
        depreciation_rate = self._calculate_depreciation_rate(specs.year, specs)
        age_adjusted_value = base_value * depreciation_rate
        
        # 3. Apply condition adjustments
        condition_adjustment = self._calculate_condition_adjustment(specs.condition_score)
        condition_adjusted_value = age_adjusted_value * condition_adjustment
        
        # 4. Apply hours analysis
        hours_analysis = self._analyze_hours(specs.year, specs.hours)
        hours_adjusted_value = condition_adjusted_value * hours_analysis['adjustment_factor']
        
        # 5. Apply market adjustments
        market_adjustment = self._calculate_market_adjustment(specs.manufacturer, specs.region)
        base_fmv = hours_adjusted_value * market_adjustment
        
        # 6. Fetch real-time market data if available
        market_data = {}
        if self.use_real_time_data and self.real_time_service:
            try:
                market_data = await self._fetch_market_data(specs.manufacturer, specs.model)
                # Apply market intelligence adjustments
                if market_data.get('average_price'):
                    market_intelligence_adjustment = self._calculate_market_intelligence_adjustment(
                        base_fmv, market_data
                    )
                    base_fmv *= (1 + market_intelligence_adjustment)
            except Exception as e:
                logger.warning(f"Real-time market data fetch failed: {e}")
        
        # 7. Calculate valuation ranges
        valuation_ranges = self._calculate_valuation_ranges(base_fmv)
        
        # 8. Calculate deal score
        deal_score = self._calculate_deal_score(specs, base_fmv, base_value, market_data)
        
        # 9. Determine market position
        market_position = self._determine_market_position(specs, base_fmv, base_value, market_data)
        
        # 10. Calculate confidence score
        confidence_score = self._calculate_confidence_score(specs, base_fmv, market_data)
        
        # 11. Calculate wear score
        wear_score = self._calculate_wear_score(specs)
        
        # 12. Identify risk factors
        risk_factors = self._identify_risk_factors(specs, base_fmv, base_value)
        
        # 13. Generate recommendations
        recommendations = self._generate_recommendations(deal_score, risk_factors, market_data)
        
        # 14. Calculate financial metrics
        financial_metrics = self._calculate_financial_metrics(specs, base_fmv, base_value)
        
        # 15. Comparable analysis
        comparable_analysis = self._generate_comparable_analysis(specs, base_fmv, market_data)
        comparable_sales = comparable_analysis.get('comparables', [])
        
        # 16. Generate financing scenarios
        financing_scenarios = self._generate_financing_scenarios(specs, base_fmv)
        
        # 17. Extract market trends
        market_trends = market_data.get('trends', {}) if market_data else {}
        
        return ValuationResult(
            fair_market_value=base_fmv,
            wholesale_value=valuation_ranges['wholesale_value'],
            retail_value=valuation_ranges['retail_value'],
            deal_score=deal_score,
            confidence_score=confidence_score,
            risk_factors=risk_factors,
            recommendations=recommendations,
            market_position=market_position,
            depreciation_rate=depreciation_rate,
            hours_analysis=hours_analysis,
            comparable_analysis=comparable_analysis,
            financial_metrics=financial_metrics,
            market_trends=market_trends,
            financing_scenarios=financing_scenarios,
            comparable_sales=comparable_sales,
            wear_score=wear_score,
            valuation_ranges=valuation_ranges
        )
    
    def _value_crane_sync(self, specs: CraneSpecs) -> ValuationResult:
        """Synchronous wrapper for async method"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.value_crane_async(specs))
    
    # ==================== CALCULATION METHODS ====================
    
    def _calculate_base_value(self, specs: CraneSpecs) -> float:
        """Calculate base value based on capacity and manufacturer"""
        base_value = specs.capacity_tons * self.base_capacity_price
        
        # Apply manufacturer premium
        manufacturer_premium = self.manufacturer_premiums.get(
            specs.manufacturer,
            self.manufacturer_premiums.get(
                specs.manufacturer.lower(),
                self.manufacturer_premiums['default']
            )
        )
        
        return base_value * manufacturer_premium
    
    def _calculate_depreciation_rate(self, year: int, specs: Optional[CraneSpecs] = None) -> float:
        """Calculate depreciation rate based on age and crane type"""
        current_year = datetime.now().year
        age = current_year - year
        
        # Use type-specific depreciation if crane type can be determined
        if specs:
            crane_type = self._determine_crane_type(specs)
            if crane_type in self.type_depreciation_curves:
                curve = self.type_depreciation_curves[crane_type]
                if age <= 3:
                    annual_rate = curve['years_0_3']
                elif age <= 7:
                    annual_rate = curve['years_4_7']
                elif age <= 15:
                    annual_rate = curve['years_8_15']
                else:
                    annual_rate = curve['years_15_plus']
                return (1 - annual_rate) ** age
        
        # Fallback to simple age-based depreciation
        if age <= 2:
            return self.depreciation_curves['new']
        elif age <= 5:
            return self.depreciation_curves['young']
        elif age <= 10:
            return self.depreciation_curves['mid']
        elif age <= 15:
            return self.depreciation_curves['mature']
        elif age <= 20:
            return self.depreciation_curves['old']
        else:
            return self.depreciation_curves['vintage']
    
    def _determine_crane_type(self, specs: CraneSpecs) -> str:
        """Determine crane type from specifications"""
        model = specs.model.lower()
        manufacturer = specs.manufacturer.lower()
        
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
        if specs.capacity_tons >= 200:
            return 'crawler'
        elif specs.capacity_tons >= 100:
            return 'all_terrain'
        else:
            return 'rough_terrain'
    
    def _calculate_condition_adjustment(self, condition_score: float) -> float:
        """Calculate condition adjustment factor"""
        if condition_score >= 0.9:
            return 1.15
        elif condition_score >= 0.8:
            return 1.08
        elif condition_score >= 0.7:
            return 1.00
        elif condition_score >= 0.6:
            return 0.92
        elif condition_score >= 0.5:
            return 0.85
        else:
            return 0.75
    
    def _analyze_hours(self, year: int, hours: int) -> Dict[str, Any]:
        """Analyze hours and calculate adjustment factor"""
        current_year = datetime.now().year
        age = current_year - year
        expected_hours_per_year = 800
        expected_total_hours = age * expected_hours_per_year
        
        hours_ratio = hours / max(expected_total_hours, 1)
        
        if hours_ratio <= 0.7:
            adjustment_factor = 1.15
        elif hours_ratio <= 0.9:
            adjustment_factor = 1.08
        elif hours_ratio <= 1.1:
            adjustment_factor = 1.00
        elif hours_ratio <= 1.3:
            adjustment_factor = 0.92
        elif hours_ratio <= 1.5:
            adjustment_factor = 0.85
        else:
            adjustment_factor = 0.75
        
        return {
            'expected_hours': expected_total_hours,
            'actual_hours': hours,
            'hours_ratio': hours_ratio,
            'adjustment_factor': adjustment_factor,
            'hours_rating': self._get_hours_rating(hours_ratio)
        }
    
    def _get_hours_rating(self, hours_ratio: float) -> str:
        """Get human-readable hours rating"""
        if hours_ratio <= 0.7:
            return "Excellent - Low Hours"
        elif hours_ratio <= 0.9:
            return "Very Good - Below Average"
        elif hours_ratio <= 1.1:
            return "Good - Normal Hours"
        elif hours_ratio <= 1.3:
            return "Fair - Above Average"
        elif hours_ratio <= 1.5:
            return "Poor - High Hours"
        else:
            return "Very Poor - Excessive Hours"
    
    def _calculate_market_adjustment(self, manufacturer: str, region: str) -> float:
        """Calculate market adjustment factor"""
        # Try direct region match first
        regional_factor = self.regional_adjustments.get(region, None)
        
        # If not found, try region mapping
        if regional_factor is None:
            region_lower = region.lower()
            if any(state in region_lower for state in ['northeast', 'ny', 'nj', 'pa', 'ct', 'ma']):
                regional_factor = self.regional_adjustments['northeast']
            elif any(state in region_lower for state in ['southeast', 'fl', 'ga', 'sc', 'nc', 'va']):
                regional_factor = self.regional_adjustments['southeast']
            elif any(state in region_lower for state in ['gulf', 'tx', 'la', 'ok', 'ar']):
                regional_factor = self.regional_adjustments['gulf_coast']
            elif any(state in region_lower for state in ['west', 'ca', 'or', 'wa', 'nv', 'az']):
                regional_factor = self.regional_adjustments['west_coast']
            elif 'canada' in region_lower or 'ca' in region_lower:
                regional_factor = self.regional_adjustments['canada']
            else:
                regional_factor = self.regional_adjustments['default']
        
        return regional_factor
    
    async def _fetch_market_data(self, manufacturer: str, model: str) -> Dict[str, Any]:
        """Fetch real-time market data from multiple sources"""
        if not self.use_real_time_data or not self.real_time_service:
            return {}
        
        try:
            await self.real_time_service.initialize()
            market_data = await self.real_time_service.get_comprehensive_market_data(manufacturer, model)
            
            # Extract and format data
            all_listings = market_data.get('listings', [])
            prices = [listing.get('price', 0) for listing in all_listings if listing.get('price', 0) > 0]
            
            return {
                'listings': all_listings,
                'average_price': np.mean(prices) if prices else 0,
                'price_range': [min(prices), max(prices)] if prices else [0, 0],
                'trends': market_data.get('market_trends', {}),
                'total_listings': len(all_listings),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Market data fetch error: {e}")
            return {}
    
    def _calculate_market_intelligence_adjustment(self, base_fmv: float, market_data: Dict[str, Any]) -> float:
        """Calculate adjustment based on market intelligence"""
        if not market_data or not market_data.get('average_price'):
            return 0.0
        
        market_avg = market_data['average_price']
        if market_avg > 0:
            market_premium = (market_avg - base_fmv) / base_fmv
            return max(-0.10, min(0.10, market_premium))
        
        return 0.0
    
    def _calculate_valuation_ranges(self, base_fmv: float) -> Dict[str, float]:
        """Calculate multiple valuation types"""
        return {
            'wholesale_value': base_fmv * 0.75,
            'fair_market_value': base_fmv,
            'retail_value': base_fmv * 1.15,
            'orderly_liquidation_value': base_fmv * 0.65,
            'forced_liquidation_value': base_fmv * 0.45,
            'insurance_replacement_value': base_fmv * 1.25
        }
    
    def _calculate_deal_score(self, specs: CraneSpecs, final_value: float, base_value: float, 
                            market_data: Dict[str, Any] = None) -> int:
        """Calculate deal score (0-100)"""
        base_score = 50
        
        # Age factor (0-20 points)
        current_year = datetime.now().year
        age = current_year - specs.year
        if age <= 2:
            age_factor = 20
        elif age <= 5:
            age_factor = 15
        elif age <= 10:
            age_factor = 10
        elif age <= 15:
            age_factor = 5
        else:
            age_factor = 0
        
        # Hours factor (0-15 points)
        if specs.hours <= 2000:
            hours_factor = 15
        elif specs.hours <= 5000:
            hours_factor = 12
        elif specs.hours <= 10000:
            hours_factor = 8
        elif specs.hours <= 15000:
            hours_factor = 4
        else:
            hours_factor = 0
        
        # Price factor (0-15 points)
        if specs.price:
            price_ratio = specs.price / final_value
            if price_ratio <= 0.9:
                price_factor = 15
            elif price_ratio <= 0.95:
                price_factor = 12
            elif price_ratio <= 1.05:
                price_factor = 8
            elif price_ratio <= 1.1:
                price_factor = 4
            else:
                price_factor = 0
        else:
            price_factor = 8
        
        # Market data bonus (0-10 points)
        market_factor = 0
        if market_data and market_data.get('average_price'):
            market_avg = market_data['average_price']
            if final_value < market_avg * 0.9:
                market_factor = 10  # Below market
            elif final_value <= market_avg * 1.1:
                market_factor = 5  # At market
        
        deal_score = min(100, base_score + age_factor + hours_factor + price_factor + market_factor)
        return deal_score
    
    def _determine_market_position(self, specs: CraneSpecs, final_value: float, base_value: float,
                                   market_data: Dict[str, Any] = None) -> str:
        """Determine market positioning"""
        if specs.price:
            price_ratio = specs.price / final_value
            if price_ratio <= 0.9:
                return "Excellent - Below Market"
            elif price_ratio <= 0.95:
                return "Very Good - Slightly Below Market"
            elif price_ratio <= 1.05:
                return "Good - At Market"
            elif price_ratio <= 1.1:
                return "Fair - Slightly Above Market"
            else:
                return "Poor - Above Market"
        elif market_data and market_data.get('average_price'):
            market_avg = market_data['average_price']
            if final_value < market_avg * 0.9:
                return "Below Market"
            elif final_value > market_avg * 1.1:
                return "Above Market"
            else:
                return "At Market"
        else:
            return "Good - At Market"
    
    def _calculate_confidence_score(self, specs: CraneSpecs, final_value: float,
                                    market_data: Dict[str, Any] = None) -> float:
        """Calculate confidence score (0.0-1.0)"""
        confidence = 0.7
        
        # Adjust based on data quality
        if specs.condition_score > 0:
            confidence += 0.1
        
        if specs.price:
            confidence += 0.1
        
        if specs.manufacturer in self.manufacturer_premiums or specs.manufacturer.lower() in self.manufacturer_premiums:
            confidence += 0.1
        
        # Market data bonus
        if market_data and market_data.get('total_listings', 0) > 0:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _calculate_wear_score(self, specs: CraneSpecs) -> float:
        """Calculate wear score (0-100)"""
        current_year = datetime.now().year
        age = current_year - specs.year
        age_factor = max(0, 100 - (age * 3))
        
        if specs.hours > 0:
            expected_hours = age * 800
            if expected_hours > 0:
                hours_factor = max(0, 100 - ((specs.hours / expected_hours - 1) * 50))
            else:
                hours_factor = 95
        else:
            hours_factor = 80
        
        if specs.capacity_tons >= 300:
            capacity_factor = 5
        elif specs.capacity_tons >= 150:
            capacity_factor = 3
        else:
            capacity_factor = 0
        
        wear_score = (age_factor * 0.6 + hours_factor * 0.4) + capacity_factor
        return min(100, max(0, wear_score))
    
    def _identify_risk_factors(self, specs: CraneSpecs, final_value: float, base_value: float) -> List[str]:
        """Identify potential risk factors"""
        risk_factors = []
        current_year = datetime.now().year
        age = current_year - specs.year
        
        if age > 20:
            risk_factors.append("Very old equipment - high maintenance risk")
        elif age > 15:
            risk_factors.append("Mature equipment - consider replacement timeline")
        
        if specs.hours > 15000:
            risk_factors.append("High hours - potential wear and tear")
        elif specs.hours > 10000:
            risk_factors.append("Above average hours - monitor condition")
        
        if specs.condition_score < 0.6:
            risk_factors.append("Poor condition - significant repairs may be needed")
        
        if specs.price and specs.price > final_value * 1.1:
            risk_factors.append("Price above market value")
        
        if final_value < base_value * 0.3:
            risk_factors.append("Value significantly below base - investigate thoroughly")
        
        return risk_factors
    
    def _generate_recommendations(self, deal_score: int, risk_factors: List[str],
                                 market_data: Dict[str, Any] = None) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if deal_score >= 80:
            recommendations.append("Excellent deal - Strong buy recommendation")
        elif deal_score >= 70:
            recommendations.append("Good deal - Consider purchasing")
        elif deal_score >= 60:
            recommendations.append("Fair deal - Negotiate for better terms")
        elif deal_score >= 50:
            recommendations.append("Marginal deal - Proceed with caution")
        else:
            recommendations.append("Poor deal - Avoid or significantly renegotiate")
        
        if "Very old equipment" in str(risk_factors):
            recommendations.append("Schedule comprehensive inspection before purchase")
        
        if "High hours" in str(risk_factors):
            recommendations.append("Request maintenance records and service history")
        
        if "Poor condition" in str(risk_factors):
            recommendations.append("Factor in repair costs to total investment")
        
        if "Price above market" in str(risk_factors):
            recommendations.append("Negotiate price down to market value")
        
        # Market timing recommendations
        if market_data and market_data.get('trends', {}).get('demand_level') == 'high':
            recommendations.append("High demand market - consider quick decision")
        
        return recommendations
    
    def _calculate_financial_metrics(self, specs: CraneSpecs, final_value: float, base_value: float) -> Dict[str, Any]:
        """Calculate financial metrics and ROI analysis"""
        if not specs.price:
            return {"error": "No price provided for financial analysis"}
        
        price = specs.price
        value_ratio = price / final_value
        discount_premium = (final_value - price) / final_value * 100
        
        rental_rates = {
            'low': 0.08, 'medium': 0.12, 'high': 0.16
        }
        
        roi_scenarios = {}
        for scenario, rate in rental_rates.items():
            annual_return = price * rate
            roi_scenarios[scenario] = {
                'annual_return': annual_return,
                'payback_years': price / annual_return if annual_return > 0 else 0,
                '5_year_total': annual_return * 5
            }
        
        return {
            'price': price,
            'value_ratio': value_ratio,
            'discount_premium_percent': discount_premium,
            'roi_scenarios': roi_scenarios,
            'breakeven_years': price / (price * 0.12) if price > 0 else 0
        }
    
    def _generate_comparable_analysis(self, specs: CraneSpecs, final_value: float,
                                     market_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comparable market analysis"""
        comparables = []
        
        # Use real market data if available
        if market_data and market_data.get('listings'):
            for listing in market_data['listings'][:5]:
                comparables.append({
                    'year': listing.get('year', specs.year),
                    'hours': listing.get('hours', specs.hours),
                    'estimated_value': listing.get('price', final_value),
                    'location': listing.get('location', 'Unknown'),
                    'source': listing.get('source', 'Market Data')
                })
        else:
            # Generate synthetic comparables
            current_year = datetime.now().year
            age = current_year - specs.year
            
            for i in range(3):
                comp_age = max(0, age + (i - 1))
                comp_hours = max(1000, specs.hours + (i - 1) * 1000)
                
                age_diff = comp_age - age
                hours_diff = comp_hours - specs.hours
                
                comp_value = final_value
                comp_value *= (1 + age_diff * 0.05)
                comp_value *= (1 + hours_diff / 10000 * 0.1)
                
                comparables.append({
                    'year': current_year - comp_age,
                    'hours': comp_hours,
                    'estimated_value': round(comp_value, -3),
                    'age_diff': age_diff,
                    'hours_diff': hours_diff,
                    'source': 'Synthetic'
                })
        
        return {
            'comparables': comparables,
            'market_trend': 'Stable' if (datetime.now().year - specs.year) <= 10 else 'Declining',
            'price_range': {
                'low': round(min(c['estimated_value'] for c in comparables), -3) if comparables else final_value * 0.9,
                'high': round(max(c['estimated_value'] for c in comparables), -3) if comparables else final_value * 1.1
            }
        }
    
    def _generate_financing_scenarios(self, specs: CraneSpecs, final_value: float) -> List[Dict[str, Any]]:
        """Generate financing scenarios"""
        scenarios = [
            {
                "scenario": "Cash Purchase",
                "down_payment": final_value,
                "monthly_payment": 0,
                "total_cost": final_value,
                "interest_rate": 0.0
            },
            {
                "scenario": "20% Down, 5% APR",
                "down_payment": final_value * 0.2,
                "monthly_payment": (final_value * 0.8 * 0.05 / 12) / (1 - (1 + 0.05/12)**(-60)) if final_value > 0 else 0,
                "total_cost": final_value * 0.2 + ((final_value * 0.8 * 0.05 / 12) / (1 - (1 + 0.05/12)**(-60)) * 60) if final_value > 0 else 0,
                "interest_rate": 0.05
            }
        ]
        
        return scenarios


# ==================== BACKWARD COMPATIBILITY ====================

# Create aliases for backward compatibility
CraneValuationEngine = UnifiedValuationEngine

# Global instance for backward compatibility
valuation_engine = UnifiedValuationEngine(use_real_time_data=False)
comprehensive_valuation_engine = UnifiedValuationEngine(use_real_time_data=True)
enhanced_valuation_engine = UnifiedValuationEngine(use_real_time_data=True)

