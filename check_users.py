import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_project.settings')

import django
django.setup()

from apps.users.models import User

users = User.objects.all()
print(f"\nTotal users in database: {users.count()}\n")
print("Existing users:")
for user in users:
    print(f"  - Email: {user.email}")
    print(f"    Username: {user.username}")
    print(f"    Role: {user.role}")
    print(f"    Active: {user.is_active}\n")

if users.count() == 0:
    print("No users found! Creating test user...")
    from apps.organizations.models import Organization
    org, _ = Organization.objects.get_or_create(name='Main Organization', defaults={'domain': 'main.org'})
    admin = User.objects.create_superuser(
        email='admin@itsm.local',
        username='admin',
        password='admin123456',
        organization=org
    )
    print(f"✅ Created admin user: admin@itsm.local")
