"""
Django management command to seed initial SLA policies
"""
from django.core.management.base import BaseCommand
from apps.sla.models import SLAPolicy, SLATarget, SLAEscalation
from apps.organizations.models import Organization


class Command(BaseCommand):
    help = 'Seed initial SLA policies for organizations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--org-name',
            type=str,
            help='Specific organization to seed (optional)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing policies first',
        )

    def handle(self, *args, **options):
        org_name = options.get('org_name')
        reset = options.get('reset', False)

        # Get organizations
        if org_name:
            orgs = Organization.objects.filter(name=org_name)
            if not orgs.exists():
                self.stdout.write(
                    self.style.ERROR(f'Organization "{org_name}" not found')
                )
                return
        else:
            orgs = Organization.objects.all()

        if not orgs.exists():
            self.stdout.write(self.style.WARNING('No organizations found'))
            return

        # Define standard SLA policies
        policies = [
            {
                'name': 'Standard Enterprise',
                'description': '24x7 support for enterprise customers',
                'coverage': '24x7',
                'response_time': 120,  # 2 hours
                'resolution_time': 480,  # 8 hours
                'targets': {
                    'critical': (30, 120),   # Response: 30 min, Resolution: 2 hours
                    'high': (60, 240),       # Response: 1 hour, Resolution: 4 hours
                    'medium': (120, 480),    # Response: 2 hours, Resolution: 8 hours
                    'low': (480, 1440),      # Response: 8 hours, Resolution: 24 hours
                }
            },
            {
                'name': 'Business Hours',
                'description': 'Support during business hours (9AM-5PM)',
                'coverage': 'business',
                'response_time': 240,    # 4 hours
                'resolution_time': 1440,  # 24 hours
                'targets': {
                    'critical': (60, 240),   # Response: 1 hour, Resolution: 4 hours
                    'high': (120, 480),      # Response: 2 hours, Resolution: 8 hours
                    'medium': (240, 1440),   # Response: 4 hours, Resolution: 24 hours
                    'low': (480, 2880),      # Response: 8 hours, Resolution: 48 hours
                }
            },
            {
                'name': 'Premium Support',
                'description': 'Reserved for critical infrastructure and priority clients',
                'coverage': '24x7',
                'response_time': 15,  # 15 minutes
                'resolution_time': 120,  # 2 hours
                'targets': {
                    'critical': (15, 60),    # Response: 15 min, Resolution: 1 hour
                    'high': (30, 120),       # Response: 30 min, Resolution: 2 hours
                    'medium': (60, 240),     # Response: 1 hour, Resolution: 4 hours
                    'low': (120, 480),       # Response: 2 hours, Resolution: 8 hours
                }
            },
        ]

        for org in orgs:
            self.stdout.write(f'\nProcessing organization: {org.name}')

            # Reset if requested
            if reset:
                SLAPolicy.objects.filter(organization=org).delete()
                self.stdout.write(
                    self.style.WARNING(f'Deleted existing policies for {org.name}')
                )

            # Create policies
            for policy_data in policies:
                targets_data = policy_data.pop('targets')

                policy, created = SLAPolicy.objects.get_or_create(
                    organization=org,
                    name=policy_data['name'],
                    defaults=policy_data
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Created policy: {policy.name}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  → Policy already exists: {policy.name}'
                        )
                    )

                # Add targets
                for severity, (response, resolution) in targets_data.items():
                    target, target_created = SLATarget.objects.get_or_create(
                        sla_policy=policy,
                        severity=severity,
                        defaults={
                            'response_time_minutes': response,
                            'resolution_time_minutes': resolution,
                        }
                    )

                    if target_created:
                        self.stdout.write(
                            f'    ✓ Created {severity} target '
                            f'(Response: {response}min, Resolution: {resolution}min)'
                        )

        self.stdout.write(
            self.style.SUCCESS(
                '\n✓ SLA policies seeding completed successfully'
            )
        )
