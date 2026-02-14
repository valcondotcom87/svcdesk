"""
Organizations Models - Multi-tenancy foundation
"""
from django.db import models
from apps.core.models import TimeStampedModel, SoftDeleteModel, AuditModel, UUIDModel


class Organization(TimeStampedModel):
    """
    Represents a single tenant organization
    Multi-tenancy foundation
    """
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='organizations/', null=True, blank=True)
    
    # Organization Info
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Settings
    is_active = models.BooleanField(default=True)
    max_users = models.IntegerField(default=100)
    max_storage_gb = models.IntegerField(default=50)
    
    # Subscription
    subscription_tier = models.CharField(
        max_length=20,
        choices=[
            ('free', 'Free'),
            ('professional', 'Professional'),
            ('enterprise', 'Enterprise'),
        ],
        default='professional'
    )
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.name


class Department(TimeStampedModel):
    """Departments within an organization"""
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='departments'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='sub_departments'
    )
    
    class Meta:
        unique_together = ['organization', 'name']
        indexes = [
            models.Index(fields=['organization']),
        ]
    
    def __str__(self):
        return self.name


class DepartmentMember(UUIDModel):
    """Department membership model"""
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('lead', 'Department Lead'),
    ]

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='department_memberships'
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['department', 'user']
        indexes = [
            models.Index(fields=['department', 'role']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department.name}"


class Team(TimeStampedModel):
    """Teams within departments"""
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='teams'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='teams'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(
        'users.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='managed_teams'
    )
    
    class Meta:
        unique_together = ['organization', 'name']
        indexes = [
            models.Index(fields=['organization', 'department']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class ModuleCategory(TimeStampedModel):
    """Configurable categories per module and organization."""

    MODULE_CHOICES = [
        ('incidents', 'Incidents'),
        ('service_requests', 'Service Requests'),
        ('problems', 'Problems'),
        ('changes', 'Changes'),
        ('assets', 'Assets'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='module_categories'
    )
    module = models.CharField(max_length=50, choices=MODULE_CHOICES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        unique_together = ['organization', 'module', 'name']
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['organization', 'module', 'is_active']),
        ]

    def __str__(self):
        return f"{self.module}:{self.name}"
