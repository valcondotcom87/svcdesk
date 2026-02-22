import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_project.settings')
django.setup()

from apps.users.views import ADConfigurationViewSet
from apps.users.models import Organization
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model

User = get_user_model()

# Get or create test user
user = User.objects.filter(email='admin@itsm.local').first()
print(f"User found: {user}")
print(f"User organization: {user.organization if user else None}")

# Test ViewSet import
print(f"\nADConfigurationViewSet: {ADConfigurationViewSet}")
print(f"Queryset: {ADConfigurationViewSet.queryset.model}")

# Test if endpoint is in router
from apps.users.urls import router
print(f"\nRouter registry:")
for prefix, viewset, basename in router.registry:
    print(f"  {prefix} -> {viewset.__name__} ({basename})")
