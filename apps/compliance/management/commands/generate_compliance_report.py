from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.compliance.models import ComplianceCheckpoint, ComplianceFramework
import json
from datetime import datetime


class Command(BaseCommand):
    help = 'Generate comprehensive compliance report'

    def add_arguments(self, parser):
        parser.add_argument(
            '--framework',
            type=str,
            help='Specific framework to report on (e.g., ISO27001)'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['text', 'json'],
            default='text',
            help='Output format'
        )

    def handle(self, *args, **options):
        framework_filter = options.get('framework')
        output_format = options.get('format')

        # Get frameworks
        frameworks = ComplianceFramework.objects.all()
        if framework_filter:
            frameworks = frameworks.filter(framework=framework_filter)

        report_data = {
            'generated_at': timezone.now().isoformat(),
            'total_frameworks': frameworks.count(),
            'frameworks': []
        }

        for framework in frameworks:
            requirements = framework.requirements.all()
            
            framework_data = {
                'framework': framework.get_framework_display(),
                'status': framework.get_status_display(),
                'progress_percentage': framework.progress_percentage,
                'version': framework.version,
                'requirements': {
                    'total': requirements.count(),
                    'not_started': requirements.filter(status='not_started').count(),
                    'in_progress': requirements.filter(status='in_progress').count(),
                    'implemented': requirements.filter(status='implemented').count(),
                    'verified': requirements.filter(status='verified').count(),
                },
                'target_certification_date': framework.target_certification_date.isoformat() if framework.target_certification_date else None,
                'certification_date': framework.certification_date.isoformat() if framework.certification_date else None,
            }
            report_data['frameworks'].append(framework_data)

        # Get compliance checkpoints
        checkpoints = ComplianceCheckpoint.objects.filter(status='completed')
        if checkpoints.exists():
            avg_score = checkpoints.aggregate(
                avg=models.Avg('compliance_score')
            )['avg']
            report_data['overall_compliance_score'] = round(avg_score, 2)
        
        # Output report
        if output_format == 'json':
            self.stdout.write(json.dumps(report_data, indent=2))
        else:
            self.stdout.write(self.style.SUCCESS('=== Compliance Report ==='))
            self.stdout.write(f"Generated: {report_data['generated_at']}\n")
            self.stdout.write(f"Total Frameworks: {report_data['total_frameworks']}\n")
            
            if 'overall_compliance_score' in report_data:
                score = report_data['overall_compliance_score']
                self.stdout.write(f"Overall Compliance Score: {score}%\n")
            
            self.stdout.write('\n--- Framework Status ---')
            for fw in report_data['frameworks']:
                self.stdout.write(f"\n{fw['framework']}")
                self.stdout.write(f"  Status: {fw['status']}")
                self.stdout.write(f"  Progress: {fw['progress_percentage']}%")
                self.stdout.write(f"  Requirements: {fw['requirements']['total']}")
                self.stdout.write(f"    - Not Started: {fw['requirements']['not_started']}")
                self.stdout.write(f"    - In Progress: {fw['requirements']['in_progress']}")
                self.stdout.write(f"    - Implemented: {fw['requirements']['implemented']}")
                self.stdout.write(f"    - Verified: {fw['requirements']['verified']}")
