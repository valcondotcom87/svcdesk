# Deployment Guide

## On-Prem (Docker Compose)
1. Provision host: 4 vCPU, 8 GB RAM, 100 GB SSD (min).
2. Install Docker Engine and Docker Compose.
3. Set environment variables and secrets in `.env.production`.
4. Deploy stack:

```bash
docker compose -f docker-compose.production.yml --env-file .env.production up -d
```

## Managed Cloud (Kubernetes)
- Namespace: `itsm-prod`
- Deployments: `api`, `worker`, `scheduler`, `frontend`, `gateway`
- StatefulSets: `postgres`, `redis`
- Ingress: TLS termination + WAF
- Secrets: stored in cloud secret manager

## HA and Scaling
- Stateless services scale horizontally.
- PostgreSQL: primary + read replicas, streaming replication.
- Redis: clustered or managed service.
- Object storage for attachments and evidence.

## Observability
- Centralized logging (JSON) to SIEM.
- Metrics via Prometheus-compatible exporters.
- Tracing with OpenTelemetry.

## Network and Security
- Reverse proxy hardened, TLS 1.2+.
- WAF in front of gateway.
- Private subnets for data tier.

## Backup and DR Summary
- Daily backups, encrypted and immutable.
- Quarterly restore drills.
- RPO <= 15 minutes, RTO <= 4 hours.
