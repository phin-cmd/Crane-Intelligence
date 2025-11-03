-- Migration: Add maintenance_files table
-- Created: 2025-11-03

BEGIN;

CREATE TABLE IF NOT EXISTS maintenance_files (
    id SERIAL PRIMARY KEY,
    maintenance_record_id INTEGER NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    file_size INTEGER NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    description TEXT,
    uploaded_by INTEGER NOT NULL,
    uploaded_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_maintenance_files_file_path UNIQUE (file_path),
    CONSTRAINT fk_maintenance_files_maintenance_record
        FOREIGN KEY (maintenance_record_id)
        REFERENCES maintenance_records (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_maintenance_files_uploaded_by
        FOREIGN KEY (uploaded_by)
        REFERENCES users (id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_maintenance_files_maintenance_record_id
    ON maintenance_files (maintenance_record_id);

CREATE INDEX IF NOT EXISTS idx_maintenance_files_uploaded_by
    ON maintenance_files (uploaded_by);

CREATE INDEX IF NOT EXISTS idx_maintenance_files_uploaded_at
    ON maintenance_files (uploaded_at);

COMMIT;
