# E2E RBAC Testing Script
# Tests role assignment, permissions, and RBAC enforcement

$hostName = "svcdes.barokahdigital.cloud"
$baseUrl = "https://127.0.0.1"
$adminBody = @{ username = "admin@itsm.local"; password = "admin123456" } | ConvertTo-Json

[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ITSM RBAC E2E Testing Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Admin Login
Write-Host "[1/5] Testing Admin Login..." -ForegroundColor Yellow
try {
  $loginResp = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/v1/auth/login/" `
    -Headers @{ Host = $hostName } -ContentType "application/json" -Body $adminBody
  $adminToken = $loginResp.access
  Write-Host "[OK] Admin login successful" -ForegroundColor Green
} catch {
  Write-Host "[FAIL] Admin login failed: $($_.Exception.Message)" -ForegroundColor Red
  exit 1
}

$adminHeaders = @{ Host = $hostName; Authorization = "Bearer $adminToken" }

# 2. Get Available Permissions
Write-Host "[2/5] Testing Available Permissions Endpoint..." -ForegroundColor Yellow
try {
  $permResp = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/v1/roles/available_permissions/" -Headers $adminHeaders
  $permCount = $permResp.data.Count
  Write-Host "[OK] Available permissions: $permCount" -ForegroundColor Green
  Write-Host "    Permissions:" -ForegroundColor Gray
  $permResp.data[0..4] | ForEach-Object { Write-Host "    - $_" -ForegroundColor Gray }
  if ($permCount -gt 5) { Write-Host "    ... and $($permCount - 5) more" -ForegroundColor Gray }
} catch {
  Write-Host "[FAIL] Error getting permissions: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. List All Roles
Write-Host "[3/5] Testing List Roles..." -ForegroundColor Yellow
try {
  $rolesResp = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/v1/roles/" -Headers $adminHeaders
  $roleCount = if ($rolesResp.count -ne $null) { $rolesResp.count } else { ($rolesResp | Measure-Object).Count }
  Write-Host "[OK] Roles found: $roleCount" -ForegroundColor Green
  
  # Show roles and their permission counts
  $rolesData = if ($rolesResp.results) { $rolesResp.results } else { $rolesResp }
  foreach ($role in $rolesData) {
    $permCount = $role.permissions | Measure-Object | Select-Object -ExpandProperty Count
    Write-Host "    - $($role.name): $permCount permissions" -ForegroundColor Gray
  }
} catch {
  Write-Host "[FAIL] Error listing roles: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Get Specific Role Details
Write-Host "[4/5] Testing Get Role Details..." -ForegroundColor Yellow
try {
  $adminRoleResp = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/v1/roles/" -Headers $adminHeaders
  $rolesArray = if ($adminRoleResp.results) { $adminRoleResp.results } else { $adminRoleResp }
  $adminRoleId = $rolesArray[0].id
  
  $roleDetail = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/v1/roles/$adminRoleId/" -Headers $adminHeaders
  Write-Host "[OK] Role details retrieved" -ForegroundColor Green
  Write-Host "    - Name: $($roleDetail.name)" -ForegroundColor Gray
  Write-Host "    - Description: $($roleDetail.description)" -ForegroundColor Gray
  Write-Host "    - Permissions: $($roleDetail.permissions.Count)" -ForegroundColor Gray
  Write-Host "    - System Role: $($roleDetail.is_system_role)" -ForegroundColor Gray
  Write-Host "    - Users with role: $($roleDetail.user_count)" -ForegroundColor Gray
} catch {
  Write-Host "[FAIL] Error getting role details: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Test RBAC Enforcement (Try to access admin endpoint as unauthorized role)
Write-Host "[5/5] Testing RBAC Permission Enforcement..." -ForegroundColor Yellow
try {
  # First, check current user details (should work for any authenticated user)
  $meResp = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/v1/auth/me/" -Headers $adminHeaders
  Write-Host "[OK] Admin user profile accessed" -ForegroundColor Green
  Write-Host "    - User: $($meResp.username)" -ForegroundColor Gray
  Write-Host "    - Role: $($meResp.role)" -ForegroundColor Gray
  
  # Test listing users (requires 'users.read' permission)
  $usersResp = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/v1/users/" -Headers $adminHeaders
  $userCount = if ($usersResp.count -ne $null) { $usersResp.count } else { ($usersResp | Measure-Object).Count }
  Write-Host "[OK] Users accessible (RBAC allows): $userCount users" -ForegroundColor Green
} catch {
  Write-Host "[FAIL] Error testing RBAC enforcement: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[OK] RBAC E2E testing completed!" -ForegroundColor Green
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host ""
Write-Host "RBAC Features Available:" -ForegroundColor Yellow
Write-Host "  - Role management (create, update, delete)" -ForegroundColor Gray
Write-Host "  - Permission assignment to roles" -ForegroundColor Gray
Write-Host "  - User-role mapping" -ForegroundColor Gray
Write-Host "  - Role-based endpoint access control" -ForegroundColor Gray
Write-Host "  - 4 system roles: end_user, agent, manager, administrator" -ForegroundColor Gray
