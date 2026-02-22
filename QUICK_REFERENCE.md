# ITSM Platform - Quick Reference Guide

## 🎯 What's Been Completed

### Infrastructure Deployment ✅
All 11 Docker Compose services are running and healthy:
- PostgreSQL database with migrations applied
- Redis cache and message broker
- Django/Gunicorn API backend
- Celery async task queue
- Celery Beat scheduler
- Elasticsearch for search/logging
- Kibana for log visualization
- Prometheus for metrics
- Grafana for dashboards
- Nginx reverse proxy

### Data Seeding ✅
Comprehensive demo data has been populated:
- **5 Sample Incidents** - Ready for testing incident workflows
- **3 Service Requests** - With different statuses for testing
- **3 Change Requests** - Standard, normal, and emergency types
- **4 Configuration Items** - Server configurations in CMDB
- **4 Services** - With categories and fulfillment workflows
- **Demo Users** - Admin, end-user, and engineer roles

### Documentation ✅
Complete deployment documentation:
- **PRODUCTION_DEPLOYMENT_GUIDE.md** - 160+ lines covering all aspects
- **README.md** - Project overview
- **IMPLEMENTATION_GUIDE.md** - Feature details
- API documentation available at `/api/v1/docs/`

## 🚀 Quick Start

### Access the System

**Web Interface**
```
URL: http://localhost
Admin Panel: http://localhost/admin/
```

**API**
```
Base URL: http://localhost/api/v1/
Health Check: http://localhost/api/v1/health/
API Docs: http://localhost/api/v1/docs/
```

**Monitoring**
```
Grafana: http://localhost:3000 (admin/admin)
Prometheus: http://localhost:9090
Kibana: http://localhost:5601
```

### Demo Login Credentials

Use these to explore the system:

```
Email:    admin@itsm.local
Password: admin123456
Role:     Administrator (full access)
```

```
Email:    enduser@itsm.local
Password: demo123456
Role:     End User (can request services)
```

```
Email:    engineer@itsm.local
Password: demo123456
Role:     IT Agent (can handle incidents)
```

## 📁 Key Files Reference

### Configuration Files
- `.env` - Current environment configuration
- `.env.example` - Template for development
- **`.env.production`** - Production configuration template (newly created)
- `docker-compose.yml` - Service definitions

### Data Seeding Scripts
- `create_admin_user.py` - Creates superuser
- `seed_demo_data.py` - Initial demo data (orgs, departments, SLAs)
- `seed_demo_users.py` - Demo user accounts
- **`seed_extended_demo_data.py`** - Extended demo data (incidents, requests, changes, CIs) ✨ NEW
- `seed_compliance_data.py` - Compliance framework data
- `seed_frameworks.py` - Compliance frameworks

### Verification Tools
- **`verify_demo_data.ps1`** - PowerShell script to verify API responses ✨ NEW

### Documentation
- `README.md` - Project overview
- `IMPLEMENTATION_GUIDE.md` - Implementation details
- **`PRODUCTION_DEPLOYMENT_GUIDE.md`** - Complete deployment guide ✨ NEW
- `INFRASTRUCTURE_READY.md` - Infrastructure status summary ✨ NEW

## 🔑 Key API Endpoints

### Authentication
```
POST   /api/v1/auth/login/
POST   /api/v1/auth/logout/
POST   /api/v1/auth/refresh/
```

### Incidents (5 seeded)
```
GET    /api/v1/incidents/incidents/
GET    /api/v1/incidents/incidents/{id}/
POST   /api/v1/incidents/incidents/
PATCH  /api/v1/incidents/incidents/{id}/
```

### Service Requests (3 seeded)
```
GET    /api/v1/service-requests/requests/
POST   /api/v1/service-requests/requests/
```

### Changes (3 seeded)
```
GET    /api/v1/changes/changes/
POST   /api/v1/changes/changes/
```

### Configuration Items (4 seeded)
```
GET    /api/v1/cmdb/items/
POST   /api/v1/cmdb/items/
```

### Organizations
```
GET    /api/v1/organizations/departments/
GET    /api/v1/organizations/department-members/
```

### SLA Management
```
GET    /api/v1/sla/slas/
GET    /api/v1/sla/targets/
```

## 🛠️ Common Tasks

### View Logs
```bash
# Backend API
docker compose logs -f backend

# PostgreSQL
docker compose logs postgres

# Celery
docker compose logs celery

# All services
docker compose logs -f
```

### Database Access
```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U itsm_user -d itsm_production

# Run Django shell
docker compose run --rm backend python manage.py shell

# Execute migrations
docker compose run --rm backend python manage.py migrate
```

### Reset Data
```bash
# Delete and reseed all demo data
docker compose down -v
docker compose up -d
docker compose run --rm backend python manage.py migrate --noinput
docker compose run --rm backend python create_admin_user.py
docker compose run --rm backend python seed_demo_data.py
docker compose run --rm backend python seed_demo_users.py
docker compose run --rm backend python seed_extended_demo_data.py
```

### Monitor Services
```bash
# View running containers
docker compose ps

# Check service health
docker compose exec backend curl http://localhost:8000/api/v1/health/

# View resource usage
docker compose stats

# Restart specific service
docker compose restart backend
```

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Nginx (Reverse Proxy)               │
│                   Port 80/443 (HTTP/HTTPS)              │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬──────────────┐
        │            │            │              │
┌───────▼─────┐ ┌────▼──────┐ ┌──▼──────────┐ ┌─▼────────┐
│  Backend    │ │ Celery   │ │ Celery Beat │ │Elastic  │
│  API        │ │ Worker   │ │ (Schedule) │ │Search   │
│ Django+     │ └────┬─────┘ └────┬────────┘ └─────────┘
│ Gunicorn    │      │            │
└───────┬─────┘      │            │
        ├────────────┼────────────┤
        │            │            │
    ┌───▼────┐  ┌───▼────┐  ┌───▼─────────┐
    │PostSQL │  │ Redis  │  │ Kibana/     │
    │Database│  │ Cache  │  │ Elasticsearch
    └────────┘  └────────┘  └─────────────┘

Monitoring:
  ├─ Prometheus (metrics collection)
  └─ Grafana (dashboards)
```

## 🔒 Security Credentials

**PostgreSQL**:
- User: `itsm_user`
- Database: `itsm_production`
- Password: Check `.env` file

**Redis**:
- No authentication required (local deployment)
- Production: Set password in `.env`

**Elasticsearch/Kibana**:
- Username: `elastic`
- Password: `elastic_password`
- Change in `.env` for production

**Django Admin**:
- Username: `admin@itsm.local`
- Password: See `.env` file

## 📈 Monitoring Dashboards

### Grafana
Access at: `http://localhost:3000`

Default Login:
- Username: `admin`
- Password: `admin`

**Available Dashboards**:
- API Performance metrics
- Database performance
- Celery task queue
- System resource usage

### Prometheus
Access at: `http://localhost:9090`

Query metrics like:
- `http_requests_total`
- `process_cpu_seconds_total`
- `process_resident_memory_bytes`

## 🚀 Production Deployment

Follow `PRODUCTION_DEPLOYMENT_GUIDE.md` for:
1. Pre-deployment checklist
2. DNS & SSL setup
3. Database configuration
4. Service startup
5. Monitoring setup
6. Backup configuration
7. Scaling strategies

**Key Steps**:
1. Copy `.env.production` to `.env`
2. Update credentials and domain
3. Configure SSL certificates
4. Run migrations
5. Deploy with `docker compose up -d`

## 📚 Documentation Index

| Document | Purpose | Location |
|----------|---------|----------|
| README.md | Project overview | Root |
| IMPLEMENTATION_GUIDE.md | Feature details | Root |
| PRODUCTION_DEPLOYMENT_GUIDE.md | Deployment walkthrough | backend/ |
| INFRASTRUCTURE_READY.md | Deployment status | backend/ |
| API Docs | Interactive API reference | `/api/v1/docs/` |

## 🆘 Troubleshooting

### Services Won't Start
```bash
# Check logs
docker compose logs backend

# Verify environment
docker compose config

# Check disk space
df -h
```

### Database Connection Failed
```bash
# Test PostgreSQL connection
docker compose exec postgres psql -U itsm_user -c "SELECT 1"

# Check database exists
docker compose exec postgres psql -U postgres -l
```

### Redis Connection Issues
```bash
# Test Redis connection
docker compose exec redis redis-cli PING

# Check Redis status
docker compose exec redis redis-cli INFO
```

### API Returns 500 Error
```bash
# View detailed error logs
docker compose logs -f backend --tail=50

# Check migrations
docker compose exec backend python manage.py showmigrations

# Run migrations if needed
docker compose exec backend python manage.py migrate --noinput
```

## 📞 Support Resources

- **GitHub Issues**: Report bugs and request features
- **Documentation**: `/api/v1/docs/` for API reference
- **Admin Panel**: `/admin/` for system configuration
- **Logs**: `docker compose logs` for troubleshooting

---

**System Status**: ✅ FULLY OPERATIONAL
**Last Updated**: 2024
**Version**: 1.0
