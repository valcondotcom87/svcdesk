# Final Deployment Checklist (Ops)

## 0) Scope
- Target domain: tsm.barokahdigital.cloud
- Stack: backend (Django), frontend (Vite build served by Nginx), Postgres, Redis, Nginx, Celery, Prometheus, Grafana

## 1) Pre-flight (VPS)
- [ ] VPS meets minimum: 4 vCPU, 8 GB RAM, 100 GB disk
- [ ] DNS A record set for tsm.barokahdigital.cloud (and www if used)
- [ ] Ports open: 80, 443, 22
- [ ] Docker Engine and Docker Compose installed
- [ ] Repo cloned to /opt/itsm-platform

## 1.1) Change window and approvals
- [ ] Change ticket created and approved
- [ ] Maintenance window communicated to stakeholders
- [ ] Rollback owner and on-call escalation assigned

## 2) Secrets and Env
- [ ] Store production secrets in CI variables or a secret manager (avoid committing .env files)
- [ ] Copy backend/.env.production -> backend/.env (only on the server, never in git)
- [ ] Set SECRET_KEY (random, strong)
- [ ] Set ALLOWED_HOSTS=tsm.barokahdigital.cloud,www.tsm.barokahdigital.cloud,nginx
- [ ] Set CORS_ALLOWED_ORIGINS and CSRF_TRUSTED_ORIGINS for production domains only
- [ ] Set DATABASE_URL and REDIS_URL with strong passwords
- [ ] Set ENVIRONMENT=production and DEBUG=False

## 3) SSL (Lets Encrypt)
- [ ] Certbot install on VPS
- [ ] Certificates issued for tsm.barokahdigital.cloud (+ www if used)
- [ ] Copy fullchain.pem and privkey.pem to backend/ssl/live/tsm.barokahdigital.cloud/
- [ ] Confirm Nginx SSL paths in backend/nginx-default.conf

## 4) Frontend build
- [ ] In /opt/itsm-platform/fe create .env.production with VITE_API_BASE_URL=https://tsm.barokahdigital.cloud/api/v1
- [ ] npm install
- [ ] npm run build
- [ ] Copy dist -> /opt/itsm-platform/backend/frontend

## 5) Compose up
- [ ] docker compose up -d --build
- [ ] docker compose ps shows all services Up/healthy

## 6) Database
- [ ] docker compose run --rm backend python manage.py migrate --noinput
- [ ] docker compose run --rm backend python manage.py createsuperuser

## 7) Static and media
- [ ] docker compose run --rm backend python manage.py collectstatic --noinput
- [ ] Ensure /app/media and /app/staticfiles are mounted volumes

## 8) Health checks
- [ ] curl https://tsm.barokahdigital.cloud/api/v1/health/ returns 200
- [ ] Login works with admin user
- [ ] Verify MFA flow (if required for admin roles)

## 9) Monitoring and alerts
- [ ] Prometheus and Grafana up (optional if used)
- [ ] Healthcheck timer enabled (itsm-healthcheck.timer)
- [ ] Alerting configured (email/telegram envs set)

## 9.1) Monitoring escalation
- [ ] Primary on-call contact confirmed
- [ ] Escalation path documented (L1 -> L2 -> L3)
- [ ] Alert severity thresholds agreed (P1/P2/P3)

## 10) Backups
- [ ] Database backup script scheduled (cron or systemd timer)
- [ ] Media backup scheduled
- [ ] Restore test completed at least once

## 10.1) Backup/restore verification
- [ ] Last backup file exists and is readable
- [ ] Dry-run restore performed in non-production
- [ ] Recovery time and recovery point objectives recorded

## 11) Security verification
- [ ] .env and ssl not in git (verify .gitignore)
- [ ] CI/secret manager values match deployed env vars
- [ ] SECURE_SSL_REDIRECT=True in production
- [ ] CORS/CSRF restricted to production domains
- [ ] Admin password rotated and stored securely

## 12) Post-deploy smoke tests
- [ ] Create incident, request, change, problem
- [ ] Confirm email notifications (if enabled)
- [ ] Confirm audit logs captured

## 13) Rollback plan (ready to execute)
- [ ] Last known good image/tag documented
- [ ] Rollback command tested in staging
- [ ] Database rollback or point-in-time restore path confirmed

## Quick commands (ops)
- Start stack: docker compose up -d
- Stop stack: docker compose down
- Logs: docker compose logs -f backend
- Rebuild: docker compose up -d --build
- Health: curl https://tsm.barokahdigital.cloud/api/v1/health/
