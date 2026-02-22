# ITSM Platform - Production Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Docker Compose Deployment](#docker-compose-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [CI/CD Pipeline Setup](#cicd-pipeline-setup)
5. [Monitoring & Observability](#monitoring--observability)
6. [Security Hardening](#security-hardening)
7. [Performance Tuning](#performance-tuning)
8. [Troubleshooting](#troubleshooting)
9. [Operations Manual](#operations-manual)

---

## Prerequisites

### Required Software
- Docker 20.10+ and Docker Compose 2.0+
- Kubernetes 1.24+ (for K8s deployment)
- kubectl 1.24+ (for K8s operations)
- Git 2.30+
- Python 3.11+ (for local development)

### Required Accounts & Access
- Docker Registry access (ghcr.io)
- Kubernetes cluster access (kubeconfig)
- Git repository access
- Cloud provider access (if deploying to cloud)

### System Requirements
- **Minimum**: 4 CPU cores, 8GB RAM, 50GB storage
- **Recommended**: 8+ CPU cores, 16GB+ RAM, 100GB+ SSD storage

---

## Docker Compose Deployment

### Quick Start

```bash
cd backend

# Copy and configure environment file
cp .env.example .env
# Edit .env with your settings

# Build and start services
docker-compose up -d

# Wait for services to be healthy
docker-compose ps

# Check logs
docker-compose logs -f backend
```

### Service Health Check

```bash
# Check if all services are healthy
docker-compose ps

# Expected output:
# backend         running (healthy)
# postgres        running (healthy)
# redis          running (healthy)
# celery         running
# celery-beat    running
# nginx          running (healthy)
# prometheus     running
# grafana        running
```

### Initial Setup

```bash
# Create database and apply migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput

# Create cache tables
docker-compose exec backend python manage.py createcachetable

# Test API
curl http://localhost/health/
```

### Accessing Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Django Admin | http://localhost/admin/ | Superuser credentials |
| API Documentation | http://localhost/api/schema/ | Public |
| Prometheus | http://localhost:9090 | Public |
| Grafana | http://localhost:3000 | admin / password from .env |

### Backup & Restore

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres itsm_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres itsm_db < backup.sql

# Backup Redis
docker-compose exec redis redis-cli --rdb /tmp/dump.rdb
docker cp $(docker-compose ps -q redis):/tmp/dump.rdb ./backup-redis.rdb

# Backup volumes
docker run --rm -v backend_postgres_data:/data -v $(pwd):/backup \
  busybox tar czf /backup/postgres_backup.tar.gz /data
```

### Scaling Services

```bash
# Scale Celery workers
docker-compose up -d --scale celery=3

# Scale API instances (requires load balancer in nginx.conf)
# Edit nginx-default.conf to add multiple backend servers
# Then restart nginx
docker-compose restart nginx
```

---

## Kubernetes Deployment

### Prerequisites

```bash
# 1. Install required tools
kubectl version --client
helm version

# 2. Configure kubeconfig
export KUBECONFIG=~/.kube/config

# 3. Create namespace
kubectl create namespace itsm-system

# 4. Create Docker registry secret
kubectl create secret docker-registry regcred \
  --docker-server=ghcr.io \
  --docker-username=your-github-username \
  --docker-password=your-github-token \
  --docker-email=your-email@example.com \
  -n itsm-system
```

### Deploy to Kubernetes

```bash
cd k8s

# Apply manifests in order
kubectl apply -f 00-namespace-config.yaml
kubectl apply -f 01-storage-and-databases.yaml
kubectl apply -f 02-api-deployment.yaml
kubectl apply -f 03-scaling-security-rbac.yaml
kubectl apply -f 04-ingress-monitoring.yaml

# Wait for all pods to be running
kubectl wait --for=condition=Ready pod -l app=itsm-api -n itsm-system --timeout=5m

# Check deployment status
kubectl rollout status deployment/itsm-api -n itsm-system
```

### Verify Deployment

```bash
# Check pods
kubectl get pods -n itsm-system

# Check services
kubectl get svc -n itsm-system

# Check ingress
kubectl get ingress -n itsm-system

# View logs
kubectl logs deployment/itsm-api -n itsm-system -f

# Access dashboard
kubectl port-forward svc/grafana 3000:3000 -n itsm-system
# Visit http://localhost:3000

# Access Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n itsm-system
# Visit http://localhost:9090
```

### Update Deployment

```bash
# Update image
kubectl set image deployment/itsm-api \
  django=ghcr.io/your-org/itsm-api:v2.1.0 \
  -n itsm-system

# Rollout new version
kubectl rollout status deployment/itsm-api -n itsm-system

# Rollback if needed
kubectl rollout undo deployment/itsm-api -n itsm-system
```

### Scale Deployment

```bash
# Manual scaling
kubectl scale deployment itsm-api --replicas=5 -n itsm-system

# Auto-scaling (already configured via HPA)
kubectl get hpa -n itsm-system
kubectl describe hpa itsm-api-hpa -n itsm-system
```

---

## CI/CD Pipeline Setup

### GitHub Actions

```bash
# Prerequisites
# 1. Push code to GitHub repository
git remote add origin https://github.com/your-org/itsm-api.git
git push -u origin main

# 2. Configure repository secrets
# In GitHub: Settings → Secrets and variables → Actions
# Add secrets:
# - GITHUB_TOKEN (automatic)
# - SONAR_TOKEN (from SonarCloud)

# 3. Configure environments
# Settings → Environments → Create "staging" and "production"
# Add deployment secrets for each environment

# The workflow will trigger on:
# - Push to main (build + deploy to production)
# - Push to develop (test + deploy to staging)
# - Pull requests (test + code quality checks)
```

### GitLab CI

```bash
# 1. Push code to GitLab
git remote add origin https://gitlab.com/your-org/itsm-api.git
git push -u origin main

# 2. Configure CI/CD variables
# In GitLab: Settings → CI/CD → Variables
# Add variables:
# - KUBE_CONFIG (base64 encoded kubeconfig)
# - REGISTRY_USER
# - REGISTRY_PASSWORD

# 3. Configure protected branches
# Settings → Protected branches
# Set main and develop as protected

# Pipeline runs automatically on push/merge
```

### Jenkins

```bash
# 1. Install Jenkins and required plugins
# Plugins needed:
# - Pipeline
# - Docker Pipeline
# - Kubernetes
# - SonarQube Scanner
# - Email Extension

# 2. Create Jenkins credentials
# Credentials → System → Global credentials
# Add credentials:
# - Docker registry credentials
# - Kubernetes kubeconfig
# - SSH deploy keys
# - SonarQube token

# 3. Create Jenkins pipeline job
# New Item → Pipeline
# Configure → Pipeline → Definition: Pipeline script from SCM
# SCM: Git
# Repository URL: https://github.com/your-org/itsm-api.git
# Branch: */main

# 4. Configure webhooks
# GitHub Settings → Webhooks
# Payload URL: https://jenkins.example.com/github-webhook/
```

---

## Monitoring & Observability

### Prometheus Metrics

```bash
# Access Prometheus
http://localhost:9090  # Docker Compose
kubectl port-forward svc/prometheus 9090:9090 -n itsm-system  # Kubernetes

# Useful queries:
# API response time (95th percentile)
histogram_quantile(0.95, django_http_request_duration_seconds)

# Error rate
rate(django_http_requests_total{status=~"5.."}[5m])

# Database connections
pg_stat_activity_count

# Redis memory usage
redis_memory_used_bytes / redis_memory_max_bytes

# CPU usage per pod
sum(rate(container_cpu_usage_seconds_total[5m])) by (pod)
```

### Grafana Dashboards

```bash
# Access Grafana
http://localhost:3000  # Docker Compose
kubectl port-forward svc/grafana 3000:3000 -n itsm-system  # Kubernetes

# Login: admin / password from .env

# Import dashboards:
# 1. Create > Import > Paste JSON
# 2. Select Prometheus data source
# 3. Save

# Recommended dashboards:
# - Django Application Metrics (search: django)
# - PostgreSQL Database (search: postgres)
# - Redis (search: redis)
# - Kubernetes Cluster (search: kubernetes)
```

### Alert Configuration

```bash
# Alertmanager configuration (create alertmanager.yml)
global:
  resolve_timeout: 5m

route:
  receiver: 'default'
  group_by: ['alertname', 'cluster']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 4h
  
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: warning
      receiver: 'slack'

receivers:
  - name: 'default'
    email_configs:
      - to: 'devops@example.com'
        from: 'alerts@example.com'
        smarthost: 'smtp.example.com:587'
        auth_username: 'alerts@example.com'
        auth_password: 'password'

  - name: 'slack'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
```

---

## Security Hardening

### Network Security

```bash
# 1. Enable TLS/SSL
# Update docker-compose.yml or K8s ingress to use HTTPS

# 2. Configure firewall rules
# Allow only necessary ports:
# - 80 (HTTP) → Redirect to HTTPS
# - 443 (HTTPS) → API
# - 9090 (Prometheus) → Internal only
# - 3000 (Grafana) → Internal only

# 3. Setup network policies (K8s)
# Already configured in 03-scaling-security-rbac.yaml

# 4. Use VPN for admin access
# Restrict access to admin panel to VPN only
```

### Database Security

```bash
# 1. Change default credentials
# Update .env with strong passwords
DB_PASSWORD=<generate-strong-password>
REDIS_PASSWORD=<generate-strong-password>

# 2. Enable PostgreSQL encryption
# In init-db.sql, add:
ALTER DATABASE itsm_db SET ssl = on;

# 3. Backup encryption
# Encrypt backups before storage
gpg --encrypt backup.sql

# 4. User permissions
# Principle of least privilege
# Create separate DB users for different services
```

### Application Security

```bash
# 1. Update SECRET_KEY
SECRET_KEY=<generate-secret-key>
# Generate: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 2. Enable Django security middleware
# In settings.py:
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {...}
X_FRAME_OPTIONS = 'DENY'

# 3. Rate limiting
# Already configured in Nginx

# 4. API authentication
# JWT tokens with expiration
# MFA for user accounts
```

### Container Security

```bash
# 1. Scan images for vulnerabilities
trivy image ghcr.io/your-org/itsm-api:latest

# 2. Use minimal base images
# Current: python:3.11-slim

# 3. Run containers as non-root
# User 1000:1000 in Dockerfile

# 4. Regular updates
# Schedule weekly image rebuilds with latest dependencies
```

---

## Performance Tuning

### Database Optimization

```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM itsm_ticket WHERE status = 'open';

-- Create indexes
CREATE INDEX idx_ticket_status ON itsm_ticket(status);
CREATE INDEX idx_ticket_created_at ON itsm_ticket(created_at DESC);

-- Vacuum and analyze
VACUUM ANALYZE;

-- PostgreSQL config tuning (in docker-compose.yml)
shared_buffers = 256MB  # 25% of RAM
effective_cache_size = 1GB
work_mem = 16MB
maintenance_work_mem = 64MB
```

### Cache Optimization

```bash
# 1. Configure Redis persistence
# In docker-compose.yml: "redis:7 redis-server --appendonly yes"

# 2. Set appropriate TTLs
# Session: 1 hour
# API responses: 5 minutes
# Static content: 24 hours

# 3. Monitor cache hit rate
redis-cli INFO stats
# Look for: keyspace_hits / (keyspace_hits + keyspace_misses)
# Target: > 90%
```

### API Optimization

```bash
# 1. Enable query optimization in Django
# settings.py:
ATOMIC_REQUESTS = False  # Use transaction management
DEBUG = False  # Disable debug mode in production

# 2. Use pagination
# Limit: 20-50 items per page
# Offset or cursor pagination

# 3. Optimize serializers
# Remove unnecessary fields
# Use select_related / prefetch_related

# 4. Caching
# Cache expensive queries
# Cache API responses
```

### Load Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Simple load test
ab -n 1000 -c 10 http://localhost/api/v1/tickets/

# Using Locust for more complex scenarios
pip install locust
locust -f locustfile.py

# Monitor metrics
# Watch Prometheus/Grafana during load test
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check if PostgreSQL is running
docker-compose ps postgres
docker-compose logs postgres

# Verify connection string
docker-compose exec backend python -c \
  "from django.db import connection; connection.ensure_connection()"

# Check network connectivity
docker-compose exec backend ping postgres:5432
```

#### 2. Celery Tasks Not Running
```bash
# Check if Celery worker is running
docker-compose logs celery

# Check Redis connectivity
docker-compose exec backend redis-cli -h redis ping

# Monitor Celery tasks
docker-compose exec backend celery -A itsm_project events

# Clear stuck tasks
docker-compose exec backend celery -A itsm_project purge
```

#### 3. Memory Issues
```bash
# Check memory usage
docker stats
docker-compose ps  # with memory columns

# Increase memory limits in docker-compose.yml
# Or reduce GUNICORN_WORKERS

# Clear old migrations/cache
docker-compose exec backend python manage.py migrate --fake-initial
docker-compose exec backend python manage.py shell
# In shell: from django.core.cache import cache; cache.clear()
```

#### 4. Pod Crashing in Kubernetes
```bash
# Check pod logs
kubectl logs pod-name -n itsm-system

# Check events
kubectl describe pod pod-name -n itsm-system

# Check resource limits
kubectl top pod -n itsm-system

# Check probes
kubectl describe pod pod-name | grep -A 5 "Liveness\|Readiness"
```

### Health Checks

```bash
# Docker Compose
curl http://localhost/health/
docker-compose exec backend python manage.py check

# Kubernetes
kubectl get endpoints -n itsm-system
kubectl get events -n itsm-system --sort-by='.lastTimestamp'
```

---

## Operations Manual

### Daily Operations

```bash
# Morning check
docker-compose ps  # Verify all services running
curl http://localhost/health/  # Check API health

# Check error logs
docker-compose logs backend | grep ERROR | head -20

# Monitor metrics
# Visit Prometheus/Grafana dashboards
```

### Weekly Tasks

```bash
# Database maintenance
docker-compose exec postgres psql -U postgres -c "VACUUM ANALYZE;"

# Clear old logs
docker exec $(docker-compose ps -q backend) \
  find /app/logs -mtime +30 -delete

# Backup database
./backup.sh  # Create automated backup script
```

### Monthly Tasks

```bash
# Dependency updates
cd backend
pip list --outdated
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
git commit -am "Update dependencies"

# Security scanning
trivy image ghcr.io/your-org/itsm-api:latest

# Performance analysis
# Review slow queries in Prometheus
# Review error rates
# Review resource usage trends
```

### Disaster Recovery

```bash
# Database recovery
docker-compose down
docker volume rm backend_postgres_data
docker-compose up -d postgres
docker-compose exec -T postgres psql -U postgres < backup.sql
docker-compose up -d

# Service recovery
docker-compose restart <service-name>

# Complete reset (WARNING: Deletes all data)
docker-compose down -v
docker-compose up -d
```

---

## Support & Contact

For issues or questions:
- Documentation: [Link to docs]
- Slack: #itsm-platform
- Email: devops@example.com
- Issues: https://github.com/your-org/itsm-api/issues
