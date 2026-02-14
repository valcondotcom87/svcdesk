# E2E Functional Test for ITSM UI
# Tests login, navigation, and data loading on key pages

$hostName = "svcdes.barokahdigital.cloud"
$baseUrl = "https://127.0.0.1"
$body = @{ username = "admin@itsm.local"; password = "admin123456" } | ConvertTo-Json

[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ITSM E2E Functional Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Login
Write-Host "[1/7] Testing Login..." -ForegroundColor Yellow
$token = $null
try {
  $loginResp = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/v1/auth/login/" `
    -Headers @{ Host = $hostName } -ContentType "application/json" -Body $body
  $token = $loginResp.access
  Write-Host "[OK] Login successful" -ForegroundColor Green
} catch {
  Write-Host "[FAIL] Login failed: $($_.Exception.Message)" -ForegroundColor Red
  exit 1
}

$headers = @{ Host = $hostName; Authorization = "Bearer $token" }

# Test Dashboard (user profile)
Write-Host "[2/7] Testing Dashboard (User Profile)..." -ForegroundColor Yellow
try {
  $profile = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/v1/auth/me/" -Headers $headers
  if ($profile.id) {
    Write-Host "[OK] User profile loaded (ID: $($profile.id))" -ForegroundColor Green
  } else {
    Write-Host "[FAIL] User profile missing" -ForegroundColor Red
  }
} catch {
  Write-Host "[FAIL] Error loading profile: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Incidents
Write-Host "[3/7] Testing Incidents..." -ForegroundColor Yellow
try {
  $incidents = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/v1/incidents/incidents/" -Headers $headers
  if ($incidents.count -ne $null) {
    $count = $incidents.count
  } else {
    $count = ($incidents | Measure-Object).Count
  }
  Write-Host "[OK] Incidents loaded ($count records)" -ForegroundColor Green
  if ($count -gt 0) {
    $incidentId = ($incidents.results)[0].id
    $detail = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/v1/incidents/incidents/$incidentId/" -Headers $headers
    Write-Host "[OK] Incident detail loaded (ID: $incidentId, Title: $($detail.title))" -ForegroundColor Green
  }
} catch {
  Write-Host "[FAIL] Error loading incidents: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Service Requests
Write-Host "[4/7] Testing Service Requests..." -ForegroundColor Yellow
try {
  $srs = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/v1/service-requests/service-requests/" -Headers $headers
  if ($srs.count -ne $null) {
    $count = $srs.count
  } else {
    $count = ($srs | Measure-Object).Count
  }
  Write-Host "[OK] Service Requests loaded ($count records)" -ForegroundColor Green
  if ($count -gt 0) {
    $srId = ($srs.results)[0].id
    $detail = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/v1/service-requests/service-requests/$srId/" -Headers $headers
    Write-Host "[OK] Service Request detail loaded (ID: $srId)" -ForegroundColor Green
  }
} catch {
  Write-Host "[FAIL] Error loading service requests: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Assets
Write-Host "[5/7] Testing Assets..." -ForegroundColor Yellow
try {
  $assets = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/v1/assets/assets/" -Headers $headers
  if ($assets.count -ne $null) {
    $count = $assets.count
  } else {
    $count = ($assets | Measure-Object).Count
  }
  Write-Host "[OK] Assets loaded ($count records)" -ForegroundColor Green
  if ($count -gt 0) {
    $assetId = ($assets.results)[0].id
    $detail = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/v1/assets/assets/$assetId/" -Headers $headers
    Write-Host "[OK] Asset detail loaded (ID: $assetId, Name: $($detail.name))" -ForegroundColor Green
  }
} catch {
  Write-Host "[FAIL] Error loading assets: $($_.Exception.Message)" -ForegroundColor Red
}

# Test Knowledge Base
Write-Host "[6/7] Testing Knowledge Base..." -ForegroundColor Yellow
try {
  $kb = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/v1/knowledge/articles/" -Headers $headers
  if ($kb.count -ne $null) {
    $count = $kb.count
  } else {
    $count = ($kb | Measure-Object).Count
  }
  Write-Host "[OK] Knowledge Articles loaded ($count records)" -ForegroundColor Green
  if ($count -gt 0) {
    $kbId = ($kb.results)[0].id
    $detail = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/v1/knowledge/articles/$kbId/" -Headers $headers
    Write-Host "[OK] Knowledge Article detail loaded (ID: $kbId, Title: $($detail.title))" -ForegroundColor Green
  }
} catch {
  Write-Host "[FAIL] Error loading knowledge articles: $($_.Exception.Message)" -ForegroundColor Red
}

# Test CMDB
Write-Host "[7/7] Testing CMDB (Configuration Items)..." -ForegroundColor Yellow
try {
  $cmdb = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/v1/cmdb/config-items/" -Headers $headers
  if ($cmdb.count -ne $null) {
    $count = $cmdb.count
  } else {
    $count = ($cmdb | Measure-Object).Count
  }
  Write-Host "[OK] Configuration Items loaded ($count records)" -ForegroundColor Green
  if ($count -gt 0) {
    $ciId = ($cmdb.results)[0].id
    $detail = Invoke-RestMethod -Method Get -Uri "$baseUrl/api/v1/cmdb/config-items/$ciId/" -Headers $headers
    Write-Host "[OK] Configuration Item detail loaded (ID: $ciId, Name: $($detail.name))" -ForegroundColor Green
  }
} catch {
  Write-Host "[FAIL] Error loading configuration items: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[OK] All functional tests completed!" -ForegroundColor Green
Write-Host "========================================"  -ForegroundColor Cyan
