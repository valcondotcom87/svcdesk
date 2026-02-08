"""
Organizations Models - Multi-tenancy foundation
"""
from django.db import models
from apps.core.models import TimeStampedModel, SoftDeleteModel, AuditModel


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
