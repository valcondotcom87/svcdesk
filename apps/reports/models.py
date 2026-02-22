"""
Reports Models - Analytics and reporting
"""
from django.db import models
from apps.core.models import TimeStampedModel


class Report(TimeStampedModel):
    """Predefined reports"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='reports'
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    report_type = models.CharField(
        max_length=50,
        choices=[
            ('incident', 'Incident'),
            ('service_request', 'Service Request'),
            ('problem', 'Problem'),
            ('change', 'Change'),
            ('sla', 'SLA'),
            ('custom', 'Custom'),
        ]
    )
    
    # Configuration
    frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('custom', 'Custom'),
        ],
        default='monthly'
    )
    
    recipients = models.ManyToManyField('users.User', related_name='assigned_reports')
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']


class ReportExecution(TimeStampedModel):
    """Report execution records"""
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    
    executed_at = models.DateTimeField()
    data_json = models.JSONField(default=dict)
    file_url = models.URLField(blank=True)
    
    class Meta:
        ordering = ['-executed_at']
        indexes = [
            models.Index(fields=['report', '-executed_at']),
        ]


class Dashboard(TimeStampedModel):
    """Custom dashboards"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='dashboards'
    )
    
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='owned_dashboards'
    )
    
    is_public = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', 'name']


class DashboardWidget(TimeStampedModel):
    """Widgets on dashboards"""
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name='widgets'
    )
    
    widget_type = models.CharField(
        max_length=50,
        choices=[
            ('metric', 'Metric'),
            ('chart', 'Chart'),
            ('table', 'Table'),
            ('list', 'List'),
        ]
    )
    
    title = models.CharField(max_length=255)
    position = models.IntegerField()
    size = models.CharField(max_length=10)  # e.g., "1x1", "2x2"
    config_json = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['position']
