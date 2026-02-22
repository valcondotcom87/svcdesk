"""
Audit Models - Compliance and audit logging
"""
from django.db import models
from apps.core.models import TimeStampedModel


class AuditLog(TimeStampedModel):
    """Comprehensive audit logging for compliance"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    
    # Action Details
    action = models.CharField(max_length=100)  # Created, Updated, Deleted, Approved, etc.
    entity_type = models.CharField(max_length=100)  # Incident, Change, User, etc.
    entity_id = models.CharField(max_length=100)
    
    # Changes
    field_name = models.CharField(max_length=100, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    
    # Network
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('failure', 'Failure'),
            ('warning', 'Warning'),
        ],
        default='success'
    )
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['entity_type', 'entity_id']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.entity_type}({self.entity_id})"


class DataRetentionPolicy(TimeStampedModel):
    """Define data retention policies for compliance"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='retention_policies'
    )
    
    data_type = models.CharField(
        max_length=100,
        choices=[
            ('closed_incidents', 'Closed Incidents'),
            ('closed_requests', 'Closed Requests'),
            ('audit_logs', 'Audit Logs'),
            ('user_data', 'User Data'),
            ('attachments', 'Attachments'),
        ]
    )
    
    retention_days = models.IntegerField()  # How long to keep data
    archive_before_delete = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['organization', 'data_type']


class ComplianceCheck(TimeStampedModel):
    """Track compliance checks and certifications"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='compliance_checks'
    )
    
    check_type = models.CharField(
        max_length=100,
        choices=[
            ('iso27001', 'ISO 27001'),
            ('nist_csf', 'NIST CSF'),
            ('gdpr', 'GDPR'),
            ('hipaa', 'HIPAA'),
            ('custom', 'Custom'),
        ]
    )
    
    check_date = models.DateTimeField()
    result = models.CharField(
        max_length=20,
        choices=[
            ('pass', 'Pass'),
            ('fail', 'Fail'),
            ('warning', 'Warning'),
        ]
    )
    
    findings = models.TextField(blank=True)
    remediation_plan = models.TextField(blank=True)
    next_check_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-check_date']
        indexes = [
            models.Index(fields=['organization', 'check_type']),
        ]
