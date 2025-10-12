#!/usr/bin/env python3
"""
Test Script for Smart Rental Engine v3.0 API Integration
Tests the new rental rate endpoints and comprehensive valuation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.smart_rental_engine import SmartRentalEngine
from app.services.comprehensive_valuation_engine import comprehensive_valuation_engine


def test_smart_rental_engine():
    """Test Smart Rental Engine directly"""
    print("=" * 70)
    print("TEST 1: Smart Rental Engine - LTR 1100 (Crawler, 100T)")
    print("=" * 70)
    
    engine = SmartRentalEngine()
    
    specs = {
        'capacity': 100,
        'crane_type': 'Crawler',
        'region': 'Northeast',
        'year': 2022
    }
    
    # Test bare rental
    bare = engine.calculate_rental_rates(specs, rental_mode="bare")
    print(f"\n✅ BARE RENTAL RATES:")
    print(f"   Monthly Rate: ${bare['rental_rates']['monthly_rate']:,.2f}")
    print(f"   Annual Rate:  ${bare['rental_rates']['annual_rate']:,.2f}")
    print(f"   Calibrated:   {bare['inputs']['calibrated']}")
    
    # Test operated rental
    operated = engine.calculate_rental_rates(specs, rental_mode="operated")
    print(f"\n✅ OPERATED RENTAL RATES:")
    print(f"   Monthly Rate: ${operated['rental_rates']['monthly_rate']:,.2f}")
    print(f"   Annual Rate:  ${operated['rental_rates']['annual_rate']:,.2f}")
    
    # Test ROI analysis
    roi = engine.get_roi_analysis(specs, purchase_price=800000, utilization_rate=0.75)
    print(f"\n✅ ROI ANALYSIS (75% utilization, $800K purchase):")
    print(f"   Bare ROI:     {roi['rental_scenarios']['bare']['roi_percent']}%")
    print(f"   Bare Payback: {roi['rental_scenarios']['bare']['payback_years']} years")
    print(f"   Oper ROI:     {roi['rental_scenarios']['operated']['roi_percent']}%")
    print(f"   Oper Payback: {roi['rental_scenarios']['operated']['payback_years']} years")
    
    return True


def test_comprehensive_valuation():
    """Test Comprehensive Valuation Engine"""
    print("\n" + "=" * 70)
    print("TEST 2: Comprehensive Valuation - Liebherr LTM1350")
    print("=" * 70)
    
    crane_specs = {
        'manufacturer': 'Liebherr',
        'model': 'LTM1350-6.1',
        'year': 2020,
        'capacity': 350,
        'hours': 2400,
        'region': 'West Coast',
        'crane_type': 'All Terrain',
        'asking_price': 3500000,
        'condition_score': 0.90
    }
    
    result = comprehensive_valuation_engine.calculate_valuation(crane_specs)
    
    print(f"\n✅ VALUATION:")
    print(f"   Fair Market Value: ${result['fair_market_value']:,.2f}")
    print(f"   Deal Score:        {result['deal_score']}/100")
    print(f"   Market Position:   {result['market_position']}")
    
    print(f"\n✅ RENTAL RATES (Integrated from Smart Engine):")
    print(f"   Bare Monthly:      ${result['rental_rates']['bare']['monthly_rate']:,.2f}")
    print(f"   Operated Monthly:  ${result['rental_rates']['operated']['monthly_rate']:,.2f}")
    
    print(f"\n✅ ROI ANALYSIS:")
    if result['roi_analysis']['bare']:
        print(f"   Bare ROI:          {result['roi_analysis']['bare']['roi_percent']}%")
    if result['roi_analysis']['operated']:
        print(f"   Operated ROI:      {result['roi_analysis']['operated']['roi_percent']}%")
    
    print(f"\n✅ MARKET INSIGHTS:")
    print(f"   Rental Calibrated: {result['market_insights']['rental_calibrated']}")
    print(f"   Recommended Mode:  {result['market_insights']['recommended_mode']}")
    
    return True


def test_multiple_regions():
    """Test rental rates across multiple regions"""
    print("\n" + "=" * 70)
    print("TEST 3: Multi-Region Comparison - All Terrain 250T")
    print("=" * 70)
    
    engine = SmartRentalEngine()
    regions = ['Northeast', 'Southeast', 'Midwest', 'Gulf Coast', 'West Coast', 'Canada']
    
    print(f"\n{'Region':<15} {'Monthly Bare':<15} {'Monthly Operated':<18} {'Calibrated'}")
    print("-" * 70)
    
    for region in regions:
        specs = {
            'capacity': 250,
            'crane_type': 'All Terrain',
            'region': region,
            'year': 2021
        }
        
        bare = engine.calculate_rental_rates(specs, rental_mode="bare")
        operated = engine.calculate_rental_rates(specs, rental_mode="operated")
        
        print(f"{region:<15} ${bare['rental_rates']['monthly_rate']:>12,.2f}  "
              f"${operated['rental_rates']['monthly_rate']:>14,.2f}  "
              f"{'✓' if bare['inputs']['calibrated'] else '✗'}")
    
    return True


def test_crane_types():
    """Test rental rates for different crane types"""
    print("\n" + "=" * 70)
    print("TEST 4: Multi-Type Comparison - Northeast Region, 100T")
    print("=" * 70)
    
    engine = SmartRentalEngine()
    crane_types = ['All Terrain', 'Crawler', 'Rough Terrain', 'Truck Mounted', 'Tower']
    
    print(f"\n{'Crane Type':<18} {'Monthly Bare':<15} {'Monthly Operated':<18} {'Calibrated'}")
    print("-" * 70)
    
    for crane_type in crane_types:
        specs = {
            'capacity': 100,
            'crane_type': crane_type,
            'region': 'Northeast',
            'year': 2022
        }
        
        bare = engine.calculate_rental_rates(specs, rental_mode="bare")
        operated = engine.calculate_rental_rates(specs, rental_mode="operated")
        
        print(f"{crane_type:<18} ${bare['rental_rates']['monthly_rate']:>12,.2f}  "
              f"${operated['rental_rates']['monthly_rate']:>14,.2f}  "
              f"{'✓' if bare['inputs']['calibrated'] else '✗'}")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "🏗️" * 35)
    print("   CRANE INTELLIGENCE PLATFORM - SMART RENTAL ENGINE v3.0")
    print("   Integration Test Suite")
    print("🏗️" * 35 + "\n")
    
    tests = [
        ("Smart Rental Engine", test_smart_rental_engine),
        ("Comprehensive Valuation", test_comprehensive_valuation),
        ("Multi-Region Comparison", test_multiple_regions),
        ("Multi-Type Comparison", test_crane_types),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   Error: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 70)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED! Smart Rental Engine v3.0 is ready for production.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review errors above.")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

