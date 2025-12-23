-- Database Optimization Script for Dev Environment
-- This script adds missing indexes and optimizes the dev database schema
-- DO NOT RUN ON PRODUCTION - This is dev-only

-- ============================================
-- INDEX OPTIMIZATION
-- ============================================

-- Users table indexes
CREATE INDEX IF NOT EXISTS idx_users_email_lower ON users(LOWER(email));
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login);
CREATE INDEX IF NOT EXISTS idx_users_is_active_verified ON users(is_active, is_verified);

-- FMV Reports indexes
CREATE INDEX IF NOT EXISTS idx_fmv_reports_user_id ON fmv_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_fmv_reports_status ON fmv_reports(status);
CREATE INDEX IF NOT EXISTS idx_fmv_reports_created_at ON fmv_reports(created_at);
CREATE INDEX IF NOT EXISTS idx_fmv_reports_user_status ON fmv_reports(user_id, status);
CREATE INDEX IF NOT EXISTS idx_fmv_reports_report_type ON fmv_reports(report_type);

-- Payments indexes
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at);
CREATE INDEX IF NOT EXISTS idx_payments_stripe_payment_intent_id ON payments(stripe_payment_intent_id);
CREATE INDEX IF NOT EXISTS idx_payments_user_status ON payments(user_id, status);

-- User Sessions indexes
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_is_active ON user_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_active ON user_sessions(user_id, is_active);

-- Usage Logs indexes
CREATE INDEX IF NOT EXISTS idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_timestamp ON usage_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_usage_logs_action_type ON usage_logs(action_type);
CREATE INDEX IF NOT EXISTS idx_usage_logs_user_timestamp ON usage_logs(user_id, timestamp);

-- Notifications indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);

-- Status History indexes
CREATE INDEX IF NOT EXISTS idx_status_history_fmv_report_id ON status_history(fmv_report_id);
CREATE INDEX IF NOT EXISTS idx_status_history_created_at ON status_history(created_at);
CREATE INDEX IF NOT EXISTS idx_status_history_status ON status_history(status);

-- Consultation Requests indexes
CREATE INDEX IF NOT EXISTS idx_consultation_requests_email ON consultation_requests(email);
CREATE INDEX IF NOT EXISTS idx_consultation_requests_created_at ON consultation_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_consultation_requests_status ON consultation_requests(status);

-- Admin Users indexes
CREATE INDEX IF NOT EXISTS idx_admin_users_email ON admin_users(email);
CREATE INDEX IF NOT EXISTS idx_admin_users_is_active ON admin_users(is_active);
CREATE INDEX IF NOT EXISTS idx_admin_users_role ON admin_users(role);

-- Audit Logs indexes
CREATE INDEX IF NOT EXISTS idx_audit_logs_admin_user_id ON audit_logs(admin_user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_type ON audit_logs(action_type);

-- Email Verification Tokens indexes
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_user_id ON email_verification_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_token ON email_verification_tokens(token);
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_expires_at ON email_verification_tokens(expires_at);

-- Password Reset Tokens indexes
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires_at ON password_reset_tokens(expires_at);

-- ============================================
-- ANALYZE TABLES (Update Statistics)
-- ============================================

ANALYZE users;
ANALYZE fmv_reports;
ANALYZE payments;
ANALYZE user_sessions;
ANALYZE usage_logs;
ANALYZE notifications;
ANALYZE status_history;
ANALYZE consultation_requests;
ANALYZE admin_users;
ANALYZE audit_logs;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Show all indexes created
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

