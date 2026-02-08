# ITSM Backend - Installation Guide

## Prerequisites

Pastikan Anda sudah menginstall:
- Python 3.11 atau lebih tinggi
- PostgreSQL 15 atau lebih tinggi
- Redis 7 atau lebih tinggi
- pip (Python package manager)

## Step 1: Setup Virtual Environment

```bash
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

## Step 2: Install Dependencies

```bash
# Install semua dependencies
pip install -r requirements.txt
```

## Step 3: Setup Database

```bash
# Login ke PostgreSQL
psql -U postgres

# Buat database
CREATE DATABASE itsm_db;

# Buat user (optional)
CREATE USER itsm_user WITH PASSWORD 'your_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE itsm_db TO itsm_user;

# Exit PostgreSQL
\q
```

## Step 4: Configure Environment Variables

```bash
# Copy file .env.example ke .env
cp .env.example .env

# Edit file .env dan sesuaikan dengan konfigurasi Anda
# Minimal yang harus diubah:
# - SECRET_KEY (generate dengan: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
# - DB_NAME, DB_USER, DB_PASSWORD
# - EMAIL_HOST_USER, EMAIL_HOST_PASSWORD (jika ingin menggunakan email)
```

## Step 5: Run Migrations

```bash
# Buat migrations
python manage.py makemigrations

# Jalankan migrations
python manage.py migrate
```

## Step 6: Create Superuser

```bash
# Buat superuser untuk akses admin
python manage.py createsuperuser

# Ikuti prompt untuk username, email, dan password
```

## Step 7: Load Initial Data

```bash
# Load data awal (roles, SLA policies, dll)
python manage.py loaddata initial_data.json
```

## Step 8: Collect Static Files

```bash
# Kumpulkan static files
python manage.py collectstatic --noinput
```

## Step 9: Run Development Server

```bash
# Jalankan server development
python manage.py runserver

# Server akan berjalan di http://localhost:8000
```

## Step 10: Setup Celery (Optional - untuk background tasks)

```bash
# Terminal 1: Jalankan Celery Worker
celery -A itsm_project worker -l info

# Terminal 2: Jalankan Celery Beat (untuk scheduled tasks)
celery -A itsm_project beat -l info
```

## Verification

### Test API
```bash
# Test health check
curl http://localhost:8000/api/v1/health/

# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"your-email@example.com","password":"your-password"}'
```

### Access Admin Panel
```
URL: http://localhost:8000/admin/
Login dengan superuser yang telah dibuat
```

### Access API Documentation
```
Swagger UI: http://localhost:8000/api/docs/
ReDoc: http://localhost:8000/api/redoc/
```

## Troubleshooting

### Error: "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### Error: "Connection refused" (PostgreSQL)
```bash
# Pastikan PostgreSQL service berjalan
# Windows:
net start postgresql-x64-15

# Linux:
sudo systemctl start postgresql

# Mac:
brew services start postgresql
```

### Error: "Connection refused" (Redis)
```bash
# Pastikan Redis service berjalan
# Windows: Download Redis for Windows atau gunakan WSL
# Linux:
sudo systemctl start redis

# Mac:
brew services start redis
```

### Error: "SECRET_KEY not found"
```bash
# Generate SECRET_KEY baru
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Copy output ke .env file
```

## Development Tools

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest apps/tickets/tests/test_models.py
```

### Code Formatting
```bash
# Format code with black
black .

# Sort imports
isort .

# Check code quality
flake8 .
pylint apps/
```

### Database Management
```bash
# Create new migration
python manage.py makemigrations app_name

# Show migrations
python manage.py showmigrations

# Rollback migration
python manage.py migrate app_name migration_name

# Reset database (DANGER!)
python manage.py flush
```

## Next Steps

1. Baca dokumentasi API di `/api/docs/`
2. Explore admin panel di `/admin/`
3. Mulai development dengan membuat tickets
4. Setup frontend (lihat `../frontend/INSTALLATION.md`)

## Support

Jika mengalami masalah, silakan:
1. Check logs di `logs/itsm.log`
2. Baca dokumentasi lengkap di root folder
3. Contact support team
