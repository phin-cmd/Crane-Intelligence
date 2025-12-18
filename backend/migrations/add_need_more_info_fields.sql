
-- Migration: Add need_more_info fields to fmv_reports table
-- Date: 2024

-- Add need_more_info_at timestamp
ALTER TABLE fmv_reports 
ADD COLUMN IF NOT EXISTS need_more_info_at TIMESTAMP WITH TIME ZONE;

-- Add need_more_info_reason text field
ALTER TABLE fmv_reports 
ADD COLUMN IF NOT EXISTS need_more_info_reason TEXT;

-- Create index on need_more_info_at for querying
CREATE INDEX IF NOT EXISTS idx_fmv_reports_need_more_info_at 
ON fmv_reports(need_more_info_at) 
WHERE need_more_info_at IS NOT NULL;

-- Note: paid_at, rejected_at, cancelled_at, rejection_reason fields are kept for backward compatibility
