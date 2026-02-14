"""
Management command to seed module categories and apply them to sample records.
"""
from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.organizations.models import Organization, ModuleCategory
from apps.incidents.models import Incident
from apps.problems.models import Problem
from apps.changes.models import Change


class Command(BaseCommand):
    help = 'Seed module categories for incidents, problems, and changes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--org-name',
            type=str,
            default=None,
            help='Target organization name (defaults to first active org)',
        )
        parser.add_argument(
            '--apply-to-records',
            action='store_true',
            help='Apply categories to recent records',
        )

    def handle(self, *args, **options):
        org_name = options.get('org_name')
        apply_to = options.get('apply_to_records', False)

        # Get organization
        if org_name:
            org = Organization.objects.filter(name=org_name, is_active=True).first()
            if not org:
                self.stdout.write(self.style.ERROR(f'Organization "{org_name}" not found'))
                return
        else:
            org = Organization.objects.filter(is_active=True).first()
            if not org:
                self.stdout.write(self.style.ERROR('No active organization found'))
                return

        self.stdout.write(f'Seeding categories for organization: {org.name}')

        # Category templates
        catalog = {
            'incidents': [
                ('Access & Identity', 'Account access, authentication, and permissions'),
                ('End-User Device', 'Laptops, desktops, mobile devices, peripherals'),
                ('Network & Connectivity', 'LAN/WAN, Wi-Fi, VPN, internet access'),
                ('Email & Collaboration', 'Email, messaging, calendaring, conferencing'),
                ('Business Application', 'ERP/CRM/LOB application incidents'),
                ('Infrastructure & Platform', 'Servers, virtualization, cloud platform'),
                ('Security & Compliance', 'Security events, malware, policy violations'),
                ('Database & Storage', 'Database services, backups, storage access'),
                ('Telephony & Unified Comms', 'PBX, VoIP, paging, contact center'),
                ('Facilities & Environment', 'Power, cooling, physical environment'),
            ],
            'problems': [
                ('Root Cause', 'Fundamental cause analysis'),
                ('Recurring', 'Recurring known issues'),
                ('Performance', 'Performance degradation'),
                ('Security', 'Security-related problems'),
                ('Integration', 'System integration issues'),
            ],
            'changes': [
                ('Infrastructure', 'Infrastructure and server changes'),
                ('Application', 'Application and software updates'),
                ('Security', 'Security patches and hardening'),
                ('Configuration', 'Configuration and settings changes'),
                ('Maintenance', 'Preventive maintenance activities'),
            ],
        }

        # Seed categories
        total_created = 0
        for module, categories in catalog.items():
            for idx, (name, description) in enumerate(categories, start=1):
                cat, created = ModuleCategory.objects.get_or_create(
                    organization=org,
                    module=module,
                    name=name,
                    defaults={
                        'description': description,
                        'sort_order': idx,
                        'is_active': True,
                    }
                )
                if created:
                    total_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Created {module}: {name}')
                    )
                else:
                    self.stdout.write(f'  - {module}: {name} (already exists)')

        self.stdout.write(
            self.style.SUCCESS(f'\nSeeded {total_created} new categories')
        )

        # Apply to recent records if requested
        if apply_to:
            self.stdout.write('Applying categories to recent records...')
            self._apply_to_records(org)

    def _apply_to_records(self, org):
        """Apply seeded categories to recent records."""
        models_and_modules = [
            (Incident, 'incidents'),
            (Problem, 'problems'),
            (Change, 'changes'),
        ]

        for model, module in models_and_modules:
            categories = list(
                ModuleCategory.objects
                .filter(organization=org, module=module, is_active=True)
                .order_by('sort_order')
                .values_list('name', flat=True)
            )

            if not categories:
                self.stdout.write(self.style.WARNING(f'  No categories found for {module}'))
                continue

            # Get recent records without category
            recent = list(
                model.objects
                .filter(organization=org, category='')
                .order_by('-created_at')[:10]
            )

            if not recent:
                self.stdout.write(f'  - No uncategorized {module} records found')
                continue

            # Assign categories cyclically
            for idx, record in enumerate(recent):
                record.category = categories[idx % len(categories)]
                record.save(update_fields=['category'])

            self.stdout.write(
                self.style.SUCCESS(f'  ✓ Categorized {len(recent)} {module}')
            )
