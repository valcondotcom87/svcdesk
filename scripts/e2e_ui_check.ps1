$hostName = "svcdes.barokahdigital.cloud"
$body = @{ username = "admin@itsm.local"; password = "admin123456" } | ConvertTo-Json

[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
$token = $null
$loginError = $null
try {
  $loginResp = Invoke-RestMethod -Method Post -Uri "https://127.0.0.1/api/v1/auth/login/" `
    -Headers @{ Host = $hostName } -ContentType "application/json" -Body $body
  $token = $loginResp.access
} catch {
  $loginError = $_
}

if (-not $token) {
  Write-Host "Login failed"
  if ($loginError) {
    Write-Host $loginError.Exception.Message
  }
  $healthResp = curl.exe -k --resolve "$hostName:443:127.0.0.1" -s -o NUL -w "%{http_code}" "https://$hostName/health"
  Write-Host "Health status: $healthResp"
  exit 1
}

Write-Host "Login OK"
$headers = @{ Host = $hostName; Authorization = "Bearer $token" }
$endpoints = @(
  "/api/v1/incidents/incidents/",
  "/api/v1/service-requests/service-requests/",
  "/api/v1/assets/assets/",
  "/api/v1/knowledge/articles/",
  "/api/v1/sla/sla-metrics/"
)

foreach ($ep in $endpoints) {
  try {
    $obj = Invoke-RestMethod -Method Get -Uri "https://127.0.0.1$ep" -Headers $headers
    $count = if ($obj.count -ne $null) { $obj.count } else { ($obj | Measure-Object).Count }
    Write-Host "$ep -> $count"
  } catch {
    Write-Host "$ep -> error"
    Write-Host $_.Exception.Message
  }
}
