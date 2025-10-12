"""
Crane Intelligence Platform – Smart Rental Engine v3.0 (Self-Calibrating)

🔧 Core Purpose:
A unified engine that:
1. Computes bare and operated rental rates
2. Adjusts automatically based on regional CSV data
3. Learns from real market observations (average, min, max per tonnage class)
4. Feeds downstream modules — ROI, utilization, and deal scoring
"""

import pandas as pd
import numpy as np
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SmartRentalEngine:
    """
    Smart Rental Engine v3.0 - Self-Calibrating Rental Rate Calculator
    Automatically learns from regional market data and adjusts rates accordingly
    """
    
    def __init__(self, rental_csv_path: Optional[str] = None):
        """
        Initialize the Smart Rental Engine
        
        Args:
            rental_csv_path: Path to the regional rental rates CSV file
        """
        if rental_csv_path is None:
            # Default path relative to backend directory
            rental_csv_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data",
                "Crane_Rental_Rates_By_Region.csv"
            )
        
        self.rental_csv_path = rental_csv_path
        self.rental_data = self._load_calibration_data()
        
        # Fallback base rates per ton if CSV is missing or incomplete
        self.base_rate_per_ton_fallback = {
            'All Terrain': 220,
            'Rough Terrain': 180,
            'Crawler': 200,
            'Truck Mounted': 160,
            'Tower': 140
        }
        
        # Regional multiplier defaults (used only as fallback)
        self.regional_multiplier_fallback = {
            'Northeast': 1.05,
            'Southeast': 0.90,
            'Midwest': 0.85,
            'Gulf Coast': 0.95,
            'West Coast': 1.10,
            'Canada': 1.00
        }
    
    def _load_calibration_data(self) -> pd.DataFrame:
        """Load calibration data from CSV file"""
        try:
            if os.path.exists(self.rental_csv_path):
                df = pd.read_csv(self.rental_csv_path)
                logger.info(f"Loaded {len(df)} rental rate records from {self.rental_csv_path}")
                return df
            else:
                logger.warning(f"Rental CSV not found at {self.rental_csv_path}, using fallback rates")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading rental CSV: {e}")
            return pd.DataFrame()
    
    def calculate_rental_rates(self, specs: Dict[str, Any], rental_mode: str = "bare") -> Dict[str, Any]:
        """
        Calculate smart rental rates based on crane specs and regional data
        
        Args:
            specs: Dictionary containing crane specifications:
                - capacity: Crane capacity in tons
                - region: Geographic region
                - crane_type: Type of crane (All Terrain, Crawler, etc.)
                - year: Manufacturing year
            rental_mode: "bare" or "operated"
        
        Returns:
            Dictionary containing rental rates and analysis
        """
        # --- INPUTS ---
        capacity = specs.get('capacity', specs.get('capacity_tons', 100))
        region = specs.get('region', 'Northeast')
        crane_type = specs.get('crane_type', 'Crawler')
        year = specs.get('year', 2022)
        current_year = 2025
        age = max(1, current_year - year)
        
        # --- 1️⃣ BASE RATE PER TON (Fallback if CSV missing) ---
        base_rate_per_ton = self.base_rate_per_ton_fallback.get(crane_type, 200)
        
        # --- 2️⃣ REGIONAL MULTIPLIER DEFAULTS ---
        regional_multiplier = self.regional_multiplier_fallback.get(region, 1.0)
        
        # --- 3️⃣ CSV CALIBRATION LOGIC ---
        calibrated = False
        if not self.rental_data.empty:
            match = self.rental_data[
                (self.rental_data['Region'].str.contains(region, case=False, na=False)) &
                (self.rental_data['Crane Type'].str.contains(crane_type, case=False, na=False))
            ]
            if not match.empty:
                # Closest capacity match
                match = match.copy()
                match['diff'] = abs(match['Tonnage'] - capacity)
                nearest = match.loc[match['diff'].idxmin()]
                base_rate_per_ton = float(nearest['Monthly Rate (USD)']) / float(nearest['Tonnage'])
                regional_multiplier = 1.0  # override with actual regional data
                calibrated = True
                logger.info(f"Calibrated rate: ${base_rate_per_ton}/ton for {crane_type} in {region}")
        
        # If CSV missing or no match, use static baseline with multiplier
        if not calibrated:
            base_rate_per_ton = base_rate_per_ton * regional_multiplier
        
        # --- 4️⃣ AGE FACTOR ---
        if age <= 3: 
            age_factor = 1.10
        elif age <= 7: 
            age_factor = 1.00
        elif age <= 12: 
            age_factor = 0.90
        else: 
            age_factor = 0.80
        
        # --- 5️⃣ CAPACITY FACTOR ---
        if capacity <= 80: 
            capacity_factor = 1.10
        elif capacity <= 150: 
            capacity_factor = 1.00
        elif capacity <= 300: 
            capacity_factor = 0.90
        else: 
            capacity_factor = 0.80
        
        # --- 6️⃣ BASE MONTHLY RATE (Bare) ---
        monthly_bare = base_rate_per_ton * capacity * age_factor * capacity_factor
        monthly_bare = max(4000, min(monthly_bare, 95000))  # Floor and ceiling
        
        # --- 7️⃣ OPERATED RATE ADJUSTMENT ---
        operated_multiplier = 1.45  # default +45%
        if rental_mode.lower() == "operated":
            # Learn operated multiplier from CSV if available
            if not self.rental_data.empty and 'Operated/Bare Ratio' in self.rental_data.columns:
                match_operated = self.rental_data[
                    (self.rental_data['Region'].str.contains(region, case=False, na=False)) &
                    (self.rental_data['Crane Type'].str.contains(crane_type, case=False, na=False))
                ]
                if not match_operated.empty:
                    operated_multiplier = float(match_operated.iloc[0]['Operated/Bare Ratio'])
            
            monthly_rate = monthly_bare * operated_multiplier
        else:
            monthly_rate = monthly_bare
        
        # --- 8️⃣ PERIOD CONVERSIONS ---
        daily_rate = round(monthly_rate / 22, 2)
        weekly_rate = round(monthly_rate / 4.33, 2)
        annual_rate = round(monthly_rate * 12, 2)
        
        # --- 9️⃣ UTILIZATION SCENARIOS ---
        utilization_scenarios = {
            f"{u}%": {
                "effective_monthly": round(monthly_rate / (u / 100), 2),
                "annualized": round((monthly_rate / (u / 100)) * 12, 2)
            }
            for u in [50, 70, 85, 95]
        }
        
        # --- 🔟 OUTPUT STRUCTURE ---
        return {
            "inputs": {
                "capacity_tons": capacity,
                "crane_type": crane_type,
                "region": region,
                "year": year,
                "age": age,
                "rental_mode": rental_mode,
                "calibrated": calibrated
            },
            "rental_rates": {
                "daily_rate": daily_rate,
                "weekly_rate": weekly_rate,
                "monthly_rate": round(monthly_rate, 2),
                "annual_rate": annual_rate
            },
            "utilization_analysis": utilization_scenarios,
            "rate_factors": {
                "base_rate_per_ton": round(base_rate_per_ton, 2),
                "age_factor": age_factor,
                "capacity_factor": capacity_factor,
                "regional_multiplier": regional_multiplier,
                "operated_multiplier": operated_multiplier if rental_mode.lower() == "operated" else 1.0
            }
        }
    
    def get_roi_analysis(self, specs: Dict[str, Any], purchase_price: float, 
                        utilization_rate: float = 0.70) -> Dict[str, Any]:
        """
        Calculate ROI analysis for a crane based on rental rates
        
        Args:
            specs: Crane specifications
            purchase_price: Purchase price of the crane
            utilization_rate: Expected utilization rate (0.0 to 1.0)
        
        Returns:
            Dictionary containing ROI analysis
        """
        # Calculate bare rental rates
        bare_rates = self.calculate_rental_rates(specs, rental_mode="bare")
        operated_rates = self.calculate_rental_rates(specs, rental_mode="operated")
        
        # Annual revenue calculations
        annual_bare_revenue = bare_rates['rental_rates']['annual_rate'] * utilization_rate
        annual_operated_revenue = operated_rates['rental_rates']['annual_rate'] * utilization_rate
        
        # Operating expenses (rough estimates)
        annual_maintenance = purchase_price * 0.05  # 5% of purchase price
        annual_insurance = purchase_price * 0.02  # 2% of purchase price
        annual_storage = 12000  # $1000/month average
        
        # Operated mode includes operator costs
        annual_operator_cost = 0
        if specs.get('rental_mode', 'bare').lower() == 'operated':
            annual_operator_cost = 80000 * utilization_rate  # $80k/year operator
        
        total_operating_expenses = annual_maintenance + annual_insurance + annual_storage + annual_operator_cost
        
        # Net operating income
        noi_bare = annual_bare_revenue - total_operating_expenses
        noi_operated = annual_operated_revenue - (total_operating_expenses + annual_operator_cost)
        
        # ROI calculations
        roi_bare = (noi_bare / purchase_price * 100) if purchase_price > 0 else 0
        roi_operated = (noi_operated / purchase_price * 100) if purchase_price > 0 else 0
        
        # Payback period (years)
        payback_bare = purchase_price / noi_bare if noi_bare > 0 else float('inf')
        payback_operated = purchase_price / noi_operated if noi_operated > 0 else float('inf')
        
        return {
            "rental_scenarios": {
                "bare": {
                    "annual_revenue": round(annual_bare_revenue, 2),
                    "net_operating_income": round(noi_bare, 2),
                    "roi_percent": round(roi_bare, 2),
                    "payback_years": round(payback_bare, 2) if payback_bare != float('inf') else None
                },
                "operated": {
                    "annual_revenue": round(annual_operated_revenue, 2),
                    "net_operating_income": round(noi_operated, 2),
                    "roi_percent": round(roi_operated, 2),
                    "payback_years": round(payback_operated, 2) if payback_operated != float('inf') else None
                }
            },
            "operating_expenses": {
                "annual_maintenance": round(annual_maintenance, 2),
                "annual_insurance": round(annual_insurance, 2),
                "annual_storage": annual_storage,
                "annual_operator_cost": round(annual_operator_cost, 2),
                "total": round(total_operating_expenses, 2)
            },
            "assumptions": {
                "purchase_price": purchase_price,
                "utilization_rate": utilization_rate,
                "utilization_percent": f"{utilization_rate * 100}%"
            }
        }


# Convenience function for direct usage
def calculate_smart_rental_rates(specs: Dict[str, Any], rental_mode: str = "bare",
                                 rental_csv: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to calculate smart rental rates
    
    Args:
        specs: Crane specifications dictionary
        rental_mode: "bare" or "operated"
        rental_csv: Optional path to rental rates CSV
    
    Returns:
        Dictionary containing rental rates and analysis
    """
    engine = SmartRentalEngine(rental_csv_path=rental_csv)
    return engine.calculate_rental_rates(specs, rental_mode)


# Example usage and testing
if __name__ == "__main__":
    # Example: LTR 1100 – Massachusetts
    specs = {
        "capacity": 100,
        "crane_type": "Crawler",
        "region": "Northeast",
        "year": 2022
    }
    
    print("🏗️ Crane Intelligence Platform – Smart Rental Engine v3.0")
    print("=" * 60)
    
    # Calculate bare rental rates
    bare = calculate_smart_rental_rates(specs, rental_mode="bare")
    print("\n📊 BARE RENTAL RATES:")
    print(f"  Daily:   ${bare['rental_rates']['daily_rate']:,.2f}")
    print(f"  Weekly:  ${bare['rental_rates']['weekly_rate']:,.2f}")
    print(f"  Monthly: ${bare['rental_rates']['monthly_rate']:,.2f}")
    print(f"  Annual:  ${bare['rental_rates']['annual_rate']:,.2f}")
    print(f"  Calibrated: {bare['inputs']['calibrated']}")
    
    # Calculate operated rental rates
    operated = calculate_smart_rental_rates(specs, rental_mode="operated")
    print("\n🚧 OPERATED RENTAL RATES:")
    print(f"  Daily:   ${operated['rental_rates']['daily_rate']:,.2f}")
    print(f"  Weekly:  ${operated['rental_rates']['weekly_rate']:,.2f}")
    print(f"  Monthly: ${operated['rental_rates']['monthly_rate']:,.2f}")
    print(f"  Annual:  ${operated['rental_rates']['annual_rate']:,.2f}")
    
    # Show utilization analysis
    print("\n📈 UTILIZATION SCENARIOS (Bare):")
    for util, data in bare['utilization_analysis'].items():
        print(f"  {util}: ${data['effective_monthly']:,.2f}/month (${data['annualized']:,.2f}/year)")
    
    # ROI Analysis
    engine = SmartRentalEngine()
    roi_analysis = engine.get_roi_analysis(specs, purchase_price=500000, utilization_rate=0.70)
    print("\n💰 ROI ANALYSIS (70% Utilization, $500K Purchase):")
    print(f"  Bare Mode:")
    print(f"    ROI: {roi_analysis['rental_scenarios']['bare']['roi_percent']}%")
    print(f"    Payback: {roi_analysis['rental_scenarios']['bare']['payback_years']} years")
    print(f"  Operated Mode:")
    print(f"    ROI: {roi_analysis['rental_scenarios']['operated']['roi_percent']}%")
    print(f"    Payback: {roi_analysis['rental_scenarios']['operated']['payback_years']} years")

