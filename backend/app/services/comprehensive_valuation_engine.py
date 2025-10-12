"""
Comprehensive Valuation Engine
Integrates smart rental rates with crane valuation analysis
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .smart_rental_engine import SmartRentalEngine

logger = logging.getLogger(__name__)


class ComprehensiveValuationEngine:
    """
    Comprehensive Crane Valuation Engine
    Provides Bloomberg-style valuation with integrated rental rate analysis
    """
    
    def __init__(self):
        """Initialize the comprehensive valuation engine"""
        self.rental_engine = SmartRentalEngine()
        
        # Manufacturer premiums (relative to baseline)
        self.manufacturer_premiums = {
            'Liebherr': 1.15,
            'Grove': 1.10,
            'Tadano': 1.12,
            'Manitowoc': 1.08,
            'Terex': 1.05,
            'Link-Belt': 1.03,
            'default': 1.00
        }
        
        # Regional adjustments for valuation
        self.regional_adjustments = {
            'Northeast': 1.05,
            'Southeast': 0.90,
            'Midwest': 0.85,
            'Gulf Coast': 0.95,
            'West Coast': 1.10,
            'Canada': 1.00,
            'default': 1.00
        }
    
    def calculate_valuation(self, crane_specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive valuation with rental rate analysis
        
        Args:
            crane_specs: Dictionary containing crane specifications
                Required: manufacturer, model, year, capacity, hours, region
                Optional: asking_price, condition_score, crane_type
        
        Returns:
            Comprehensive valuation result dictionary
        """
        # Extract specs
        manufacturer = crane_specs.get('manufacturer', 'Unknown')
        model = crane_specs.get('model', 'Unknown')
        year = crane_specs.get('year', 2020)
        capacity = crane_specs.get('capacity', crane_specs.get('capacity_tons', 100))
        hours = crane_specs.get('hours', 0)
        region = crane_specs.get('region', 'Northeast')
        asking_price = crane_specs.get('asking_price', crane_specs.get('price'))
        condition_score = crane_specs.get('condition_score', 0.8)
        crane_type = crane_specs.get('crane_type', 'All Terrain')
        
        # Calculate base valuation
        current_year = 2025
        age = max(1, current_year - year)
        
        # Base value calculation (simplified for demo)
        base_value_per_ton = 12000  # $12k per ton baseline
        
        # Age depreciation
        if age <= 3:
            age_factor = 0.95
        elif age <= 7:
            age_factor = 0.85
        elif age <= 12:
            age_factor = 0.70
        else:
            age_factor = 0.50
        
        # Hours factor (assuming 800 hours/year average)
        expected_hours = age * 800
        if hours == 0:
            hours_factor = 0.90  # Unknown hours penalty
        elif hours < expected_hours * 0.7:
            hours_factor = 1.05  # Low hours premium
        elif hours < expected_hours * 1.3:
            hours_factor = 1.00  # Normal hours
        else:
            hours_factor = 0.85  # High hours discount
        
        # Manufacturer premium
        mfr_premium = self.manufacturer_premiums.get(manufacturer, self.manufacturer_premiums['default'])
        
        # Regional adjustment
        regional_adj = self.regional_adjustments.get(region, self.regional_adjustments['default'])
        
        # Calculate fair market value
        fair_market_value = (
            base_value_per_ton * 
            capacity * 
            age_factor * 
            hours_factor * 
            mfr_premium * 
            regional_adj *
            condition_score
        )
        
        # Wholesale and retail ranges
        wholesale_value = fair_market_value * 0.85
        retail_value = fair_market_value * 1.15
        
        # --- RENTAL RATE ANALYSIS INTEGRATION ---
        rental_specs = {
            'capacity': capacity,
            'capacity_tons': capacity,
            'region': region,
            'crane_type': crane_type,
            'year': year
        }
        
        # Calculate both bare and operated rental rates
        bare_rental = self.rental_engine.calculate_rental_rates(rental_specs, rental_mode="bare")
        operated_rental = self.rental_engine.calculate_rental_rates(rental_specs, rental_mode="operated")
        
        # ROI Analysis if purchase price is provided
        roi_analysis_bare = None
        roi_analysis_operated = None
        if asking_price:
            roi_analysis_bare = self.rental_engine.get_roi_analysis(
                rental_specs, 
                purchase_price=asking_price, 
                utilization_rate=0.70
            )
            roi_analysis_operated = self.rental_engine.get_roi_analysis(
                rental_specs, 
                purchase_price=asking_price, 
                utilization_rate=0.70
            )
        
        # Deal scoring
        deal_score = self._calculate_deal_score(
            asking_price if asking_price else fair_market_value,
            fair_market_value,
            age,
            hours,
            expected_hours
        )
        
        # Wear score
        wear_score = self._calculate_wear_score(hours, expected_hours, condition_score)
        
        # Financing scenarios by region
        financing_scenarios = self._generate_financing_scenarios(
            fair_market_value,
            bare_rental,
            operated_rental,
            roi_analysis_bare,
            roi_analysis_operated
        )
        
        # Market insights
        market_insights = {
            "rental_calibrated": bare_rental['inputs']['calibrated'],
            "rental_market_position": self._assess_rental_position(bare_rental, operated_rental),
            "recommended_mode": "operated" if operated_rental['rental_rates']['monthly_rate'] > bare_rental['rental_rates']['monthly_rate'] * 1.3 else "bare",
            "utilization_breakeven": self._calculate_utilization_breakeven(asking_price if asking_price else fair_market_value, bare_rental)
        }
        
        # Comparable analysis (mock data for now)
        comparable_analysis = self._generate_comparable_analysis(manufacturer, model, capacity, year, region)
        
        # Return comprehensive result
        return {
            # Core valuation
            "fair_market_value": round(fair_market_value, 2),
            "wholesale_value": round(wholesale_value, 2),
            "retail_value": round(retail_value, 2),
            "confidence_score": 0.85,  # Based on data availability
            
            # Scoring
            "deal_score": deal_score,
            "wear_score": wear_score,
            "market_position": self._assess_market_position(asking_price if asking_price else fair_market_value, fair_market_value),
            
            # Rental rates (integrated from Smart Rental Engine)
            "rental_rates": {
                "bare": bare_rental['rental_rates'],
                "operated": operated_rental['rental_rates'],
                "utilization_scenarios": bare_rental['utilization_analysis']
            },
            
            # Financing and ROI
            "financing_scenarios": financing_scenarios,
            "roi_analysis": {
                "bare": roi_analysis_bare['rental_scenarios']['bare'] if roi_analysis_bare else None,
                "operated": roi_analysis_operated['rental_scenarios']['operated'] if roi_analysis_operated else None
            },
            
            # Market intelligence
            "market_insights": market_insights,
            "comparable_analysis": comparable_analysis,
            
            # Input echo
            "inputs": {
                "manufacturer": manufacturer,
                "model": model,
                "year": year,
                "capacity_tons": capacity,
                "hours": hours,
                "region": region,
                "crane_type": crane_type,
                "asking_price": asking_price
            },
            
            # Metadata
            "valuation_date": datetime.utcnow().isoformat(),
            "engine_version": "3.0"
        }
    
    def _calculate_deal_score(self, asking_price: float, fair_market_value: float, 
                              age: int, hours: int, expected_hours: int) -> int:
        """Calculate deal score (0-100)"""
        if asking_price == 0 or fair_market_value == 0:
            return 50
        
        # Price component (0-50 points)
        price_ratio = asking_price / fair_market_value
        if price_ratio <= 0.80:
            price_score = 50
        elif price_ratio <= 0.90:
            price_score = 40
        elif price_ratio <= 1.00:
            price_score = 30
        elif price_ratio <= 1.10:
            price_score = 20
        else:
            price_score = 10
        
        # Condition component (0-30 points)
        if age <= 3:
            age_score = 20
        elif age <= 7:
            age_score = 15
        elif age <= 12:
            age_score = 10
        else:
            age_score = 5
        
        # Hours component (0-20 points)
        if hours == 0:
            hours_score = 10  # Unknown
        elif hours < expected_hours * 0.7:
            hours_score = 20  # Low hours
        elif hours < expected_hours * 1.3:
            hours_score = 15  # Normal hours
        else:
            hours_score = 5  # High hours
        
        total_score = min(100, price_score + age_score + hours_score)
        return int(total_score)
    
    def _calculate_wear_score(self, hours: int, expected_hours: int, condition_score: float) -> float:
        """Calculate wear score (0.0-1.0)"""
        if hours == 0:
            return condition_score * 0.9  # Unknown penalty
        
        hours_ratio = hours / expected_hours if expected_hours > 0 else 1.0
        
        if hours_ratio < 0.7:
            hours_wear = 0.95
        elif hours_ratio < 1.3:
            hours_wear = 0.85
        else:
            hours_wear = 0.70
        
        return round(condition_score * hours_wear, 2)
    
    def _assess_market_position(self, asking_price: float, fair_market_value: float) -> str:
        """Assess market position"""
        if asking_price == 0 or fair_market_value == 0:
            return "Unknown"
        
        ratio = asking_price / fair_market_value
        if ratio <= 0.85:
            return "Excellent Value"
        elif ratio <= 0.95:
            return "Good Value"
        elif ratio <= 1.05:
            return "Fair Market"
        elif ratio <= 1.15:
            return "Premium"
        else:
            return "Overpriced"
    
    def _generate_financing_scenarios(self, fair_market_value: float, 
                                     bare_rental: Dict, operated_rental: Dict,
                                     roi_bare: Optional[Dict], roi_operated: Optional[Dict]) -> List[Dict]:
        """Generate financing scenarios"""
        scenarios = []
        
        # Scenario 1: Cash Purchase - Bare Rental
        if roi_bare:
            scenarios.append({
                "scenario": "Cash Purchase - Bare Rental",
                "purchase_price": fair_market_value,
                "financing_type": "Cash",
                "rental_mode": "bare",
                "monthly_rental_income": bare_rental['rental_rates']['monthly_rate'],
                "annual_rental_income": bare_rental['rental_rates']['annual_rate'],
                "roi_percent": roi_bare['rental_scenarios']['bare']['roi_percent'],
                "payback_years": roi_bare['rental_scenarios']['bare']['payback_years']
            })
        
        # Scenario 2: Cash Purchase - Operated Rental
        if roi_operated:
            scenarios.append({
                "scenario": "Cash Purchase - Operated Rental",
                "purchase_price": fair_market_value,
                "financing_type": "Cash",
                "rental_mode": "operated",
                "monthly_rental_income": operated_rental['rental_rates']['monthly_rate'],
                "annual_rental_income": operated_rental['rental_rates']['annual_rate'],
                "roi_percent": roi_operated['rental_scenarios']['operated']['roi_percent'],
                "payback_years": roi_operated['rental_scenarios']['operated']['payback_years']
            })
        
        # Scenario 3: 80% Financing - Bare Rental
        down_payment = fair_market_value * 0.20
        financed_amount = fair_market_value * 0.80
        monthly_payment = financed_amount * 0.008  # Approx 8% annual rate / 12 months for 60 months
        
        scenarios.append({
            "scenario": "80% Financing - Bare Rental",
            "purchase_price": fair_market_value,
            "financing_type": "80% LTV Loan",
            "down_payment": round(down_payment, 2),
            "monthly_payment": round(monthly_payment, 2),
            "rental_mode": "bare",
            "monthly_rental_income": bare_rental['rental_rates']['monthly_rate'],
            "monthly_cash_flow": round(bare_rental['rental_rates']['monthly_rate'] * 0.70 - monthly_payment, 2)
        })
        
        return scenarios
    
    def _assess_rental_position(self, bare_rental: Dict, operated_rental: Dict) -> str:
        """Assess rental market position"""
        bare_monthly = bare_rental['rental_rates']['monthly_rate']
        operated_monthly = operated_rental['rental_rates']['monthly_rate']
        
        operated_premium = (operated_monthly / bare_monthly - 1) * 100
        
        if operated_premium > 50:
            return "High Premium for Operated"
        elif operated_premium > 40:
            return "Standard Premium for Operated"
        else:
            return "Lower Premium for Operated"
    
    def _calculate_utilization_breakeven(self, purchase_price: float, bare_rental: Dict) -> str:
        """Calculate utilization breakeven percentage"""
        annual_rate = bare_rental['rental_rates']['annual_rate']
        
        # Simplified breakeven: Operating expenses + depreciation vs revenue
        annual_expenses = purchase_price * 0.10  # 10% of purchase price for expenses
        
        breakeven_revenue = annual_expenses
        utilization_breakeven = (breakeven_revenue / annual_rate) * 100 if annual_rate > 0 else 0
        
        return f"{min(100, max(0, utilization_breakeven)):.0f}%"
    
    def _generate_comparable_analysis(self, manufacturer: str, model: str, 
                                     capacity: float, year: int, region: str) -> Dict:
        """Generate comparable analysis (mock data for now)"""
        return {
            "comparable_count": 5,
            "price_range": {
                "low": round(capacity * 10000, 2),
                "average": round(capacity * 12000, 2),
                "high": round(capacity * 14000, 2)
            },
            "market_activity": "Moderate",
            "days_on_market_avg": 45,
            "regional_demand": "High" if region in ['Northeast', 'West Coast'] else "Moderate"
        }


# Singleton instance
comprehensive_valuation_engine = ComprehensiveValuationEngine()


# Example usage
if __name__ == "__main__":
    # Test case: LTM 1350 - Liebherr
    crane_specs = {
        'manufacturer': 'Liebherr',
        'model': 'LTM1350-6.1',
        'year': 2020,
        'capacity': 350,
        'hours': 2400,
        'region': 'Northeast',
        'crane_type': 'All Terrain',
        'asking_price': 2500000,
        'condition_score': 0.90
    }
    
    print("🏗️ Comprehensive Valuation Engine - Test")
    print("=" * 60)
    
    result = comprehensive_valuation_engine.calculate_valuation(crane_specs)
    
    print(f"\n📊 VALUATION RESULTS:")
    print(f"  Fair Market Value: ${result['fair_market_value']:,.2f}")
    print(f"  Wholesale Value: ${result['wholesale_value']:,.2f}")
    print(f"  Retail Value: ${result['retail_value']:,.2f}")
    print(f"  Deal Score: {result['deal_score']}/100")
    print(f"  Market Position: {result['market_position']}")
    
    print(f"\n💵 RENTAL RATES:")
    print(f"  Bare Monthly: ${result['rental_rates']['bare']['monthly_rate']:,.2f}")
    print(f"  Operated Monthly: ${result['rental_rates']['operated']['monthly_rate']:,.2f}")
    
    print(f"\n📈 ROI ANALYSIS:")
    if result['roi_analysis']['bare']:
        print(f"  Bare Mode ROI: {result['roi_analysis']['bare']['roi_percent']}%")
        print(f"  Bare Payback: {result['roi_analysis']['bare']['payback_years']} years")
    if result['roi_analysis']['operated']:
        print(f"  Operated Mode ROI: {result['roi_analysis']['operated']['roi_percent']}%")
        print(f"  Operated Payback: {result['roi_analysis']['operated']['payback_years']} years")

