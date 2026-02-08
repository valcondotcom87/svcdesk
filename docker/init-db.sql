-- Initialize PostgreSQL for ITSM
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create schema
CREATE SCHEMA IF NOT EXISTS itsm;

-- Create indexes for better performance
CREATE INDEX idx_compliance_framework_org ON compliance_complianceframework(organization_id);
CREATE INDEX idx_compliance_requirement_framework ON compliance_compliancerequirement(framework_id);
CREATE INDEX idx_compliance_requirement_owner ON compliance_compliancerequirement(owner_id);
CREATE INDEX idx_audit_log_timestamp ON compliance_immutableauditlog(timestamp);

-- Create audit trigger
CREATE OR REPLACE FUNCTION audit_trigger() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO compliance_immutableauditlog (
        action,
        model_name,
        object_id,
        user_id,
        timestamp,
        changes
    ) VALUES (
        TG_OP,
        TG_TABLE_NAME,
        NEW.id,
        CURRENT_USER,
        NOW(),
        row_to_json(NEW)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA itsm TO itsm_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO itsm_user;
ALTER DEFAULT PRIVILEGES FOR USER postgres IN SCHEMA public GRANT ALL ON TABLES TO itsm_user;
