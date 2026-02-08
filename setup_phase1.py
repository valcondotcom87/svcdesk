#!/usr/bin/env python
"""
Phase 1 Implementation - Create all Django apps and initial structure
Run this script to set up the complete ITSM application structure
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_project.settings')
django.setup()

from django.core.management import execute_from_command_line

APPS_TO_CREATE = [
    'organizations',
    'incidents',
    'service_requests',
    'problems',
    'changes',
    'cmdb',
    'sla',
    'workflows',
    'notifications',
    'reports',
    'audit',
]

def create_apps():
    """Create all required Django apps"""
    apps_dir = 'apps'
    
    for app_name in APPS_TO_CREATE:
        app_path = os.path.join(apps_dir, app_name)
        
        # Skip if app already exists
        if os.path.exists(app_path):
            print(f"✓ App '{app_name}' already exists")
            continue
        
        # Create app directory
        os.makedirs(app_path, exist_ok=True)
        
        # Create __init__.py
        with open(os.path.join(app_path, '__init__.py'), 'w') as f:
            f.write(f'"""\n{app_name.replace("_", " ").title()} App\n"""\n')
        
        # Create apps.py
        class_name = ''.join(word.title() for word in app_name.split('_'))
        with open(os.path.join(app_path, 'apps.py'), 'w') as f:
            f.write(f'''"""
{class_name} App Configuration
"""
from django.apps import AppConfig


class {class_name}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app_name}'
    verbose_name = '{app_name.replace("_", " ").title()}'
''')
        
        # Create models.py
        with open(os.path.join(app_path, 'models.py'), 'w') as f:
            f.write(f'''"""
{class_name} Models
"""
from django.db import models
from apps.core.models import TimeStampedModel, SoftDeleteModel, AuditModel

# Create your models here.
''')
        
        # Create serializers.py
        with open(os.path.join(app_path, 'serializers.py'), 'w') as f:
            f.write(f'''"""
{class_name} Serializers
"""
from rest_framework import serializers

# Create your serializers here.
''')
        
        # Create views.py
        with open(os.path.join(app_path, 'views.py'), 'w') as f:
            f.write(f'''"""
{class_name} Views
"""
from rest_framework import viewsets, permissions
from apps.core.permissions import IsTenantUser

# Create your views here.
''')
        
        # Create admin.py
        with open(os.path.join(app_path, 'admin.py'), 'w') as f:
            f.write(f'''"""
{class_name} Admin
"""
from django.contrib import admin

# Register your models here.
''')
        
        # Create urls.py
        with open(os.path.join(app_path, 'urls.py'), 'w') as f:
            f.write(f'''"""
{class_name} URLs
"""
from django.urls import path
from . import views

urlpatterns = [
]
''')
        
        # Create tests.py
        with open(os.path.join(app_path, 'tests.py'), 'w') as f:
            f.write(f'''"""
{class_name} Tests
"""
from django.test import TestCase

# Create your tests here.
''')
        
        print(f"✓ Created app: {app_name}")

if __name__ == '__main__':
    print("Creating Django apps...")
    create_apps()
    print("\nAll apps created successfully!")
    print("\nNext steps:")
    print("1. Create models in each app")
    print("2. Create serializers for API")
    print("3. Create viewsets and urls")
    print("4. Run: python manage.py makemigrations")
    print("5. Run: python manage.py migrate")
