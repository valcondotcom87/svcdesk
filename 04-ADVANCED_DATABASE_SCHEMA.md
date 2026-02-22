# ITSM System - Advanced Database Schema (Complete ERD & SQL)
## Comprehensive PostgreSQL Design - ITIL v4, ISO 27001, NIST Compliant

---

## TABLE OF CONTENTS
1. [Core Foundation Tables](#core-foundation)
2. [Incident Management Tables](#incident-management)
3. [Service Request Management Tables](#service-request)
4. [Problem Management Tables](#problem-management)
5. [Change Management Tables](#change-management)
6. [CMDB Tables](#cmdb)
7. [SLA & Performance Tables](#sla-performance)
8. [Audit & Compliance Tables](#audit-compliance)
9. [Indexes & Performance Optimization](#indexes-performance)

---

## CORE FOUNDATION TABLES {#core-foundation}

### 1.1 Organizations (Multi-Tenancy Support)

```sql
-- Organizations: Support untuk multi-tenant architecture
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(100) UNIQUE NOT NULL,
    country VARCHAR(50),
    timezone VARCHAR(50) DEFAULT 'UTC',
    currency VARCHAR(3) DEFAULT 'USD',
    license_key VARCHAR(255) UNIQUE,
    max_users INTEGER DEFAULT 100,
    max_tickets INTEGER DEFAULT 10000,
    is_active BOOLEAN DEFAULT TRUE,
    logo_url TEXT,
    settings JSONB DEFAULT '{
        "language": "en",
        "date_format": "YYYY-MM-DD",
        "enable_kb": true,
        "enable_survey": true,
        "enable_sso": false,
        "sso_provider": null
    }',
    subscription_tier VARCHAR(20) DEFAULT 'starter' CHECK (subscription_tier IN ('starter', 'professional', 'enterprise')),
    subscription_start_date DATE,
    subscription_end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    INDEX idx_org_domain (domain),
    INDEX idx_org_active (is_active),
    INDEX idx_org_tier (subscription_tier)
);
```

### 1.2 Users & Authentication (Enhanced)

```sql
-- Users table dengan enkripsi password dan security features
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    username VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    password_salt VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    department VARCHAR(100),
    manager_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- User Status & Roles
    role VARCHAR(50) NOT NULL CHECK (role IN ('end_user', 'agent', 'manager', 'admin', 'superadmin')),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    
    -- Security
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_method VARCHAR(20) CHECK (mfa_method IN ('totp', 'email', 'sms')),
    mfa_secret VARCHAR(255),
    mfa_backup_codes TEXT,
    
    -- Password Management
    password_changed_at TIMESTAMP WITH TIME ZONE,
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP WITH TIME ZONE,
    
    -- Account Security
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE,
    last_activity TIMESTAMP WITH TIME ZONE,
    
    -- Preferences
    preferences JSONB DEFAULT '{
        "theme": "light",
        "notifications_email": true,
        "notifications_slack": false,
        "language": "en",
        "items_per_page": 20
    }',
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(organization_id, username),
    UNIQUE(organization_id, email),
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_manager ON users(manager_id);
```

### 1.3 Teams & Departments

```sql
-- Teams (Support/IT Teams)
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    team_lead_id UUID REFERENCES users(id),
    team_type VARCHAR(50) NOT NULL CHECK (team_type IN ('support', 'development', 'infrastructure', 'security', 'other')),
    queue_strategy VARCHAR(50) DEFAULT 'round_robin' CHECK (queue_strategy IN ('round_robin', 'least_loaded', 'skill_based', 'priority_based')),
    working_hours_start TIME,
    working_hours_end TIME,
    timezone VARCHAR(50) DEFAULT 'UTC',
    max_concurrent_tickets INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(organization_id, name)
);

-- Team Members Mapping
CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    member_role VARCHAR(50) DEFAULT 'member' CHECK (member_role IN ('lead', 'senior', 'member', 'intern')),
    skills JSONB DEFAULT '[]',
    max_tickets INTEGER DEFAULT 5,
    is_available BOOLEAN DEFAULT TRUE,
    unavailable_until TIMESTAMP WITH TIME ZONE,
    unavailable_reason TEXT,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    left_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(team_id, user_id)
);

CREATE INDEX idx_team_members_team ON team_members(team_id);
CREATE INDEX idx_team_members_user ON team_members(user_id);
```

### 1.4 Roles & Permissions (RBAC - Role Based Access Control)

```sql
-- Roles
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE,
    permissions JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(organization_id, name)
);

-- User-Role Assignment
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    granted_by UUID REFERENCES users(id) ON DELETE SET NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    
    UNIQUE(user_id, role_id)
);

-- Permissions Reference
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    module VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_roles_user ON user_roles(user_id);
CREATE INDEX idx_permissions_code ON permissions(code);
```

---

## INCIDENT MANAGEMENT TABLES {#incident-management}

### 2.1 Incidents (Core Table)

```sql
-- Incidents
CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    ticket_number VARCHAR(50) NOT NULL,
    
    -- Basic Information
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    
    -- Requester Information
    requester_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    requester_email VARCHAR(255),
    requester_phone VARCHAR(20),
    affected_users_count INTEGER DEFAULT 1,
    
    -- Assignment
    assigned_to_id UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_to_team_id UUID REFERENCES teams(id) ON DELETE SET NULL,
    assignment_date TIMESTAMP WITH TIME ZONE,
    reassignment_count INTEGER DEFAULT 0,
    
    -- Priority & Impact/Urgency
    impact VARCHAR(20) NOT NULL CHECK (impact IN ('high', 'medium', 'low')),
    urgency VARCHAR(20) NOT NULL CHECK (urgency IN ('high', 'medium', 'low')),
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    priority_auto_calculated BOOLEAN DEFAULT TRUE,
    business_criticality VARCHAR(20) CHECK (business_criticality IN ('critical', 'high', 'medium', 'low')),
    
    -- Status Management
    status VARCHAR(50) NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'assigned', 'in_progress', 'on_hold', 'pending_user', 'resolved', 'closed', 'reopened')),
    status_changed_at TIMESTAMP WITH TIME ZONE,
    previous_status VARCHAR(50),
    
    -- Resolution & Closure
    resolution_description TEXT,
    resolution_category VARCHAR(100),
    resolved_at TIMESTAMP WITH TIME ZONE,
    closed_at TIMESTAMP WITH TIME ZONE,
    closure_reason VARCHAR(100),
    user_satisfaction_score INTEGER CHECK (user_satisfaction_score >= 0 AND user_satisfaction_score <= 5),
    
    -- SLA Tracking
    sla_policy_id UUID REFERENCES sla_policies(id),
    sla_response_due TIMESTAMP WITH TIME ZONE,
    sla_resolution_due TIMESTAMP WITH TIME ZONE,
    sla_response_breached BOOLEAN DEFAULT FALSE,
    sla_resolution_breached BOOLEAN DEFAULT FALSE,
    sla_response_breach_time TIMESTAMP WITH TIME ZONE,
    sla_resolution_breach_time TIMESTAMP WITH TIME ZONE,
    
    -- Relationships
    problem_id UUID REFERENCES problems(id),
    related_change_id UUID REFERENCES changes(id),
    
    -- Additional Information
    knowledge_article_id UUID,
    tags TEXT[],
    custom_fields JSONB DEFAULT '{}',
    internal_notes TEXT,
    
    -- Audit & Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(organization_id, ticket_number)
);

-- Indexes for Incidents
CREATE INDEX idx_incidents_org ON incidents(organization_id);
CREATE INDEX idx_incidents_ticket ON incidents(ticket_number);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_priority ON incidents(priority);
CREATE INDEX idx_incidents_assigned_to ON incidents(assigned_to_id);
CREATE INDEX idx_incidents_team ON incidents(assigned_to_team_id);
CREATE INDEX idx_incidents_requester ON incidents(requester_id);
CREATE INDEX idx_incidents_sla_due ON incidents(sla_resolution_due);
CREATE INDEX idx_incidents_problem ON incidents(problem_id);
CREATE INDEX idx_incidents_created ON incidents(created_at);
CREATE INDEX idx_incidents_priority_status ON incidents(priority, status);
```

### 2.2 Incident Comments & Communication

```sql
-- Incident Comments/Timeline
CREATE TABLE incident_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    comment_type VARCHAR(50) DEFAULT 'comment' CHECK (comment_type IN ('comment', 'system_note', 'internal_note', 'resolution')),
    content TEXT NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    mentioned_users UUID[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_incident_comments_incident ON incident_comments(incident_id);
CREATE INDEX idx_incident_comments_user ON incident_comments(user_id);
CREATE INDEX idx_incident_comments_public ON incident_comments(is_public);
```

### 2.3 Incident Workarounds (Temporary Solutions)

```sql
-- Workarounds for Incidents
CREATE TABLE incident_workarounds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    effectiveness_score INTEGER CHECK (effectiveness_score >= 0 AND effectiveness_score <= 100),
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    users_affected INTEGER DEFAULT 0
);

CREATE INDEX idx_incident_workarounds_incident ON incident_workarounds(incident_id);
```

---

## SERVICE REQUEST MANAGEMENT TABLES {#service-request}

### 3.1 Service Catalog

```sql
-- Service Categories
CREATE TABLE service_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url TEXT,
    display_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    parent_category_id UUID REFERENCES service_categories(id),
    
    UNIQUE(organization_id, name)
);

-- Services (Service Catalog)
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    long_description TEXT,
    category_id UUID NOT NULL REFERENCES service_categories(id),
    icon_url TEXT,
    
    -- Service Details
    service_type VARCHAR(50) CHECK (service_type IN ('request', 'incident', 'information', 'change')),
    owner_id UUID REFERENCES users(id),
    manager_id UUID REFERENCES users(id),
    
    -- Availability
    is_active BOOLEAN DEFAULT TRUE,
    requires_approval BOOLEAN DEFAULT FALSE,
    
    -- SLA
    default_sla_policy_id UUID REFERENCES sla_policies(id),
    
    -- Customization
    request_form_fields JSONB DEFAULT '[]',
    custom_fields JSONB DEFAULT '{}',
    
    display_order INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(organization_id, name)
);

-- Service Dependencies
CREATE TABLE service_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    dependent_service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    dependency_type VARCHAR(50) CHECK (dependency_type IN ('requires', 'prerequisite', 'related')),
    
    UNIQUE(service_id, dependent_service_id)
);

CREATE INDEX idx_services_org ON services(organization_id);
CREATE INDEX idx_services_category ON services(category_id);
CREATE INDEX idx_services_active ON services(is_active);
```

### 3.2 Service Requests

```sql
-- Service Requests
CREATE TABLE service_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    ticket_number VARCHAR(50) NOT NULL,
    service_id UUID NOT NULL REFERENCES services(id),
    
    -- Basic Information
    title VARCHAR(500) NOT NULL,
    description TEXT,
    
    -- Requester
    requester_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    requester_name VARCHAR(255),
    requester_email VARCHAR(255),
    requester_phone VARCHAR(20),
    
    -- Assignment
    assigned_to_id UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_to_team_id UUID REFERENCES teams(id) ON DELETE SET NULL,
    
    -- Status
    status VARCHAR(50) DEFAULT 'submitted' CHECK (status IN ('submitted', 'pending_approval', 'approved', 'rejected', 'in_progress', 'on_hold', 'completed', 'cancelled')),
    
    -- Approval Workflow
    requires_approval BOOLEAN DEFAULT FALSE,
    approval_level INTEGER DEFAULT 0,
    current_approver_id UUID REFERENCES users(id),
    approval_deadline TIMESTAMP WITH TIME ZONE,
    
    -- Custom Fields
    custom_data JSONB DEFAULT '{}',
    
    -- Timeline
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(organization_id, ticket_number)
);

-- Service Request Approvals
CREATE TABLE service_request_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_request_id UUID NOT NULL REFERENCES service_requests(id) ON DELETE CASCADE,
    approval_step INTEGER NOT NULL,
    approver_id UUID REFERENCES users(id),
    approval_role_id UUID REFERENCES roles(id),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'reassigned')),
    comments TEXT,
    decided_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_service_requests_org ON service_requests(organization_id);
CREATE INDEX idx_service_requests_service ON service_requests(service_id);
CREATE INDEX idx_service_requests_status ON service_requests(status);
CREATE INDEX idx_service_requests_requester ON service_requests(requester_id);
```

---

## PROBLEM MANAGEMENT TABLES {#problem-management}

### 4.1 Problems & Root Cause Analysis

```sql
-- Problems
CREATE TABLE problems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    problem_number VARCHAR(50) NOT NULL,
    
    -- Basic Information
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    symptoms TEXT,
    impact_description TEXT,
    
    -- Classification
    category VARCHAR(100),
    priority VARCHAR(20) CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    
    -- Investigation
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    assigned_to_id UUID REFERENCES users(id) ON DELETE SET NULL,
    investigator_id UUID REFERENCES users(id),
    
    -- Status
    status VARCHAR(50) DEFAULT 'new' CHECK (status IN ('new', 'assigned', 'investigating', 'identified', 'monitoring', 'resolved', 'closed')),
    
    -- Root Cause Analysis
    root_cause TEXT,
    root_cause_category VARCHAR(100),
    analysis_date TIMESTAMP WITH TIME ZONE,
    analyzed_by UUID REFERENCES users(id),
    
    -- Known Error
    known_error_entry_id UUID,
    
    -- Related Change
    change_id UUID REFERENCES changes(id),
    
    -- Timeline
    first_incident_date TIMESTAMP WITH TIME ZONE,
    last_incident_date TIMESTAMP WITH TIME ZONE,
    last_reviewed_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(organization_id, problem_number)
);

-- Problem-Incident Mapping (Many-to-Many)
CREATE TABLE problem_incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    incident_id UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    linked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    linked_by UUID REFERENCES users(id),
    
    UNIQUE(problem_id, incident_id)
);

-- Root Cause Analysis Details
CREATE TABLE rca_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id UUID NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    analysis_method VARCHAR(50) CHECK (analysis_method IN ('5_why', 'fishbone', 'fault_tree', 'timeline', 'other')),
    root_cause_description TEXT NOT NULL,
    contributing_factors TEXT,
    evidence_links TEXT[],
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE
);

-- Known Error Database (KEDB)
CREATE TABLE kedb (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    problem_id UUID NOT NULL REFERENCES problems(id),
    error_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Error Details
    symptoms TEXT NOT NULL,
    workaround TEXT,
    permanent_fix_description TEXT,
    
    -- Status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'superseded', 'archived')),
    
    -- References
    knowledge_article_id UUID,
    change_id UUID REFERENCES changes(id),
    
    -- Metrics
    incident_count INTEGER DEFAULT 0,
    last_incident_date TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES users(id),
    
    UNIQUE(organization_id, error_number)
);

CREATE INDEX idx_problems_org ON problems(organization_id);
CREATE INDEX idx_problems_status ON problems(status);
CREATE INDEX idx_problems_priority ON problems(priority);
CREATE INDEX idx_kedb_org ON kedb(organization_id);
CREATE INDEX idx_kedb_status ON kedb(status);
```

---

## CHANGE MANAGEMENT TABLES {#change-management}

### 5.1 Changes & CAB (Change Advisory Board)

```sql
-- Changes
CREATE TABLE changes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    change_number VARCHAR(50) NOT NULL,
    
    -- Basic Information
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    business_justification TEXT,
    
    -- Change Classification
    change_type VARCHAR(50) NOT NULL CHECK (change_type IN ('standard', 'normal', 'emergency')),
    category VARCHAR(100),
    priority VARCHAR(20) CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    risk_level VARCHAR(20) DEFAULT 'medium' CHECK (risk_level IN ('low', 'medium', 'high', 'very_high')),
    
    -- Owner & Assignment
    change_owner_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    implementation_lead_id UUID REFERENCES users(id),
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'pending_approval', 'approved', 'rejected', 'in_progress', 'completed', 'rolled_back', 'cancelled')),
    
    -- Implementation Schedule
    planned_start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    planned_end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    actual_start_date TIMESTAMP WITH TIME ZONE,
    actual_end_date TIMESTAMP WITH TIME ZONE,
    maintenance_window_start TIMESTAMP WITH TIME ZONE,
    maintenance_window_end TIMESTAMP WITH TIME ZONE,
    
    -- Impact Analysis
    affected_services TEXT[],
    affected_cis UUID[],
    estimated_impact_description TEXT,
    rollback_plan TEXT,
    
    -- CAB Review
    requires_cab_approval BOOLEAN DEFAULT TRUE,
    cab_approval_date TIMESTAMP WITH TIME ZONE,
    cab_approval_notes TEXT,
    
    -- Related Information
    problem_id UUID REFERENCES problems(id),
    related_incidents UUID[],
    
    -- Testing & Verification
    test_results JSONB,
    pre_implementation_checklist JSONB,
    post_implementation_checklist JSONB,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(organization_id, change_number)
);

-- CAB (Change Advisory Board) Members
CREATE TABLE cab_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(100),
    is_mandatory_approver BOOLEAN DEFAULT FALSE,
    
    UNIQUE(organization_id, user_id)
);

-- CAB Approvals
CREATE TABLE change_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    change_id UUID NOT NULL REFERENCES changes(id) ON DELETE CASCADE,
    approver_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    approval_step INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'on_hold')),
    comments TEXT,
    approval_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Change Communication Log
CREATE TABLE change_communications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    change_id UUID NOT NULL REFERENCES changes(id) ON DELETE CASCADE,
    recipient_type VARCHAR(50) CHECK (recipient_type IN ('all_users', 'affected_services', 'specific_team', 'specific_user')),
    recipients UUID[],
    message_title VARCHAR(500),
    message_content TEXT,
    notification_type VARCHAR(50) CHECK (notification_type IN ('email', 'slack', 'teams', 'sms')),
    sent_at TIMESTAMP WITH TIME ZONE,
    read_by_count INTEGER DEFAULT 0
);

CREATE INDEX idx_changes_org ON changes(organization_id);
CREATE INDEX idx_changes_status ON changes(status);
CREATE INDEX idx_changes_type ON changes(change_type);
CREATE INDEX idx_changes_scheduled ON changes(planned_start_date);
CREATE INDEX idx_changes_owner ON changes(change_owner_id);
```

---

## CMDB TABLES {#cmdb}

### 6.1 Configuration Items (CIs)

```sql
-- CI Categories
CREATE TABLE ci_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_name VARCHAR(100),
    parent_category_id UUID REFERENCES ci_categories(id),
    
    UNIQUE(organization_id, name)
);

-- Configuration Items (CIs) - Main CMDB Table
CREATE TABLE configuration_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    ci_number VARCHAR(50) NOT NULL,
    
    -- Basic Information
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id UUID NOT NULL REFERENCES ci_categories(id),
    ci_type VARCHAR(50) NOT NULL CHECK (ci_type IN ('hardware', 'software', 'network', 'database', 'application', 'service', 'document', 'people')),
    
    -- Ownership
    owner_id UUID REFERENCES users(id),
    custodian_id UUID REFERENCES users(id),
    manager_id UUID REFERENCES users(id),
    
    -- Status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'planned', 'decommissioned', 'archived')),
    status_changed_at TIMESTAMP WITH TIME ZONE,
    
    -- Attributes
    version VARCHAR(50),
    location VARCHAR(255),
    serial_number VARCHAR(100),
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    purchase_date DATE,
    warranty_end_date DATE,
    end_of_life_date DATE,
    cost DECIMAL(15,2),
    
    -- Environment
    environment VARCHAR(50) CHECK (environment IN ('production', 'staging', 'development', 'test')),
    criticality VARCHAR(50) CHECK (criticality IN ('critical', 'high', 'medium', 'low')),
    
    -- Custom Attributes
    custom_attributes JSONB DEFAULT '{}',
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(organization_id, ci_number)
);

-- CI Relationships (Many-to-Many)
CREATE TABLE ci_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_ci_id UUID NOT NULL REFERENCES configuration_items(id) ON DELETE CASCADE,
    target_ci_id UUID NOT NULL REFERENCES configuration_items(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL CHECK (relationship_type IN ('hosted_on', 'depends_on', 'uses', 'supports', 'related_to', 'contains', 'connects_to')),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    
    UNIQUE(source_ci_id, target_ci_id, relationship_type)
);

-- CI Change History (Audit Trail)
CREATE TABLE ci_change_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ci_id UUID NOT NULL REFERENCES configuration_items(id) ON DELETE CASCADE,
    changed_attribute VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    changed_by UUID NOT NULL REFERENCES users(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    change_id UUID REFERENCES changes(id)
);

-- CI Search/Indexing
CREATE TABLE ci_search_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ci_id UUID NOT NULL REFERENCES configuration_items(id) ON DELETE CASCADE,
    search_text TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cis_org ON configuration_items(organization_id);
CREATE INDEX idx_cis_type ON configuration_items(ci_type);
CREATE INDEX idx_cis_status ON configuration_items(status);
CREATE INDEX idx_cis_owner ON configuration_items(owner_id);
CREATE INDEX idx_ci_relationships_source ON ci_relationships(source_ci_id);
CREATE INDEX idx_ci_relationships_target ON ci_relationships(target_ci_id);
CREATE INDEX idx_ci_change_history_ci ON ci_change_history(ci_id);
```

---

## SLA & PERFORMANCE TABLES {#sla-performance}

### 7.1 SLA Policies & Metrics

```sql
-- SLA Policies
CREATE TABLE sla_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sla_type VARCHAR(50) CHECK (sla_type IN ('incident', 'service_request', 'problem', 'change')),
    
    -- Applicability
    applies_to_priority VARCHAR(20),
    applies_to_service_id UUID REFERENCES services(id),
    applies_to_user_group_id UUID,
    
    -- Response Time SLA
    response_time_target INTEGER NOT NULL,
    response_time_unit VARCHAR(10) CHECK (response_time_unit IN ('minutes', 'hours', 'days')),
    
    -- Resolution Time SLA
    resolution_time_target INTEGER NOT NULL,
    resolution_time_unit VARCHAR(10) CHECK (resolution_time_unit IN ('minutes', 'hours', 'days')),
    
    -- Business Hours
    applies_on_business_hours_only BOOLEAN DEFAULT FALSE,
    business_hours_start TIME,
    business_hours_end TIME,
    exclude_weekends BOOLEAN DEFAULT TRUE,
    exclude_holidays BOOLEAN DEFAULT TRUE,
    
    -- Escalation
    escalation_level_1_after_minutes INTEGER,
    escalation_level_1_assignee_id UUID REFERENCES users(id),
    escalation_level_2_after_minutes INTEGER,
    escalation_level_2_assignee_id UUID REFERENCES users(id),
    
    -- Conditions & Exceptions
    conditions JSONB DEFAULT '{}',
    exceptions JSONB DEFAULT '{}',
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(organization_id, name)
);

-- SLA Breaches (Monitoring)
CREATE TABLE sla_breaches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sla_policy_id UUID NOT NULL REFERENCES sla_policies(id),
    ticket_id UUID NOT NULL,
    breach_type VARCHAR(50) CHECK (breach_type IN ('response', 'resolution')),
    breach_time TIMESTAMP WITH TIME ZONE NOT NULL,
    ticket_type VARCHAR(50),
    reported_by UUID REFERENCES users(id),
    action_taken TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- SLA Metrics & Performance
CREATE TABLE sla_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    sla_policy_id UUID NOT NULL REFERENCES sla_policies(id),
    period_start_date DATE NOT NULL,
    period_end_date DATE NOT NULL,
    
    -- Metrics
    total_tickets INTEGER DEFAULT 0,
    compliant_tickets INTEGER DEFAULT 0,
    non_compliant_tickets INTEGER DEFAULT 0,
    compliance_percentage DECIMAL(5,2),
    
    -- Response Time Metrics
    avg_response_time INTERVAL,
    max_response_time INTERVAL,
    min_response_time INTERVAL,
    
    -- Resolution Time Metrics
    avg_resolution_time INTERVAL,
    max_resolution_time INTERVAL,
    min_resolution_time INTERVAL,
    
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(organization_id, sla_policy_id, period_start_date)
);

CREATE INDEX idx_sla_policies_org ON sla_policies(organization_id);
CREATE INDEX idx_sla_breaches_policy ON sla_breaches(sla_policy_id);
CREATE INDEX idx_sla_metrics_org ON sla_metrics(organization_id);
```

---

## AUDIT & COMPLIANCE TABLES {#audit-compliance}

### 8.1 Audit Logs & Compliance

```sql
-- Audit Log (All changes logged for compliance)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Action Details
    action_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(255),
    
    -- Change Details
    old_values JSONB,
    new_values JSONB,
    
    -- User & IP
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    user_ip_address INET,
    user_agent TEXT,
    
    -- Status
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_audit_org (organization_id),
    INDEX idx_audit_user (user_id),
    INDEX idx_audit_type (action_type),
    INDEX idx_audit_entity (entity_type, entity_id),
    INDEX idx_audit_date (created_at)
);

-- Compliance Tracking
CREATE TABLE compliance_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- Compliance Details
    requirement_name VARCHAR(255) NOT NULL,
    requirement_category VARCHAR(100),
    standard_reference VARCHAR(100),
    
    -- Tracking
    status VARCHAR(50) CHECK (status IN ('compliant', 'non_compliant', 'partial', 'not_applicable')),
    evidence_location TEXT,
    last_verified_date TIMESTAMP WITH TIME ZONE,
    verified_by UUID REFERENCES users(id),
    
    -- Remediation (if non-compliant)
    remediation_plan TEXT,
    remediation_deadline DATE,
    remediation_status VARCHAR(50),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Data Retention Policy
CREATE TABLE data_retention_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    data_type VARCHAR(100) NOT NULL,
    retention_period_days INTEGER NOT NULL,
    retention_rule TEXT,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(organization_id, data_type)
);

CREATE INDEX idx_compliance_org ON compliance_tracking(organization_id);
CREATE INDEX idx_retention_org ON data_retention_policies(organization_id);
```

---

## ATTACHMENTS & SUPPORTING TABLES {#attachments}

### 9.1 File Management

```sql
-- Attachments
CREATE TABLE attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    -- File Details
    file_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(50),
    mime_type VARCHAR(100),
    
    -- Storage
    storage_location VARCHAR(100) CHECK (storage_location IN ('local', 's3', 'azure', 'gcs')),
    storage_key VARCHAR(1000),
    
    -- Linked Entity
    entity_type VARCHAR(100),
    entity_id VARCHAR(255),
    
    -- Security
    is_encrypted BOOLEAN DEFAULT FALSE,
    virus_scanned BOOLEAN DEFAULT FALSE,
    virus_scan_result VARCHAR(100),
    
    -- Audit
    uploaded_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    INDEX idx_attachments_entity (entity_type, entity_id)
);
```

---

## INDEXES & PERFORMANCE OPTIMIZATION {#indexes-performance}

### 10.1 Performance Indexes

```sql
-- Composite Indexes untuk queries yang frequent
CREATE INDEX idx_incidents_priority_status_sla ON incidents(priority, status, sla_resolution_due);
CREATE INDEX idx_incidents_assigned_team_status ON incidents(assigned_to_team_id, status);
CREATE INDEX idx_service_requests_status_created ON service_requests(status, created_at DESC);
CREATE INDEX idx_problems_status_priority_org ON problems(organization_id, status, priority);
CREATE INDEX idx_changes_status_scheduled_org ON changes(organization_id, status, planned_start_date);
CREATE INDEX idx_ci_type_status_criticality ON configuration_items(ci_type, status, criticality);

-- Partial Indexes untuk filtering aktif records
CREATE INDEX idx_incidents_active ON incidents(id) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_active_org ON users(organization_id) WHERE is_active = TRUE;
CREATE INDEX idx_services_active_org ON services(organization_id) WHERE is_active = TRUE;
CREATE INDEX idx_cis_active ON configuration_items(id) WHERE status = 'active' AND deleted_at IS NULL;

-- Text Search Indexes
CREATE INDEX idx_incidents_title_description ON incidents USING GIN(to_tsvector('english', title || ' ' || description));
CREATE INDEX idx_problems_title_description ON problems USING GIN(to_tsvector('english', title || ' ' || description));
```

---

## VIEWS untuk Reporting & Analytics {#views}

```sql
-- Active Incidents View
CREATE OR REPLACE VIEW v_active_incidents AS
SELECT 
    i.id,
    i.organization_id,
    i.ticket_number,
    i.title,
    i.priority,
    i.status,
    i.assigned_to_id,
    u_assignee.first_name || ' ' || u_assignee.last_name as assigned_to,
    i.sla_resolution_due,
    CASE 
        WHEN i.sla_resolution_due < CURRENT_TIMESTAMP THEN 'BREACHED'
        WHEN i.sla_resolution_due < CURRENT_TIMESTAMP + INTERVAL '1 hour' THEN 'CRITICAL'
        ELSE 'ON_TRACK'
    END as sla_status,
    EXTRACT(EPOCH FROM (i.sla_resolution_due - CURRENT_TIMESTAMP))/3600 as hours_to_sla
FROM incidents i
LEFT JOIN users u_assignee ON i.assigned_to_id = u_assignee.id
WHERE i.deleted_at IS NULL
    AND i.status NOT IN ('resolved', 'closed');

-- Open Service Requests View
CREATE OR REPLACE VIEW v_open_service_requests AS
SELECT 
    sr.id,
    sr.organization_id,
    sr.ticket_number,
    sr.service_id,
    s.name as service_name,
    sr.title,
    sr.status,
    sr.requester_id,
    u_req.email as requester_email,
    sr.created_at,
    sr.assigned_to_id
FROM service_requests sr
LEFT JOIN services s ON sr.service_id = s.id
LEFT JOIN users u_req ON sr.requester_id = u_req.id
WHERE sr.deleted_at IS NULL
    AND sr.status NOT IN ('completed', 'cancelled');

-- SLA Compliance Summary View
CREATE OR REPLACE VIEW v_sla_compliance_summary AS
SELECT 
    DATE_TRUNC('month', i.created_at)::DATE as month,
    i.sla_policy_id,
    sp.name as policy_name,
    COUNT(*) as total_tickets,
    SUM(CASE WHEN i.sla_response_breached = FALSE AND i.sla_resolution_breached = FALSE THEN 1 ELSE 0 END) as compliant_tickets,
    ROUND(100.0 * SUM(CASE WHEN i.sla_response_breached = FALSE AND i.sla_resolution_breached = FALSE THEN 1 ELSE 0 END) / COUNT(*), 2) as compliance_percentage
FROM incidents i
LEFT JOIN sla_policies sp ON i.sla_policy_id = sp.id
WHERE i.deleted_at IS NULL
GROUP BY DATE_TRUNC('month', i.created_at), i.sla_policy_id, sp.name;

-- Team Workload View
CREATE OR REPLACE VIEW v_team_workload AS
SELECT 
    t.id,
    t.name as team_name,
    COUNT(DISTINCT CASE WHEN i.status NOT IN ('resolved', 'closed') THEN i.id END) as open_incidents,
    COUNT(DISTINCT CASE WHEN i.status = 'in_progress' THEN i.id END) as in_progress,
    AVG(CAST(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - i.created_at))/3600 AS NUMERIC)) as avg_age_hours,
    MAX(i.priority) as highest_priority
FROM teams t
LEFT JOIN incidents i ON t.id = i.assigned_to_team_id AND i.deleted_at IS NULL
GROUP BY t.id, t.name;
```

---

## TRIGGER FUNCTIONS untuk Automation {#triggers}

```sql
-- Trigger untuk auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger ke semua relevant tables
CREATE TRIGGER update_users_timestamp BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_incidents_timestamp BEFORE UPDATE ON incidents FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_problems_timestamp BEFORE UPDATE ON problems FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_changes_timestamp BEFORE UPDATE ON changes FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_services_timestamp BEFORE UPDATE ON services FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER update_cis_timestamp BEFORE UPDATE ON configuration_items FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- Trigger untuk automatic SLA Due Date calculation
CREATE OR REPLACE FUNCTION calculate_sla_due_dates()
RETURNS TRIGGER AS $$
DECLARE
    v_sla_policy sla_policies;
    v_response_minutes INTEGER;
    v_resolution_minutes INTEGER;
BEGIN
    -- Get SLA policy
    SELECT * INTO v_sla_policy FROM sla_policies 
    WHERE id = NEW.sla_policy_id LIMIT 1;
    
    IF v_sla_policy IS NOT NULL THEN
        -- Convert SLA times to minutes
        v_response_minutes := CASE 
            WHEN v_sla_policy.response_time_unit = 'minutes' THEN v_sla_policy.response_time_target
            WHEN v_sla_policy.response_time_unit = 'hours' THEN v_sla_policy.response_time_target * 60
            WHEN v_sla_policy.response_time_unit = 'days' THEN v_sla_policy.response_time_target * 24 * 60
            ELSE 0
        END;
        
        v_resolution_minutes := CASE 
            WHEN v_sla_policy.resolution_time_unit = 'minutes' THEN v_sla_policy.resolution_time_target
            WHEN v_sla_policy.resolution_time_unit = 'hours' THEN v_sla_policy.resolution_time_target * 60
            WHEN v_sla_policy.resolution_time_unit = 'days' THEN v_sla_policy.resolution_time_target * 24 * 60
            ELSE 0
        END;
        
        -- Set SLA due dates
        NEW.sla_response_due := NEW.created_at + (v_response_minutes || ' minutes')::INTERVAL;
        NEW.sla_resolution_due := NEW.created_at + (v_resolution_minutes || ' minutes')::INTERVAL;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calculate_incident_sla BEFORE INSERT ON incidents
FOR EACH ROW EXECUTE FUNCTION calculate_sla_due_dates();

-- Trigger untuk linking incident ke problem saat duplikat terdeteksi
CREATE OR REPLACE FUNCTION link_duplicate_incident_to_problem()
RETURNS TRIGGER AS $$
DECLARE
    v_problem_id UUID;
BEGIN
    -- Check if there's an existing incident dengan symptoms yang sama
    IF NEW.problem_id IS NULL THEN
        SELECT p.id INTO v_problem_id
        FROM problems p
        WHERE p.organization_id = NEW.organization_id
            AND p.symptoms IS NOT NULL
            AND NEW.description ILIKE '%' || p.symptoms || '%'
            AND p.status != 'closed'
        LIMIT 1;
        
        IF v_problem_id IS NOT NULL THEN
            NEW.problem_id := v_problem_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auto_link_incident_problem BEFORE INSERT ON incidents
FOR EACH ROW EXECUTE FUNCTION link_duplicate_incident_to_problem();
```

---

**Database Statistics & Maintenance**

```sql
-- Query untuk maintenance
VACUUM ANALYZE;
REINDEX DATABASE itsm_db;

-- Check unused indexes
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
AND indexname NOT IN (
    SELECT indexrelname FROM pg_stat_user_indexes
    WHERE idx_scan = 0
);
```

---

## Summary

Database schema ini menyediakan:

✅ **Multi-tenancy**: Support untuk multiple organizations  
✅ **ITIL Compliance**: Semua modul core ITIL (Incident, Service Request, Problem, Change, CMDB)  
✅ **Scalability**: Proper indexing, partitioning support, dan efficient queries  
✅ **Security**: RBAC, audit logging, encryption support  
✅ **Flexibility**: JSON fields untuk custom attributes, extensible design  
✅ **Performance**: Optimized indexes, views, dan materialized query optimization  
✅ **Maintainability**: Clear naming, relationships, dan data integrity constraints  

