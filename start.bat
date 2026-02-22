@echo off
REM ITSM Application Setup & Startup Script (Windows)
REM This script sets up and starts the entire ITSM application

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo ITSM System - Phase 1 Setup - Windows
echo ==========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Compose is not installed
    echo Please install Docker Compose or use Docker Desktop which includes it
    pause
    exit /b 1
)

REM Navigate to backend directory
cd /d "%~dp0\backend"

echo.
echo Step 1: Building Docker images...
docker-compose build
if %errorlevel% neq 0 (
    echo ERROR: Failed to build Docker images
    pause
    exit /b 1
)

echo.
echo Step 2: Starting services (PostgreSQL, Redis, Django)...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start services
    pause
    exit /b 1
)

echo.
echo Step 3: Waiting for services to be ready...
timeout /t 10 /nobreak

echo.
echo Step 4: Running database migrations...
docker-compose exec -T backend python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: Migration failed
    pause
    exit /b 1
)

echo.
echo Step 5: Initializing database with sample data...
docker-compose exec -T backend python init_phase1.py
if %errorlevel% neq 0 (
    echo ERROR: Initialization failed
    pause
    exit /b 1
)

echo.
echo ==========================================
echo SUCCESS: SETUP COMPLETE!
echo ==========================================
echo.
echo Admin Interface: http://localhost:8000/admin/
echo Username: admin
echo Password: admin123456
echo.
echo API Documentation:
echo Swagger: http://localhost:8000/api/schema/swagger-ui/
echo ReDoc: http://localhost:8000/api/schema/redoc/
echo.
echo Database: postgres://postgres:postgres@localhost:5432/itsm_db
echo Cache: redis://localhost:6379
echo.
echo Useful Commands:
echo - View logs: docker-compose logs -f backend
echo - Stop services: docker-compose down
echo - Run tests: docker-compose exec backend pytest
echo.
echo Ready for Development!
echo ==========================================
echo.
pause
