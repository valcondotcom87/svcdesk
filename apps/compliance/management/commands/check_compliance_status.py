from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.compliance.models import VulnerabilityTracking
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Check compliance status for overdue remediation and SLAs'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Compliance Status Check ===\n'))

        # Check overdue vulnerabilities
        today = timezone.now().date()
        overdue_vulns = VulnerabilityTracking.objects.filter(
            target_remediation_date__lt=today,
            status__in=['open', 'acknowledged', 'in_progress']
        )

        self.stdout.write(f"Overdue Vulnerabilities: {overdue_vulns.count()}")
        if overdue_vulns.exists():
            self.stdout.write(self.style.WARNING('\nOverdue Vulnerabilities:'))
            for vuln in overdue_vulns[:10]:  # Show first 10
                days_overdue = (today - vuln.target_remediation_date).days
                self.stdout.write(
                    f"  - {vuln.vulnerability_id}: {vuln.title} "
                    f"({days_overdue} days overdue)"
                )

        # Check upcoming remediations (next 7 days)
        upcoming_vulns = VulnerabilityTracking.objects.filter(
            target_remediation_date__gte=today,
            target_remediation_date__lte=today + timedelta(days=7),
            status__in=['open', 'acknowledged', 'in_progress']
        )

        self.stdout.write(f"\nRemediations Due in Next 7 Days: {upcoming_vulns.count()}")
        if upcoming_vulns.exists():
            self.stdout.write(self.style.WARNING('\nUpcoming Remediations:'))
            for vuln in upcoming_vulns[:10]:
                days_remaining = (vuln.target_remediation_date - today).days
                self.stdout.write(
                    f"  - {vuln.vulnerability_id}: {vuln.title} "
                    f"(Due in {days_remaining} days)"
                )

        # Vulnerability severity breakdown
        self.stdout.write('\n--- Vulnerability Severity Breakdown ---')
        severity_levels = ['critical', 'high', 'medium', 'low']
        for severity in severity_levels:
            count = VulnerabilityTracking.objects.filter(
                severity=severity,
                status__in=['open', 'acknowledged', 'in_progress']
            ).count()
            self.stdout.write(f"  {severity.capitalize()}: {count}")

        # Summary
        open_vulns = VulnerabilityTracking.objects.filter(
            status__in=['open', 'acknowledged', 'in_progress']
        ).count()
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal Open Vulnerabilities: {open_vulns}'))
        
        if overdue_vulns.count() == 0:
            self.stdout.write(self.style.SUCCESS('✓ All remediation SLAs are on track'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  {overdue_vulns.count()} remediations overdue'))
