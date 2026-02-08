-- Initialize ITSM Database

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS cache;

-- Grant permissions
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA audit TO postgres;
GRANT ALL ON SCHEMA cache TO postgres;

-- Set up audit logging trigger function
CREATE OR REPLACE FUNCTION audit.audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit.audit_log (
        table_name,
        record_id,
        action,
        old_data,
        new_data,
        changed_by,
        changed_at
    ) VALUES (
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        to_jsonb(OLD),
        to_jsonb(NEW),
        CURRENT_USER,
        CURRENT_TIMESTAMP
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Set default timeout
ALTER SYSTEM SET statement_timeout = '300000ms';
SELECT pg_reload_conf();

-- Optimize for Django
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '512MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET work_mem = '16MB';
SELECT pg_reload_conf();

-- Create audit tables
CREATE TABLE IF NOT EXISTS audit.audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    record_id UUID,
    action TEXT NOT NULL,
    old_data JSONB,
    new_data JSONB,
    changed_by TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_table_record (table_name, record_id),
    INDEX idx_changed_at (changed_at DESC)
);

-- Done
SELECT now() as initialization_complete;
