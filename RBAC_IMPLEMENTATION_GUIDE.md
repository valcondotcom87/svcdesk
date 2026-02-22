# ITSM RBAC (Role-Based Access Control) Implementation Guide

## Overview

The ITSM system implements a comprehensive Role-Based Access Control (RBAC) system that governs access to all features and endpoints. The system is built on:

- **Django Permission Framework** - For granular permission management
- **JWT Authentication** - For secure token-based access
- **Role Model** - For grouping permissions
- **UserRole Model** - For assigning roles to users
- **Custom Permission Classes** - For endpoint protection

## System Roles

### 1. End User
- **Description:** Can submit incidents and service requests
- **Permissions:** 5
  - incidents.create, incidents.read
  - service_requests.create, service_requests.read
  - knowledge.read

**Use Case:** Customers, employees submitting requests

---

### 2. Agent
- **Description:** Support agent who resolves incidents and service requests
- **Permissions:** 11
  - incidents.create, incidents.read, incidents.update, incidents.resolve
  - service_requests.create, service_requests.read, service_requests.update, service_requests.fulfill
  - knowledge.read, cmdb.read, assets.read

**Use Case:** First-line support team members

---

### 3. Manager
- **Description:** Manager overseeing teams and managing workflow
- **Permissions:** 40 (includes all agent permissions plus)
  - incidents.delete, incidents.close
  - service_requests.approve, service_requests.delete
  - problems (full CRUD + resolve)
  - changes (full CRUD + approve, implement)
  - knowledge (full CRUD + publish)
  - cmdb.update, assets.update, assets.assign
  - sla.update, reports (create, export)
  - users.reset_password

**Use Case:** Team leads, managers, senior engineers

---

### 4. Administrator
- **Description:** Full system access with all permissions
- **Permissions:** 53 (ALL permissions including)
  - All CRUD operations on all modules
  - User management
  - Role and permission administration
  - Settings and configuration
  - Compliance and audit functions

**Use Case:** System administrators, IT operations

---

## Available Permissions

### Incident Management
- `incidents.create` - Create new incidents
- `incidents.read` - View incidents
- `incidents.update` - Update incident details
- `incidents.delete` - Delete incidents
- `incidents.resolve` - Mark incidents as resolved
- `incidents.close` - Close resolved incidents

### Service Request Management
- `service_requests.create` - Submit service requests
- `service_requests.read` - View service requests
- `service_requests.update` - Update requests
- `service_requests.delete` - Delete requests
- `service_requests.approve` - Approve pending requests
- `service_requests.fulfill` - Mark as fulfilled

### Problem Management
- `problems.create`, `problems.read`, `problems.update`, `problems.delete`
- `problems.resolve` - Mark as resolved

### Change Management
- `changes.create`, `changes.read`, `changes.update`, `changes.delete`
- `changes.approve` - Approve changes
- `changes.implement` - Implement approved changes

### Asset Management
- `assets.create`, `assets.read`, `assets.update`, `assets.delete`
- `assets.assign` - Assign assets to users/teams

### CMDB
- `cmdb.create`, `cmdb.read`, `cmdb.update`, `cmdb.delete`

### Knowledge Management
- `knowledge.create`, `knowledge.read`, `knowledge.update`, `knowledge.delete`
- `knowledge.publish` - Publish articles to knowledge base

### SLA Management
- `sla.create`, `sla.read`, `sla.update`, `sla.delete`

### Reports
- `reports.read` - View reports
- `reports.create` - Generate custom reports
- `reports.export` - Export report data

### User Management
- `users.create` - Create new users
- `users.read` - View user information
- `users.update` - Update user profiles
- `users.delete` - Delete users
- `users.reset_password` - Reset user passwords

### Administrative
- `admin.roles` - Manage roles and permissions
- `admin.settings` - Configure system settings
- `admin.audit_logs` - Access audit logs
- `admin.compliance` - Manage compliance

---

## API Endpoints for RBAC Management

### List All Roles
```bash
GET /api/v1/roles/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "count": 4,
  "results": [
    {
      "id": "uuid",
      "name": "administrator",
      "description": "Administrator - Full system access",
      "permissions": ["incidents.create", "incidents.read", ...],
      "is_system_role": true,
      "user_count": 1,
      "created_at": "2026-02-12T...",
      "updated_at": "2026-02-12T..."
    }
  ]
}
```

### Get Role Details
```bash
GET /api/v1/roles/{role_id}/
Authorization: Bearer {token}
```

### Create Custom Role (Admin Only)
```bash
POST /api/v1/roles/
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "name": "custom_role",
  "description": "Custom role description",
  "permissions": ["incidents.read", "incidents.create"]
}
```

### Update Role Permissions (Admin Only)
```bash
POST /api/v1/roles/{role_id}/update_permissions/
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "permissions": ["incidents.create", "incidents.read", "incidents.update"]
}
```

### Assign Role to User (Admin Only)
```bash
POST /api/v1/roles/{role_id}/assign_user/
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "user_id": "user-uuid"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user": "user-uuid",
    "user_name": "John Doe",
    "role": "role-uuid",
    "role_name": "manager",
    "assigned_at": "2026-02-12T...",
    "assigned_by": "admin-uuid"
  }
}
```

### Remove Role from User (Admin Only)
```bash
DELETE /api/v1/roles/{role_id}/unassign_user/
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "user_id": "user-uuid"
}
```

### List Available Permissions
```bash
GET /api/v1/roles/available_permissions/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "count": 53,
  "data": [
    "incidents.create",
    "incidents.read",
    "incidents.update",
    ...
  ]
}
```

---

## Usage Examples

### Assign Manager Role to User
```powershell
$body = @{ user_id = "user-id-123" } | ConvertTo-Json
Invoke-RestMethod -Method Post `
  -Uri "https://api.example.com/api/v1/roles/manager-role-id/assign_user/" `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body $body
```

### Create Custom Support Team Role
```powershell
$roleBody = @{
  name = "support_team"
  description = "Support Team Role"
  permissions = @(
    "incidents.create",
    "incidents.read",
    "incidents.update",
    "incidents.resolve",
    "knowledge.read",
    "cmdb.read"
  )
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "https://api.example.com/api/v1/roles/" `
  -Headers @{ Authorization = "Bearer $admin_token" } `
  -ContentType "application/json" `
  -Body $roleBody
```

### Update Role Permissions
```powershell
$permBody = @{
  permissions = @(
    "incidents.create",
    "incidents.read",
    "incidents.update",
    "service_requests.read"
  )
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "https://api.example.com/api/v1/roles/role-id/update_permissions/" `
  -Headers @{ Authorization = "Bearer $admin_token" } `
  -ContentType "application/json" `
  -Body $permBody
```

---

## Permission Checking in Code

### Using Decorators
```python
from apps.core.permissions import require_role, require_permission

@require_role('manager', 'admin')
@api_view(['POST'])
def resolve_incident(request):
    """Only managers and admins can resolve incidents"""
    ...

@require_permission('incidents.delete')
@api_view(['DELETE'])
def delete_incident(request):
    """Only users with delete permission can delete"""
    ...
```

### Using Permission Classes
```python
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import IsManager, HasRole

class IncidentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsManager]
    
    def destroy(self, request, *args, **kwargs):
        """Delete requires manager role"""
        ...
```

### Checking Permissions in Views
```python
from apps.users.models import UserRole

def can_delete_incident(user):
    """Check if user has incidents.delete permission"""
    if user.is_superuser:
        return True
    
    user_roles = UserRole.objects.filter(user=user).select_related('role')
    for user_role in user_roles:
        if 'incidents.delete' in user_role.role.permissions:
            return True
    
    return False
```

---

## Best Practices

### For Administrators
1. **Use System Roles** - Don't modify system roles; create custom roles if needed
2. **Regular Audits** - Review user role assignments regularly
3. **Least Privilege** - Assign minimum required permissions
4. **Team-Based Roles** - Create roles aligned with team structure
5. **Documentation** - Document custom roles and their purposes

### For Developers
1. **Check Permissions Early** - Validate permissions at view level
2. **Use Appropriate Classes** - Use `IsManager`, `IsAgent`, etc. for clarity
3. **Log Permission Denials** - Track denied access attempts
4. **Test with Different Roles** - Test features with various role levels
5. **Document Requirements** - Clearly state which roles can access each endpoint

### For Security
1. **Disable Default End User** - Remove default end_user role from admins
2. **Strong Passwords** - Enforce strong password policies
3. **MFA Enabled** - Require MFA for administrative accounts
4. **Audit Logs** - Monitor role assignment changes
5. **Role Separation** - Keep sensitive roles separate from general roles

---

## Testing RBAC

Run the RBAC test suite:
```powershell
.\backend\scripts\e2e_rbac_test.ps1
```

This tests:
- Role listing and details
- Available permissions
- Permission assignment
- RBAC enforcement

---

## Support and Documentation

- System roles are immutable (cannot be deleted)
- Users can have multiple roles
- Permissions are cumulative (user has all permissions from all assigned roles)
- Changes take effect immediately
- All role changes are logged in audit trail

For more information, see:
- `backend/apps/core/permissions.py` - Permission classes
- `backend/apps/users/views.py` - RBAC endpoints
- `backend/apps/users/models.py` - Data models
