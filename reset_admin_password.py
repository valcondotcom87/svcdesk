import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_project.settings')

import django
django.setup()

from apps.users.models import User
from django.utils import timezone
from django.contrib.auth.hashers import make_password

updated = User.objects.filter(email='admin@itsm.local').update(
	password=make_password('admin123456'),
	password_changed_at=timezone.now(),
)

print(f"✅ Reset password for admin@itsm.local to: admin123456 (rows={updated})")
