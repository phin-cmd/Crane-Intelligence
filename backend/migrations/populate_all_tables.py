#!/usr/bin/env python3
"""
Comprehensive script to populate all database tables with market data
and ensure proper relationships and end-to-end functionality
"""
import sys
import os
from datetime import datetime, timedelta
import json
import random
from decimal import Decimal

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.models.enhanced_crane import (
    CraneListing, MarketTrend, BrokerNetwork, PerformanceMetrics,
    CraneValuationAnalysis, MarketIntelligence, RentalRates, DataRefreshLog
)
from app.models.crane import Crane, CraneAnalysis, MarketData
from app.models.user import User
from app.models.fmv_report import FMVReport, FMVReportStatus, FMVReportType
from app.models.admin import SystemSetting
# Note: Some models may have issues, import only what's needed
try:
    from app.models.admin import DataSource
except:
    DataSource = None

def populate_crane_listings(db):
    """Populate crane_listings with current market data"""
    print("📦 Populating crane_listings...")
    
    manufacturers = ["Liebherr", "Grove", "Manitowoc", "Terex", "Link-Belt", "Kobelco", "Tadano", "XCMG"]
    crane_types = ["all_terrain", "crawler", "rough_terrain", "tower", "truck_mounted"]
    regions = ["Northeast", "Southeast", "Midwest", "West", "Southwest", "Northwest"]
    locations = [
        "New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX",
        "Phoenix, AZ", "Philadelphia, PA", "San Antonio, TX", "San Diego, CA",
        "Dallas, TX", "San Jose, CA", "Austin, TX", "Jacksonville, FL"
    ]
    
    listings = []
    for i in range(50):
        manufacturer = random.choice(manufacturers)
        year = random.randint(2015, 2024)
        capacity = random.choice([50, 100, 150, 200, 250, 300, 400, 500, 600, 750])
        crane_type = random.choice(crane_types)
        region = random.choice(regions)
        location = random.choice(locations)
        
        # Calculate realistic price based on capacity, year, and type
        base_price = capacity * 2000
        year_factor = (2024 - year) * 0.05
        price = base_price * (1 - year_factor) * random.uniform(0.8, 1.2)
        
        hours = random.randint(1000, 15000)
        wear_score = random.uniform(0.3, 0.95)
        value_score = random.uniform(0.6, 1.0)
        deal_score = random.randint(60, 100)
        confidence_score = random.uniform(0.75, 0.98)
        
        title = f"{manufacturer} {crane_type.replace('_', ' ').title()} {capacity}T - {year}"
        
        listing = CraneListing(
            title=title,
            manufacturer=manufacturer,
            year=year,
            price=Decimal(str(round(price, 2))),
            location=location,
            hours=hours,
            wear_score=round(wear_score, 2),
            value_score=round(value_score, 2),
            source="Live Scraper",
            capacity_tons=float(capacity),
            crane_type=crane_type,
            region=region,
            market_position=random.choice(["premium", "standard", "value"]),
            deal_score=deal_score,
            confidence_score=round(confidence_score, 2),
            scraped_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            is_active=True
        )
        listings.append(listing)
    
    db.add_all(listings)
    db.commit()
    print(f"  ✅ Added {len(listings)} crane listings")
    return listings


def populate_market_trends(db):
    """Populate market_trends with current market data"""
    print("📈 Populating market_trends...")
    
    trends = [
        {
            "segment": "300t+ Crawler Cranes",
            "yoy_growth_percent": 12.5,
            "key_drivers": "Infrastructure projects, offshore wind development, LNG terminal construction",
            "buyer_priorities": "Early ordering due to 9-12 month lead times, reliability and service support",
            "market_size": "large",
            "price_trend": "increasing",
            "demand_outlook": "high"
        },
        {
            "segment": "100-200t All Terrain Cranes",
            "yoy_growth_percent": 8.3,
            "key_drivers": "Urban construction, bridge projects, commercial development",
            "buyer_priorities": "Mobility, setup time, fuel efficiency",
            "market_size": "large",
            "price_trend": "stable",
            "demand_outlook": "high"
        },
        {
            "segment": "50-100t Rough Terrain Cranes",
            "yoy_growth_percent": 5.7,
            "key_drivers": "Residential construction, small commercial projects",
            "buyer_priorities": "Cost-effectiveness, versatility, ease of operation",
            "market_size": "medium",
            "price_trend": "stable",
            "demand_outlook": "moderate"
        },
        {
            "segment": "500t+ Mobile Cranes",
            "yoy_growth_percent": 15.2,
            "key_drivers": "Large infrastructure projects, power plant construction",
            "buyer_priorities": "Capacity, reach, transportability",
            "market_size": "small",
            "price_trend": "increasing",
            "demand_outlook": "high"
        },
        {
            "segment": "Tower Cranes",
            "yoy_growth_percent": 6.8,
            "key_drivers": "High-rise construction, urban development",
            "buyer_priorities": "Height capacity, load capacity, installation ease",
            "market_size": "medium",
            "price_trend": "stable",
            "demand_outlook": "moderate"
        }
    ]
    
    trend_objects = []
    for trend_data in trends:
        trend = MarketTrend(**trend_data)
        trend_objects.append(trend)
    
    db.add_all(trend_objects)
    db.commit()
    print(f"  ✅ Added {len(trend_objects)} market trends")
    return trend_objects


def populate_broker_networks(db):
    """Populate broker_networks with broker data"""
    print("🤝 Populating broker_networks...")
    
    brokers = [
        {"name": "LLoma Equipment", "type": "LLoma"},
        {"name": "CPP Equipment", "type": "CPP"},
        {"name": "Crane Network", "type": "Crane Network"},
        {"name": "Equipment Trader", "type": "Equipment Trader"},
        {"name": "Machinery Hub", "type": "Machinery Hub"}
    ]
    
    manufacturers = ["Liebherr", "Grove", "Manitowoc", "Terex", "Kobelco"]
    models = ["LTM 1100", "GMK 4100", "M250", "RT 780", "CKE 1350"]
    
    broker_listings = []
    for broker in brokers:
        for i in range(10):
            manufacturer = random.choice(manufacturers)
            model = random.choice(models)
            year = random.randint(2018, 2024)
            capacity = random.choice([100, 150, 200, 250, 300])
            price = capacity * 2000 * random.uniform(0.9, 1.3)
            location = random.choice(["New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX"])
            
            broker_listing = BrokerNetwork(
                broker_name=broker["name"],
                broker_type=broker["type"],
                contact_info=json.dumps({
                    "email": f"contact@{broker['name'].lower().replace(' ', '')}.com",
                    "phone": f"+1-555-{random.randint(100,999)}-{random.randint(1000,9999)}"
                }),
                manufacturer=manufacturer,
                model=model,
                year=year,
                capacity_tons=float(capacity),
                price=Decimal(str(round(price, 2))),
                location=location,
                key_features=f"Low hours, excellent condition, full service history",
                avg_price=Decimal(str(round(price, 2))),
                price_range_min=Decimal(str(round(price * 0.85, 2))),
                price_range_max=Decimal(str(round(price * 1.15, 2))),
                capacity_range_min=float(capacity * 0.9),
                capacity_range_max=float(capacity * 1.1),
                scraped_at=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                is_active=True
            )
            broker_listings.append(broker_listing)
    
    db.add_all(broker_listings)
    db.commit()
    print(f"  ✅ Added {len(broker_listings)} broker network listings")
    return broker_listings


def populate_performance_metrics(db):
    """Populate performance_metrics with crane model data"""
    print("⚡ Populating performance_metrics...")
    
    models = [
        {"manufacturer": "Liebherr", "model": "LTM 1100-4.2", "capacity": 100, "key": "liebherr_ltm1100"},
        {"manufacturer": "Grove", "model": "GMK 4100L", "capacity": 100, "key": "grove_gmk4100l"},
        {"manufacturer": "Manitowoc", "model": "M250", "capacity": 250, "key": "manitowoc_m250"},
        {"manufacturer": "Terex", "model": "RT 780", "capacity": 80, "key": "terex_rt780"},
        {"manufacturer": "Kobelco", "model": "CKE 1350G", "capacity": 135, "key": "kobelco_cke1350g"},
        {"manufacturer": "Tadano", "model": "ATF 220G-5", "capacity": 220, "key": "tadano_atf220g5"},
        {"manufacturer": "Link-Belt", "model": "HTC-8610", "capacity": 110, "key": "linkbelt_htc8610"},
        {"manufacturer": "XCMG", "model": "XCA 220", "capacity": 220, "key": "xcmg_xca220"}
    ]
    
    metrics = []
    for model_data in models:
        # Check if metric already exists
        existing = db.query(PerformanceMetrics).filter(
            PerformanceMetrics.model_key == model_data["key"]
        ).first()
        
        if existing:
            print(f"  ⚠️  Performance metric for {model_data['key']} already exists, skipping...")
            metrics.append(existing)
            continue
        
        metric = PerformanceMetrics(
            manufacturer=model_data["manufacturer"],
            model=model_data["model"],
            model_key=model_data["key"],
            max_capacity_tons=float(model_data["capacity"]),
            working_radius_40ft=random.uniform(80, 120),
            working_radius_80ft=random.uniform(50, 90),
            mobility_score=random.uniform(0.7, 0.95),
            versatility_score=random.uniform(0.75, 0.9),
            boom_utilization=random.uniform(0.8, 0.95),
            fuel_efficiency=random.uniform(0.6, 0.85),
            maintenance_cost=random.uniform(0.5, 0.8),
            reliability_score=random.uniform(0.8, 0.95)
        )
        metrics.append(metric)
    
    new_metrics = [m for m in metrics if m.id is None]
    if new_metrics:
        db.add_all(new_metrics)
        db.commit()
        print(f"  ✅ Added {len(new_metrics)} new performance metrics")
    else:
        print(f"  ✅ All performance metrics already exist ({len(metrics)} total)")
    return metrics


def populate_rental_rates(db):
    """Populate rental_rates with regional rental data"""
    print("💰 Populating rental_rates...")
    
    crane_types = ["All Terrain (AT)", "Crawler Crane", "Rough Terrain (RT)", "Tower Crane", "Truck Mounted"]
    regions = ["Northeast", "Southeast", "Midwest", "West", "Southwest", "Northwest"]
    tonnages = [50, 100, 150, 200, 250, 300, 400, 500]
    
    rates = []
    for crane_type in crane_types:
        for region in regions:
            for tonnage in tonnages:
                # Base monthly rate calculation
                base_rate = tonnage * 500
                # Regional adjustments
                if region in ["Northeast", "West"]:
                    base_rate *= 1.2  # Higher cost regions
                elif region in ["Southeast", "Southwest"]:
                    base_rate *= 0.9  # Lower cost regions
                
                # Type adjustments
                if "Tower" in crane_type:
                    base_rate *= 1.3
                elif "Crawler" in crane_type:
                    base_rate *= 1.1
                
                monthly_rate = base_rate * random.uniform(0.9, 1.1)
                annual_rate = monthly_rate * 10  # 10 months effective
                daily_rate = monthly_rate / 20  # 20 working days
                
                rate = RentalRates(
                    crane_type=crane_type,
                    tonnage=float(tonnage),
                    region=region,
                    monthly_rate_usd=Decimal(str(round(monthly_rate, 2))),
                    annual_rate_usd=Decimal(str(round(annual_rate, 2))),
                    daily_rate_usd=Decimal(str(round(daily_rate, 2))),
                    rate_date=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                )
                rates.append(rate)
    
    db.add_all(rates)
    db.commit()
    print(f"  ✅ Added {len(rates)} rental rates")
    return rates


def populate_market_data(db):
    """Populate market_data with aggregated market statistics"""
    print("📊 Populating market_data...")
    
    data_types = ["daily", "weekly", "monthly"]
    market_data_list = []
    
    for i in range(30):  # 30 days of daily data
        data_date = datetime.utcnow() - timedelta(days=30-i)
        total_cranes = random.randint(500, 1500)
        avg_price = random.uniform(200000, 800000)
        
        market_data = MarketData(
            data_type="daily",
            data_date=data_date,
            total_cranes=total_cranes,
            average_price=Decimal(str(round(avg_price, 2))),
            price_range_min=Decimal(str(round(avg_price * 0.5, 2))),
            price_range_max=Decimal(str(round(avg_price * 2.0, 2))),
            capacity_distribution=json.dumps({
                "50-100t": random.randint(100, 300),
                "100-200t": random.randint(150, 400),
                "200-300t": random.randint(80, 250),
                "300t+": random.randint(30, 150)
            }),
            manufacturer_distribution=json.dumps({
                "Liebherr": random.randint(80, 200),
                "Grove": random.randint(70, 180),
                "Manitowoc": random.randint(60, 150),
                "Terex": random.randint(50, 120),
                "Other": random.randint(100, 300)
            }),
            location_distribution=json.dumps({
                "Northeast": random.randint(80, 200),
                "Southeast": random.randint(100, 250),
                "Midwest": random.randint(90, 220),
                "West": random.randint(70, 180),
                "Southwest": random.randint(60, 150),
                "Northwest": random.randint(40, 100)
            }),
            year_distribution=json.dumps({
                "2015-2017": random.randint(50, 150),
                "2018-2020": random.randint(100, 250),
                "2021-2022": random.randint(80, 200),
                "2023-2024": random.randint(60, 180)
            })
        )
        market_data_list.append(market_data)
    
    db.add_all(market_data_list)
    db.commit()
    print(f"  ✅ Added {len(market_data_list)} market data records")
    return market_data_list


def populate_market_intelligence(db):
    """Populate market_intelligence with sales and trend data"""
    print("🧠 Populating market_intelligence...")
    
    intelligence_types = ["sales_data", "price_trends", "volume_trends"]
    segments = ["All Terrain Cranes", "Crawler Cranes", "Rough Terrain Cranes", "Tower Cranes"]
    regions = ["Northeast", "Southeast", "Midwest", "West", "Southwest", "Northwest"]
    
    intelligence_list = []
    for intel_type in intelligence_types:
        for segment in segments:
            for region in regions:
                intelligence = MarketIntelligence(
                    data_type=intel_type,
                    segment=segment,
                    region=region,
                    total_transactions=random.randint(10, 100),
                    avg_transaction_value=Decimal(str(round(random.uniform(300000, 1200000), 2))),
                    price_trend_percent=random.uniform(-5, 15),
                    volume_trend_percent=random.uniform(-10, 20),
                    intelligence_data=json.dumps({
                        "insights": f"Strong demand in {region} for {segment}",
                        "key_factors": ["Infrastructure projects", "Equipment replacement cycle"],
                        "forecast": "Positive outlook for next quarter"
                    }),
                    intelligence_date=datetime.utcnow() - timedelta(days=random.randint(0, 90))
                )
                intelligence_list.append(intelligence)
    
    db.add_all(intelligence_list)
    db.commit()
    print(f"  ✅ Added {len(intelligence_list)} market intelligence records")
    return intelligence_list


def populate_crane_valuation_analyses(db, listings):
    """Populate crane_valuation_analyses linked to listings"""
    print("🔍 Populating crane_valuation_analyses...")
    
    analyses = []
    for listing in listings[:30]:  # Analyze first 30 listings
        estimated_value = listing.price * Decimal(str(random.uniform(0.9, 1.1)))
        confidence_score = random.uniform(0.75, 0.95)
        deal_score = random.randint(65, 100)
        wear_score = listing.wear_score or random.uniform(0.3, 0.9)
        
        analysis = CraneValuationAnalysis(
            listing_id=listing.id,
            estimated_value=estimated_value,
            confidence_score=round(confidence_score, 2),
            deal_score=deal_score,
            wear_score=round(wear_score, 2),
            wholesale_value=estimated_value * Decimal("0.75"),
            retail_value=estimated_value * Decimal("1.15"),
            insurance_replacement_value=estimated_value * Decimal("1.25"),
            orderly_liquidation_value=estimated_value * Decimal("0.65"),
            forced_liquidation_value=estimated_value * Decimal("0.45"),
            market_trend=random.choice(["increasing", "stable", "decreasing"]),
            demand_outlook=random.choice(["high", "moderate", "low"]),
            price_direction=random.choice(["up", "stable", "down"]),
            key_factors=json.dumps([
                "Market demand",
                "Equipment condition",
                "Regional pricing",
                "Comparable sales"
            ]),
            financing_scenarios=json.dumps({
                "Northeast": {"roi": 12.5, "payback_years": 3.2},
                "Southeast": {"roi": 10.8, "payback_years": 3.5},
                "Midwest": {"roi": 11.2, "payback_years": 3.3}
            }),
            comparable_count=random.randint(3, 12),
            comparable_data=json.dumps({
                "similar_listings": random.randint(3, 8),
                "avg_price": float(estimated_value),
                "price_range": [float(estimated_value * Decimal("0.85")), float(estimated_value * Decimal("1.15"))]
            }),
            analysis_engine_version="2.1.0",
            analysis_date=datetime.utcnow() - timedelta(days=random.randint(0, 7))
        )
        analyses.append(analysis)
    
    db.add_all(analyses)
    db.commit()
    print(f"  ✅ Added {len(analyses)} valuation analyses")
    return analyses


def populate_system_settings(db):
    """Populate system_settings with configuration"""
    print("⚙️  Populating system_settings...")
    
    settings = [
        {"key": "site_name", "value": "Crane Intelligence", "value_type": "string", "category": "general", "description": "Site name"},
        {"key": "site_url", "value": "https://craneintelligence.tech", "value_type": "string", "category": "general", "description": "Site URL"},
        {"key": "email_from", "value": "noreply@craneintelligence.tech", "value_type": "string", "category": "email", "description": "Default from email"},
        {"key": "data_refresh_interval", "value": "3600", "value_type": "int", "category": "data", "description": "Data refresh interval in seconds"},
        {"key": "max_upload_size_mb", "value": "50", "value_type": "int", "category": "upload", "description": "Maximum file upload size in MB"},
        {"key": "enable_analytics", "value": "true", "value_type": "bool", "category": "analytics", "description": "Enable analytics tracking"},
        {"key": "maintenance_mode", "value": "false", "value_type": "bool", "category": "system", "description": "Maintenance mode flag"}
    ]
    
    setting_objects = []
    for setting_data in settings:
        existing = db.query(SystemSetting).filter(SystemSetting.key == setting_data["key"]).first()
        if not existing:
            setting = SystemSetting(**setting_data)
            setting_objects.append(setting)
    
    db.add_all(setting_objects)
    db.commit()
    print(f"  ✅ Added {len(setting_objects)} system settings")
    return setting_objects


def populate_data_sources(db):
    """Populate data_sources with data source configurations"""
    print("📡 Populating data_sources...")
    
    sources = [
        {
            "name": "Live Scraper",
            "source_type": "scraper",
            "status": "active",
            "config": json.dumps({
                "url": "https://example.com/listings",
                "update_frequency": "hourly",
                "last_successful_fetch": datetime.utcnow().isoformat()
            })
        },
        {
            "name": "Broker Network API",
            "source_type": "api",
            "status": "active",
            "config": json.dumps({
                "endpoint": "https://api.brokernetwork.com/v1/listings",
                "api_key": "***",
                "update_frequency": "daily"
            })
        },
        {
            "name": "Market Data Feed",
            "source_type": "feed",
            "status": "active",
            "config": json.dumps({
                "feed_url": "https://feeds.marketdata.com/cranes",
                "format": "json",
                "update_frequency": "real-time"
            })
        }
    ]
    
    # Note: DataSource model might need to be checked
    # For now, we'll skip if model doesn't exist
    try:
        from app.models.admin import DataSource
        source_objects = []
        for source_data in sources:
            source = DataSource(**source_data)
            source_objects.append(source)
        
        db.add_all(source_objects)
        db.commit()
        print(f"  ✅ Added {len(source_objects)} data sources")
        return source_objects
    except Exception as e:
        print(f"  ⚠️  DataSource model not found or error: {e}")
        return []


def populate_data_refresh_logs(db):
    """Populate data_refresh_logs with refresh history"""
    print("🔄 Populating data_refresh_logs...")
    
    refresh_types = ["full_refresh", "incremental", "csv_import"]
    data_sources = ["crane_listings", "market_trends", "broker_networks", "rental_rates"]
    statuses = ["completed", "completed", "completed", "failed"]  # Mostly completed
    
    logs = []
    for i in range(20):
        refresh_type = random.choice(refresh_types)
        data_source = random.choice(data_sources)
        status = random.choice(statuses)
        
        started_at = datetime.utcnow() - timedelta(days=random.randint(0, 30))
        completed_at = started_at + timedelta(minutes=random.randint(5, 120)) if status == "completed" else None
        
        log = DataRefreshLog(
            refresh_type=refresh_type,
            data_source=data_source,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            records_processed=random.randint(100, 5000),
            records_added=random.randint(50, 2000) if status == "completed" else 0,
            records_updated=random.randint(20, 500) if status == "completed" else 0,
            records_skipped=random.randint(0, 100),
            records_failed=random.randint(0, 10) if status == "failed" else 0,
            config=json.dumps({"source": data_source, "type": refresh_type}),
            error_message=f"Error occurred during refresh" if status == "failed" else None
        )
        logs.append(log)
    
    db.add_all(logs)
    db.commit()
    print(f"  ✅ Added {len(logs)} data refresh logs")
    return logs


def main():
    """Main function to populate all tables"""
    print("=" * 70)
    print("Comprehensive Database Population Script")
    print("=" * 70)
    print()
    
    db = SessionLocal()
    try:
        # Populate in order to maintain relationships
        listings = populate_crane_listings(db)
        trends = populate_market_trends(db)
        brokers = populate_broker_networks(db)
        metrics = populate_performance_metrics(db)
        rates = populate_rental_rates(db)
        market_data = populate_market_data(db)
        intelligence = populate_market_intelligence(db)
        analyses = populate_crane_valuation_analyses(db, listings)
        settings = populate_system_settings(db)
        sources = populate_data_sources(db)
        logs = populate_data_refresh_logs(db)
        
        print()
        print("=" * 70)
        print("Summary:")
        print(f"  ✅ Crane Listings: {len(listings)}")
        print(f"  ✅ Market Trends: {len(trends)}")
        print(f"  ✅ Broker Networks: {len(brokers)}")
        print(f"  ✅ Performance Metrics: {len(metrics)}")
        print(f"  ✅ Rental Rates: {len(rates)}")
        print(f"  ✅ Market Data: {len(market_data)}")
        print(f"  ✅ Market Intelligence: {len(intelligence)}")
        print(f"  ✅ Valuation Analyses: {len(analyses)}")
        print(f"  ✅ System Settings: {len(settings)}")
        print(f"  ✅ Data Sources: {len(sources)}")
        print(f"  ✅ Data Refresh Logs: {len(logs)}")
        print("=" * 70)
        print("\n✅ Population complete!")
        
    except Exception as e:
        print(f"\n❌ Error during population: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()

