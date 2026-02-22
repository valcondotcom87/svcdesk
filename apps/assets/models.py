import uuid
from django.db import models
from apps.core.models import AuditModel


class AssetCategory(AuditModel):
    """Asset categories."""

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='asset_categories'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['organization', 'name']
        ordering = ['name']

    def __str__(self):
        return self.name


class Asset(AuditModel):
    """Asset inventory record."""

    ASSET_TYPE_CHOICES = [
        ('hardware', 'Hardware'),
        ('software', 'Software'),
        ('virtual', 'Virtual'),
        ('network', 'Network'),
        ('data', 'Data'),
        ('service', 'Service'),
        ('facility', 'Facility'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('in_use', 'In Use'),
        ('in_stock', 'In Stock'),
        ('maintenance', 'Maintenance'),
        ('planned', 'Planned'),
        ('retired', 'Retired'),
        ('disposed', 'Disposed'),
    ]

    LIFECYCLE_STAGE_CHOICES = [
        ('planning', 'Planning'),
        ('acquisition', 'Acquisition'),
        ('in_use', 'In Use'),
        ('maintenance', 'Maintenance'),
        ('retired', 'Retired'),
        ('disposed', 'Disposed'),
    ]

    CRITICALITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    DATA_CLASSIFICATION_CHOICES = [
        ('public', 'Public'),
        ('internal', 'Internal'),
        ('confidential', 'Confidential'),
        ('restricted', 'Restricted'),
    ]

    IMPACT_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]

    RISK_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    RECOVERY_PRIORITY_CHOICES = [
        ('p1', 'P1 - Critical'),
        ('p2', 'P2 - High'),
        ('p3', 'P3 - Medium'),
        ('p4', 'P4 - Low'),
    ]

    BUSINESS_VALUE_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    CSF_FUNCTION_CHOICES = [
        ('govern', 'Govern'),
        ('identify', 'Identify'),
        ('protect', 'Protect'),
        ('detect', 'Detect'),
        ('respond', 'Respond'),
        ('recover', 'Recover'),
    ]

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='assets'
    )
    asset_tag = models.CharField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES, default='hardware')
    category = models.ForeignKey(
        AssetCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assets'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_use')
    lifecycle_stage = models.CharField(
        max_length=20,
        choices=LIFECYCLE_STAGE_CHOICES,
        default='in_use'
    )
    criticality = models.CharField(max_length=20, choices=CRITICALITY_CHOICES, default='medium')
    current_owner = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_assets'
    )
    business_owner = models.CharField(max_length=255, blank=True)
    technical_owner = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    related_service = models.CharField(max_length=255, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    warranty_expires = models.DateField(null=True, blank=True)
    serial_number = models.CharField(max_length=255, blank=True)
    system_name = models.CharField(max_length=255, blank=True)
    data_classification = models.CharField(
        max_length=20,
        choices=DATA_CLASSIFICATION_CHOICES,
        default='internal'
    )
    confidentiality_impact = models.CharField(
        max_length=20,
        choices=IMPACT_LEVEL_CHOICES,
        default='moderate'
    )
    integrity_impact = models.CharField(
        max_length=20,
        choices=IMPACT_LEVEL_CHOICES,
        default='moderate'
    )
    availability_impact = models.CharField(
        max_length=20,
        choices=IMPACT_LEVEL_CHOICES,
        default='moderate'
    )
    fips_impact_level = models.CharField(
        max_length=20,
        choices=IMPACT_LEVEL_CHOICES,
        default='moderate'
    )
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, default='medium')
    recovery_priority = models.CharField(max_length=10, choices=RECOVERY_PRIORITY_CHOICES, default='p3')
    business_value = models.CharField(max_length=20, choices=BUSINESS_VALUE_CHOICES, default='medium')
    authorization_boundary = models.TextField(blank=True)
    dependencies = models.TextField(blank=True)
    compliance_tags = models.CharField(max_length=255, blank=True)
    csf_function = models.CharField(max_length=20, choices=CSF_FUNCTION_CHOICES, default='identify')
    csf_category = models.CharField(max_length=100, blank=True)
    iso_control = models.CharField(max_length=100, blank=True)
    nist_control = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['asset_tag']),
        ]

    def __str__(self):
        return f"{self.asset_tag} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.asset_tag:
            self.asset_tag = f"AST-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class AssetDepreciation(AuditModel):
    """Asset depreciation tracking."""

    METHOD_CHOICES = [
        ('straight_line', 'Straight Line'),
        ('declining_balance', 'Declining Balance'),
    ]

    asset = models.OneToOneField(
        Asset,
        on_delete=models.CASCADE
    )
    depreciation_method = models.CharField(max_length=30, choices=METHOD_CHOICES, default='straight_line')
    useful_life_years = models.IntegerField(default=3)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    accumulated_depreciation = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    residual_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_calculated_at = models.DateTimeField(null=True, blank=True)


class AssetMaintenance(AuditModel):
    """Maintenance history for assets."""

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE
    )
    maintenance_type = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    performed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    maintenance_date = models.DateField()
    next_due = models.DateField(null=True, blank=True)


class AssetTransfer(AuditModel):
    """Asset transfer log."""

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE
    )
    from_user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_transfers_from'
    )
    to_user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_transfers_to'
    )
    transfer_date = models.DateTimeField()
    transfer_notes = models.TextField(blank=True)
