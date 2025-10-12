# Smart Rental Engine v3.0 - Quick Start Guide

## 🚀 5-Minute Integration Guide

### Prerequisites
```bash
pip install pandas numpy fastapi pydantic
```

### Basic Usage

#### 1. Calculate Rental Rates

```python
from app.services import SmartRentalEngine

engine = SmartRentalEngine()

specs = {
    'capacity': 100,              # Crane capacity in tons
    'crane_type': 'Crawler',      # All Terrain, Crawler, Rough Terrain, etc.
    'region': 'Northeast',        # Northeast, Southeast, Midwest, etc.
    'year': 2022                  # Manufacturing year
}

# Get bare rental rates
bare = engine.calculate_rental_rates(specs, rental_mode="bare")
print(f"Monthly Rate: ${bare['rental_rates']['monthly_rate']:,.2f}")

# Get operated rental rates
operated = engine.calculate_rental_rates(specs, rental_mode="operated")
print(f"Monthly Rate: ${operated['rental_rates']['monthly_rate']:,.2f}")
```

#### 2. ROI Analysis

```python
roi = engine.get_roi_analysis(
    specs, 
    purchase_price=800000,
    utilization_rate=0.70  # 70% utilization
)

print(f"Bare ROI: {roi['rental_scenarios']['bare']['roi_percent']}%")
print(f"Bare Payback: {roi['rental_scenarios']['bare']['payback_years']} years")
print(f"Operated ROI: {roi['rental_scenarios']['operated']['roi_percent']}%")
```

#### 3. Comprehensive Valuation

```python
from app.services import comprehensive_valuation_engine

crane = {
    'manufacturer': 'Liebherr',
    'model': 'LTM1350-6.1',
    'year': 2020,
    'capacity': 350,
    'hours': 2400,
    'region': 'Northeast',
    'crane_type': 'All Terrain',
    'asking_price': 2500000
}

result = comprehensive_valuation_engine.calculate_valuation(crane)

# Access results
print(f"FMV: ${result['fair_market_value']:,.2f}")
print(f"Deal Score: {result['deal_score']}/100")
print(f"Rental: ${result['rental_rates']['bare']['monthly_rate']:,.2f}/mo")
```

### API Endpoints

#### Get Rental Rates
```bash
curl "http://localhost:8000/api/v1/enhanced-data/rental-rates?capacity=100&region=Northeast&crane_type=Crawler&rental_mode=bare"
```

#### Get ROI Analysis
```bash
curl "http://localhost:8000/api/v1/enhanced-data/rental-roi-analysis?capacity=100&region=Northeast&purchase_price=800000&utilization_rate=0.75"
```

### Supported Values

**Regions:**
- Northeast, Southeast, Midwest, Gulf Coast, West Coast, Canada

**Crane Types:**
- All Terrain, Crawler, Rough Terrain, Truck Mounted, Tower

**Rental Modes:**
- bare (equipment only)
- operated (with operator)

### Key Features

✅ **Self-Calibrating** - Learns from CSV data automatically  
✅ **Multi-Region** - 6 regions with distinct pricing  
✅ **Multi-Type** - 5 crane types supported  
✅ **ROI Analysis** - Complete financial breakdown  
✅ **Utilization Scenarios** - 50%, 70%, 85%, 95% utilization  

### Testing

Run the test suite:
```bash
cd backend
python3 test_smart_rental_api.py
```

Expected output: **4/4 tests passed ✅**

### Updating Rates

Edit the CSV file:
```bash
backend/data/Crane_Rental_Rates_By_Region.csv
```

Add your data:
```csv
Region,Crane Type,Tonnage,Monthly Rate (USD),Operated/Bare Ratio,Market Source,Last Updated
Northeast,All Terrain,100,20000,1.45,Your Source,2025-01-15
```

Restart the service - rates automatically recalibrate!

### Common Issues

**Issue:** Rates not calibrated  
**Solution:** Check CSV file exists at `backend/data/Crane_Rental_Rates_By_Region.csv`

**Issue:** Import error  
**Solution:** Ensure you're importing from `app.services`

**Issue:** Wrong rates  
**Solution:** Verify region, crane_type, and capacity match CSV data

### Support

For full documentation, see: `SMART_RENTAL_ENGINE_V3_IMPLEMENTATION.md`

---

**Version:** 3.0 | **Status:** Production Ready ✅

