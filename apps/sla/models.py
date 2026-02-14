"""
SLA Models - Service Level Agreements
"""
from django.db import models
from apps.core.models import TimeStampedModel, AuditModel


class SLAPolicy(AuditModel):
    """SLA Policy definitions"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='sla_policies'
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Applicability
    service = models.ForeignKey(
        'service_requests.Service',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sla_policies'
    )
    incident_category = models.CharField(max_length=100, blank=True)
    applies_to_priority = models.CharField(
        max_length=20,
        choices=[
            ('critical', 'Critical'),
            ('high', 'High'),
            ('medium', 'Medium'),
            ('low', 'Low'),
        ],
        blank=True
    )
    
    # Response Time (in minutes)
    response_time = models.IntegerField()  # Target first response time
    
    # Resolution Time (in minutes)
    resolution_time = models.IntegerField()  # Target resolution time
    
    # Business Hours
    BUSINESS_HOURS_CHOICES = [
        ('24x7', '24x7'),
        ('business', 'Business Hours (9-5)'),
        ('extended', 'Extended Hours (8-8)'),
    ]
    coverage = models.CharField(
        max_length=20,
        choices=BUSINESS_HOURS_CHOICES,
        default='24x7'
    )
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        return self.name


class SLATarget(AuditModel):
    """SLA targets per severity"""
    sla_policy = models.ForeignKey(
        SLAPolicy,
        on_delete=models.CASCADE,
        related_name='targets'
    )

    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)

    # Targets are stored in minutes
    response_time_minutes = models.IntegerField()
    resolution_time_minutes = models.IntegerField()

    class Meta:
        unique_together = ['sla_policy', 'severity']
        ordering = ['severity']
        indexes = [
            models.Index(fields=['sla_policy', 'severity']),
        ]


class SLABreach(AuditModel):
    """Track SLA breaches"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='sla_breaches'
    )
    
    incident = models.OneToOneField(
        'incidents.Incident',
        on_delete=models.CASCADE,
        related_name='sla_breach_record',
        null=True,
        blank=True
    )
    
    service_request = models.OneToOneField(
        'service_requests.ServiceRequest',
        on_delete=models.CASCADE,
        related_name='sla_breach_record',
        null=True,
        blank=True
    )
    
    sla_policy = models.ForeignKey(
        SLAPolicy,
        on_delete=models.SET_NULL,
        null=True,
        related_name='breaches'
    )
    
    # Breach Details
    BREACH_TYPE = [
        ('response', 'Response Time'),
        ('resolution', 'Resolution Time'),
    ]
    breach_type = models.CharField(max_length=20, choices=BREACH_TYPE)
    
    target_time = models.DateTimeField()
    breached_at = models.DateTimeField()
    breach_duration_minutes = models.IntegerField()
    
    is_acknowledged = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-breached_at']
        indexes = [
            models.Index(fields=['organization', 'breach_type']),
            models.Index(fields=['is_acknowledged']),
        ]


class SLAEscalation(AuditModel):
    """SLA escalation rules and tracking"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='sla_escalations'
    )
    
    sla_policy = models.ForeignKey(
        SLAPolicy,
        on_delete=models.CASCADE,
        related_name='escalations'
    )
    
    # Escalation Timing
    ESCALATION_LEVEL = [
        (1, 'Level 1'),
        (2, 'Level 2'),
        (3, 'Level 3'),
    ]
    level = models.IntegerField(choices=ESCALATION_LEVEL)
    escalate_after_minutes = models.IntegerField()
    
    # Action
    escalate_to_team = models.ForeignKey(
        'organizations.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='escalated_incidents'
    )
    escalate_to_user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='escalated_incidents'
    )
    
    notify_managers = models.BooleanField(default=True)
    action_description = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['sla_policy', 'level']
        ordering = ['level']


class SLAMetric(TimeStampedModel):
    """SLA performance metrics"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='sla_metrics'
    )
    
    # Time Period
    year = models.IntegerField()
    month = models.IntegerField()
    
    # Metrics
    total_incidents = models.IntegerField(default=0)
    breached_incidents = models.IntegerField(default=0)
    compliance_percentage = models.FloatField(default=100.0)
    
    # Target vs Actual
    target_compliance = models.FloatField(default=95.0)
    is_compliant = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['organization', 'year', 'month']
        ordering = ['-year', '-month']
        indexes = [
            models.Index(fields=['organization', 'year', 'month']),
        ]
