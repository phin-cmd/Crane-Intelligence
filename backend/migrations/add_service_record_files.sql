-- Migration: Add service_record_files column to fmv_reports table
-- This column stores an array of service record file URLs

ALTER TABLE fmv_reports 
ADD COLUMN IF NOT EXISTS service_record_files JSON;

-- Update existing records to have empty array if null
UPDATE fmv_reports 
SET service_record_files = '[]'::json 
WHERE service_record_files IS NULL;

