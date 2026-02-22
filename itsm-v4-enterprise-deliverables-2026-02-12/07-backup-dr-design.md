# Backup and DR Design

## Scope
- PostgreSQL data (tickets, CMDB, SLA, users)
- Redis data (queues and cache)
- Object storage (attachments and evidence)
- Audit logs and SIEM exports
- Configuration and secrets (encrypted)

## Backup Strategy
- Full DB backup daily (encrypted).
- Incremental backups every 15 minutes (WAL or PITR).
- Object storage replication to secondary region.
- Audit log export daily to immutable storage.

## Retention
- Daily backups: 30 days.
- Monthly backups: 12 months.
- Audit logs: minimum 1 year (per compliance).

## DR Targets
- RPO: 15 minutes.
- RTO: 4 hours.

## DR Runbook
1. Declare incident and freeze changes.
2. Promote standby DB or restore from latest snapshot.
3. Restore object storage and audit logs.
4. Validate integrity and perform smoke tests.
5. Resume services and notify stakeholders.

## Testing
- Quarterly restore drills.
- Annual full DR simulation.
