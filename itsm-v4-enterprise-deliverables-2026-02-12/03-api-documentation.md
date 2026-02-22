# API Documentation (OpenAPI Outline)

## Overview
- Base URL: `https://{tenant-domain}/api/v1`
- Auth: OAuth2 / OIDC with JWT, SSO via Azure AD / Google / LDAP / SAML
- Tenant-aware: all endpoints scoped by tenant context
- Pagination: `page`, `page_size` (default 50)
- Rate limiting: 60 req/min per user (configurable)

## Common Headers
- `Authorization: Bearer <token>`
- `X-Tenant-ID: <tenant_id>` (if not using tenant subdomain)

## Error Model
```json
{
  "error": "validation_error",
  "details": {
    "field": ["message"]
  },
  "trace_id": "trc-12345"
}
```

## Core Endpoints (Summary)
- Incidents: `GET /incidents`, `POST /incidents`, `POST /incidents/{id}/resolve`
- Service Requests: `GET /service-requests`, `POST /service-requests`, `POST /service-requests/{id}/approve`
- Problems: `GET /problems`, `POST /problems`, `POST /problems/{id}/close`
- Changes: `GET /changes`, `POST /changes`, `POST /changes/{id}/approve`
- CMDB: `GET /cmdb/cis`, `POST /cmdb/cis`, `GET /cmdb/relationships`
- Assets: `GET /assets`, `POST /assets`, `POST /assets/{id}/retire`
- SLA: `GET /reports/sla`, `GET /reports/mttr`, `GET /reports/mtbf`
- Knowledge: `GET /knowledge`, `POST /knowledge`, `POST /knowledge/{id}/publish`
- Workflow: `GET /workflows`, `POST /workflows`, `POST /workflows/{id}/deploy`
- Admin: `GET /admin/tenants`, `POST /admin/tenants`, `GET /admin/audit`

## OpenAPI Snippet (Example)
```yaml
openapi: 3.0.3
info:
  title: ITSM API
  version: 1.0.0
servers:
  - url: https://{tenant-domain}/api/v1
paths:
  /incidents:
    get:
      summary: List incidents
      parameters:
        - in: query
          name: status
          schema:
            type: string
      responses:
        "200":
          description: Incident list
    post:
      summary: Create incident
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/IncidentCreate"
      responses:
        "201":
          description: Created
  /incidents/{id}/resolve:
    post:
      summary: Resolve incident
      parameters:
        - in: path
          name: id
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/IncidentResolve"
      responses:
        "200":
          description: Resolved
components:
  schemas:
    IncidentCreate:
      type: object
      required: [title, impact, urgency, service_id]
      properties:
        title:
          type: string
        description:
          type: string
        impact:
          type: string
        urgency:
          type: string
        service_id:
          type: string
        ci_id:
          type: string
    IncidentResolve:
      type: object
      required: [resolution_notes]
      properties:
        resolution_notes:
          type: string
```
