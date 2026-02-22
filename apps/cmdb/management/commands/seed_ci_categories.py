"""
Management command to seed CI categories for CMDB.
"""
from django.core.management.base import BaseCommand

from apps.cmdb.models import CICategory
from apps.organizations.models import Organization


class Command(BaseCommand):
    help = "Seed CI categories for CMDB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--org-name",
            type=str,
            default=None,
            help="Target organization name (defaults to all active orgs)",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing CI categories before seeding",
        )

    def handle(self, *args, **options):
        org_name = options.get("org_name")
        reset = options.get("reset", False)

        if org_name:
            orgs = Organization.objects.filter(name=org_name, is_active=True)
        else:
            orgs = Organization.objects.filter(is_active=True)

        if not orgs.exists():
            self.stdout.write(self.style.ERROR("No active organizations found"))
            return

        catalog = [
            ("Service", "Business or technical services"),
            ("Application", "Business and support applications"),
            ("Database", "Database platforms and instances"),
            ("Network", "Network devices and connectivity"),
            ("Server", "Physical or virtual servers"),
            ("Endpoint", "User devices and peripherals"),
            ("Security", "Security controls and tooling"),
            ("Facility", "Facilities and environmental systems"),
        ]

        for org in orgs:
            self.stdout.write(f"Seeding CI categories for: {org.name}")

            if reset:
                CICategory.objects.filter(organization=org).delete()
                self.stdout.write(self.style.WARNING("  - Existing categories cleared"))

            created_count = 0
            for name, description in catalog:
                _, created = CICategory.objects.get_or_create(
                    organization=org,
                    name=name,
                    defaults={"description": description},
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"  * {name}"))
                else:
                    self.stdout.write(f"  - {name} (exists)")

            self.stdout.write(
                self.style.SUCCESS(f"Seeded {created_count} CI categories for {org.name}")
            )
