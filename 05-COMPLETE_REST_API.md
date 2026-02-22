# ITSM System - Complete REST API Documentation
## API Specification & Implementation Guide (OpenAPI 3.0)

---

## TABLE OF CONTENTS
1. [API Overview & Standards](#api-overview)
2. [Authentication & Security](#authentication)
3. [Incident Management APIs](#incident-apis)
4. [Service Request APIs](#service-request-apis)
5. [Problem Management APIs](#problem-apis)
6. [Change Management APIs](#change-apis)
7. [CMDB APIs](#cmdb-apis)
8. [SLA & Reporting APIs](#sla-apis)
9. [Error Handling & Response Codes](#error-handling)

---

## API OVERVIEW & STANDARDS {#api-overview}

### 1.1 API Design Principles

```
Base URL: https://itsm-api.example.com/api/v1
Content-Type: application/json
API Version: 1.0
OpenAPI Spec: /api/v1/docs
```

### 1.2 Request/Response Format

**Standard Request Header:**
```json
{
    "Content-Type": "application/json",
    "Authorization": "Bearer {jwt_token}",
    "X-Organization-ID": "{org_id}",
    "X-API-Version": "1.0",
    "X-Request-ID": "{unique_request_id}"
}
```

**Standard Success Response (200-299):**
```json
{
    "success": true,
    "status_code": 200,
    "message": "Operation completed successfully",
    "data": {
        // Response payload
    },
    "meta": {
        "request_id": "req_1234567890",
        "timestamp": "2026-02-08T10:30:00Z",
        "api_version": "1.0"
    }
}
```

**Paginated Response:**
```json
{
    "success": true,
    "status_code": 200,
    "data": [
        // Array of items
    ],
    "pagination": {
        "total_count": 150,
        "page": 1,
        "page_size": 20,
        "total_pages": 8,
        "has_next": true,
        "has_prev": false
    },
    "meta": {
        "request_id": "req_1234567890",
        "timestamp": "2026-02-08T10:30:00Z"
    }
}
```

**Error Response:**
```json
{
    "success": false,
    "status_code": 400,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input parameters",
        "details": [
            {
                "field": "priority",
                "message": "Must be one of: critical, high, medium, low"
            }
        ]
    },
    "meta": {
        "request_id": "req_1234567890",
        "timestamp": "2026-02-08T10:30:00Z"
    }
}
```

### 1.3 API Rate Limiting

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1644316200
```

---

## AUTHENTICATION & SECURITY {#authentication}

### 2.1 JWT Authentication

**POST /auth/login**
```
Endpoint: https://itsm-api.example.com/api/v1/auth/login
Method: POST
Content-Type: application/json

Request Body:
{
    "username": "john.doe@example.com",
    "password": "secure_password",
    "remember_me": false
}

Response (200 OK):
{
    "success": true,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "expires_in": 3600,
        "token_type": "Bearer",
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "john.doe",
            "email": "john.doe@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": "agent",
            "organization_id": "550e8400-e29b-41d4-a716-446655440001"
        }
    }
}
```

**POST /auth/refresh**
```
Endpoint: https://itsm-api.example.com/api/v1/auth/refresh
Method: POST
Content-Type: application/json

Request Body:
{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response (200 OK):
{
    "success": true,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "expires_in": 3600,
        "token_type": "Bearer"
    }
}
```

**POST /auth/logout**
```
Endpoint: https://itsm-api.example.com/api/v1/auth/logout
Method: POST
Authorization: Bearer {jwt_token}

Response (200 OK):
{
    "success": true,
    "message": "Logged out successfully"
}
```

### 2.2 RBAC Implementation

```
Roles:
- end_user: Can create tickets, view own tickets
- agent: Can view/update tickets, create problems/changes
- manager: Can approve changes, manage team
- admin: Full system access within organization
- superadmin: Global system access

Permissions stored in JWT:
{
    "iss": "itsm-system",
    "sub": "550e8400-e29b-41d4-a716-446655440000",
    "exp": 1644316200,
    "iat": 1644312600,
    "org_id": "550e8400-e29b-41d4-a716-446655440001",
    "role": "agent",
    "permissions": ["incident:read", "incident:create", "incident:update", "problem:read"],
    "teams": ["550e8400-e29b-41d4-a716-446655440002"],
    "scope": "access"
}
```

---

## INCIDENT MANAGEMENT APIs {#incident-apis}

### 3.1 Create Incident

**POST /incidents**
```
Endpoint: https://itsm-api.example.com/api/v1/incidents
Method: POST
Authorization: Bearer {jwt_token}
Permissions Required: incident:create

Request Body:
{
    "title": "Email service is down",
    "description": "Users cannot access email since 10:30 AM",
    "category": "Email",
    "subcategory": "Access",
    "impact": "high",
    "urgency": "high",
    "affected_users_count": 150,
    "business_criticality": "critical",
    "affected_services": ["email", "calendar"],
    "requester_email": "john.doe@example.com",
    "requester_phone": "+62-12345678",
    "custom_fields": {
        "department": "Sales",
        "cost_center": "CC001"
    }
}

Response (201 Created):
{
    "success": true,
    "status_code": 201,
    "message": "Incident created successfully",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "ticket_number": "INC-000001",
        "title": "Email service is down",
        "description": "Users cannot access email since 10:30 AM",
        "status": "new",
        "impact": "high",
        "urgency": "high",
        "priority": "critical",  // Auto-calculated from impact x urgency
        "priority_auto_calculated": true,
        "requester_id": "550e8400-e29b-41d4-a716-446655440004",
        "assigned_to_id": null,
        "assigned_to_team_id": null,
        "sla_response_due": "2026-02-08T11:30:00Z",  // 1 hour after creation
        "sla_resolution_due": "2026-02-08T14:30:00Z",  // 4 hours after creation
        "created_at": "2026-02-08T10:30:00Z",
        "created_by": "550e8400-e29b-41d4-a716-446655440000"
    }
}
```

### 3.2 Get Incident Details

**GET /incidents/{incident_id}**
```
Endpoint: https://itsm-api.example.com/api/v1/incidents/550e8400-e29b-41d4-a716-446655440003
Method: GET
Authorization: Bearer {jwt_token}
Permissions Required: incident:read

Response (200 OK):
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "ticket_number": "INC-000001",
        "title": "Email service is down",
        "description": "Users cannot access email since 10:30 AM",
        "status": "assigned",
        "impact": "high",
        "urgency": "high",
        "priority": "critical",
        "assigned_to": {
            "id": "550e8400-e29b-41d4-a716-446655440005",
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "team": "Email Support Team"
        },
        "sla_status": "ON_TRACK",
        "sla_response_due": "2026-02-08T11:30:00Z",
        "sla_resolution_due": "2026-02-08T14:30:00Z",
        "hours_to_sla": 3.5,
        "timeline": [
            {
                "timestamp": "2026-02-08T10:30:00Z",
                "action": "created",
                "user": "System",
                "details": "Incident created"
            },
            {
                "timestamp": "2026-02-08T10:35:00Z",
                "action": "priority_calculated",
                "user": "System",
                "details": "Priority auto-calculated as critical"
            },
            {
                "timestamp": "2026-02-08T10:40:00Z",
                "action": "assigned",
                "user": "Support Manager",
                "details": "Assigned to Email Support Team"
            }
        ],
        "comments": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440006",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440005",
                    "name": "Jane Smith"
                },
                "content": "Investigating email server logs. Found unusual connection attempts.",
                "is_public": false,
                "created_at": "2026-02-08T10:45:00Z"
            }
        ],
        "attachments": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440007",
                "file_name": "server_logs.txt",
                "file_size": 1024,
                "uploaded_by": "Jane Smith",
                "uploaded_at": "2026-02-08T10:50:00Z"
            }
        ],
        "related_changes": [],
        "related_problems": []
    }
}
```

### 3.3 List Incidents (with Filters)

**GET /incidents**
```
Query Parameters:
- status: new,assigned,in_progress,on_hold,resolved,closed (comma-separated)
- priority: critical,high,medium,low (comma-separated)
- assigned_to: {user_id}
- assigned_team: {team_id}
- requester: {user_id}
- sla_status: ON_TRACK,CRITICAL,BREACHED
- page: 1
- limit: 20
- sort_by: created_at,-priority,-sla_resolution_due
- search: {search_text}
- date_from: 2026-01-01T00:00:00Z
- date_to: 2026-02-08T23:59:59Z

Example Request:
GET /incidents?status=new,assigned&priority=critical,high&page=1&limit=20&sort_by=-priority,-sla_resolution_due

Response (200 OK):
{
    "success": true,
    "data": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440003",
            "ticket_number": "INC-000001",
            "title": "Email service is down",
            "status": "assigned",
            "priority": "critical",
            "assigned_to_name": "Jane Smith",
            "assigned_team_name": "Email Support Team",
            "sla_status": "ON_TRACK",
            "hours_to_sla": 3.5,
            "created_at": "2026-02-08T10:30:00Z"
        },
        // ... more incidents
    ],
    "pagination": {
        "total_count": 45,
        "page": 1,
        "page_size": 20,
        "total_pages": 3,
        "has_next": true
    }
}
```

### 3.4 Update Incident

**PUT /incidents/{incident_id}**
```
Endpoint: https://itsm-api.example.com/api/v1/incidents/550e8400-e29b-41d4-a716-446655440003
Method: PUT
Authorization: Bearer {jwt_token}
Permissions Required: incident:update

Request Body:
{
    "status": "in_progress",
    "priority": "high",  // Manual override of auto-calculated priority
    "assigned_to_id": "550e8400-e29b-41d4-a716-446655440005",
    "internal_notes": "Started investigating email server issues",
    "custom_fields": {
        "investigation_status": "in_progress"
    }
}

Response (200 OK):
{
    "success": true,
    "message": "Incident updated successfully",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "ticket_number": "INC-000001",
        "status": "in_progress",
        "priority": "high",
        "updated_at": "2026-02-08T10:55:00Z",
        "updated_by": "550e8400-e29b-41d4-a716-446655440000"
    }
}
```

### 3.5 Resolve Incident

**POST /incidents/{incident_id}/resolve**
```
Endpoint: https://itsm-api.example.com/api/v1/incidents/550e8400-e29b-41d4-a716-446655440003/resolve
Method: POST
Authorization: Bearer {jwt_token}
Permissions Required: incident:update

Request Body:
{
    "resolution_description": "Restarted email server. Issue resolved.",
    "resolution_category": "restart_service",
    "workaround_provided": false,
    "link_to_knowledge": "KB-12345"
}

Response (200 OK):
{
    "success": true,
    "message": "Incident marked as resolved",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "status": "resolved",
        "resolved_at": "2026-02-08T12:00:00Z",
        "sla_resolution_met": true
    }
}
```

### 3.6 Close Incident

**POST /incidents/{incident_id}/close**
```
Endpoint: https://itsm-api.example.com/api/v1/incidents/550e8400-e29b-41d4-a716-446655440003/close
Method: POST
Authorization: Bearer {jwt_token}
Permissions Required: incident:update

Request Body:
{
    "closure_reason": "successfully_resolved",
    "user_satisfaction_score": 5,
    "survey_comments": "Issue resolved quickly and efficiently",
    "link_to_problem": null,
    "create_problem": false
}

Response (200 OK):
{
    "success": true,
    "message": "Incident closed successfully",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "status": "closed",
        "closed_at": "2026-02-08T13:00:00Z"
    }
}
```

### 3.7 Add Comment to Incident

**POST /incidents/{incident_id}/comments**
```
Endpoint: https://itsm-api.example.com/api/v1/incidents/550e8400-e29b-41d4-a716-446655440003/comments
Method: POST
Authorization: Bearer {jwt_token}

Request Body:
{
    "content": "Investigating with the database team",
    "is_public": true,
    "comment_type": "comment",
    "mentioned_users": ["550e8400-e29b-41d4-a716-446655440008", "550e8400-e29b-41d4-a716-446655440009"]
}

Response (201 Created):
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440010",
        "content": "Investigating with the database team",
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "John Manager"
        },
        "created_at": "2026-02-08T11:30:00Z"
    }
}
```

---

## SERVICE REQUEST MANAGEMENT APIs {#service-request-apis}

### 4.1 Create Service Request

**POST /service-requests**
```
Endpoint: https://itsm-api.example.com/api/v1/service-requests
Method: POST
Authorization: Bearer {jwt_token}
Permissions Required: service_request:create

Request Body:
{
    "service_id": "550e8400-e29b-41d4-a716-446655440011",
    "title": "Request for new laptop",
    "description": "Need a new laptop for new employee in Sales department",
    "custom_data": {
        "employee_name": "Alex Johnson",
        "laptop_specs": "Windows, 16GB RAM, 512GB SSD",
        "cost_center": "CC001",
        "needed_by": "2026-02-15"
    }
}

Response (201 Created):
{
    "success": true,
    "status_code": 201,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440012",
        "ticket_number": "SR-000001",
        "service_id": "550e8400-e29b-41d4-a716-446655440011",
        "service_name": "Hardware Procurement",
        "title": "Request for new laptop",
        "status": "submitted",
        "requires_approval": true,
        "approval_level": 0,
        "current_approver": {
            "id": "550e8400-e29b-41d4-a716-446655440013",
            "name": "Sarah Manager",
            "email": "sarah.manager@example.com"
        },
        "approval_deadline": "2026-02-09T10:00:00Z",
        "created_at": "2026-02-08T10:30:00Z"
    }
}
```

### 4.2 Get Service Catalog

**GET /services**
```
Query Parameters:
- category: {category_id}
- active_only: true
- search: {text}
- page: 1
- limit: 20

Response (200 OK):
{
    "success": true,
    "data": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440011",
            "name": "Hardware Procurement",
            "description": "Request new hardware or equipment",
            "category": "IT Services",
            "icon_url": "https://cdn.example.com/hardware.png",
            "requires_approval": true,
            "request_form_fields": [
                {
                    "name": "employee_name",
                    "type": "text",
                    "required": true,
                    "label": "Employee Name"
                },
                {
                    "name": "device_type",
                    "type": "select",
                    "required": true,
                    "label": "Device Type",
                    "options": ["Laptop", "Desktop", "Printer", "Monitor"]
                }
            ]
        },
        // ... more services
    ],
    "pagination": {
        "total_count": 15,
        "page": 1,
        "page_size": 20,
        "total_pages": 1
    }
}
```

### 4.3 Approve Service Request

**POST /service-requests/{request_id}/approve**
```
Endpoint: https://itsm-api.example.com/api/v1/service-requests/550e8400-e29b-41d4-a716-446655440012/approve
Method: POST
Authorization: Bearer {jwt_token}
Permissions Required: service_request:approve

Request Body:
{
    "comments": "Approved - budget available",
    "approval_level": 1
}

Response (200 OK):
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440012",
        "ticket_number": "SR-000001",
        "status": "approved",
        "current_approver": null,
        "approval_deadline": null
    }
}
```

### 4.4 Reject Service Request

**POST /service-requests/{request_id}/reject**
```
Endpoint: https://itsm-api.example.com/api/v1/service-requests/550e8400-e29b-41d4-a716-446655440012/reject
Method: POST
Authorization: Bearer {jwt_token}
Permissions Required: service_request:approve

Request Body:
{
    "comments": "Budget not available this quarter",
    "approval_level": 1
}

Response (200 OK):
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440012",
        "ticket_number": "SR-000001",
        "status": "rejected"
    }
}
```

---

## PROBLEM MANAGEMENT APIs {#problem-apis}

### 5.1 Create Problem

**POST /problems**
```
Endpoint: https://itsm-api.example.com/api/v1/problems
Method: POST
Authorization: Bearer {jwt_token}
Permissions Required: problem:create

Request Body:
{
    "title": "Recurring email authentication failures",
    "description": "Multiple users experiencing authentication issues with email",
    "symptoms": "Users receive 'Invalid credentials' error despite correct password",
    "impact_description": "Users unable to access email, productivity impact high",
    "category": "Authentication",
    "priority": "high",
    "incident_ids": [
        "550e8400-e29b-41d4-a716-446655440003",
        "550e8400-e29b-41d4-a716-446655440014"
    ]
}

Response (201 Created):
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440015",
        "problem_number": "PRB-000001",
        "title": "Recurring email authentication failures",
        "status": "new",
        "priority": "high",
        "related_incidents": 2,
        "created_at": "2026-02-08T10:30:00Z"
    }
}
```

### 5.2 Perform Root Cause Analysis

**POST /problems/{problem_id}/rca**
```
Endpoint: https://itsm-api.example.com/api/v1/problems/550e8400-e29b-41d4-a716-446655440015/rca
Method: POST
Authorization: Bearer {jwt_token}
Permissions Required: problem:update

Request Body:
{
    "analysis_method": "5_why",
    "root_cause_description": "LDAP replication lag between servers causing authentication cache invalidation",
    "contributing_factors": "Network latency, server maintenance schedule conflict",
    "evidence_links": ["server_log_001.txt", "network_trace_001.pcap"]
}

Response (200 OK):
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440016",
        "problem_id": "550e8400-e29b-41d4-a716-446655440015",
        "root_cause_description": "LDAP replication lag between servers...",
        "analysis_date": "2026-02-08T11:30:00Z",
        "analyzed_by": "Jane Smith"
    }
}
```

### 5.3 Create Known Error (KEDB)

**POST /kedb**
```
Endpoint: https://itsm-api.example.com/api/v1/kedb
Method: POST
Authorization: Bearer {jwt_token}
Permissions Required: problem:update,kedb:create

Request Body:
{
    "problem_id": "550e8400-e29b-41d4-a716-446655440015",
    "symptoms": "Users receive 'Invalid credentials' error when logging into email",
    "workaround": "Ask users to clear browser cache and try again, or use OWA directly",
    "permanent_fix_description": "Upgrade LDAP replication interval from 30min to 5min"
}

Response (201 Created):
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440017",
        "error_number": "KEDB-000001",
        "problem_id": "550e8400-e29b-41d4-a716-446655440015",
        "symptoms": "Users receive 'Invalid credentials' error...",
        "status": "active",
        "created_at": "2026-02-08T12:00:00Z"
    }
}
```

---

## CHANGE MANAGEMENT APIs {#change-apis}

### 6.1 Create Change Request

**POST /changes**
```
Endpoint: https://itsm-api.example.com/api/v1/changes
Method: POST
Authorization: Bearer {jwt_token}
Permissions Required: change:create

Request Body:
{
    "title": "Upgrade email server to v2024.1",
    "description": "Upgrade email server to latest version for security patches",
    "business_justification": "Critical security updates required",
    "change_type": "normal",
    "category": "Application Update",
    "priority": "high",
    "risk_level": "high",
    "change_owner_id": "550e8400-e29b-41d4-a716-446655440018",
    "planned_start_date": "2026-02-15T22:00:00Z",
    "planned_end_date": "2026-02-16T06:00:00Z",
    "affected_services": ["email", "calendar"],
    "estimated_impact_description": "Email service unavailable for ~2 hours during maintenance window",
    "rollback_plan": "Restore from pre-upgrade backup if issues occur",
    "requires_cab_approval": true
}

Response (201 Created):
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440019",
        "change_number": "CHG-000001",
        "title": "Upgrade email server to v2024.1",
        "status": "draft",
        "change_type": "normal",
        "priority": "high",
        "requires_cab_approval": true,
        "created_at": "2026-02-08T10:30:00Z"
    }
}
```

### 6.2 Submit Change for Approval

**POST /changes/{change_id}/submit**
```
Endpoint: https://itsm-api.example.com/api/v1/changes/550e8400-e29b-41d4-a716-446655440019/submit
Method: POST
Authorization: Bearer {jwt_token}
Permissions Required: change:update

Response (200 OK):
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440019",
        "status": "pending_approval",
        "cab_members_to_approve": 5,
        "approval_deadline": "2026-02-10T10:00:00Z"
    }
}
```

### 6.3 CAB Approval

**POST /changes/{change_id}/approve**
```
Endpoint: https://itsm-api.example.com/api/v1/changes/550e8400-e29b-41d4-a716-446655440019/approve
Method: POST
Authorization: Bearer {jwt_token}
Permissions Required: change:approve

Request Body:
{
    "comments": "Change looks good. Testing completed successfully.",
    "approval_step": 1
}

Response (200 OK):
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440019",
        "approvals_count": 3,
        "approvals_required": 5,
        "status": "pending_approval"
    }
}
```

### 6.4 Implement Change

**POST /changes/{change_id}/implement**
```
Endpoint: https://itsm-api.example.com/api/v1/changes/550e8400-e29b-41d4-a716-446655440019/implement
Method: POST
Authorization: Bearer {jwt_token}
Permissions Required: change:implement

Request Body:
{
    "actual_start_date": "2026-02-15T22:05:00Z"
}

Response (200 OK):
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440019",
        "status": "in_progress",
        "actual_start_date": "2026-02-15T22:05:00Z"
    }
}
```

### 6.5 Complete Change

**POST /changes/{change_id}/complete**
```
Endpoint: https://itsm-api.example.com/api/v1/changes/550e8400-e29b-41d4-a716-446655440019/complete
Method: POST
Authorization: Bearer {jwt_token}
Permissions Required: change:implement

Request Body:
{
    "actual_end_date": "2026-02-16T05:55:00Z",
    "test_results": {
        "status": "success",
        "details": "All functionality tested and working correctly"
    }
}

Response (200 OK):
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440019",
        "status": "completed",
        "actual_end_date": "2026-02-16T05:55:00Z"
    }
}
```

---

## CMDB APIs {#cmdb-apis}

### 7.1 Create Configuration Item

**POST /cmdb/configuration-items**
```
Endpoint: https://itsm-api.example.com/api/v1/cmdb/configuration-items
Method: POST
Authorization: Bearer {jwt_token}
Permissions Required: cmdb:create

Request Body:
{
    "name": "Exchange Server 2024",
    "description": "Primary email server",
    "category_id": "550e8400-e29b-41d4-a716-446655440020",
    "ci_type": "application",
    "owner_id": "550e8400-e29b-41d4-a716-446655440018",
    "version": "2024.1",
    "location": "Data Center A",
    "serial_number": "EX-DC-2024-001",
    "manufacturer": "Microsoft",
    "model": "Exchange Server Enterprise",
    "environment": "production",
    "criticality": "critical"
}

Response (201 Created):
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440021",
        "ci_number": "CI-000001",
        "name": "Exchange Server 2024",
        "status": "active",
        "created_at": "2026-02-08T10:30:00Z"
    }
}
```

### 7.2 Create CI Relationship

**POST /cmdb/relationships**
```
Endpoint: https://itsm-api.example.com/api/v1/cmdb/relationships
Method: POST
Authorization: Bearer {jwt_token}
Permissions Required: cmdb:update

Request Body:
{
    "source_ci_id": "550e8400-e29b-41d4-a716-446655440021",
    "target_ci_id": "550e8400-e29b-41d4-a716-446655440022",
    "relationship_type": "hosted_on",
    "description": "Exchange Server hosted on this hardware"
}

Response (201 Created):
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440023",
        "relationship_type": "hosted_on"
    }
}
```

### 7.3 Get Impact Analysis

**GET /cmdb/configuration-items/{ci_id}/impact-analysis**
```
Endpoint: https://itsm-api.example.com/api/v1/cmdb/configuration-items/550e8400-e29b-41d4-a716-446655440021/impact-analysis
Method: GET
Authorization: Bearer {jwt_token}

Response (200 OK):
{
    "success": true,
    "data": {
        "ci_id": "550e8400-e29b-41d4-a716-446655440021",
        "ci_name": "Exchange Server 2024",
        "dependent_cis": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440024",
                "name": "Mail Client Application",
                "relationship_type": "depends_on",
                "criticality": "high"
            }
        ],
        "supporting_cis": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440022",
                "name": "Server Hardware",
                "relationship_type": "hosted_on",
                "criticality": "critical"
            }
        ],
        "affected_services": ["email", "calendar"],
        "potential_impact": "HIGH - Email service would be unavailable"
    }
}
```

---

## SLA & REPORTING APIs {#sla-apis}

### 8.1 Get SLA Dashboard

**GET /dashboard/sla**
```
Endpoint: https://itsm-api.example.com/api/v1/dashboard/sla
Method: GET
Authorization: Bearer {jwt_token}

Query Parameters:
- period: today,week,month,year,custom
- date_from: 2026-01-01
- date_to: 2026-02-08

Response (200 OK):
{
    "success": true,
    "data": {
        "summary": {
            "total_incidents": 150,
            "compliant_incidents": 135,
            "non_compliant_incidents": 15,
            "overall_compliance_percentage": 90.0
        },
        "by_priority": [
            {
                "priority": "critical",
                "total": 10,
                "compliant": 8,
                "compliance_percentage": 80.0
            },
            {
                "priority": "high",
                "total": 40,
                "compliant": 38,
                "compliance_percentage": 95.0
            }
        ],
        "by_policy": [
            {
                "policy_id": "550e8400-e29b-41d4-a716-446655440025",
                "policy_name": "Critical - 1hr Response",
                "total": 10,
                "compliant": 8,
                "compliance_percentage": 80.0,
                "avg_response_time_minutes": 45,
                "avg_resolution_time_hours": 2.5
            }
        ],
        "trends": [
            {
                "date": "2026-02-01",
                "compliance_percentage": 88.5
            },
            {
                "date": "2026-02-02",
                "compliance_percentage": 89.2
            },
            // ... more dates
        ]
    }
}
```

### 8.2 SLA Breach Report

**GET /reports/sla-breaches**
```
Endpoint: https://itsm-api.example.com/api/v1/reports/sla-breaches
Method: GET
Authorization: Bearer {jwt_token}

Query Parameters:
- breach_type: response,resolution
- period: month

Response (200 OK):
{
    "success": true,
    "data": {
        "total_breaches": 15,
        "breaches": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440026",
                "ticket_number": "INC-000005",
                "ticket_title": "Database connection timeout",
                "breach_type": "resolution",
                "sla_policy": "Critical - 4hr Resolution",
                "breached_by_minutes": 25,
                "breach_time": "2026-02-05T14:45:00Z",
                "priority": "critical"
            }
        ],
        "by_team": [
            {
                "team_name": "Database Team",
                "breach_count": 5,
                "percentage": 33.3
            }
        ]
    }
}
```

---

## ERROR HANDLING & RESPONSE CODES {#error-handling}

### 9.1 HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Successful GET/PUT |
| 201 | Created | Incident created |
| 204 | No Content | Resource deleted |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing JWT token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Duplicate ticket number |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Maintenance mode |

### 9.2 Error Response Examples

**Validation Error (400)**
```json
{
    "success": false,
    "status_code": 400,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Input validation failed",
        "details": [
            {
                "field": "priority",
                "message": "Must be one of: critical, high, medium, low"
            },
            {
                "field": "impact",
                "message": "This field is required"
            }
        ]
    }
}
```

**Authorization Error (403)**
```json
{
    "success": false,
    "status_code": 403,
    "error": {
        "code": "INSUFFICIENT_PERMISSIONS",
        "message": "You do not have permission to access this resource",
        "required_permissions": ["incident:update"],
        "your_permissions": ["incident:read"]
    }
}
```

**Rate Limit Error (429)**
```json
{
    "success": false,
    "status_code": 429,
    "error": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "Too many requests",
        "retry_after_seconds": 60
    }
}
```

---

## API Implementation Notes

✅ **Authentication**: JWT tokens with 1-hour expiration  
✅ **CORS**: Configured for secure cross-origin requests  
✅ **Rate Limiting**: 1000 requests/hour per user  
✅ **Caching**: Response caching with ETags  
✅ **Versioning**: API versioning in URL path (/api/v1, /api/v2)  
✅ **Documentation**: OpenAPI 3.0 spec at /api/v1/docs  
✅ **Logging**: All requests logged with request_id for tracing  
✅ **Webhooks**: Supported for notifications (optional)  

