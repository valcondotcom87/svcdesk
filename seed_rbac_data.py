#!/usr/bin/env python
"""
RBAC (Role-Based Access Control) Data Seeding Script
Seeds default roles with comprehensive permissions
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_project.settings')
django.setup()

from apps.users.models import Role, User, UserRole

# Define system roles with permissions
SYSTEM_ROLES = {
    'end_user': {
        'description': 'End User - Can submit incidents and service requests',
        'permissions': [
            'incidents.create',
            'incidents.read',
            'service_requests.create',
            'service_requests.read',
            'knowledge.read',
        ],
        'is_system': True,
    },
    'agent': {
        'description': 'Support Agent - Can resolve incidents and service requests',
        'permissions': [
            'incidents.create',
            'incidents.read',
            'incidents.update',
            'incidents.resolve',
            'service_requests.create',
            'service_requests.read',
            'service_requests.update',
            'service_requests.fulfill',
            'knowledge.read',
            'cmdb.read',
            'assets.read',
        ],
        'is_system': True,
    },
    'manager': {
        'description': 'Manager - Can manage incidents, service requests, and teams',
        'permissions': [
            'incidents.create',
            'incidents.read',
            'incidents.update',
            'incidents.delete',
            'incidents.resolve',
            'incidents.close',
            'service_requests.create',
            'service_requests.read',
            'service_requests.update',
            'service_requests.delete',
            'service_requests.approve',
            'service_requests.fulfill',
            'problems.create',
            'problems.read',
            'problems.update',
            'problems.delete',
            'problems.resolve',
            'changes.create',
            'changes.read',
            'changes.update',
            'changes.delete',
            'changes.approve',
            'changes.implement',
            'knowledge.create',
            'knowledge.read',
            'knowledge.update',
            'knowledge.delete',
            'knowledge.publish',
            'cmdb.read',
            'cmdb.update',
            'assets.read',
            'assets.update',
            'assets.assign',
            'sla.read',
            'sla.update',
            'reports.read',
            'reports.create',
            'reports.export',
            'users.read',
            'users.reset_password',
        ],
        'is_system': True,
    },
    'administrator': {
        'description': 'Administrator - Full system access',
        'permissions': [
            # All permissions
            'incidents.create',
            'incidents.read',
            'incidents.update',
            'incidents.delete',
            'incidents.resolve',
            'incidents.close',
            'service_requests.create',
            'service_requests.read',
            'service_requests.update',
            'service_requests.delete',
            'service_requests.approve',
            'service_requests.fulfill',
            'problems.create',
            'problems.read',
            'problems.update',
            'problems.delete',
            'problems.resolve',
            'changes.create',
            'changes.read',
            'changes.update',
            'changes.delete',
            'changes.approve',
            'changes.implement',
            'assets.create',
            'assets.read',
            'assets.update',
            'assets.delete',
            'assets.assign',
            'cmdb.create',
            'cmdb.read',
            'cmdb.update',
            'cmdb.delete',
            'knowledge.create',
            'knowledge.read',
            'knowledge.update',
            'knowledge.delete',
            'knowledge.publish',
            'sla.create',
            'sla.read',
            'sla.update',
            'sla.delete',
            'reports.read',
            'reports.create',
            'reports.export',
            'users.create',
            'users.read',
            'users.update',
            'users.delete',
            'users.reset_password',
            'admin.roles',
            'admin.settings',
            'admin.audit_logs',
            'admin.compliance',
        ],
        'is_system': True,
    },
}

def seed_rbac_roles():
    """Seed all system roles with permissions"""
    created_count = 0
    updated_count = 0
    
    print("=" * 60)
    print("Seeding RBAC Roles and Permissions")
    print("=" * 60)
    
    for role_name, role_config in SYSTEM_ROLES.items():
        role, created = Role.objects.update_or_create(
            name=role_name,
            defaults={
                'description': role_config['description'],
                'permissions': role_config['permissions'],
                'is_system_role': role_config['is_system'],
            }
        )
        
        if created:
            print(f"✓ Created role: {role_name}")
            print(f"  - Permissions: {len(role_config['permissions'])}")
            created_count += 1
        else:
            print(f"✓ Updated role: {role_name}")
            print(f"  - Permissions: {len(role_config['permissions'])}")
            updated_count += 1
    
    print()
    print(f"RBAC Seeding Complete!")
    print(f"  Created: {created_count} roles")
    print(f"  Updated: {updated_count} roles")
    print()


def assign_admin_roles():
    """Assign administrator role to admin users"""
    print("=" * 60)
    print("Assigning Roles to Admin Users")
    print("=" * 60)
    
    admin_role = Role.objects.filter(name='administrator').first()
    if not admin_role:
        print("✗ Administrator role not found")
        return
    
    # Get all admin/superuser accounts
    admin_users = User.objects.filter(is_superuser=True, is_staff=True)
    
    assigned_count = 0
    for user in admin_users:
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=admin_role,
            defaults={'assigned_by': user}  # Self-assigned
        )
        
        if created:
            print(f"✓ Assigned administrator role to: {user.get_full_name()} ({user.email})")
            assigned_count += 1
    
    if assigned_count == 0:
        print("No admin users to assign roles to")
    
    print()


def print_role_summary():
    """Print summary of all roles and permissions"""
    print("=" * 60)
    print("RBAC Role Summary")
    print("=" * 60)
    
    for role in Role.objects.all().order_by('name'):
        print(f"\nRole: {role.name}")
        print(f"  Description: {role.description}")
        print(f"  System Role: {'Yes' if role.is_system_role else 'No'}")
        print(f"  Permissions: {len(role.permissions)}")
        
        # Print first 5 permissions as sample
        for perm in role.permissions[:5]:
            print(f"    - {perm}")
        
        if len(role.permissions) > 5:
            print(f"    ... and {len(role.permissions) - 5} more permissions")
        
        # Show assigned users
        user_count = role.role_users.count()
        print(f"  Users with this role: {user_count}")


if __name__ == '__main__':
    try:
        seed_rbac_roles()
        assign_admin_roles()
        print_role_summary()
        
        print("\n" + "=" * 60)
        print("RBAC Setup Complete!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Error during RBAC seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
