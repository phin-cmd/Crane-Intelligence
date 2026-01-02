-- SQL script to create visitor_tracking table
-- Run this directly in PostgreSQL if needed

CREATE TABLE IF NOT EXISTS visitor_tracking (
    id SERIAL PRIMARY KEY,
    visitor_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    user_id INTEGER,
    page_url TEXT NOT NULL,
    page_title VARCHAR(500),
    referrer TEXT,
    referrer_domain VARCHAR(255),
    user_agent TEXT,
    browser VARCHAR(100),
    browser_version VARCHAR(50),
    device_type VARCHAR(50),
    device_brand VARCHAR(100),
    device_model VARCHAR(100),
    os VARCHAR(100),
    os_version VARCHAR(50),
    screen_width INTEGER,
    screen_height INTEGER,
    screen_resolution VARCHAR(50),
    ip_address VARCHAR(45),
    country VARCHAR(100),
    country_code VARCHAR(2),
    region VARCHAR(100),
    city VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    timezone VARCHAR(100),
    time_on_page INTEGER,
    scroll_depth INTEGER,
    exit_page BOOLEAN DEFAULT FALSE,
    bounce BOOLEAN DEFAULT FALSE,
    traffic_source VARCHAR(50),
    campaign VARCHAR(255),
    medium VARCHAR(100),
    source VARCHAR(255),
    keyword VARCHAR(255),
    language VARCHAR(10),
    is_bot BOOLEAN DEFAULT FALSE,
    is_mobile BOOLEAN DEFAULT FALSE,
    is_tablet BOOLEAN DEFAULT FALSE,
    is_desktop BOOLEAN DEFAULT FALSE,
    visited_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    additional_metadata TEXT
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_visitor_tracking_visitor_id ON visitor_tracking(visitor_id);
CREATE INDEX IF NOT EXISTS idx_visitor_tracking_session_id ON visitor_tracking(session_id);
CREATE INDEX IF NOT EXISTS idx_visitor_tracking_user_id ON visitor_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_visitor_tracking_visited_at ON visitor_tracking(visited_at);
CREATE INDEX IF NOT EXISTS idx_visitor_tracking_page_url ON visitor_tracking(page_url);
CREATE INDEX IF NOT EXISTS idx_visitor_tracking_country ON visitor_tracking(country);
CREATE INDEX IF NOT EXISTS idx_visitor_tracking_device_type ON visitor_tracking(device_type);
CREATE INDEX IF NOT EXISTS idx_visitor_date ON visitor_tracking(visitor_id, visited_at);
CREATE INDEX IF NOT EXISTS idx_user_date ON visitor_tracking(user_id, visited_at);
CREATE INDEX IF NOT EXISTS idx_page_date ON visitor_tracking(page_url, visited_at);
CREATE INDEX IF NOT EXISTS idx_country_date ON visitor_tracking(country, visited_at);
CREATE INDEX IF NOT EXISTS idx_device_date ON visitor_tracking(device_type, visited_at);

COMMENT ON TABLE visitor_tracking IS 'Tracks website visitors, demographics, and behavior analytics';

