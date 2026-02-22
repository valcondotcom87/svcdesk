# 05. API Documentation Sample (OpenAPI Style)

## Authentication
- OAuth2 / OIDC / SAML via SSO
- JWT for API calls

## Example Endpoints

### Create Incident
```
POST /api/v1/incidents
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "VPN access issues",
  "description": "User cannot connect to VPN",
  "impact": "high",
  "urgency": "medium",
  "service_id": "svc-123",
  "ci_id": "ci-9901",
  "requester_id": "usr-2001"
}
```

### Update Incident Status
```
POST /api/v1/incidents/{id}/resolve
{
  "resolution_notes": "Reset VPN profile and reissued cert"
}
```

### Submit Service Request
```
POST /api/v1/service-requests
{
  "service_id": "svc-8001",
  "title": "New laptop provision",
  "inputs": {"cpu": "i7", "ram": "16GB", "os": "Windows"}
}
```

### Change Approval
```
POST /api/v1/changes/{id}/approve
{
  "comments": "CAB approved with low risk"
}
```

### SLA Report
```
GET /api/v1/reports/sla?from=2026-01-01&to=2026-01-31
```

## Error Model
```
{
  "error": "validation_error",
  "details": {
    "title": ["This field is required."]
  },
  "trace_id": "trc-9fe2c9"
}
```
