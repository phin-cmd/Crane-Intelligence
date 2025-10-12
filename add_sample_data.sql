-- Add sample crane listings
INSERT INTO crane_listings (manufacturer, model, year, capacity, condition, location, price, mileage, description)
VALUES 
('Liebherr', 'LTM 1200-5.1', 2018, 200.0, 'excellent', 'Houston, TX', 850000.00, 5000, 'Excellent condition mobile crane with low hours'),
('Manitowoc', 'MLC300', 2020, 300.0, 'excellent', 'Chicago, IL', 1200000.00, 2000, 'Crawler crane in pristine condition'),
('Grove', 'GMK5250L', 2019, 250.0, 'good', 'Los Angeles, CA', 750000.00, 8000, 'All terrain crane with recent service'),
('Tadano', 'ATF 130G-5', 2017, 130.0, 'good', 'Miami, FL', 680000.00, 12000, 'Well-maintained all terrain crane'),
('Link-Belt', 'RTC-8090 II', 2021, 90.0, 'excellent', 'Denver, CO', 920000.00, 1500, 'Nearly new rough terrain crane'),
('Terex', 'AC 100/4L', 2016, 100.0, 'fair', 'Seattle, WA', 550000.00, 15000, 'Reliable all terrain crane'),
('Kobelco', 'CK1600G-2', 2019, 160.0, 'excellent', 'Boston, MA', 980000.00, 4500, 'High-capacity crawler crane'),
('Sany', 'SCC8500', 2020, 850.0, 'good', 'Atlanta, GA', 1500000.00, 3000, 'Heavy-duty crawler crane'),
('Zoomlion', 'QY70V', 2018, 70.0, 'good', 'Phoenix, AZ', 480000.00, 9000, 'Versatile mobile crane'),
('Demag', 'AC 220-5', 2019, 220.0, 'excellent', 'Dallas, TX', 1100000.00, 6000, 'Premium all terrain crane')
ON CONFLICT DO NOTHING;

-- Add sample market data
INSERT INTO market_data (crane_type, make, model, year, average_price, price_trend, market_volume, data_date, region)
VALUES
('Mobile Crane', 'Liebherr', 'LTM 1200-5.1', 2018, 825000.00, 'stable', 15, CURRENT_DATE, 'North America'),
('Crawler Crane', 'Manitowoc', 'MLC300', 2020, 1150000.00, 'up', 8, CURRENT_DATE, 'North America'),
('All Terrain', 'Grove', 'GMK5250L', 2019, 720000.00, 'down', 22, CURRENT_DATE, 'North America'),
('All Terrain', 'Tadano', 'ATF 130G-5', 2017, 650000.00, 'stable', 18, CURRENT_DATE, 'North America'),
('Rough Terrain', 'Link-Belt', 'RTC-8090 II', 2021, 900000.00, 'up', 12, CURRENT_DATE, 'North America'),
('All Terrain', 'Terex', 'AC 100/4L', 2016, 530000.00, 'stable', 25, CURRENT_DATE, 'North America'),
('Crawler Crane', 'Kobelco', 'CK1600G-2', 2019, 950000.00, 'up', 10, CURRENT_DATE, 'North America'),
('Crawler Crane', 'Sany', 'SCC8500', 2020, 1450000.00, 'up', 6, CURRENT_DATE, 'North America'),
('Mobile Crane', 'Zoomlion', 'QY70V', 2018, 460000.00, 'stable', 20, CURRENT_DATE, 'North America'),
('All Terrain', 'Demag', 'AC 220-5', 2019, 1080000.00, 'up', 12, CURRENT_DATE, 'North America'),
('Mobile Crane', 'Liebherr', 'LTM 1200-5.1', 2018, 820000.00, 'stable', 14, CURRENT_DATE - INTERVAL '30 days', 'North America'),
('Crawler Crane', 'Manitowoc', 'MLC300', 2020, 1120000.00, 'up', 7, CURRENT_DATE - INTERVAL '30 days', 'North America'),
('All Terrain', 'Grove', 'GMK5250L', 2019, 750000.00, 'stable', 20, CURRENT_DATE - INTERVAL '30 days', 'North America')
ON CONFLICT DO NOTHING;

-- Add sample data sources
INSERT INTO data_sources (source_name, source_type, base_url, is_active)
VALUES
('CraneMarket', 'marketplace', 'https://cranemarket.com', true),
('RitchieList', 'auction', 'https://ritchielist.com', true),
('IronPlanet', 'auction', 'https://ironplanet.com', true),
('MachineryTrader', 'marketplace', 'https://machinerytrader.com', true),
('CraneNetwork', 'dealer', 'https://cranenetwork.com', true)
ON CONFLICT DO NOTHING;

-- Add welcome notifications for existing users
INSERT INTO notifications (user_id, title, message, type)
SELECT 
    u.id,
    'Welcome to Crane Intelligence!',
    'Thank you for joining Crane Intelligence. Explore our market analysis, valuation tools, and comprehensive crane listings.',
    'info'
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM notifications n WHERE n.user_id = u.id
)
ON CONFLICT DO NOTHING;

