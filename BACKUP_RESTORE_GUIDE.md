# Backup and Restore Guide

Date: 2026-02-14
Scope: Application data (database), file uploads (media), and configuration secrets.

## Backup Strategy

### 1) Database Backup (PostgreSQL)
- Use `pg_dump` for logical backups.
- Example:
  - `pg_dump -Fc -h <host> -U <user> <db_name> > itsm_db_YYYYMMDD.dump`
- Store backups in encrypted storage (S3 with SSE-KMS or equivalent).
- Keep at least 30 days of daily backups; retain monthly snapshots for 12 months.

### 2) Media Files (Uploads)
- Backup `media/` directory (or configured media volume).
- If using object storage, enable versioning and lifecycle rules.

### 3) Configuration and Secrets
- Backup environment configuration (.env) without committing secrets to source control.
- Store encryption keys (if enabled) in a secrets manager (AWS Secrets Manager, Vault, Azure Key Vault).

## Restore Procedure

### 1) Restore Database
- Example:
  - `pg_restore -h <host> -U <user> -d <db_name> --clean --if-exists itsm_db_YYYYMMDD.dump`
- Verify migrations: `python manage.py migrate`.

### 2) Restore Media
- Replace `media/` content with backup snapshot.
- Verify file permissions and ownership.

### 3) Validate Application
- Run health check: `/api/v1/health/`
- Run a basic login and list endpoint test.

## Verification
- Perform quarterly restore tests.
- Record RPO and RTO targets and compare with actual results.

## Automation
- Use a scheduled job (cron or managed scheduler) for backups.
- Ensure backup success/failure notifications are sent to the security or ops team.

## Retention & Disposal
- Follow retention requirements in your policy (e.g., 30-90 days for operational backups, 7 years for audit logs).
- Securely delete expired backups.
