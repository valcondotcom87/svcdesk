#!/bin/bash
# ITSM Application Setup & Startup Script
# This script sets up and starts the entire ITSM application

set -e

echo "=========================================="
echo "ITSM System - Phase 1 Setup & Startup"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Navigate to backend directory
cd backend

echo "📦 Step 1: Building Docker images..."
docker-compose build

echo ""
echo "🚀 Step 2: Starting services (PostgreSQL, Redis, Django)..."
docker-compose up -d

echo ""
echo "⏳ Step 3: Waiting for services to be ready..."
sleep 10

echo ""
echo "📊 Step 4: Running database migrations..."
docker-compose exec -T backend python manage.py migrate

echo ""
echo "🔧 Step 5: Initializing database with sample data..."
docker-compose exec -T backend python init_phase1.py

echo ""
echo "=========================================="
echo "✅ SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "📍 Application Access Points:"
echo "   Admin Interface: http://localhost:8000/admin/"
echo "   Username: admin"
echo "   Password: admin123456"
echo ""
echo "📚 API Documentation:"
echo "   Swagger UI: http://localhost:8000/api/schema/swagger-ui/"
echo "   ReDoc: http://localhost:8000/api/schema/redoc/"
echo ""
echo "📊 Database:"
echo "   PostgreSQL: localhost:5432"
echo "   User: postgres"
echo "   Password: postgres"
echo "   Database: itsm_db"
echo ""
echo "💾 Cache:"
echo "   Redis: localhost:6379"
echo ""
echo "🛠️  Useful Commands:"
echo "   - View logs: docker-compose logs -f backend"
echo "   - Stop services: docker-compose down"
echo "   - Access shell: docker-compose exec backend python manage.py shell"
echo "   - Run tests: docker-compose exec backend pytest"
echo ""
echo "📖 Documentation:"
echo "   - Phase 1 Complete: ./PHASE_1_COMPLETE.md"
echo "   - Database Schema: ../04-ADVANCED_DATABASE_SCHEMA.md"
echo "   - REST API: ../05-COMPLETE_REST_API.md"
echo "   - Quick Reference: ../09-QUICK_REFERENCE_GUIDE.md"
echo ""
echo "=========================================="
echo "🎉 Ready for Development!"
echo "=========================================="
