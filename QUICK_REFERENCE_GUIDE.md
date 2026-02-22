# ITSM Platform - Quick Reference Guide

## 🚀 Quick Start

### Local Development (5 minutes)
```bash
cd backend
cp .env.example .env
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

### Access Services
| Service | URL | Credentials |
|---------|-----|-------------|
| API | http://localhost | Public |
| Admin | http://localhost/admin/ | Superuser |
| Prometheus | http://localhost:9090 | Public |
| Grafana | http://localhost:3000 | admin/password |

---

## 📋 Common Commands

### Docker Compose
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f backend

# Execute command
docker-compose exec backend python manage.py shell

# Scale service
docker-compose up -d --scale celery=3

# Health check
docker-compose ps
```

### Database Operations
```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Backup database
docker-compose exec postgres pg_dump -U postgres itsm_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres itsm_db < backup.sql

# Database shell
docker-compose exec postgres psql -U postgres -d itsm_db
```

### Kubernetes
```bash
# Deploy
kubectl apply -f k8s/

# Check status
kubectl get pods -n itsm-system
kubectl rollout status deployment/itsm-api -n itsm-system

# View logs
kubectl logs deployment/itsm-api -n itsm-system -f

# Scale
kubectl scale deployment itsm-api --replicas=5 -n itsm-system

# Port forward
kubectl port-forward svc/grafana 3000:3000 -n itsm-system
```

---

## 🔍 Monitoring

### Key Dashboards
- **API Performance**: http://localhost:3000/d/api-dashboard
- **Infrastructure**: http://localhost:3000/d/infrastructure
- **Database**: http://localhost:3000/d/database
- **Redis**: http://localhost:3000/d/redis

### Alert Status
```bash
curl http://localhost:9090/api/v1/alerts | jq
```

### Common Queries
```promql
# API response time
histogram_quantile(0.95, django_http_request_duration_seconds)

# Error rate
rate(django_http_requests_total{status=~"5.."}[5m])

# Database connections
pg_stat_activity_count

# Memory usage
container_memory_usage_bytes
```

---

## 🐛 Troubleshooting

### API Down
```bash
# Check service status
docker-compose ps backend

# View logs
docker-compose logs backend | tail -50

# Restart service
docker-compose restart backend

# Check database connection
docker-compose exec backend python manage.py check
```

### Celery Not Processing Tasks
```bash
# Check if worker running
docker-compose ps celery

# View worker logs
docker-compose logs celery | tail -50

# Check Redis connection
docker-compose exec backend redis-cli -h redis ping

# Inspect active tasks
docker-compose exec backend celery -A itsm_project inspect active

# Clear stuck tasks
docker-compose exec backend celery -A itsm_project purge
```

### Memory Issues
```bash
# Check memory usage
docker stats

# Check PostgreSQL memory
docker-compose exec postgres psql -U postgres -c "SELECT sum(heap_blks_read) FROM pg_statio_user_tables;"

# Clear cache
docker-compose exec backend python manage.py shell
# In shell: from django.core.cache import cache; cache.clear()
```

### Slow Queries
```bash
# Check slow queries
docker-compose exec postgres psql -U postgres -c \
  "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# Create index
docker-compose exec postgres psql -U postgres -c \
  "CREATE INDEX idx_ticket_status ON itsm_ticket(status);"

# Analyze query
docker-compose exec postgres psql -U postgres -c \
  "EXPLAIN ANALYZE SELECT * FROM itsm_ticket WHERE status = 'open';"
```

---

## 📦 Deployment

### GitHub Actions
```bash
# Push to trigger pipeline
git push origin main

# View workflow status
# Settings → Actions → CI/CD Pipeline

# Redeploy
git commit --allow-empty -m "Redeploy"
git push
```

### Kubernetes
```bash
# Update image
kubectl set image deployment/itsm-api \
  django=ghcr.io/your-org/itsm-api:v2.1.0 \
  -n itsm-system

# Rollback
kubectl rollout undo deployment/itsm-api -n itsm-system
```

---

## 🔐 Security

### Update Secrets
```bash
# Generate new secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Update .env
SECRET_KEY=<new-secret-key>

# Kubernetes secret
kubectl create secret generic itsm-secrets \
  --from-literal=SECRET_KEY=<new-value> \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Scan for Vulnerabilities
```bash
# Scan Docker image
trivy image ghcr.io/your-org/itsm-api:latest

# Scan code
bandit -r backend/apps

# Check dependencies
pip install safety
safety check
```

---

## 📊 Performance Tuning

### Database Optimization
```sql
-- Check slow queries
SELECT query, mean_exec_time FROM pg_stat_statements 
WHERE mean_exec_time > 100 ORDER BY mean_exec_time DESC;

-- Vacuum and analyze
VACUUM ANALYZE;

-- Create missing indexes
CREATE INDEX idx_name ON table_name(column);

-- Monitor connections
SELECT count(*) FROM pg_stat_activity;
```

### Cache Optimization
```bash
# Check Redis memory
docker-compose exec redis redis-cli INFO memory

# Monitor hit rate
docker-compose exec redis redis-cli INFO stats

# Clear cache
docker-compose exec redis redis-cli FLUSHALL
```

### Load Testing
```bash
# Simple load test
ab -n 1000 -c 10 http://localhost/api/v1/tickets/

# Using Apache Bench
apachebench -n 1000 -c 50 http://localhost/

# Using curl
for i in {1..100}; do curl http://localhost/health/ & done
```

---

## 🔄 Backup & Recovery

### Automated Backups
```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres itsm_db | gzip > backup_$(date +%Y%m%d).sql.gz

# Backup with timestamp
docker-compose exec postgres pg_dump -U postgres itsm_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup to S3
docker-compose exec postgres pg_dump -U postgres itsm_db | \
  aws s3 cp - s3://bucket/backup_$(date +%Y%m%d).sql.gz
```

### Restore from Backup
```bash
# 1. Stop application
docker-compose stop backend celery

# 2. Restore database
docker-compose exec -T postgres psql -U postgres itsm_db < backup.sql

# 3. Restart application
docker-compose up -d

# 4. Verify
docker-compose exec backend python manage.py check
```

---

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale Celery workers
docker-compose up -d --scale celery=5

# Scale API (requires load balancer)
docker-compose up -d --scale backend=3

# Kubernetes
kubectl scale deployment itsm-api --replicas=5 -n itsm-system
```

### Vertical Scaling
```bash
# Increase resource limits in docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

# Kubernetes
kubectl set resources deployment itsm-api \
  --limits=cpu=2000m,memory=2Gi \
  -n itsm-system
```

---

## 🛠️ Maintenance

### Daily Tasks
```bash
# Check health
curl http://localhost/health/

# Monitor errors
docker-compose logs backend | grep ERROR

# Check resources
docker stats
```

### Weekly Tasks
```bash
# Database maintenance
docker-compose exec postgres psql -U postgres -c "VACUUM ANALYZE;"

# Update dependencies
cd backend && pip install --upgrade -r requirements.txt

# Backup verification
ls -lh backup_*.sql
```

### Monthly Tasks
```bash
# Security scanning
trivy image ghcr.io/your-org/itsm-api:latest

# Performance analysis
# Review Prometheus metrics

# Log rotation
find logs -mtime +30 -delete

# Disaster recovery drill
# Test backup restoration process
```

---

## 📞 Support

### Documentation
- [Deployment Guide](PRODUCTION_DEPLOYMENT_GUIDE.md)
- [Operations Manual](OPERATIONS_MANUAL.md)
- [API Documentation](http://localhost/api/schema/)
- [Phase 3 Summary](PHASE_3_COMPLETION_SUMMARY.md)

### Useful Links
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Django Admin: http://localhost/admin/
- API Docs: http://localhost/api/schema/
- Kubernetes Dashboard: https://kubernetes-dashboard.example.com

### Contacts
- DevOps: devops@example.com
- Database: dba@example.com
- Backend: backend@example.com
- Infrastructure: infra@example.com

---

## ⚡ Emergency Procedures

### Service Down
```bash
# 1. Identify issue
docker-compose ps
docker-compose logs <service>

# 2. Restart service
docker-compose restart <service>

# 3. Check status
docker-compose ps

# 4. Verify
curl http://localhost/health/
```

### Database Recovery
```bash
# 1. Check status
docker-compose exec postgres psql -U postgres -c "SELECT version();"

# 2. Kill long-running queries
docker-compose exec postgres psql -U postgres -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE duration > '5 minutes';"

# 3. Vacuum database
docker-compose exec postgres psql -U postgres -c "VACUUM ANALYZE;"

# 4. Restart
docker-compose restart postgres
```

### Out of Memory
```bash
# 1. Check memory
docker stats

# 2. Identify heavy service
top  # Inside container

# 3. Scale up
docker-compose up -d --scale celery=1  # Reduce scale

# 4. Restart services
docker-compose restart

# 5. Monitor
watch docker stats
```

---

## 🎯 Key Metrics

### Target Values
| Metric | Target | Alert |
|--------|--------|-------|
| Uptime | > 99.9% | < 99.9% |
| P95 Response Time | < 1s | > 1s |
| Error Rate | < 0.1% | > 1% |
| CPU Usage | < 70% | > 80% |
| Memory Usage | < 75% | > 90% |
| Disk Space | > 10% free | < 10% free |
| DB Connections | < 80 | > 80 |
| Cache Hit Rate | > 90% | < 80% |

---

**Last Updated**: 2024
**Version**: 1.0
**Status**: Production Ready
