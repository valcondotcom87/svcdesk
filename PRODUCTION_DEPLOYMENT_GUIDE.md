# ITSM Platform - Production Deployment Guide

## Overview

This guide covers deploying the ITSM platform to a production environment using Docker Compose and containerized services.

## Architecture

The production stack includes:

- **PostgreSQL 15**: Primary relational database
- **Redis 7**: Cache, message broker, session store
- **Elasticsearch 8**: Full-text search and analytics
- **Kibana**: Log visualization and monitoring
- **Nginx**: Reverse proxy and load balancer
- **Django/Gunicorn**: API backend (4 workers)
- **Celery**: Asynchronous task queue
- **Celery Beat**: Scheduled task manager
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization

## Pre-Deployment Checklist

### 1. System Requirements

```
CPU: 4+ cores
RAM: 8+ GB
Storage: 100+ GB (adjust for data retention policies)
Network: Outbound HTTPS access for external integrations
OS: Linux (Ubuntu 20.04+ recommended) or Windows with Docker Desktop
```

### 2. Dependencies

- Docker Engine 20.10+
- Docker Compose 1.29+
- Git for version control
- SSL/TLS certificates (Let's Encrypt recommended)

### 3. DNS & Domain Setup

1. Point your domain to your server's IP address
2. Configure DNS A record: `itsm.yourdomain.com → server-ip`
3. (Optional) Add CNAME for www: `www.itsm.yourdomain.com → itsm.yourdomain.com`

### 4. SSL/TLS Certificate Preparation

```bash
# Using Let's Encrypt with Certbot
sudo apt-get install certbot
sudo certbot certonly --standalone -d itsm.yourdomain.com -d www.itsm.yourdomain.com

# Certificates will be at:
# /etc/letsencrypt/live/itsm.yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/itsm.yourdomain.com/privkey.pem
```

## Step 1: Environment Setup

### 1.1 Clone Repository

```bash
git clone <repository-url> /opt/itsm-platform
cd /opt/itsm-platform/backend
```

### 1.2 Prepare Environment File

```bash
# Copy production template
cp .env.production .env

# Edit with production secrets
nano .env  # or use your preferred editor
```

### 1.3 Update Critical Settings in `.env`

```bash
# Generate secure Django SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Then update:
SECRET_KEY=<generated-key>
ALLOWED_HOSTS=itsm.yourdomain.com,www.itsm.yourdomain.com,nginx
DATABASE_URL=postgresql://itsm_user:strong_password_here@postgres:5432/itsm_production
REDIS_URL=redis://:redis_password@redis:6379/0
```

### 1.4 Configure Nginx SSL

Copy SSL certificates to nginx volume:

```bash
mkdir -p ./nginx/certs
sudo cp /etc/letsencrypt/live/itsm.yourdomain.com/fullchain.pem ./nginx/certs/
sudo cp /etc/letsencrypt/live/itsm.yourdomain.com/privkey.pem ./nginx/certs/
sudo chown -R 1000:1000 ./nginx/certs
```

Update [nginx/nginx.conf](nginx/nginx.conf) to include SSL configuration:

```nginx
server {
    listen 443 ssl default_server;
    listen [::]:443 ssl default_server;
    
    server_name itsm.yourdomain.com www.itsm.yourdomain.com;
    
    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    
    # SSL configuration...
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name _;
    return 301 https://$host$request_uri;
}
```

## Step 2: Initialize Database

### 2.1 Create Database User (PostgreSQL)

```bash
# Connect to postgres container or external database
psql -U postgres -h postgres-server

# Execute:
CREATE USER itsm_user WITH PASSWORD 'strong_password_here';
CREATE DATABASE itsm_production OWNER itsm_user;
GRANT ALL PRIVILEGES ON DATABASE itsm_production TO itsm_user;
```

### 2.2 Run Migrations

```bash
docker compose run --rm backend python manage.py migrate --noinput
```

### 2.3 Create Superuser

```bash
docker compose run --rm backend python manage.py createsuperuser
# Follow prompts to create admin user
```

### 2.4 Load Initial Data (Optional)

```bash
# Create default organization
docker compose run --rm backend python seed_demo_data.py

# Create demo users (optional)
docker compose run --rm backend python seed_demo_users.py
```

## Step 3: Start Services

### 3.1 Start Docker Compose Stack

```bash
cd /opt/itsm-platform/backend

# Start all services in background
docker compose up -d

# Verify services are running
docker compose ps

# Expected output: All services should show "running" or "healthy" status
```

### 3.2 Verify Service Health

```bash
# Check backend health
curl https://itsm.yourdomain.com/api/v1/health/

# Check Postgres
docker compose exec postgres pg_isready -U itsm_user -d itsm_production

# Check Redis
docker compose exec redis redis-cli PING

# Check Elasticsearch
curl -u elastic:elastic_password https://elasticsearch:9200/_cluster/health

# View logs
docker compose logs -f backend  # Follow backend logs
docker compose logs postgres    # View postgres logs
```

## Step 4: Post-Deployment Configuration

### 4.1 Collect Static Files

```bash
docker compose run --rm backend python manage.py collectstatic --noinput
```

### 4.2 Configure Email (SendGrid)

```bash
# Update .env with SendGrid credentials:
EMAIL_HOST_PASSWORD=SG.your-sendgrid-api-key

# Test email sending:
docker compose run --rm backend python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'noreply@itsm.yourdomain.com', ['admin@yourdomain.com'])
```

### 4.3 Setup Monitoring & Alerts

**Prometheus** (metrics collection):
- Access at: `https://itsm.yourdomain.com/prometheus`
- Configure scrape: `prometheus.yml`

**Grafana** (dashboard visualization):
- Access at: `https://itsm.yourdomain.com:3000`
- Default credentials: admin/admin
- Create dashboards from Prometheus data source

**Sentry** (error tracking):
- Sign up at sentry.io
- Update `SENTRY_DSN` in .env
- Errors will be automatically reported

### 4.4 Configure Backup Strategy

```bash
# Create backup script (backup.sh)
#!/bin/bash
BACKUP_DIR="/backups/itsm-$(date +%Y%m%d-%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup database
docker compose exec -T postgres pg_dump -U itsm_user itsm_production > $BACKUP_DIR/database.sql

# Backup user uploads
docker compose exec -T backend tar czf - media/ > $BACKUP_DIR/media.tar.gz

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/ s3://itsm-backups-production/ --recursive

# Keep only last 30 days
find /backups -mtime +30 -exec rm -rf {} \;
```

Schedule in crontab:

```bash
# Daily backup at 2 AM
0 2 * * * /opt/itsm-platform/backend/scripts/backup.sh
```

## Step 5: Update & Maintenance

### 5.1 Apply Updates

```bash
# Pull latest code
git pull origin main

# Apply migrations
docker compose run --rm backend python manage.py migrate

# Restart services
docker compose restart
```

### 5.2 Database Maintenance

```bash
# Optimize PostgreSQL
docker compose exec -T postgres VACUUM FULL ANALYZE;

# Check database size
docker compose exec postgres psql -U itsm_user -d itsm_production -c "SELECT pg_size_pretty(pg_database_size('itsm_production'));"
```

### 5.3 Log Rotation

```bash
# Configure Docker log rotation in /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}

# Restart Docker
sudo systemctl restart docker
```

## Step 6: SSL Certificate Renewal

```bash
# Configure auto-renewal with Certbot
sudo certbot renew --quiet --pre-hook "cd /opt/itsm-platform/backend && docker compose down" --post-hook "cd /opt/itsm-platform/backend && docker compose up -d"

# Add to crontab for automatic renewal (runs monthly)
0 0 1 * * /usr/bin/certbot renew --quiet
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker compose logs backend
docker compose logs postgres

# Verify environment variables
docker compose config

# Check disk space
df -h
```

### Database Connection Errors

```bash
# Test database connection
docker compose exec backend python manage.py dbshell

# Check PostgreSQL logs
docker compose logs postgres
```

### High Memory Usage

```bash
# Check resource usage
docker compose stats

# Monitor Redis memory
docker compose exec redis redis-cli INFO memory

# Monitor Elasticsearch memory
curl -s -u elastic:elastic_password http://elasticsearch:9200/_nodes/stats/jvm | jq '.nodes[].jvm.mem'
```

### Celery Tasks Not Running

```bash
# Check Celery worker
docker compose logs celery

# Restart worker
docker compose restart celery

# Check Redis connection
docker compose exec redis redis-cli PING

# Verify task queue
docker compose exec redis redis-cli LLEN celery
```

## Performance Tuning

### Database

```bash
# Increase connection pool in .env
DB_POOL_SIZE=30

# Adjust shared_buffers in postgres
postgresql.conf: shared_buffers = 256MB (25% of total RAM)
```

### Redis

```bash
# Increase maxmemory
docker compose exec redis redis-cli CONFIG SET maxmemory 2gb
docker compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Nginx

```bash
# Increase worker connections in nginx.conf
worker_processes auto;
worker_connections 2048;
```

### Django/Gunicorn

```bash
# Increase workers in docker-compose.yml
--workers 8  # Adjust based on CPU cores (rule: 2*cores + 1)
--worker-class gthread  # For threading
--threads 4  # Threads per worker
```

## Security Best Practices

- [ ] Generate strong random `SECRET_KEY`
- [ ] Use strong database & Redis passwords
- [ ] Enable SSL/TLS (SECURE_SSL_REDIRECT=True)
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Set up firewall rules (only expose ports 80/443)
- [ ] Regularly update Docker images and dependencies
- [ ] Enable audit logging (AUDIT_LOG_ENABLED=True)
- [ ] Configure proper file permissions (chmod 600 on .env)
- [ ] Use environment secrets management (Vault/Secrets Manager)
- [ ] Enable 2FA for admin accounts
- [ ] Regular security audits and pen testing

## Scaling Recommendations

### Horizontal Scaling

For high-traffic environments:

1. **Database**: Use managed PostgreSQL (AWS RDS, Azure Database, etc.)
2. **Cache**: Use managed Redis (AWS ElastiCache, Azure Cache, etc.)
3. **Load Balancing**: Deploy multiple backend instances behind load balancer
4. **Search**: Use managed Elasticsearch (Elastic Cloud, AWS OpenSearch, etc.)

### Example: Docker Swarm

```bash
docker swarm init
docker stack deploy -c docker-compose.yml itsm
```

### Example: Kubernetes

```bash
# Generate K8s manifests from docker-compose
kompose convert -f docker-compose.yml

# Deploy to cluster
kubectl apply -f .
```

## Support & Documentation

- API Documentation: `/api/v1/docs/`
- Admin Panel: `/admin/`
- Prometheus: `/prometheus`
- Grafana: `:3000`

For issues and support, refer to the main [README.md](../README.md) and [IMPLEMENTATION_GUIDE.md](../IMPLEMENTATION_GUIDE.md).

---

Last Updated: 2024
Version: 1.0
