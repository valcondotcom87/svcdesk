import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "itsm_project.settings")

import django

django.setup()

from apps.users.models import User

email = "admin@itsm.local"
password = "admin123456"

if User.objects.filter(email=email).exists():
    print(f"Admin user already exists: {email}")
else:
    user = User.objects.create_superuser(
        email=email,
        username="admin",
        password=password,
        first_name="Admin",
        last_name="User",
    )
    print(f"Created admin user: {user.email}")
