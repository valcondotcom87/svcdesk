import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_project.settings')

import django
django.setup()

from apps.users.models import User

admin = User.objects.get(email='admin@itsm.local')
admin.set_password('admin123456')
admin.save()

print(f"✅ Reset password for admin@itsm.local to: admin123456")
