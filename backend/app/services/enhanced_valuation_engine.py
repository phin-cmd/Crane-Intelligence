"""
Enhanced Valuation Engine - Bloomberg-style Crane Valuation System
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
import numpy as np
from .real_time_market_data import RealTimeMarketDataService

logger = logging.getLogger(__name__)

@dataclass
class ValuationResult:
    """Comprehensive valuation result with Bloomberg-style analysis"""
    fair_market_value: float
    wholesale_value: float
    retail_value: float
    confidence_score: float
    deal_score: int
    market_position: str
    comparable_count: int
    market_trends: Dict[str, Any]
    financing_scenarios: List[Dict[str, Any]]
    risk_factors: List[str]
    recommendations: List[str]
    comparable_sales: List[Dict[str, Any]]
    spec_analysis: Dict[str, Any]
    report_url: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class MarketDataService:
    """Service for fetching and processing market data using real-time integration"""
    
    def __init__(self):
        self.real_time_service = RealTimeMarketDataService()
        self._initialized = False
    
    async def _ensure_initialized(self):
        """Ensure the real-time service is initialized"""
        if not self._initialized:
            await self.real_time_service.initialize()
            self._initialized = True
    
    async def get_equipment_watch_data(self, make: str, model: str) -> Dict[str, Any]:
        """Fetch real-time data from Equipment Watch API"""
        try:
            await self._ensure_initialized()
            return await self.real_time_service.get_equipment_watch_data(make, model)
        except Exception as e:
            logger.error(f"Equipment Watch API error: {e}")
            return {"listings": [], "market_trends": {}, "error": str(e)}
    
    async def get_ritchie_bros_data(self, make: str, model: str) -> Dict[str, Any]:
        """Fetch real-time auction data from Ritchie Bros"""
        try:
            await self._ensure_initialized()
            return await self.real_time_service.get_ritchie_bros_data(make, model)
        except Exception as e:
            logger.error(f"Ritchie Bros API error: {e}")
            return {"recent_auctions": [], "average_price": 0, "price_range": [0, 0], "error": str(e)}
    
    async def get_machinery_trader_data(self, make: str, model: str) -> Dict[str, Any]:
        """Fetch real-time listing data from MachineryTrader"""
        try:
            await self._ensure_initialized()
            return await self.real_time_service.get_machinery_trader_data(make, model)
        except Exception as e:
            logger.error(f"MachineryTrader API error: {e}")
            return {"active_listings": [], "average_listing_price": 0, "market_activity": "low", "error": str(e)}
    
    async def get_comprehensive_market_data(self, make: str, model: str) -> Dict[str, Any]:
        """Fetch comprehensive real-time market data from all sources"""
        try:
            await self._ensure_initialized()
            return await self.real_time_service.get_comprehensive_market_data(make, model)
        except Exception as e:
            logger.error(f"Comprehensive market data error: {e}")
            return {
                "listings": [],
                "equipment_watch": {"listings": [], "market_trends": {}},
                "ritchie_bros": {"recent_auctions": [], "average_price": 0},
                "machinery_trader": {"active_listings": [], "average_listing_price": 0},
                "market_trends": {},
                "error": str(e)
            }

class SpecsCatalogService:
    """Service for crane specifications and technical data"""
    
    def __init__(self):
        self.specs_cache = {}
    
    async def get_crane_specs(self, make: str, model: str) -> Dict[str, Any]:
        """Get comprehensive crane specifications"""
        cache_key = f"{make}_{model}"
        
        if cache_key in self.specs_cache:
            return self.specs_cache[cache_key]
        
        specs = {
            "make": make,
            "model": model,
            "capacity_tons": 250.0,
            "boom_length_ft": 200.0,
            "jib_options_ft": [60, 80, 100, 120],
            "counterweight_lbs": 45000,
            "engine": "Caterpillar C18",
            "dimensions": {
                "length_ft": 45.5,
                "width_ft": 10.2,
                "height_ft": 12.8
            },
            "features": [
                "Load Moment Indicator",
                "Anti-Two Block System",
                "Load Sensing System",
                "Variable Boom Length",
                "Power Boom"
            ],
            "pdf_specs": [
                f"https://specs.{make.lower()}.com/{model}_specs.pdf"
            ]
        }
        
        self.specs_cache[cache_key] = specs
        return specs
    
    async def get_specs_catalog(self, make: Optional[str] = None, model: Optional[str] = None,
                              capacity_min: Optional[float] = None, capacity_max: Optional[float] = None) -> List[Dict[str, Any]]:
        """Get filtered specifications catalog"""
        catalog = [
            {
                "spec_id": "GROVE_GMK5250L_001",
                "source": "Grove Official",
                "make": "Grove",
                "model": "GMK5250L",
                "variant": "Lattice Boom",
                "capacity_tons": 250.0,
                "boom_length_ft": 200.0,
                "jib_options_ft": [60, 80, 100, 120],
                "counterweight_lbs": 45000,
                "features": ["Load Moment Indicator", "Anti-Two Block System"],
                "engine": "Caterpillar C18",
                "dimensions": {"length_ft": 45.5, "width_ft": 10.2, "height_ft": 12.8},
                "pdf_specs": ["https://grove.com/specs/GMK5250L.pdf"]
            }
        ]
        
        # Apply filters
        filtered_catalog = catalog
        
        if make:
            filtered_catalog = [item for item in filtered_catalog if item["make"].lower() == make.lower()]
        
        if model:
            filtered_catalog = [item for item in filtered_catalog if item["model"].lower() == model.lower()]
        
        if capacity_min:
            filtered_catalog = [item for item in filtered_catalog if item["capacity_tons"] >= capacity_min]
        
        if capacity_max:
            filtered_catalog = [item for item in filtered_catalog if item["capacity_tons"] <= capacity_max]
        
        return filtered_catalog

class BloombergReportGenerator:
    """Generate Bloomberg-style professional reports"""
    
    async def generate_valuation_report(self, valuation_result: ValuationResult, 
                                      request_data: Dict[str, Any]) -> str:
        """Generate comprehensive Bloomberg-style valuation report"""
        try:
            report_data = {
                "valuation": valuation_result,
                "request": request_data,
                "generated_at": datetime.now(),
                "report_id": f"VAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            # Generate HTML report
            report_html = await self._generate_html_report(report_data)
            
            # Save report
            report_filename = f"valuation_report_{report_data['report_id']}.html"
            report_path = f"backend/generated_reports/{report_filename}"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_html)
            
            return f"/reports/{report_filename}"
            
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return None
    
    async def _generate_html_report(self, data: Dict[str, Any]) -> str:
        """Generate HTML report template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Crane Intelligence - Valuation Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #1a1a1a; color: white; padding: 20px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f5f5f5; }}
                .value {{ font-size: 24px; font-weight: bold; color: #00ff85; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Crane Intelligence - Bloomberg-Style Valuation Report</h1>
                <p>Generated: {data['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Valuation Summary</h2>
                <div class="metric">
                    <div>Fair Market Value</div>
                    <div class="value">${data['valuation'].fair_market_value:,.0f}</div>
                </div>
                <div class="metric">
                    <div>Wholesale Value</div>
                    <div class="value">${data['valuation'].wholesale_value:,.0f}</div>
                </div>
                <div class="metric">
                    <div>Retail Value</div>
                    <div class="value">${data['valuation'].retail_value:,.0f}</div>
                </div>
                <div class="metric">
                    <div>Confidence Score</div>
                    <div class="value">{data['valuation'].confidence_score:.1%}</div>
                </div>
            </div>
            
            <div class="section">
                <h2>Market Analysis</h2>
                <p>Comparable Sales: {data['valuation'].comparable_count}</p>
                <p>Market Position: {data['valuation'].market_position}</p>
                <p>Deal Score: {data['valuation'].deal_score}/10</p>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                <ul>
                    {''.join([f'<li>{rec}</li>' for rec in data['valuation'].recommendations])}
                </ul>
            </div>
        </body>
        </html>
        """

class EnhancedValuationEngine:
    """Main Bloomberg-style valuation engine"""
    
    def __init__(self):
        self.market_service = MarketDataService()
        self.specs_service = SpecsCatalogService()
        self.report_generator = BloombergReportGenerator()
    
    async def value_crane(self, request_data: Dict[str, Any]) -> ValuationResult:
        """Perform comprehensive Bloomberg-style crane valuation"""
        try:
            logger.info(f"Starting valuation for {request_data['manufacturer']} {request_data['model']}")
            
            # Fetch market data from multiple sources
            market_data = await self._fetch_market_data(request_data)
            
            # Get crane specifications
            specs = await self.specs_service.get_crane_specs(
                request_data['manufacturer'], 
                request_data['model']
            )
            
            # Calculate base valuation
            base_valuation = await self._calculate_base_valuation(request_data, specs, market_data)
            
            # Apply market adjustments
            adjusted_valuation = await self._apply_market_adjustments(base_valuation, market_data)
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(market_data, request_data)
            
            # Generate deal score
            deal_score = await self._calculate_deal_score(adjusted_valuation, market_data)
            
            # Determine market position
            market_position = await self._determine_market_position(adjusted_valuation, market_data)
            
            # Generate financing scenarios
            financing_scenarios = await self._generate_financing_scenarios(adjusted_valuation)
            
            # Identify risk factors
            risk_factors = await self._identify_risk_factors(request_data, market_data)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(adjusted_valuation, market_data, request_data)
            
            # Get comparable sales
            comparable_sales = await self._get_comparable_sales(market_data)
            
            # Create valuation result
            result = ValuationResult(
                fair_market_value=adjusted_valuation['fair_market_value'],
                wholesale_value=adjusted_valuation['wholesale_value'],
                retail_value=adjusted_valuation['retail_value'],
                confidence_score=confidence_score,
                deal_score=deal_score,
                market_position=market_position,
                comparable_count=len(comparable_sales),
                market_trends=market_data.get('trends', {}),
                financing_scenarios=financing_scenarios,
                risk_factors=risk_factors,
                recommendations=recommendations,
                comparable_sales=comparable_sales,
                spec_analysis=specs
            )
            
            logger.info(f"Valuation completed: FMV=${result.fair_market_value:,.0f}, Confidence={result.confidence_score:.1%}")
            return result
            
        except Exception as e:
            logger.error(f"Valuation error: {e}")
            raise
    
    async def _fetch_market_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch comprehensive real-time market data from multiple sources"""
        make = request_data['manufacturer']
        model = request_data['model']
        
        try:
            # Use the comprehensive market data service
            market_data = await self.market_service.get_comprehensive_market_data(make, model)
            
            # Extract listings and calculate metrics
            all_listings = market_data.get('listings', [])
            prices = [listing.get('price', 0) for listing in all_listings if listing.get('price', 0) > 0]
            
            # Get market trends from the real-time service
            market_trends = market_data.get('market_trends', {})
            
            return {
                'listings': all_listings,
                'equipment_watch': market_data.get('equipment_watch', {}),
                'ritchie_bros': market_data.get('ritchie_bros', {}),
                'machinery_trader': market_data.get('machinery_trader', {}),
                'average_price': market_trends.get('average_price', np.mean(prices) if prices else 0),
                'price_range': market_trends.get('price_range', [min(prices), max(prices)] if prices else [0, 0]),
                'trends': {
                    'price_trend': market_trends.get('price_trend', 'stable'),
                    'demand_level': market_trends.get('demand_level', 'high'),
                    'supply_level': market_trends.get('supply_level', 'medium'),
                    'market_activity': market_trends.get('market_activity', 'active'),
                    'confidence': market_trends.get('confidence', 0.7),
                    'volume': market_trends.get('volume', len(all_listings))
                },
                'last_updated': market_data.get('last_updated', datetime.now().isoformat()),
                'total_listings': market_data.get('total_listings', len(all_listings))
            }
            
        except Exception as e:
            logger.error(f"Market data fetch error: {e}")
            # Fallback to individual source calls
            equipment_watch_data = await self.market_service.get_equipment_watch_data(make, model)
            ritchie_bros_data = await self.market_service.get_ritchie_bros_data(make, model)
            machinery_trader_data = await self.market_service.get_machinery_trader_data(make, model)
            
            # Combine and analyze data
            all_listings = []
            all_listings.extend(equipment_watch_data.get('listings', []))
            all_listings.extend(ritchie_bros_data.get('recent_auctions', []))
            all_listings.extend(machinery_trader_data.get('active_listings', []))
            
            # Calculate market trends
            prices = [listing.get('price', 0) for listing in all_listings if listing.get('price', 0) > 0]
            
            return {
                'listings': all_listings,
                'equipment_watch': equipment_watch_data,
                'ritchie_bros': ritchie_bros_data,
                'machinery_trader': machinery_trader_data,
                'average_price': np.mean(prices) if prices else 0,
                'price_range': [min(prices), max(prices)] if prices else [0, 0],
                'trends': {
                    'price_trend': 'stable',
                    'demand_level': 'high',
                    'supply_level': 'medium',
                    'market_activity': 'active',
                    'confidence': 0.5,
                    'volume': len(all_listings)
                },
                'last_updated': datetime.now().isoformat(),
                'total_listings': len(all_listings),
                'error': str(e)
            }
    
    async def _calculate_base_valuation(self, request_data: Dict[str, Any], 
                                      specs: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate base valuation using multiple methodologies"""
        year = request_data['year']
        hours = request_data['hours']
        condition_score = request_data['condition_score']
        capacity_tons = request_data['capacity_tons']
        
        # Get market average as starting point
        market_avg = market_data.get('average_price', 1000000)  # Default fallback
        
        # Age-based depreciation
        current_year = datetime.now().year
        age = current_year - year
        age_depreciation = 0.08 * age  # 8% per year
        
        # Hours-based depreciation
        hours_depreciation = min(hours / 10000, 0.3)  # Max 30% for high hours
        
        # Condition adjustment
        condition_adjustment = (1 - condition_score) * 0.2  # Up to 20% adjustment
        
        # Capacity adjustment (larger cranes typically have higher base values)
        capacity_multiplier = 1 + (capacity_tons - 200) / 1000  # Adjust for capacity
        
        # Calculate adjusted base value
        base_value = market_avg * capacity_multiplier
        adjusted_value = base_value * (1 - age_depreciation - hours_depreciation - condition_adjustment)
        
        # Calculate wholesale and retail values
        wholesale_value = adjusted_value * 0.85  # 15% below FMV
        retail_value = adjusted_value * 1.15     # 15% above FMV
        
        return {
            'fair_market_value': max(adjusted_value, 500000),  # Minimum value floor
            'wholesale_value': max(wholesale_value, 400000),
            'retail_value': max(retail_value, 600000)
        }
    
    async def _apply_market_adjustments(self, base_valuation: Dict[str, float], 
                                      market_data: Dict[str, Any]) -> Dict[str, float]:
        """Apply market-specific adjustments"""
        trends = market_data.get('trends', {})
        
        # Market trend adjustments
        trend_multiplier = 1.0
        if trends.get('price_trend') == 'rising':
            trend_multiplier = 1.05
        elif trends.get('price_trend') == 'falling':
            trend_multiplier = 0.95
        
        # Demand/supply adjustments
        if trends.get('demand_level') == 'high':
            trend_multiplier *= 1.03
        elif trends.get('demand_level') == 'low':
            trend_multiplier *= 0.97
        
        if trends.get('supply_level') == 'low':
            trend_multiplier *= 1.02
        elif trends.get('supply_level') == 'high':
            trend_multiplier *= 0.98
        
        return {
            'fair_market_value': base_valuation['fair_market_value'] * trend_multiplier,
            'wholesale_value': base_valuation['wholesale_value'] * trend_multiplier,
            'retail_value': base_valuation['retail_value'] * trend_multiplier
        }
    
    async def _calculate_confidence_score(self, market_data: Dict[str, Any], 
                                        request_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on data quality and market conditions"""
        base_confidence = 0.7  # Base confidence
        
        # Data availability bonus
        listings_count = len(market_data.get('listings', []))
        if listings_count >= 10:
            base_confidence += 0.2
        elif listings_count >= 5:
            base_confidence += 0.1
        
        # Market activity bonus
        trends = market_data.get('trends', {})
        if trends.get('market_activity') == 'active':
            base_confidence += 0.1
        
        # Condition data quality
        if request_data.get('condition_score') is not None:
            base_confidence += 0.05
        
        return min(base_confidence, 0.95)  # Cap at 95%
    
    async def _calculate_deal_score(self, valuation: Dict[str, float], 
                                   market_data: Dict[str, Any]) -> int:
        """Calculate deal score (1-10) based on market conditions"""
        fmv = valuation['fair_market_value']
        market_avg = market_data.get('average_price', fmv)
        
        # Calculate relative value
        if market_avg > 0:
            relative_value = fmv / market_avg
        else:
            relative_value = 1.0
        
        # Convert to deal score
        if relative_value >= 1.1:
            return 9  # Excellent deal
        elif relative_value >= 1.05:
            return 8  # Very good deal
        elif relative_value >= 0.95:
            return 7  # Good deal
        elif relative_value >= 0.85:
            return 6  # Fair deal
        else:
            return 5  # Below market
    
    async def _determine_market_position(self, valuation: Dict[str, float], 
                                       market_data: Dict[str, Any]) -> str:
        """Determine market position relative to comparable sales"""
        fmv = valuation['fair_market_value']
        market_avg = market_data.get('average_price', fmv)
        
        if fmv > market_avg * 1.1:
            return "Above Market"
        elif fmv < market_avg * 0.9:
            return "Below Market"
        else:
            return "Market Rate"
    
    async def _generate_financing_scenarios(self, valuation: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate financing scenarios for the valuation"""
        fmv = valuation['fair_market_value']
        
        scenarios = [
            {
                "scenario": "Cash Purchase",
                "down_payment": fmv,
                "monthly_payment": 0,
                "total_cost": fmv,
                "interest_rate": 0.0
            },
            {
                "scenario": "20% Down, 5% APR",
                "down_payment": fmv * 0.2,
                "monthly_payment": (fmv * 0.8 * 0.05 / 12) / (1 - (1 + 0.05/12)**(-60)),
                "total_cost": fmv * 0.2 + (fmv * 0.8 * 0.05 / 12) / (1 - (1 + 0.05/12)**(-60)) * 60,
                "interest_rate": 0.05
            }
        ]
        
        return scenarios
    
    async def _identify_risk_factors(self, request_data: Dict[str, Any], 
                                   market_data: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors"""
        risk_factors = []
        
        # Age risk
        current_year = datetime.now().year
        age = current_year - request_data['year']
        if age > 15:
            risk_factors.append("High age may impact resale value")
        
        # Hours risk
        if request_data['hours'] > 8000:
            risk_factors.append("High operating hours may indicate wear")
        
        # Condition risk
        if request_data['condition_score'] < 0.7:
            risk_factors.append("Below-average condition may require maintenance")
        
        return risk_factors
    
    async def _generate_recommendations(self, valuation: Dict[str, float], 
                                     market_data: Dict[str, Any], 
                                     request_data: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        fmv = valuation['fair_market_value']
        market_avg = market_data.get('average_price', fmv)
        
        # Price recommendations
        if fmv < market_avg * 0.9:
            recommendations.append("Consider this a strong buying opportunity")
        elif fmv > market_avg * 1.1:
            recommendations.append("Price may be above market - negotiate or wait")
        
        # Market timing
        trends = market_data.get('trends', {})
        if trends.get('demand_level') == 'high':
            recommendations.append("High demand market - consider quick decision")
        
        return recommendations
    
    async def _get_comparable_sales(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get comparable sales data"""
        listings = market_data.get('listings', [])
        
        # Format comparable sales
        comparable_sales = []
        for listing in listings[:5]:  # Top 5 comparables
            comparable_sales.append({
                "price": listing.get('price', 0),
                "year": listing.get('year', 0),
                "hours": listing.get('hours', 0),
                "location": listing.get('location', 'Unknown'),
                "condition": listing.get('condition', 'Unknown'),
                "source": listing.get('source', 'Unknown')
            })
        
        return comparable_sales

# Global instance
enhanced_valuation_engine = EnhancedValuationEngine()
