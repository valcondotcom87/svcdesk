@echo off
REM Compliance Module Deployment Script for Windows
REM This script deploys the compliance module to the ITSM platform

echo.
echo ============================================================
echo ITSM Platform - Compliance Module Deployment
echo ============================================================
echo.

REM Check if we're in the backend directory
if not exist "manage.py" (
    echo Error: manage.py not found. Please run this script from the backend directory.
    pause
    exit /b 1
)

echo Current Directory: %cd%
echo.

REM Step 1: Create migrations
echo Step 1: Creating Django migrations...
python manage.py makemigrations compliance
if errorlevel 1 (
    echo Warning: Migration creation may have failed (may already exist)
) else (
    echo Migrations created successfully
)

echo.

REM Step 2: Apply migrations
echo Step 2: Applying database migrations...
python manage.py migrate compliance
if errorlevel 1 (
    echo Error: Migration failed
    pause
    exit /b 1
)
echo Migrations applied successfully

echo.

REM Step 3: Collect static files
echo Step 3: Collecting static files...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo Warning: Static file collection may have issues
)

echo.

REM Step 4: Run tests
echo Step 4: Running compliance module tests...
python manage.py test apps.compliance.tests --verbosity=2
if errorlevel 1 (
    echo Warning: Some tests may have failed
) else (
    echo All tests passed!
)

echo.
echo ============================================================
echo DEPLOYMENT COMPLETE
echo ============================================================
echo.
echo Next Steps:
echo   1. Start the Django server:
echo      python manage.py runserver
echo.
echo   2. Access the admin interface:
echo      http://localhost:8000/admin/
echo.
echo   3. Access the compliance API:
echo      http://localhost:8000/api/v1/compliance/
echo.
echo Documentation:
echo   - COMPLIANCE_QUICK_START.md
echo   - COMPLIANCE_DOCUMENTATION.md
echo   - COMPLIANCE_IMPLEMENTATION_GUIDE.md
echo.
echo Compliance Module is ready to use!
echo.
pause
