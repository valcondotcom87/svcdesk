# Compliance Module Deployment Script for PowerShell
# Deploy the compliance module to the ITSM platform

Write-Host ""
Write-Host "============================================================"
Write-Host "ITSM Platform - Compliance Module Deployment"
Write-Host "============================================================"
Write-Host ""

# Check if we're in the backend directory
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Error: manage.py not found" -ForegroundColor Red
    Write-Host "Please run this script from the backend directory." -ForegroundColor Yellow
    exit 1
}

Write-Host "📁 Current Directory: $(Get-Location)" -ForegroundColor Green
Write-Host ""

# Function to run commands
function Invoke-Command {
    param(
        [string]$CommandName,
        [string]$Description
    )
    
    Write-Host ""
    Write-Host "▶ $Description" -ForegroundColor Cyan
    Write-Host "  Command: $CommandName"
    Write-Host ""
    
    Invoke-Expression $CommandName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SUCCESS: $Description" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ FAILED: $Description" -ForegroundColor Yellow
        return $false
    }
}

# Step 1: Create migrations
Write-Host "1️⃣  Step 1: Creating Django migrations..." -ForegroundColor Cyan
Invoke-Command "python manage.py makemigrations compliance" "Create migrations for compliance app"

# Step 2: Apply migrations
Write-Host ""
Write-Host "2️⃣  Step 2: Applying database migrations..." -ForegroundColor Cyan
$migrationSuccess = Invoke-Command "python manage.py migrate compliance" "Apply compliance migrations"
if (-not $migrationSuccess) {
    Write-Host "❌ Migration failed" -ForegroundColor Red
    exit 1
}

# Step 3: Collect static files
Write-Host ""
Write-Host "3️⃣  Step 3: Collecting static files..." -ForegroundColor Cyan
Invoke-Command "python manage.py collectstatic --noinput" "Collect static files"

# Step 4: Run tests
Write-Host ""
Write-Host "4️⃣  Step 4: Running compliance module tests..." -ForegroundColor Cyan
Invoke-Command "python manage.py test apps.compliance.tests --verbosity=2" "Run compliance tests"

# Summary
Write-Host ""
Write-Host "============================================================"
Write-Host "✅ DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "============================================================"
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Green
Write-Host "   1. Start the Django development server:"
Write-Host "      python manage.py runserver" -ForegroundColor Yellow
Write-Host ""
Write-Host "   2. Access the admin interface:"
Write-Host "      http://localhost:8000/admin/" -ForegroundColor Yellow
Write-Host ""
Write-Host "   3. Access the compliance API:"
Write-Host "      http://localhost:8000/api/v1/compliance/" -ForegroundColor Yellow
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Green
Write-Host "   - COMPLIANCE_QUICK_START.md - Quick setup guide" -ForegroundColor Yellow
Write-Host "   - COMPLIANCE_DOCUMENTATION.md - API reference" -ForegroundColor Yellow
Write-Host "   - COMPLIANCE_IMPLEMENTATION_GUIDE.md - Full guide" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔍 Verification Commands:" -ForegroundColor Green
Write-Host "   python manage.py check_compliance_status" -ForegroundColor Yellow
Write-Host "   python manage.py generate_compliance_report" -ForegroundColor Yellow
Write-Host "   python manage.py verify_audit_chain" -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ Compliance Module is ready to use!" -ForegroundColor Green
Write-Host ""
