#!/usr/bin/env python
"""
Initialize ITSM Django Project
Run this script to set up the complete Django environment
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_project.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization, Department, Team
from apps.users.models import UserRole, UserPermission

User = get_user_model()


def create_initial_organization():
    """Create initial organization"""
    org, created = Organization.objects.get_or_create(
        name='Default Organization',
        defaults={
            'slug': 'default-org',
            'email': 'admin@itsm.local',
            'subscription_tier': 'enterprise'
        }
    )
    if created:
        print(f"✓ Created organization: {org.name}")
    else:
        print(f"✓ Organization exists: {org.name}")
    return org


def create_default_roles(org):
    """Create default RBAC roles"""
    roles_config = [
        {
            'name': 'Administrator',
            'permissions': [
                ('incidents', 'create'), ('incidents', 'read'), ('incidents', 'update'), ('incidents', 'delete'),
                ('service_requests', 'create'), ('service_requests', 'read'), ('service_requests', 'update'), ('service_requests', 'delete'),
                ('problems', 'create'), ('problems', 'read'), ('problems', 'update'), ('problems', 'delete'),
                ('changes', 'create'), ('changes', 'read'), ('changes', 'update'), ('changes', 'delete'), ('changes', 'approve'),
                ('cmdb', 'create'), ('cmdb', 'read'), ('cmdb', 'update'), ('cmdb', 'delete'),
                ('reports', 'read'),
                ('admin', 'create'), ('admin', 'read'), ('admin', 'update'), ('admin', 'delete'),
            ]
        },
        {
            'name': 'Manager',
            'permissions': [
                ('incidents', 'create'), ('incidents', 'read'), ('incidents', 'update'),
                ('service_requests', 'create'), ('service_requests', 'read'), ('service_requests', 'update'), ('service_requests', 'approve'),
                ('problems', 'create'), ('problems', 'read'), ('problems', 'update'),
                ('changes', 'read'), ('changes', 'approve'),
                ('cmdb', 'read'),
                ('reports', 'read'),
            ]
        },
        {
            'name': 'Agent/Technician',
            'permissions': [
                ('incidents', 'read'), ('incidents', 'update'), ('incidents', 'resolve'),
                ('service_requests', 'read'), ('service_requests', 'update'),
                ('problems', 'read'), ('problems', 'update'),
                ('changes', 'read'),
                ('cmdb', 'read'),
            ]
        },
        {
            'name': 'End User',
            'permissions': [
                ('incidents', 'create'), ('incidents', 'read'),
                ('service_requests', 'create'), ('service_requests', 'read'),
                ('problems', 'read'),
            ]
        },
    ]
    
    for role_config in roles_config:
        role, created = UserRole.objects.get_or_create(
            organization=org,
            name=role_config['name'],
            defaults={'is_default': role_config['name'] == 'End User'}
        )
        
        if created:
            print(f"✓ Created role: {role.name}")
            
            # Create permissions for this role
            for module, action in role_config['permissions']:
                UserPermission.objects.get_or_create(
                    role=role,
                    module=module,
                    action=action
                )
        else:
            print(f"✓ Role exists: {role.name}")


def create_default_departments_teams(org):
    """Create default department and teams"""
    # Create IT Department
    dept, _ = Department.objects.get_or_create(
        organization=org,
        name='IT Department',
        defaults={'description': 'Information Technology Department'}
    )
    
    # Create teams
    teams_config = [
        {'name': 'Incident Management', 'description': 'Handles incident tickets'},
        {'name': 'Service Desk', 'description': 'First line of support'},
        {'name': 'Infrastructure', 'description': 'Infrastructure and systems'},
        {'name': 'Applications', 'description': 'Application support'},
    ]
    
    for team_config in teams_config:
        team, created = Team.objects.get_or_create(
            organization=org,
            department=dept,
            name=team_config['name'],
            defaults={'description': team_config['description']}
        )
        if created:
            print(f"✓ Created team: {team.name}")


def create_superuser():
    """Create initial superuser"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@itsm.local',
            password='admin123456'
        )
        print("✓ Created superuser: admin / admin123456")
    else:
        print("✓ Superuser already exists")


def main():
    """Run all initialization steps"""
    print("\n" + "="*60)
    print("ITSM System - Phase 1 Initialization")
    print("="*60 + "\n")
    
    # Run migrations
    print("Running database migrations...")
    call_command('migrate')
    print("✓ Migrations completed\n")
    
    # Create initial data
    print("Creating initial data...")
    org = create_initial_organization()
    create_superuser()
    create_default_roles(org)
    create_default_departments_teams(org)
    
    print("\n" + "="*60)
    print("✓ Phase 1 Initialization Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start development server: python manage.py runserver")
    print("2. Access admin: http://localhost:8000/admin/")
    print("3. Login with: admin / admin123456")
    print("4. Create API users and test endpoints")
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    main()
