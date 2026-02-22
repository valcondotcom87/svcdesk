# ITSM System - Quick Start Guide

Panduan cepat untuk memulai development ITSM System.

---

## 🚀 Quick Setup (5 Menit)

### Prerequisites Check
```bash
# Check Python version (harus 3.11+)
python --version

# Check PostgreSQL (harus 15+)
psql --version

# Check Redis (harus 7+)
redis-cli --version

# Check pip
pip --version
```

### One-Command Setup (Windows)
```bash
# Jalankan dari root directory itsm-system
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
echo Setup complete! Edit .env file then run: python manage.py migrate
```

### One-Command Setup (Linux/Mac)
```bash
# Jalankan dari root directory itsm-system
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
echo "Setup complete! Edit .env file then run: python manage.py migrate"
```

---

## 📝 Step-by-Step Setup

### 1. Setup Database (2 menit)
```bash
# Login ke PostgreSQL
psql -U postgres

# Buat database
CREATE DATABASE itsm_db;

# Buat user (optional)
CREATE USER itsm_user WITH PASSWORD 'itsm_password';
GRANT ALL PRIVILEGES ON DATABASE itsm_db TO itsm_user;

# Exit
\q
```

### 2. Configure Environment (1 menit)
```bash
cd backend

# Copy .env file
cp .env.example .env

# Edit .env file - minimal yang harus diubah:
# DB_NAME=itsm_db
# DB_USER=itsm_user
# DB_PASSWORD=itsm_password
# SECRET_KEY=(generate dengan command di bawah)
```

Generate SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Install Dependencies (2 menit)
```bash
# Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 4. Initialize Database (1 menit)
```bash
# Create migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Username: admin
# Email: admin@itsm.com
# Password: (pilih password yang kuat)
```

### 5. Run Development Server (30 detik)
```bash
# Start server
python manage.py runserver

# Server akan berjalan di: http://localhost:8000
```

---

## ✅ Verification

### Test 1: Server Running
```bash
# Buka browser ke:
http://localhost:8000/admin/

# Login dengan superuser yang dibuat
```

### Test 2: API Health Check
```bash
# Test dengan curl:
curl http://localhost:8000/api/v1/health/

# Atau buka di browser:
http://localhost:8000/api/v1/health/
```

### Test 3: API Documentation
```bash
# Swagger UI:
http://localhost:8000/api/docs/

# ReDoc:
http://localhost:8000/api/redoc/
```

---

## 🔧 Development Workflow

### Daily Development
```bash
# 1. Aktifkan virtual environment
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Pull latest changes
git pull

# 3. Install new dependencies (jika ada)
pip install -r requirements.txt

# 4. Run migrations (jika ada)
python manage.py migrate

# 5. Start server
python manage.py runserver
```

### Create New App
```bash
# Template:
python manage.py startapp app_name apps/app_name

# Example:
python manage.py startapp tickets apps/tickets

# Jangan lupa tambahkan ke INSTALLED_APPS di settings.py
```

### Database Operations
```bash
# Create migrations
python manage.py makemigrations

# Show migrations
python manage.py showmigrations

# Run migrations
python manage.py migrate

# Rollback migration
python manage.py migrate app_name migration_name

# Reset database (DANGER!)
python manage.py flush
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test
pytest apps/tickets/tests/test_models.py

# Run with verbose output
pytest -v
```

### Code Quality
```bash
# Format code
black .

# Sort imports
isort .

# Check code quality
flake8 .
pylint apps/
```

---

## 🐛 Troubleshooting

### Error: "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### Error: "Connection refused" (PostgreSQL)
```bash
# Windows:
net start postgresql-x64-15

# Linux:
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Mac:
brew services start postgresql
```

### Error: "Connection refused" (Redis)
```bash
# Windows: Install Redis via WSL or download Windows version

# Linux:
sudo systemctl start redis
sudo systemctl enable redis

# Mac:
brew services start redis
```

### Error: "SECRET_KEY not found"
```bash
# Generate new SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Copy output ke .env file
```

### Error: "Port 8000 already in use"
```bash
# Run on different port
python manage.py runserver 8001

# Or kill process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

---

## 📚 Useful Commands

### Django Management
```bash
# Create superuser
python manage.py createsuperuser

# Change password
python manage.py changepassword username

# Shell
python manage.py shell

# Database shell
python manage.py dbshell

# Collect static files
python manage.py collectstatic

# Check for issues
python manage.py check
```

### Celery (Background Tasks)
```bash
# Terminal 1: Start Celery Worker
celery -A itsm_project worker -l info

# Terminal 2: Start Celery Beat (Scheduler)
celery -A itsm_project beat -l info

# Terminal 3: Monitor Celery
celery -A itsm_project flower
# Access at: http://localhost:5555
```

### Database Backup & Restore
```bash
# Backup
pg_dump -U postgres itsm_db > backup.sql

# Restore
psql -U postgres itsm_db < backup.sql
```

---

## 🎯 Next Steps

1. ✅ Setup complete
2. 📖 Read documentation in root folder
3. 💻 Start implementing apps (see IMPLEMENTATION_STATUS.md)
4. 🧪 Write tests
5. 🚀 Deploy to production

---

## 📞 Need Help?

- 📖 Documentation: Check root folder for detailed docs
- 🐛 Issues: Check IMPLEMENTATION_STATUS.md
- 💬 Support: Contact development team

---

**Happy Coding! 🎉**
