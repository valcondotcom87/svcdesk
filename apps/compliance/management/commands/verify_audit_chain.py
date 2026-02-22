from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.compliance.models import ImmutableAuditLog
import hashlib


class Command(BaseCommand):
    help = 'Verify integrity of immutable audit log hash chain'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Verify logs for specific user email'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Check logs from last N days (default: 30)'
        )

    def handle(self, *args, **options):
        user_email = options.get('user')
        days_back = options.get('days')

        # Get logs
        logs = ImmutableAuditLog.objects.all()
        
        if user_email:
            logs = logs.filter(user__email=user_email)
        
        # Filter by days
        cutoff_date = timezone.now() - timezone.timedelta(days=days_back)
        logs = logs.filter(timestamp__gte=cutoff_date)

        logs = logs.order_by('timestamp')

        self.stdout.write(self.style.SUCCESS('=== Audit Log Hash Chain Verification ===\n'))
        self.stdout.write(f"Verifying {logs.count()} logs...\n")

        issues = []
        valid_count = 0

        for log in logs:
            if log.hash_chain_valid:
                valid_count += 1
            else:
                issues.append({
                    'log_id': log.id,
                    'user': log.user.email if log.user else 'System',
                    'action': log.get_action_display(),
                    'timestamp': log.timestamp,
                    'issue': 'Hash chain integrity compromised'
                })

        self.stdout.write(f"Valid logs: {valid_count}/{logs.count()}")
        
        if issues:
            self.stdout.write(self.style.WARNING(f'\n⚠️  Found {len(issues)} integrity issues:\n'))
            for issue in issues:
                self.stdout.write(
                    f"  - Log ID {issue['log_id']}: {issue['user']} - "
                    f"{issue['action']} at {issue['timestamp']}"
                )
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ All audit logs verified - No integrity issues found!'))
