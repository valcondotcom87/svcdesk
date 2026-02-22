"""
Script to create all Django app stubs
Run this to create all required apps with basic structure
"""
import os

APPS = [
    'users',
    'organizations', 
    'tickets',
    'incidents',
    'service_requests',
    'problems',
    'changes',
    'cmdb',
    'sla',
    'workflows',
    'notifications',
    'reports',
    'audit'
]

APP_TEMPLATE = {
    '__init__.py': '''"""
{app_name_title} App
"""
default_app_config = 'apps.{app_name}.apps.{app_class}Config'
''',
    'apps.py': '''"""
{app_name_title} App Configuration
"""
from django.apps import AppConfig


class {app_class}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app_name}'
    verbose_name = '{app_name_title}'
''',
    'models.py': '''"""
{app_name_title} Models
"""
from django.db import models
from apps.core.models import TimeStampedModel, SoftDeleteModel, AuditModel

# Create your models here.
''',
    'admin.py': '''"""
{app_name_title} Admin
"""
from django.contrib import admin

# Register your models here.
''',
    'views.py': '''"""
{app_name_title} Views
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

# Create your views here.
''',
    'serializers.py': '''"""
{app_name_title} Serializers
"""
from rest_framework import serializers

# Create your serializers here.
''',
    'urls.py': '''"""
{app_name_title} URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = '{app_name}'

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
''',
    'tests.py': '''"""
{app_name_title} Tests
"""
from django.test import TestCase

# Create your tests here.
''',
}

def create_app_structure(app_name):
    """Create app directory structure"""
    app_path = f'apps/{app_name}'
    
    # Create app directory
    os.makedirs(app_path, exist_ok=True)
    
    # Get app class name (capitalize and remove underscores)
    app_class = ''.join(word.capitalize() for word in app_name.split('_'))
    app_name_title = ' '.join(word.capitalize() for word in app_name.split('_'))
    
    # Create files
    for filename, template in APP_TEMPLATE.items():
        filepath = os.path.join(app_path, filename)
        content = template.format(
            app_name=app_name,
            app_class=app_class,
            app_name_title=app_name_title
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f'✅ Created app: {app_name}')

def main():
    """Main function"""
    print('Creating Django apps...\n')
    
    for app in APPS:
        create_app_structure(app)
    
    print(f'\n✅ Successfully created {len(APPS)} apps!')
    print('\nNext steps:')
    print('1. Implement models in each app')
    print('2. Run: python manage.py makemigrations')
    print('3. Run: python manage.py migrate')

if __name__ == '__main__':
    main()
