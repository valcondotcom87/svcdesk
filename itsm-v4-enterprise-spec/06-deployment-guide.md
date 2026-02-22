# 06. Deployment Guide (On-Prem & Cloud)

## On-Prem (Docker Compose)
1. Provision host: 4 vCPU, 8GB RAM, 100GB SSD
2. Install Docker Engine + Compose
3. Set production env vars
4. Run stack

```
docker compose -f docker-compose.production.yml --env-file .env.production up -d
```

## Cloud (Kubernetes)
- Namespace: `itsm-prod`
- Deployments: api, worker, scheduler, nginx
- StatefulSets: postgres, redis
- Ingress: TLS termination + WAF
- Secrets: stored in cloud secret manager

### K8s Minimum Objects
- Deployment: `itsm-api`, `itsm-worker`, `itsm-beat`, `itsm-frontend`
- StatefulSet: `itsm-postgres`, `itsm-redis`
- ConfigMap: `itsm-config`
- Secret: `itsm-secrets`
- Ingress: `itsm-ingress`

## Backup and DR
- Daily database backups
- Object storage replication
- Restore drills every quarter
- RPO 15 minutes, RTO 4 hours
