# 07. Security Hardening Checklist

## Core
- TLS 1.2+ enforced
- Strong ciphers and HSTS enabled
- Secrets in vault (not in repo)
- MFA for privileged roles
- Password policy: 12+ chars, rotation for admins

## Application
- RBAC per module and per action
- Immutable audit log with hash chaining
- Rate limiting + IP throttling
- Input validation (OWASP)
- File upload scanning

## Data Protection
- Encryption at rest (DB + object storage)
- Encryption in transit (HTTPS + mTLS internal)
- Data retention policy with legal holds

## Infrastructure
- Network segmentation (DMZ, app, data)
- Least privilege IAM
- CIS benchmark hardening for OS
- Backup encryption

## Monitoring
- SIEM integration (audit + auth events)
- Alerting for SLA breach and escalation
- Anomaly detection on login patterns
