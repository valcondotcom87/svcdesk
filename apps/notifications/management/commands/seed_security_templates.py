"""
Seed security notification templates.
"""
from django.core.management.base import BaseCommand

from apps.notifications.models import NotificationTemplate
from apps.organizations.models import Organization


class Command(BaseCommand):
    help = 'Seed security notification templates for lockout alerts.'

    def add_arguments(self, parser):
        parser.add_argument('--organization-id', type=str, help='Optional organization ID to seed.')

    def handle(self, *args, **options):
        org_id = options.get('organization_id')
        organizations = Organization.objects.all()
        if org_id:
            organizations = organizations.filter(id=org_id)

        created = 0
        updated = 0

        for org in organizations:
            for channel in ['in_app', 'email']:
                template, was_created = NotificationTemplate.objects.update_or_create(
                    organization=org,
                    name='security_lockout',
                    channel=channel,
                    defaults={
                        'subject': 'Security alert: account locked',
                        'body': (
                            'User account locked: {user_email}\n'
                            'Reason: {reason}\n'
                            'IP: {ip_address}\n'
                            'Lockout duration: {lockout_minutes} minutes'
                        ),
                        'is_active': True,
                    },
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Security templates ready. Created: {created}, updated: {updated}.'
        ))
