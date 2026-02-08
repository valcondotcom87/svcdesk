"""
CMDB Models - Configuration Management Database
"""
from django.db import models
from apps.core.models import TimeStampedModel, AuditModel


class CICategory(TimeStampedModel):
    """Configuration Item categories"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='ci_categories'
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    
    class Meta:
        unique_together = ['organization', 'name']
        verbose_name_plural = "CI Categories"


class ConfigurationItem(AuditModel):
    """CMDB - Configuration Items (infrastructure, services, etc.)"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='configuration_items'
    )
    
    # Identification
    ci_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        CICategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='items'
    )
    
    # Details
    description = models.TextField(blank=True)
    type = models.CharField(max_length=100)  # Hardware, Software, Service, etc.
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('retired', 'Retired'),
            ('pending', 'Pending'),
        ],
        default='active',
        db_index=True
    )
    
    # Ownership
    owner_team = models.ForeignKey(
        'organizations.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_cis'
    )
    
    # Technical Details
    version = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=255, blank=True)
    manufacturer = models.CharField(max_length=255, blank=True)
    
    # Location
    location = models.CharField(max_length=255, blank=True)
    
    # Lifecycle
    acquisition_date = models.DateField(null=True, blank=True)
    disposal_date = models.DateField(null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    
    class Meta:
        unique_together = ['organization', 'ci_number']
        ordering = ['name']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'category']),
            models.Index(fields=['ci_number']),
        ]
    
    def __str__(self):
        return f"{self.ci_number} - {self.name}"


class CIRelationship(TimeStampedModel):
    """Relationships between configuration items"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='ci_relationships'
    )
    
    source_ci = models.ForeignKey(
        ConfigurationItem,
        on_delete=models.CASCADE,
        related_name='outgoing_relationships'
    )
    target_ci = models.ForeignKey(
        ConfigurationItem,
        on_delete=models.CASCADE,
        related_name='incoming_relationships'
    )
    
    # Relationship Type
    RELATIONSHIP_TYPES = [
        ('depends_on', 'Depends On'),
        ('supports', 'Supports'),
        ('connected_to', 'Connected To'),
        ('part_of', 'Part Of'),
        ('used_by', 'Used By'),
        ('installed_on', 'Installed On'),
    ]
    relationship_type = models.CharField(max_length=50, choices=RELATIONSHIP_TYPES)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['source_ci', 'target_ci', 'relationship_type']
        indexes = [
            models.Index(fields=['source_ci', 'is_active']),
            models.Index(fields=['target_ci', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.source_ci.name} {self.relationship_type} {self.target_ci.name}"


class CIAttribute(TimeStampedModel):
    """Custom attributes for configuration items"""
    ci = models.ForeignKey(
        ConfigurationItem,
        on_delete=models.CASCADE,
        related_name='attributes'
    )
    
    attribute_name = models.CharField(max_length=100)
    attribute_value = models.TextField()
    
    class Meta:
        unique_together = ['ci', 'attribute_name']


class CIChangeHistory(AuditModel):
    """Track changes to configuration items"""
    ci = models.ForeignKey(
        ConfigurationItem,
        on_delete=models.CASCADE,
        related_name='change_history'
    )
    
    change_request = models.ForeignKey(
        'changes.Change',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='affected_cis_history'
    )
    
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    change_description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ci', '-created_at']),
        ]


class CIRelated(TimeStampedModel):
    """Related incidents, problems, and changes for a CI"""
    ci = models.ForeignKey(
        ConfigurationItem,
        on_delete=models.CASCADE,
        related_name='related_items'
    )
    
    incident = models.ForeignKey(
        'incidents.Incident',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    problem = models.ForeignKey(
        'problems.Problem',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    change = models.ForeignKey(
        'changes.Change',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['ci']),
        ]
