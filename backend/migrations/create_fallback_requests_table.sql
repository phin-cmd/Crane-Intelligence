-- Migration: Create fallback_requests table
-- This table stores manual valuation requests for cranes not found in the database

CREATE TABLE IF NOT EXISTS fallback_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    user_email VARCHAR(255) NOT NULL,
    
    -- Crane details
    manufacturer VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    serial_number VARCHAR(255),
    capacity_tons FLOAT NOT NULL,
    crane_type VARCHAR(100) NOT NULL,
    operating_hours INTEGER NOT NULL,
    mileage INTEGER,
    boom_length FLOAT,
    jib_length FLOAT,
    max_hook_height FLOAT,
    max_radius FLOAT,
    region VARCHAR(100) NOT NULL,
    condition VARCHAR(50) NOT NULL,
    additional_specs TEXT,
    special_features TEXT,
    usage_history TEXT,
    
    -- Status and workflow
    status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    
    -- Admin/analyst fields
    assigned_analyst VARCHAR(255),
    analyst_notes TEXT,
    rejection_reason TEXT,
    
    -- Linked FMV report (created after valuation)
    linked_fmv_report_id INTEGER REFERENCES fmv_reports(id) ON DELETE SET NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    in_review_at TIMESTAMP WITH TIME ZONE,
    valuation_started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    rejected_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_fallback_requests_user_id ON fallback_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_fallback_requests_user_email ON fallback_requests(user_email);
CREATE INDEX IF NOT EXISTS idx_fallback_requests_status ON fallback_requests(status);
CREATE INDEX IF NOT EXISTS idx_fallback_requests_created_at ON fallback_requests(created_at);

