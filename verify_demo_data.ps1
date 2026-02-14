# Get auth token
$resp = Invoke-RestMethod -Method Post -Uri http://localhost/api/v1/auth/login/ -ContentType 'application/json' -Body '{"username":"admin@itsm.local","password":"admin123456"}' -ErrorAction SilentlyContinue

if ($resp) {
    $token = $resp.access
    Write-Host "[OK] Authentication successful"
    
    # Get incidents
    $incidents = Invoke-RestMethod -Method Get -Uri 'http://localhost/api/v1/incidents/incidents/?limit=100' -Headers @{Authorization = "Bearer $token"} -ErrorAction SilentlyContinue
    $incCount = $incidents.count
    Write-Host "[OK] Incidents: $incCount"
    
    # Get service requests
    $requests = Invoke-RestMethod -Method Get -Uri 'http://localhost/api/v1/service-requests/requests/?limit=100' -Headers @{Authorization = "Bearer $token"} -ErrorAction SilentlyContinue
    $reqCount = $requests.count
    Write-Host "[OK] Service Requests: $reqCount"
    
    # Get changes
    $changes = Invoke-RestMethod -Method Get -Uri 'http://localhost/api/v1/changes/changes/?limit=100' -Headers @{Authorization = "Bearer $token"} -ErrorAction SilentlyContinue
    $chgCount = $changes.count
    Write-Host "[OK] Changes: $chgCount"
    
    # Get configuration items
    $cis = Invoke-RestMethod -Method Get -Uri 'http://localhost/api/v1/cmdb/items/?limit=100' -Headers @{Authorization = "Bearer $token"} -ErrorAction SilentlyContinue
    $ciCount = $cis.count
    Write-Host "[OK] Configuration Items: $ciCount"
    
    Write-Host ""
    Write-Host "=== Extended Demo Data Summary ==="
    Write-Host "Incidents: $incCount"
    Write-Host "Service Requests: $reqCount"
    Write-Host "Changes: $chgCount"
    Write-Host "Configuration Items: $ciCount"
} else {
    Write-Host "[ERROR] Authentication failed"
}
