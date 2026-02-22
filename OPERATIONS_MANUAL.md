# ITSM Platform - Operations Manual

## Table of Contents
1. [System Overview](#system-overview)
2. [Service Management](#service-management)
3. [Monitoring & Alerts](#monitoring--alerts)
4. [Scaling & Load Balancing](#scaling--load-balancing)
5. [Backup & Recovery](#backup--recovery)
6. [Performance Tuning](#performance-tuning)
7. [Incident Response](#incident-response)
8. [Maintenance Windows](#maintenance-windows)

---

## System Overview

### Architecture

```
Internet
   ↓
Load Balancer (External)
   ↓
Nginx (Reverse Proxy)
   ↓
├── Django API (Gunicorn × 4 workers)
├── Celery Workers (Async tasks)
├── Celery Beat (Scheduled tasks)
├── PostgreSQL (Database)
├── Redis (Cache)
└── Prometheus + Grafana (Monitoring)
```

### Service Dependencies

```
API → PostgreSQL (required)
API → Redis (cache, not critical)
Celery → Redis (required)
Celery Beat → PostgreSQL + Redis (required)
Prometheus → All services (metrics)
Grafana → Prometheus (visualization)
```

### Resource Allocation

| Service | CPU | Memory | Storage |
|---------|-----|--------|---------|
| PostgreSQL | 1 core | 2GB | 50GB |
| Redis | 0.5 core | 512MB | 10GB |
| Django API | 1 core | 1GB | 10GB |
| Celery Workers (×2) | 2 cores | 2GB | 5GB |
| Celery Beat | 0.5 core | 256MB | 1GB |
| Nginx | 0.5 core | 256MB | 1GB |
| Prometheus | 0.5 core | 512MB | 20GB |
| Grafana | 0.5 core | 256MB | 1GB |
| **TOTAL** | **8 cores** | **8.5GB** | **98GB** |

---

## Service Management

### Docker Compose Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend

# View logs
docker-compose logs -f backend

# View service status
docker-compose ps

# Execute command in service
docker-compose exec backend python manage.py shell

# Scale service
docker-compose up -d --scale celery=3

# Update service
docker-compose pull && docker-compose up -d
```

### Kubernetes Commands

```bash
# Get all resources
kubectl get all -n itsm-system

# Get deployment status
kubectl rollout status deployment/itsm-api -n itsm-system

# Scale deployment
kubectl scale deployment itsm-api --replicas=5 -n itsm-system

# View logs
kubectl logs deployment/itsm-api -n itsm-system -f

# Execute command in pod
kubectl exec -it pod-name -n itsm-system -- bash

# Describe resource
kubectl describe pod pod-name -n itsm-system

# Get events
kubectl get events -n itsm-system --sort-by='.lastTimestamp'
```

### Service Startup Order

```
1. PostgreSQL (health check: pg_isready)
   └─ Wait: 30-60 seconds

2. Redis (health check: redis-cli ping)
   └─ Wait: 10-30 seconds

3. Django API (health check: /health/ endpoint)
   ├─ Runs migrations on startup
   ├─ Waits for DB + Redis healthy
   └─ Wait: 1-2 minutes for full startup

4. Celery Worker
   ├─ Waits for API + Redis healthy
   └─ Ready: 30-60 seconds

5. Celery Beat
   ├─ Waits for API + Redis healthy
   └─ Ready: 30-60 seconds

6. Nginx
   ├─ Waits for API healthy
   └─ Ready: immediately

7. Prometheus & Grafana
   └─ Ready: immediately
```

---

## Monitoring & Alerts

### Key Metrics to Monitor

#### Application Metrics
- **Request Rate**: requests/sec (target: < 1000 req/s)
- **Response Time**: p95 (target: < 1 second)
- **Error Rate**: 5xx errors/sec (target: < 1%)
- **Active Requests**: concurrent (target: < 100)

#### Database Metrics
- **Connection Count**: (target: < 80)
- **Query Time**: p95 (target: < 100ms)
- **Disk Space**: (alert: < 10% free)
- **Replication Lag**: (target: < 10ms)

#### Cache Metrics
- **Hit Rate**: (target: > 90%)
- **Memory Usage**: (alert: > 85%)
- **Eviction Rate**: (target: < 1%)

#### Infrastructure Metrics
- **CPU Usage**: (alert: > 80%)
- **Memory Usage**: (alert: > 90%)
- **Disk I/O**: (alert: > 80%)
- **Network I/O**: (alert: > 80%)

### Alert Triggers

| Alert | Severity | Threshold | Action |
|-------|----------|-----------|--------|
| API Down | Critical | 2 min | Page on-call |
| High Error Rate | Warning | > 5% | Check logs |
| High Response Time | Warning | p95 > 1s | Scale up |
| High CPU Usage | Warning | > 80% | Scale up |
| Database Down | Critical | 1 min | Page on-call |
| Redis Down | Warning | 1 min | Check connection |
| Low Disk Space | Warning | < 10% | Cleanup/expand |

### Viewing Alerts

```bash
# Prometheus alert status
curl http://localhost:9090/api/v1/alerts | jq

# Grafana (web UI)
# http://localhost:3000

# Alertmanager
curl http://localhost:9093/api/v1/alerts | jq
```

---

## Scaling & Load Balancing

### Horizontal Scaling

#### Docker Compose
```bash
# Scale Celery workers
docker-compose up -d --scale celery=5

# Scale API instances (requires load balancer config)
# 1. Add upstream servers to nginx-default.conf:
upstream django {
    server backend:8000;
    server backend-2:8000;
    server backend-3:8000;
}

# 2. Recreate instances:
docker-compose up -d --scale backend=3
```

#### Kubernetes
```bash
# Scale deployment
kubectl scale deployment itsm-api --replicas=5 -n itsm-system

# HPA will auto-scale based on metrics:
kubectl get hpa -n itsm-system
kubectl describe hpa itsm-api-hpa -n itsm-system

# Manual HPA adjustment
kubectl patch hpa itsm-api-hpa -n itsm-system \
  -p '{"spec":{"maxReplicas":15}}'
```

### Vertical Scaling (Increase Resources)

```bash
# Docker Compose: Update docker-compose.yml
services:
  backend:
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
      reservations:
        cpus: '1.0'
        memory: 1G

# Kubernetes: Update deployment
kubectl set resources deployment itsm-api \
  --limits=cpu=2000m,memory=2Gi \
  --requests=cpu=1000m,memory=1Gi \
  -n itsm-system
```

### Load Balancing Strategy

#### DNS Load Balancing
```bash
# Round-robin DNS
api.example.com → 10.0.1.1 (API-1)
api.example.com → 10.0.1.2 (API-2)
api.example.com → 10.0.1.3 (API-3)
```

#### Application Load Balancer (ALB)
```bash
# Configure sticky sessions (if needed)
# By default: random routing

# Health check path
/health/

# Connection draining
30 seconds
```

#### Nginx Load Balancing
```nginx
upstream django_cluster {
    least_conn;  # Least connections algorithm
    server backend-1:8000 max_fails=3 fail_timeout=30s;
    server backend-2:8000 max_fails=3 fail_timeout=30s;
    server backend-3:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}
```

---

## Backup & Recovery

### Backup Strategy

#### Database Backups
```bash
# Full backup (daily)
docker-compose exec postgres pg_dump -U postgres itsm_db | gzip > backup_$(date +%Y%m%d).sql.gz

# Incremental backup (hourly) - using WAL archiving
# Already configured in PostgreSQL

# Backup to S3
docker-compose exec postgres pg_dump -U postgres itsm_db | \
  aws s3 cp - s3://backup-bucket/itsm-db/backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

#### Redis Backups
```bash
# Backup Redis
docker-compose exec redis redis-cli BGSAVE
docker cp $(docker-compose ps -q redis):/data/dump.rdb ./redis_backup.rdb

# Backup to S3
aws s3 cp redis_backup.rdb s3://backup-bucket/itsm-redis/$(date +%Y%m%d_%H%M%S).rdb
```

#### File Backups
```bash
# Backup media files
tar czf media_backup_$(date +%Y%m%d).tar.gz backend/media/

# Backup static files (can be regenerated)
tar czf static_backup_$(date +%Y%m%d).tar.gz backend/static/
```

### Backup Retention Policy

| Backup Type | Retention | Frequency | Location |
|------------|-----------|-----------|----------|
| Hourly (full DB) | 24 hours | Hourly | Local |
| Daily (full DB) | 30 days | Daily | Local + S3 |
| Weekly (full) | 12 weeks | Weekly | S3 |
| Monthly (full) | 12 months | Monthly | S3 Glacier |

### Restore Procedures

#### Database Restore
```bash
# 1. Stop application
docker-compose stop backend celery celery-beat

# 2. Drop existing database
docker-compose exec postgres dropdb -U postgres itsm_db

# 3. Create new database
docker-compose exec postgres createdb -U postgres itsm_db

# 4. Restore from backup
docker-compose exec -T postgres psql -U postgres itsm_db < backup.sql

# 5. Start application
docker-compose up -d

# 6. Verify
docker-compose exec backend python manage.py check
```

#### Redis Restore
```bash
# 1. Stop Celery
docker-compose stop celery celery-beat

# 2. Replace dump file
docker cp redis_backup.rdb $(docker-compose ps -q redis):/data/dump.rdb

# 3. Restart Redis
docker-compose restart redis

# 4. Start Celery
docker-compose up -d celery celery-beat
```

---

## Performance Tuning

### Database Tuning

```sql
-- Check slow queries
SELECT query, mean_exec_time, calls FROM pg_stat_statements
WHERE mean_exec_time > 100 ORDER BY mean_exec_time DESC;

-- Create indexes for slow queries
CREATE INDEX idx_ticket_status_created ON itsm_ticket(status, created_at DESC);

-- Vacuum and analyze
VACUUM ANALYZE;

-- Increase work_mem for sorting/hashing
SET work_mem TO '256MB';
```

### Redis Tuning

```bash
# Monitor memory usage
redis-cli INFO memory

# Set memory limit and eviction policy
# In docker-compose.yml:
command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru

# Monitor hit rate
redis-cli INFO stats
# Look for: keyspace_hits / (keyspace_hits + keyspace_misses)
```

### Django Tuning

```python
# settings.py

# Use select_related / prefetch_related
from django.db.models import Prefetch

# Cache middleware
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    ...
    'django.middleware.cache.FetchFromCacheMiddleware',
]

# Cache timeout
CACHE_TIMEOUT = 300  # 5 minutes

# Database connection pooling
DATABASES = {
    'default': {
        ...
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

### Nginx Tuning

```nginx
# nginx.conf

# Worker processes
worker_processes auto;

# Worker connections
events {
    worker_connections 10000;
    use epoll;
}

# Gzip compression
gzip on;
gzip_vary on;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript application/json;

# Caching
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g;
proxy_cache api_cache;
proxy_cache_valid 200 5m;
```

---

## Incident Response

### Classification

| Severity | Impact | Response Time |
|----------|--------|---|
| Critical | Complete outage | 15 minutes |
| High | Partial outage | 1 hour |
| Medium | Degraded performance | 4 hours |
| Low | Minor issues | 1 day |

### Incident Response Workflow

```
1. DETECT
   └─ Alert triggered or user report
   
2. ACKNOWLEDGE
   └─ Assign to on-call engineer
   └─ Declare incident in Slack
   
3. DIAGNOSE
   └─ Gather logs and metrics
   └─ Identify root cause
   
4. MITIGATE
   └─ Implement temporary fix
   └─ Scale up resources if needed
   
5. RESOLVE
   └─ Implement permanent fix
   └─ Deploy to production
   
6. REVIEW
   └─ Post-mortem analysis
   └─ Update runbooks
```

### Common Issues & Solutions

#### Issue: High Memory Usage
```bash
# 1. Identify culprit
docker stats

# 2. Gather metrics
kubectl top pods -n itsm-system

# 3. Scale up
docker-compose up -d --scale celery=3
# OR
kubectl scale deployment itsm-api --replicas=5 -n itsm-system

# 4. Investigate root cause
docker-compose logs backend | grep -i memory
```

#### Issue: Database Slowness
```bash
# 1. Check connection count
docker-compose exec postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# 2. Identify slow queries
docker-compose exec postgres psql -U postgres -c \
  "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# 3. Kill long-running queries
docker-compose exec postgres psql -U postgres -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE duration > '5 minutes';"

# 4. Vacuum database
docker-compose exec postgres psql -U postgres -c "VACUUM ANALYZE;"
```

#### Issue: Celery Tasks Stuck
```bash
# 1. Check Redis
docker-compose exec backend redis-cli info

# 2. View tasks
docker-compose exec backend celery -A itsm_project inspect active

# 3. Clear stuck tasks
docker-compose exec backend celery -A itsm_project purge

# 4. Restart worker
docker-compose restart celery
```

---

## Maintenance Windows

### Pre-Maintenance Checklist

```bash
# 1. Notify users
# Send notification: "Maintenance scheduled for 2:00-2:30 AM UTC"

# 2. Backup database
docker-compose exec postgres pg_dump -U postgres itsm_db > pre_maintenance_backup.sql

# 3. Disable monitoring alerts (temporary)
# In Alertmanager: disable notifications

# 4. Prepare rollback plan
git log --oneline | head -5
```

### Zero-Downtime Deployment

```bash
# 1. Create new version
docker build -t ghcr.io/your-org/itsm-api:v2.1.0 backend/
docker push ghcr.io/your-org/itsm-api:v2.1.0

# 2. Kubernetes rolling update
kubectl set image deployment/itsm-api \
  django=ghcr.io/your-org/itsm-api:v2.1.0 \
  -n itsm-system

# 3. Monitor rollout
kubectl rollout status deployment/itsm-api -n itsm-system

# 4. Verify
curl https://api.example.com/api/v1/
kubectl logs deployment/itsm-api -n itsm-system -f

# 5. Rollback if needed
kubectl rollout undo deployment/itsm-api -n itsm-system
```

### Maintenance Tasks

#### Daily
- Monitor error logs (< 5 errors/hour target)
- Check backup completion
- Review performance metrics

#### Weekly
- Database VACUUM ANALYZE
- Clear old logs (> 30 days)
- Update dependencies (security patches)

#### Monthly
- Full security scanning
- Performance analysis & tuning
- Capacity planning review
- Disaster recovery drill

#### Quarterly
- Major version upgrades
- Infrastructure assessment
- Security audit
- Cost optimization review

### Post-Maintenance

```bash
# 1. Verify all services
docker-compose ps
kubectl get all -n itsm-system

# 2. Run health checks
curl http://localhost/health/
curl http://localhost/api/v1/

# 3. Check logs for errors
docker-compose logs backend | grep ERROR

# 4. Re-enable alerts
# In Alertmanager: enable notifications

# 5. Send completion notification
# "Maintenance completed successfully"

# 6. Monitor for 1 hour
# Watch error rate, latency, resource usage
```

---

## Contacts & Escalation

| Role | Contact | On-call |
|------|---------|---------|
| DevOps | devops@example.com | PagerDuty |
| Database Admin | dba@example.com | On-call rotation |
| Backend Lead | backend-lead@example.com | - |
| Infrastructure | infra@example.com | - |

---

## References

- Deployment Guide: [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)
- API Documentation: [http://localhost/api/schema/](http://localhost/api/schema/)
- Prometheus Docs: [https://prometheus.io/docs/](https://prometheus.io/docs/)
- Kubernetes Docs: [https://kubernetes.io/docs/](https://kubernetes.io/docs/)
