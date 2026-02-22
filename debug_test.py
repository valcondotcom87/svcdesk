#!/usr/bin/env python
import os
import sys
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_project.settings')

import django
django.setup()

from rest_framework.test import APIClient
from apps.users.models import User

# Test with existing user if available, else create one  
try:
    user = User.objects.get(email='admin@itsm.local')
except User.DoesNotExist:
    print("Could not find admin@itsm.local user")
    sys.exit(1)

# Test the request with REST APIClient
client = APIClient()
print('Testing POST /api/v1/auth/login/ with APIClient')
response = client.post('/api/v1/auth/login/', {
    'username': 'admin@itsm.local',
    'password': 'admin123456'
}, format='json')
print(f'Status: {response.status_code}')
if response.status_code in [301, 302, 303, 307, 308]:
    location = response.get('Location', 'unknown')
    print(f'Redirect to: {location}')
else:
    print(f'Content Type: {response}')
    if hasattr(response, 'data'):
        print(f'Response data: {response.data}')
    else:
        print(f'Response content: {response.content.decode()[:300]}')



