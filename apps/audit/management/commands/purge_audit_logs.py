"""
Purge audit logs based on retention policy.
"""
from django.core.management.base import BaseCommand

from apps.audit.tasks import purge_audit_logs


class Command(BaseCommand):
    help = 'Purge audit logs based on retention settings.'

    def handle(self, *args, **options):
        result = purge_audit_logs()
        deleted = result.get('deleted', 0)
        self.stdout.write(self.style.SUCCESS(f'Purged audit logs. Deleted: {deleted}.'))
