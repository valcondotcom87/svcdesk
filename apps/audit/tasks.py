"""
Audit cleanup tasks
"""
from celery import shared_task
from django.utils import timezone
from django.conf import settings

from apps.audit.models import AuditLog, DataRetentionPolicy


@shared_task
def purge_audit_logs():
    """Purge audit logs beyond retention policy."""
    total_deleted = 0
    policies = DataRetentionPolicy.objects.filter(data_type='audit_logs')

    if policies.exists():
        for policy in policies:
            cutoff = timezone.now() - timezone.timedelta(days=policy.retention_days)
            deleted, _ = AuditLog.objects.filter(
                organization=policy.organization,
                created_at__lt=cutoff,
            ).delete()
            total_deleted += deleted
    else:
        cutoff = timezone.now() - timezone.timedelta(days=settings.AUDIT_LOG_RETENTION_DAYS)
        deleted, _ = AuditLog.objects.filter(created_at__lt=cutoff).delete()
        total_deleted += deleted

    return {"deleted": total_deleted}
