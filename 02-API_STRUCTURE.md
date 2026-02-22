# ITSM System - REST API Structure
## API Endpoints & Documentation (OpenAPI 3.0 Compliant)

---

## 1. API OVERVIEW

### 1.1 Base URL
```
Production: https://api.itsm.company.com/v1
Staging: https://api-staging.itsm.company.com/v1
Development: http://localhost:8000/api/v1
```

### 1.2 Authentication
All API requests require authentication using JWT (JSON Web Tokens).

**Authentication Flow:**
```
1. POST /auth/login → Returns access_token + refresh_token
2. Include in headers: Authorization: Bearer {access_token}
3. Token expires in 1 hour
4. Use POST /auth/refresh to get new access_token
```

### 1.3 Standard Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "uuid"
  }
}
```

### 1.4 Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "uuid"
  }
}
```

### 1.5 HTTP Status Codes
- `200 OK`: Successful GET, PUT, PATCH
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### 1.6 Pagination
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 25,
    "total": 150,
    "total_pages": 6,
    "has_next": true,
    "has_prev": false
  }
}
```

### 1.7 Filtering & Sorting
```
GET /tickets?status=open&priority=high&sort=-created_at&page=1&per_page=25
```

---

## 2. AUTHENTICATION ENDPOINTS

### 2.1 Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "mfa_code": "123456" // Optional, if MFA enabled
}

Response 200:
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "agent",
      "organization_id": "uuid"
    }
  }
}
```

### 2.2 Refresh Token
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}

Response 200:
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600
  }
}
```

### 2.3 Logout
```http
POST /auth/logout
Authorization: Bearer {access_token}

Response 204: No Content
```

### 2.4 Password Reset Request
```http
POST /auth/password-reset/request
Content-Type: application/json

{
  "email": "user@example.com"
}

Response 200:
{
  "success": true,
  "message": "Password reset email sent"
}
```

### 2.5 Password Reset Confirm
```http
POST /auth/password-reset/confirm
Content-Type: application/json

{
  "token": "reset_token_from_email",
  "new_password": "NewSecurePassword123!"
}

Response 200:
{
  "success": true,
  "message": "Password reset successful"
}
```

### 2.6 Enable MFA
```http
POST /auth/mfa/enable
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": {
    "secret": "JBSWY3DPEHPK3PXP",
    "qr_code": "data:image/png;base64,iVBORw0KG...",
    "backup_codes": ["12345678", "87654321", ...]
  }
}
```

---

## 3. USER MANAGEMENT ENDPOINTS

### 3.1 List Users
```http
GET /users?page=1&per_page=25&role=agent&is_active=true
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "username": "john.doe",
      "email": "john.doe@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "agent",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

### 3.2 Get User Details
```http
GET /users/{user_id}
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": {
    "id": "uuid",
    "username": "john.doe",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "role": "agent",
    "is_active": true,
    "is_verified": true,
    "mfa_enabled": true,
    "last_login": "2024-01-15T10:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "teams": [
      {
        "id": "uuid",
        "name": "Service Desk Team"
      }
    ]
  }
}
```

### 3.3 Create User
```http
POST /users
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "username": "jane.smith",
  "email": "jane.smith@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "password": "SecurePassword123!",
  "role": "agent",
  "phone": "+1234567890",
  "team_ids": ["uuid1", "uuid2"]
}

Response 201:
{
  "success": true,
  "data": {
    "id": "uuid",
    "username": "jane.smith",
    "email": "jane.smith@example.com",
    ...
  },
  "message": "User created successfully"
}
```

### 3.4 Update User
```http
PATCH /users/{user_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "first_name": "Jane",
  "phone": "+0987654321",
  "is_active": true
}

Response 200:
{
  "success": true,
  "data": { ... },
  "message": "User updated successfully"
}
```

### 3.5 Delete User
```http
DELETE /users/{user_id}
Authorization: Bearer {access_token}

Response 204: No Content
```

---

## 4. TICKET MANAGEMENT ENDPOINTS

### 4.1 List Tickets
```http
GET /tickets?status=open&priority=high&assigned_to_me=true&page=1&per_page=25
Authorization: Bearer {access_token}

Query Parameters:
- status: new, assigned, in_progress, on_hold, resolved, closed
- priority: critical, high, medium, low
- ticket_type: incident, service_request, problem, change
- assigned_to_me: true/false
- requester_id: uuid
- assigned_to_id: uuid
- assigned_team_id: uuid
- category: string
- created_after: ISO 8601 date
- created_before: ISO 8601 date
- sla_breached: true/false
- search: string (searches title and description)
- sort: field_name or -field_name (descending)

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "ticket_number": "INC-20240115-001234",
      "ticket_type": "incident",
      "title": "Email service down",
      "description": "Users unable to access email",
      "status": "in_progress",
      "priority": "high",
      "requester": {
        "id": "uuid",
        "name": "John Doe",
        "email": "john.doe@example.com"
      },
      "assigned_to": {
        "id": "uuid",
        "name": "Jane Smith",
        "email": "jane.smith@example.com"
      },
      "assigned_team": {
        "id": "uuid",
        "name": "Service Desk Team"
      },
      "category": "Email",
      "subcategory": "Outlook",
      "sla": {
        "response_due_at": "2024-01-15T11:00:00Z",
        "resolution_due_at": "2024-01-15T18:00:00Z",
        "response_breached": false,
        "resolution_breached": false
      },
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": { ... }
}
```

### 4.2 Get Ticket Details
```http
GET /tickets/{ticket_id}
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": {
    "id": "uuid",
    "ticket_number": "INC-20240115-001234",
    "ticket_type": "incident",
    "title": "Email service down",
    "description": "Users unable to access email since 10:00 AM",
    "status": "in_progress",
    "priority": "high",
    "requester": { ... },
    "assigned_to": { ... },
    "assigned_team": { ... },
    "category": "Email",
    "subcategory": "Outlook",
    "tags": ["email", "outlook", "urgent"],
    "custom_fields": {
      "affected_users_count": 50,
      "business_impact": "High"
    },
    "sla": {
      "policy_name": "Default Incident SLA - High",
      "response_due_at": "2024-01-15T11:00:00Z",
      "resolution_due_at": "2024-01-15T18:00:00Z",
      "first_response_at": "2024-01-15T10:15:00Z",
      "response_breached": false,
      "resolution_breached": false,
      "time_remaining_minutes": 420
    },
    "incident_details": {
      "impact": "high",
      "urgency": "high",
      "escalation_level": 1,
      "related_problem_id": null
    },
    "configuration_items": [
      {
        "id": "uuid",
        "name": "Exchange Server 01",
        "ci_type": "Server"
      }
    ],
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "resolved_at": null,
    "closed_at": null
  }
}
```

### 4.3 Create Ticket (Incident)
```http
POST /tickets
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "ticket_type": "incident",
  "title": "Cannot access shared drive",
  "description": "Getting 'Access Denied' error when trying to open \\\\fileserver\\shared",
  "priority": "medium", // Optional, will be calculated for incidents
  "category": "File Server",
  "subcategory": "Access Issues",
  "requester_id": "uuid", // Optional, defaults to current user
  "assigned_to_id": "uuid", // Optional
  "assigned_team_id": "uuid", // Optional
  "tags": ["file-server", "access"],
  "custom_fields": {
    "location": "Building A, Floor 3"
  },
  "incident_details": {
    "impact": "medium",
    "urgency": "high"
  },
  "configuration_item_ids": ["uuid1", "uuid2"]
}

Response 201:
{
  "success": true,
  "data": {
    "id": "uuid",
    "ticket_number": "INC-20240115-001235",
    ...
  },
  "message": "Incident created successfully"
}
```

### 4.4 Update Ticket
```http
PATCH /tickets/{ticket_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "status": "in_progress",
  "assigned_to_id": "uuid",
  "priority": "high",
  "tags": ["urgent", "file-server"]
}

Response 200:
{
  "success": true,
  "data": { ... },
  "message": "Ticket updated successfully"
}
```

### 4.5 Assign Ticket
```http
POST /tickets/{ticket_id}/assign
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "assigned_to_id": "uuid", // Optional
  "assigned_team_id": "uuid", // Optional
  "comment": "Assigning to network team for investigation"
}

Response 200:
{
  "success": true,
  "data": { ... },
  "message": "Ticket assigned successfully"
}
```

### 4.6 Resolve Ticket
```http
POST /tickets/{ticket_id}/resolve
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "resolution_notes": "Reset user permissions on file server. Issue resolved.",
  "root_cause": "Permissions were accidentally removed during maintenance",
  "notify_requester": true
}

Response 200:
{
  "success": true,
  "data": { ... },
  "message": "Ticket resolved successfully"
}
```

### 4.7 Close Ticket
```http
POST /tickets/{ticket_id}/close
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "closure_notes": "Confirmed with user that issue is resolved",
  "satisfaction_rating": 5 // 1-5 scale
}

Response 200:
{
  "success": true,
  "data": { ... },
  "message": "Ticket closed successfully"
}
```

### 4.8 Reopen Ticket
```http
POST /tickets/{ticket_id}/reopen
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "reason": "Issue has recurred",
  "comment": "User reports same error again"
}

Response 200:
{
  "success": true,
  "data": { ... },
  "message": "Ticket reopened successfully"
}
```

---

## 5. COMMENTS & ATTACHMENTS

### 5.1 List Comments
```http
GET /tickets/{ticket_id}/comments?page=1&per_page=25
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "content": "Investigating the issue now",
      "is_internal": false,
      "is_system_generated": false,
      "user": {
        "id": "uuid",
        "name": "Jane Smith",
        "email": "jane.smith@example.com"
      },
      "attachments": [
        {
          "id": "uuid",
          "file_name": "screenshot.png",
          "file_size": 102400,
          "mime_type": "image/png",
          "download_url": "/attachments/uuid/download"
        }
      ],
      "created_at": "2024-01-15T10:15:00Z"
    }
  ],
  "pagination": { ... }
}
```

### 5.2 Add Comment
```http
POST /tickets/{ticket_id}/comments
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "content": "I've reset the permissions. Please try accessing the drive again.",
  "is_internal": false,
  "notify_requester": true
}

Response 201:
{
  "success": true,
  "data": { ... },
  "message": "Comment added successfully"
}
```

### 5.3 Upload Attachment
```http
POST /tickets/{ticket_id}/attachments
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

file: [binary data]
comment_id: uuid (optional)

Response 201:
{
  "success": true,
  "data": {
    "id": "uuid",
    "file_name": "error_log.txt",
    "file_size": 5120,
    "mime_type": "text/plain",
    "download_url": "/attachments/uuid/download"
  },
  "message": "Attachment uploaded successfully"
}
```

### 5.4 Download Attachment
```http
GET /attachments/{attachment_id}/download
Authorization: Bearer {access_token}

Response 200:
Content-Type: [mime_type]
Content-Disposition: attachment; filename="error_log.txt"
[binary data]
```

---

## 6. SERVICE REQUEST ENDPOINTS

### 6.1 List Service Catalog
```http
GET /service-catalog?category=Hardware&is_active=true
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "New Laptop Request",
      "description": "Request a new laptop for employee",
      "category": "Hardware",
      "icon": "laptop",
      "requires_approval": true,
      "estimated_delivery_time": 72,
      "form_fields": [
        {
          "name": "laptop_model",
          "label": "Laptop Model",
          "type": "select",
          "required": true,
          "options": ["Dell Latitude 5420", "HP EliteBook 840"]
        },
        {
          "name": "justification",
          "label": "Business Justification",
          "type": "textarea",
          "required": true
        }
      ]
    }
  ]
}
```

### 6.2 Create Service Request
```http
POST /tickets
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "ticket_type": "service_request",
  "service_catalog_id": "uuid",
  "title": "New Laptop Request - John Doe",
  "description": "Requesting new laptop for new employee",
  "requested_for_id": "uuid", // Optional, different from requester
  "form_data": {
    "laptop_model": "Dell Latitude 5420",
    "justification": "New hire starting next week"
  }
}

Response 201:
{
  "success": true,
  "data": {
    "id": "uuid",
    "ticket_number": "SR-20240115-001001",
    "approval_status": "pending",
    ...
  },
  "message": "Service request created successfully"
}
```

### 6.3 Approve Service Request
```http
POST /service-requests/{request_id}/approve
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "comments": "Approved. Proceed with laptop procurement."
}

Response 200:
{
  "success": true,
  "data": { ... },
  "message": "Service request approved"
}
```

### 6.4 Reject Service Request
```http
POST /service-requests/{request_id}/reject
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "rejection_reason": "Budget constraints. Please resubmit next quarter."
}

Response 200:
{
  "success": true,
  "data": { ... },
  "message": "Service request rejected"
}
```

---

## 7. PROBLEM MANAGEMENT ENDPOINTS

### 7.1 Create Problem
```http
POST /tickets
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "ticket_type": "problem",
  "title": "Recurring email service outages",
  "description": "Email service has been experiencing intermittent outages over the past week",
  "priority": "high",
  "problem_details": {
    "impact_assessment": "Affects 200+ users during outages",
    "related_incident_ids": ["uuid1", "uuid2", "uuid3"]
  }
}

Response 201:
{
  "success": true,
  "data": {
    "id": "uuid",
    "ticket_number": "PRB-20240115-000050",
    ...
  },
  "message": "Problem record created successfully"
}
```

### 7.2 Link Incidents to Problem
```http
POST /problems/{problem_id}/link-incidents
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "incident_ids": ["uuid1", "uuid2", "uuid3"]
}

Response 200:
{
  "success": true,
  "message": "Incidents linked to problem successfully"
}
```

### 7.3 Create Known Error
```http
POST /known-errors
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "problem_id": "uuid",
  "title": "Exchange Server Memory Leak",
  "description": "Exchange server experiences memory leak after 48 hours of uptime",
  "symptoms": "Email delays, server unresponsiveness",
  "root_cause": "Memory leak in Exchange transport service",
  "workaround": "Restart Exchange transport service daily",
  "permanent_solution": "Apply Microsoft patch KB5012345",
  "category": "Email",
  "affected_cis": ["uuid1", "uuid2"]
}

Response 201:
{
  "success": true,
  "data": { ... },
  "message": "Known error created successfully"
}
```

### 7.4 Search Known Errors
```http
GET /known-errors/search?q=email+outage&category=Email
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "title": "Exchange Server Memory Leak",
      "description": "...",
      "workaround": "...",
      "times_referenced": 15,
      "relevance_score": 0.95
    }
  ]
}
```

---

## 8. CHANGE MANAGEMENT ENDPOINTS

### 8.1 Create Change Request
```http
POST /tickets
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "ticket_type": "change",
  "title": "Upgrade Exchange Server to 2019",
  "description": "Upgrade email server from Exchange 2016 to 2019",
  "priority": "medium",
  "change_details": {
    "change_type": "normal",
    "risk_level": "medium",
    "risk_assessment": "Potential email downtime during upgrade",
    "impact_analysis": "All email users will be affected",
    "affected_services": ["Email", "Calendar"],
    "affected_ci_ids": ["uuid1", "uuid2"],
    "implementation_plan": "1. Backup current server\n2. Install Exchange 2019\n3. Migrate mailboxes\n4. Test functionality",
    "backout_plan": "Restore from backup if issues occur",
    "test_plan": "Send test emails, verify calendar sync",
    "planned_start_date": "2024-01-20T02:00:00Z",
    "planned_end_date": "2024-01-20T06:00:00Z"
  }
}

Response 201:
{
  "success": true,
  "data": {
    "id": "uuid",
    "ticket_number": "CHG-20240115-000100",
    "cab_approval_status": "pending",
    ...
  },
  "message": "Change request created successfully"
}
```

### 8.2 Submit for CAB Approval
```http
POST /changes/{change_id}/submit-for-approval
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "cab_meeting_date": "2024-01-18T14:00:00Z"
}

Response 200:
{
  "success": true,
  "message": "Change submitted for CAB approval"
}
```

### 8.3 CAB Vote
```http
POST /changes/{change_id}/cab-vote
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "decision": "approved", // approved, rejected, abstained
  "comments": "Approved with condition: perform during maintenance window"
}

Response 200:
{
  "success": true,
  "message": "Vote recorded successfully"
}
```

### 8.4 Implement Change
```http
POST /changes/{change_id}/implement
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "actual_start_date": "2024-01-20T02:00:00Z",
  "implementation_notes": "Starting Exchange upgrade process"
}

Response 200:
{
  "success": true,
  "message": "Change implementation started"
}
```

### 8.5 Complete Change
```http
POST /changes/{change_id}/complete
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "actual_end_date": "2024-01-20T05:30:00Z",
  "implementation_status": "completed", // completed, failed, rolled_back
  "implementation_notes": "Upgrade completed successfully. All tests passed."
}

Response 200:
{
  "success": true,
  "message": "Change completed successfully"
}
```

---

## 9. CMDB ENDPOINTS

### 9.1 List Configuration Items
```http
GET /configuration-items?ci_type=Server&status=active&page=1&per_page=25
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "ci_number": "CI-SRV-001234",
      "name": "Exchange Server 01",
      "ci_type": "Server",
      "ci_class": "hardware",
      "status": "active",
      "owner": {
        "id": "uuid",
        "name": "IT Department"
      },
      "location": "Data Center A, Rack 12",
      "ip_address": "192.168.1.100",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

### 9.2 Get CI Details
```http
GET /configuration-items/{ci_id}
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": {
    "id": "uuid",
    "ci_number": "CI-SRV-001234",
    "name": "Exchange Server 01",
    "description": "Primary email server",
    "ci_type": "Server",
    "ci_class": "hardware",
    "status": "active",
    "owner": { ... },
    "managed_by_team": { ... },
    "location": "Data Center A",
    "data_center": "DC-A",
    "rack_position": "Rack 12, U10-U12",
    "manufacturer": "Dell",
    "model": "PowerEdge R740",
    "serial_number": "SN123456789",
    "asset_tag": "ASSET-001234",
    "ip_address": "192.168.1.100",
    "mac_address": "00:1A:2B:3C:4D:5E",
    "hostname": "exch-srv-01.company.com",
    "purchase_date": "2023-01-15",
    "warranty_expiry_date": "2026-01-15",
    "cost": 15000.00,
    "attributes": {
      "cpu": "Intel Xeon Gold 6230",
      "ram": "128GB",
      "storage": "2TB SSD RAID 10",
      "os": "Windows Server 2019"
    },
    "relationships": {
      "depends_on": [
        {
          "id": "uuid",
          "name": "Network Switch 01",
          "relationship_type": "depends_on"
        }
      ],
      "hosts": [
        {
          "id": "uuid",
          "name": "Exchange Application",
          "relationship_type": "hosts"
        }
      ]
    },
    "related_tickets": {
      "total": 15,
      "open": 2,
      "recent": [...]
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
  }
}
```

### 9.3 Create Configuration Item
```http
POST /configuration-items
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Web Server 03",
  "description": "Production web server",
  "ci_category_id": "uuid",
  "ci_type": "Server",
  "ci_class": "hardware",
  "status": "active",
  "owner_id": "uuid",
  "managed_by_team_id": "uuid",
  "location": "Data Center B",
  "manufacturer": "HP",
  "model": "ProLiant DL380",
  "serial_number": "SN987654321",
  "ip_address": "192.168.2.50",
  "attributes": {
    "cpu": "Intel Xeon Silver 4214",
    "ram": "64GB",
    "os": "Ubuntu 22.04 LTS"
  }
}

Response 201:
{
  "success": true,
  "data": { ... },
  "message": "Configuration item created successfully"
}
```

### 9.4 Create CI Relationship
```http
POST /configuration-items/{ci_id}/relationships
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "child_ci_id": "uuid",
  "relationship_type": "hosts", // hosts, depends_on, connects_to, runs_on, uses, part_of
  "description": "Exchange application runs on this server"
}

Response 201:
{
  "success": true,
  "message": "Relationship created successfully"
}
```

### 9.5 Get CI Impact Analysis
```http
GET /configuration-items/{ci_id}/impact-analysis
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": {
    "ci": { ... },
    "dependent_cis": [
      {
        "id": "uuid",
        "name": "Email Application",
        "ci_type": "Application",
        "relationship": "runs_on"
      }
    ],
    "dependency_cis": [
      {
        "id": "uuid",
        "name": "Network Switch 01",
        "ci_type": "Network Device",
        "relationship": "depends_on"
      }
    ],
    "affected_services": ["Email", "Calendar"],
    "related_tickets": {
      "open": 2,
      "total": 15
    },
    "risk_assessment": "high" // Based on dependencies
  }
}
```

---

## 10. SLA MANAGEMENT ENDPOINTS

### 10.1 List SLA Policies
```http
GET /sla-policies?ticket_type=incident&is_active=true
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Default Incident SLA - Critical",
      "ticket_type": "incident",
      "priority": "critical",
      "response_time": 15,
      "resolution_time": 240,
      "is_active": true,
      "is_default": false
    }
  ]
}
```

### 10.2 Get SLA Compliance Report
```http
GET /reports/sla-compliance?start_date=2024-01-01&end_date=2024-01-31&ticket_type=incident
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": {
    "period": {
      "start": "2024-01-01",
      "end": "2024-01-31"
    },
    "overall": {
      "total_tickets": 500,
      "response_compliance": 92.5,
      "resolution_compliance": 87.3
    },
    "by_priority": [
      {
        "priority": "critical",
        "total": 50,
        "response_met": 48,
        "response_breached": 2,
        "resolution_met": 45,
        "resolution_breached": 5,
        "response_compliance_pct": 96.0,
        "resolution_compliance_pct": 90.0
      }
    ],
    "trends": [
      {
        "date": "2024-01-01",
        "compliance_pct": 85.0
      }
    ]
  }
}
```

---

## 11. REPORTING & ANALYTICS ENDPOINTS

### 11.1 Dashboard Statistics
```http
GET /dashboard/statistics
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": {
    "tickets": {
      "total_open": 150,
      "new": 25,
      "in_progress": 75,
      "on_hold": 10,
      "pending_approval": 15,
      "total_closed_today": 30,
      "total_closed_this_month": 450
    },
    "sla": {
      "at_risk": 12,
      "breached": 5,
      "compliance_rate": 92.5
    },
    "by_priority": {
      "critical": 5,
      "high": 25,
      "medium": 80,
      "low": 40
    },
    "by_type": {
      "incident": 100,
      "service_request": 35,
      "problem": 10,
      "change": 5
    },
    "my_tickets": {
      "assigned_to_me": 15,
      "created_by_me": 8
    }
  }
}
```

### 11.2 Ticket Volume Report
```http
GET /reports/ticket-volume?start_date=2024-01-01&end_date=2024-01-31&group_by=day
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": {
    "period": {
      "start": "2024-01-01",
      "end": "2024-01-31"
    },
    "total_tickets": 500,
    "breakdown": [
      {
        "date": "2024-01-01",
        "created": 15,
        "resolved": 12,
        "closed": 10
      }
    ]
  }
}
```

### 11.3 Agent Performance Report
```http
GET /reports/agent-performance?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": [
    {
      "agent": {
        "id": "uuid",
        "name": "Jane Smith",
        "email": "jane.smith@example.com"
      },
      "metrics": {
        "total_assigned": 75,
        "total_resolved": 68,
        "total_closed": 65,
        "avg_resolution_time_hours": 4.5,
        "sla_compliance_pct": 94.5,
        "customer_satisfaction_avg": 4.7
      }
    }
  ]
}
```

---

## 12. NOTIFICATION ENDPOINTS

### 12.1 List Notifications
```http
GET /notifications?status=unread&page=1&per_page=25
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "notification_type": "in_app",
      "subject": "New ticket assigned to you",
      "message": "Ticket INC-20240115-001234 has been assigned to you",
      "ticket_id": "uuid",
      "status": "unread",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

### 12.2 Mark as Read
```http
PATCH /notifications/{notification_id}/read
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "message": "Notification marked as read"
}
```

### 12.3 Mark All as Read
```http
POST /notifications/mark-all-read
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "message": "All notifications marked as read"
}
```

---

## 13. SEARCH ENDPOINTS

### 13.1 Global Search
```http
GET /search?q=email+server&type=all&page=1&per_page=25
Authorization: Bearer {access_token}

Query Parameters:
- q: search query
- type: all, tickets, users, cis, known_errors
- filters: JSON object with additional filters

Response 200:
{
  "success": true,
  "data": {
    "tickets": [
      {
        "id": "uuid",
        "ticket_number": "INC-20240115-001234",
        "title": "Email server down",
        "relevance_score": 0.95
      }
    ],
    "configuration_items": [
      {
        "id": "uuid",
        "name": "Exchange Server 01",
        "ci_type": "Server",
        "relevance_score": 0.88
      }
    ],
    "known_errors": [
      {
        "id": "uuid",
        "title": "Exchange Server Memory Leak",
        "relevance_score": 0.82
      }
    ]
  },
  "pagination": { ... }
}
```

---

## 14. AUDIT LOG ENDPOINTS

### 14.1 List Audit Logs
```http
GET /audit-logs?action=login&start_date=2024-01-01&page=1&per_page=25
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "user": {
        "id": "uuid",
        "name": "John Doe",
        "email": "john.doe@example.com"
      },
      "action": "login",
      "resource_type": "user",
      "resource_id": "uuid",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "status": "success",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

---

## 15. WEBHOOK ENDPOINTS

### 15.1 List Webhooks
```http
GET /webhooks
Authorization: Bearer {access_token}

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Slack Notification",
      "url": "https://hooks.slack.com/services/...",
      "events": ["ticket.created", "ticket.assigned", "sla.breached"],
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 15.2 Create Webhook
```http
POST /webhooks
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Teams Notification",
  "url": "https://company.webhook.office.com/...",
  "events": ["ticket.created", "ticket.resolved"],
  "secret": "webhook_secret_key",
  "is_active": true
}

Response 201:
{
  "success": true,
  "data": { ... },
  "message": "Webhook created successfully"
}
```

---

## 16. RATE LIMITING

All API endpoints are rate-limited to prevent abuse:

- **Authenticated requests**: 1000 requests per hour per user
- **Unauthenticated requests**: 100 requests per hour per IP

Rate limit headers included in response:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1642252800
```

When rate limit is exceeded:
```http
Response 429:
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "retry_after": 3600
  }
}
```

---

## 17. WEBHOOKS PAYLOAD EXAMPLES

### 17.1 Ticket Created Event
```json
{
  "event": "ticket.created",
  "timestamp": "2024-01-15T10:00:00Z",
  "data": {
    "ticket": {
      "id": "uuid",
      "ticket_number": "INC-20240115-001234",
      "ticket_type": "incident",
      "title": "Email service down",
      "status": "new",
      "priority": "high",
      "requester": { ... },
      "created_at": "2024-01-15T10:00:00Z"
    }
  }
}
```

### 17.2 SLA Breach Event
```json
{
  "event": "sla.breached",
  "timestamp": "2024-01-15T11:00:00Z",
  "data": {
    "ticket": { ... },
    "sla_type": "response", // or "resolution"
    "due_at": "2024-01-15T11:00:00Z",
    "breach_duration_minutes": 15
  }
}
```

---

## 18. ERROR CODES REFERENCE

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `AUTHENTICATION_REQUIRED` | Authentication token missing or invalid |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions |
| `RESOURCE_NOT_FOUND` | Requested resource does not exist |
| `RESOURCE_CONFLICT` | Resource already exists or conflict detected |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `SLA_POLICY_NOT_FOUND` | No matching SLA policy found |
| `TICKET_ALREADY_CLOSED` | Cannot modify closed ticket |
| `INVALID_STATUS_TRANSITION` | Invalid ticket status change |
| `CAB_APPROVAL_REQUIRED` | Change requires CAB approval |
| `ATTACHMENT_TOO_LARGE` | File size exceeds limit |
| `INVALID_FILE_TYPE` | File type not allowed |
| `INTERNAL_SERVER_ERROR` | Unexpected server error |

---

## 19. API VERSIONING

The API uses URL-based versioning:
- Current version: `/api/v1/`
- When breaking changes are introduced, a new version will be released: `/api/v2/`
- Old versions will be supported for at least 12 months after deprecation notice

---

## 20. BEST PRACTICES

### 20.1 Pagination
Always use pagination for list endpoints to avoid performance issues:
```
GET /tickets?page=1&per_page=25
```

### 20.2 Field Selection
Use `fields` parameter to request only needed fields:
```
GET /tickets?fields=id,ticket_number,title,status
```

### 20.3 Filtering
Combine multiple filters for precise queries:
```
GET /tickets?status=open&priority=high&assigned_to_me=true&created_after=2024-01-01
```

### 20.4 Sorting
Sort results using `sort` parameter (prefix with `-` for descending):
```
GET /tickets?sort=-created_at,priority
```

### 20.5 Caching
Use ETags for efficient caching:
```
Request:
GET /tickets/uuid
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"

Response 304: Not Modified (if unchanged)
Response 200: Updated data with new ETag
```

---

## CONCLUSION

This API structure provides:

✅ **RESTful Design**: Standard HTTP methods and status codes
✅ **Comprehensive Coverage**: All ITIL modules fully supported
✅ **Security**: JWT authentication, RBAC, rate limiting
✅ **Developer-Friendly**: Clear documentation, consistent responses
✅ **Scalability**: Pagination, filtering, field selection
✅ **Integration-Ready**: Webhooks, search, audit logs

**Total Endpoints**: 100+
**Authentication**: JWT with refresh tokens
**Rate Limiting**: 1000 req/hour (authenticated)
**API Version**: v1

**Next**: Business Logic Implementation & Pseudo-code
