#!/usr/bin/env python
"""
Seed initial compliance frameworks
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_project.settings')
django.setup()

from apps.compliance.models import ComplianceFramework
from apps.organizations.models import Organization
from apps.users.models import User

print("=" * 60)
print("SEEDING INITIAL COMPLIANCE FRAMEWORKS")
print("=" * 60)

org = Organization.objects.first()
if not org:
    print("ERROR: No organization found!")
    exit(1)

print(f"\nOrganization: {org.name}")

admin = User.objects.get(email='admin@itsm.local')
print(f"Admin User: {admin.email}")

frameworks = [
    'ISO27001',
    'PCI_DSS', 
    'GDPR',
    'SOC2',
    'NIST_CSF'
]

print(f"\nSeeding {len(frameworks)} compliance frameworks...")
print("-" * 60)

created = 0
for fw in frameworks:
    obj, is_new = ComplianceFramework.objects.get_or_create(
        framework=fw,
        organization=org,
        defaults={'responsible_person': admin, 'status': 'in_progress'}
    )
    if is_new:
        created += 1
        print(f"✓ Created: {obj.get_framework_display()}")
    else:
        print(f"• Already exists: {obj.get_framework_display()}")

print("-" * 60)
print(f"\nTotal frameworks seeded: {created}")
print(f"Total frameworks available: {ComplianceFramework.objects.count()}")

print("\n" + "=" * 60)
print("SEEDING COMPLETE!")
print("=" * 60)
