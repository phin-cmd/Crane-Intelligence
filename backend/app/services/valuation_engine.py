"""
Crane Intelligence Platform - Core Valuation Engine
Implements the sophisticated valuation algorithms from the original platform
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import math


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


@dataclass
class ValuationResult:
    """Complete valuation result"""
    fair_market_value: float
    deal_score: int  # 0-100
    confidence_score: float  # 0.0-1.0
    risk_factors: List[str]
    recommendations: List[str]
    market_position: str
    depreciation_rate: float
    hours_analysis: Dict[str, Any]
    comparable_analysis: Dict[str, Any]
    financial_metrics: Dict[str, Any]


class CraneValuationEngine:
    """Professional-grade crane valuation engine"""
    
    def __init__(self):
        # Manufacturer premium factors
        self.manufacturer_premiums = {
            'Liebherr': 1.15,
            'Grove': 1.10,
            'Tadano': 1.08,
            'Manitowoc': 1.05,
            'Terex': 1.02,
            'Link-Belt': 1.00,
            'default': 1.00
        }
        
        # Regional market adjustments
        self.regional_adjustments = {
            'TX': 1.05,  # Texas premium
            'CA': 1.08,  # California premium
            'NY': 1.06,  # New York premium
            'FL': 1.03,  # Florida premium
            'default': 1.00
        }
        
        # Base capacity pricing (per ton)
        self.base_capacity_price = 12000
        
        # Depreciation curves by age
        self.depreciation_curves = {
            'new': 1.00,      # 0-2 years
            'young': 0.85,    # 3-5 years
            'mid': 0.70,      # 6-10 years
            'mature': 0.50,   # 11-15 years
            'old': 0.35,      # 16-20 years
            'vintage': 0.25   # 20+ years
        }
    
    def value_crane(self, specs: CraneSpecs) -> ValuationResult:
        """Main valuation method - comprehensive analysis"""
        
        # 1. Calculate base value
        base_value = self._calculate_base_value(specs)
        
        # 2. Apply depreciation
        depreciation_rate = self._calculate_depreciation_rate(specs.year)
        age_adjusted_value = base_value * depreciation_rate
        
        # 3. Apply condition adjustments
        condition_adjustment = self._calculate_condition_adjustment(specs.condition_score)
        condition_adjusted_value = age_adjusted_value * condition_adjustment
        
        # 4. Apply hours analysis
        hours_analysis = self._analyze_hours(specs.year, specs.hours)
        hours_adjusted_value = condition_adjusted_value * hours_analysis['adjustment_factor']
        
        # 5. Apply market adjustments
        market_adjustment = self._calculate_market_adjustment(specs.manufacturer, specs.region)
        final_value = hours_adjusted_value * market_adjustment
        
        # 6. Calculate deal score
        deal_score = self._calculate_deal_score(specs, final_value, base_value)
        
        # 7. Determine market position
        market_position = self._determine_market_position(specs, final_value, base_value)
        
        # 8. Calculate confidence score
        confidence_score = self._calculate_confidence_score(specs, final_value)
        
        # 9. Identify risk factors
        risk_factors = self._identify_risk_factors(specs, final_value, base_value)
        
        # 10. Generate recommendations
        recommendations = self._generate_recommendations(deal_score, risk_factors)
        
        # 11. Calculate financial metrics
        financial_metrics = self._calculate_financial_metrics(specs, final_value, base_value)
        
        # 12. Comparable analysis
        comparable_analysis = self._generate_comparable_analysis(specs, final_value)
        
        return ValuationResult(
            fair_market_value=final_value,
            deal_score=deal_score,
            confidence_score=confidence_score,
            risk_factors=risk_factors,
            recommendations=recommendations,
            market_position=market_position,
            depreciation_rate=depreciation_rate,
            hours_analysis=hours_analysis,
            comparable_analysis=comparable_analysis,
            financial_metrics=financial_metrics
        )
    
    def _calculate_base_value(self, specs: CraneSpecs) -> float:
        """Calculate base value based on capacity and manufacturer"""
        base_value = specs.capacity_tons * self.base_capacity_price
        
        # Apply manufacturer premium
        manufacturer_premium = self.manufacturer_premiums.get(
            specs.manufacturer, 
            self.manufacturer_premiums['default']
        )
        
        return base_value * manufacturer_premium
    
    def _calculate_depreciation_rate(self, year: int) -> float:
        """Calculate depreciation rate based on age"""
        current_year = datetime.now().year
        age = current_year - year
        
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
    
    def _calculate_condition_adjustment(self, condition_score: float) -> float:
        """Calculate condition adjustment factor"""
        # Map condition score (0.0-1.0) to adjustment factor (0.85-1.15)
        if condition_score >= 0.9:
            return 1.15  # Excellent condition
        elif condition_score >= 0.8:
            return 1.08  # Very good condition
        elif condition_score >= 0.7:
            return 1.00  # Good condition
        elif condition_score >= 0.6:
            return 0.92  # Fair condition
        elif condition_score >= 0.5:
            return 0.85  # Poor condition
        else:
            return 0.75  # Very poor condition
    
    def _analyze_hours(self, year: int, hours: int) -> Dict[str, Any]:
        """Analyze hours and calculate adjustment factor"""
        current_year = datetime.now().year
        age = current_year - year
        
        # Expected hours per year
        expected_hours_per_year = 800
        expected_total_hours = age * expected_hours_per_year
        
        # Calculate hours ratio
        hours_ratio = hours / max(expected_total_hours, 1)
        
        # Determine adjustment factor
        if hours_ratio <= 0.7:
            adjustment_factor = 1.15  # Low hours - premium
        elif hours_ratio <= 0.9:
            adjustment_factor = 1.08  # Below average hours
        elif hours_ratio <= 1.1:
            adjustment_factor = 1.00  # Normal hours
        elif hours_ratio <= 1.3:
            adjustment_factor = 0.92  # Above average hours
        elif hours_ratio <= 1.5:
            adjustment_factor = 0.85  # High hours
        else:
            adjustment_factor = 0.75  # Very high hours
        
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
        regional_factor = self.regional_adjustments.get(region, self.regional_adjustments['default'])
        return regional_factor
    
    def _calculate_deal_score(self, specs: CraneSpecs, final_value: float, base_value: float) -> int:
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
                price_factor = 15  # Great price
            elif price_ratio <= 0.95:
                price_factor = 12  # Good price
            elif price_ratio <= 1.05:
                price_factor = 8   # Fair price
            elif price_ratio <= 1.1:
                price_factor = 4   # High price
            else:
                price_factor = 0   # Very high price
        else:
            price_factor = 8  # Neutral if no price given
        
        # Calculate final score
        deal_score = min(100, base_score + age_factor + hours_factor + price_factor)
        
        return deal_score
    
    def _determine_market_position(self, specs: CraneSpecs, final_value: float, base_value: float) -> str:
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
        else:
            return "Good - At Market"
    
    def _calculate_confidence_score(self, specs: CraneSpecs, final_value: float) -> float:
        """Calculate confidence score (0.0-1.0)"""
        # Base confidence
        confidence = 0.7
        
        # Adjust based on data quality
        if specs.condition_score > 0:
            confidence += 0.1
        
        if specs.price:
            confidence += 0.1
        
        # Adjust based on manufacturer data availability
        if specs.manufacturer in self.manufacturer_premiums:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _identify_risk_factors(self, specs: CraneSpecs, final_value: float, base_value: float) -> List[str]:
        """Identify potential risk factors"""
        risk_factors = []
        current_year = datetime.now().year
        age = current_year - specs.year
        
        # Age-related risks
        if age > 20:
            risk_factors.append("Very old equipment - high maintenance risk")
        elif age > 15:
            risk_factors.append("Mature equipment - consider replacement timeline")
        
        # Hours-related risks
        if specs.hours > 15000:
            risk_factors.append("High hours - potential wear and tear")
        elif specs.hours > 10000:
            risk_factors.append("Above average hours - monitor condition")
        
        # Condition risks
        if specs.condition_score < 0.6:
            risk_factors.append("Poor condition - significant repairs may be needed")
        
        # Price risks
        if specs.price and specs.price > final_value * 1.1:
            risk_factors.append("Price above market value")
        
        # Market risks
        if final_value < base_value * 0.3:
            risk_factors.append("Value significantly below base - investigate thoroughly")
        
        return risk_factors
    
    def _generate_recommendations(self, deal_score: int, risk_factors: List[str]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Deal score recommendations
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
        
        # Risk mitigation recommendations
        if "Very old equipment" in str(risk_factors):
            recommendations.append("Schedule comprehensive inspection before purchase")
        
        if "High hours" in str(risk_factors):
            recommendations.append("Request maintenance records and service history")
        
        if "Poor condition" in str(risk_factors):
            recommendations.append("Factor in repair costs to total investment")
        
        if "Price above market" in str(risk_factors):
            recommendations.append("Negotiate price down to market value")
        
        return recommendations
    
    def _calculate_financial_metrics(self, specs: CraneSpecs, final_value: float, base_value: float) -> Dict[str, Any]:
        """Calculate financial metrics and ROI analysis"""
        if not specs.price:
            return {"error": "No price provided for financial analysis"}
        
        # Basic metrics
        price = specs.price
        value_ratio = price / final_value
        discount_premium = (final_value - price) / final_value * 100
        
        # ROI scenarios (assuming rental income)
        rental_rates = {
            'low': 0.08,    # 8% annual return
            'medium': 0.12,  # 12% annual return
            'high': 0.16     # 16% annual return
        }
        
        roi_scenarios = {}
        for scenario, rate in rental_rates.items():
            annual_return = price * rate
            roi_scenarios[scenario] = {
                'annual_return': annual_return,
                'payback_years': price / annual_return,
                '5_year_total': annual_return * 5
            }
        
        return {
            'price': price,
            'value_ratio': value_ratio,
            'discount_premium_percent': discount_premium,
            'roi_scenarios': roi_scenarios,
            'breakeven_years': price / (price * 0.12)  # Medium scenario
        }
    
    def _generate_comparable_analysis(self, specs: CraneSpecs, final_value: float) -> Dict[str, Any]:
        """Generate comparable market analysis"""
        # This would typically pull from a database of recent sales
        # For now, we'll generate synthetic comparables
        
        current_year = datetime.now().year
        age = current_year - specs.year
        
        # Generate synthetic comparable data
        comparables = []
        for i in range(3):
            comp_age = max(0, age + (i - 1))  # -1, 0, +1 years
            comp_hours = max(1000, specs.hours + (i - 1) * 1000)  # ±1000 hours
            
            # Adjust value based on age and hours differences
            age_diff = comp_age - age
            hours_diff = comp_hours - specs.hours
            
            comp_value = final_value
            comp_value *= (1 + age_diff * 0.05)  # 5% per year difference
            comp_value *= (1 + hours_diff / 10000 * 0.1)  # 10% per 10k hours difference
            
            comparables.append({
                'year': current_year - comp_age,
                'hours': comp_hours,
                'estimated_value': round(comp_value, -3),  # Round to nearest thousand
                'age_diff': age_diff,
                'hours_diff': hours_diff
            })
        
        return {
            'comparables': comparables,
            'market_trend': 'Stable' if age <= 10 else 'Declining',
            'price_range': {
                'low': round(min(c['estimated_value'] for c in comparables), -3),
                'high': round(max(c['estimated_value'] for c in comparables), -3)
            }
        }


# Example usage and testing
if __name__ == "__main__":
    # Test the valuation engine
    engine = CraneValuationEngine()
    
    # Test crane specs
    test_specs = CraneSpecs(
        manufacturer="Liebherr",
        model="LTM1350-6.1",
        year=2022,
        capacity_tons=350,
        hours=1200,
        condition_score=0.95,
        region="TX",
        price=2950000
    )
    
    # Run valuation
    result = engine.value_crane(test_specs)
    
    print("=== CRANE VALUATION RESULTS ===")
    print(f"Fair Market Value: ${result.fair_market_value:,.0f}")
    print(f"Deal Score: {result.deal_score}/100")
    print(f"Confidence: {result.confidence_score:.1%}")
    print(f"Market Position: {result.market_position}")
    print(f"Risk Factors: {', '.join(result.risk_factors)}")
    print(f"Recommendations: {', '.join(result.recommendations)}")
