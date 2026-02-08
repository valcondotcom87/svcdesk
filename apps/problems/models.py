"""
Problems Models - Problem management and known errors
"""
from django.db import models
from apps.core.models import TimeStampedModel, AuditModel


class Problem(AuditModel):
    """Problem management - root cause analysis"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='problems'
    )
    
    # Identifiers
    ticket_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # People
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='owned_problems'
    )
    
    # Status
    STATUS_CHOICES = [
        ('identified', 'Identified'),
        ('investigating', 'Investigating'),
        ('diagnosed', 'Diagnosed'),
        ('solution_identified', 'Solution Identified'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='identified')
    
    # Impact
    affected_users = models.IntegerField(default=0)
    affected_services = models.CharField(max_length=500, blank=True)
    
    # RCA
    root_cause = models.TextField(blank=True)
    workaround = models.TextField(blank=True)
    permanent_solution = models.TextField(blank=True)
    
    # Timeline
    first_incident_date = models.DateTimeField(null=True, blank=True)
    identified_date = models.DateTimeField(null=True, blank=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    
    # Related Change
    change_request = models.OneToOneField(
        'changes.Change',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='problem'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['ticket_number']),
        ]
    
    def __str__(self):
        return f"{self.ticket_number} - {self.title}"


class RootCauseAnalysis(AuditModel):
    """Root cause analysis details"""
    problem = models.OneToOneField(
        Problem,
        on_delete=models.CASCADE,
        related_name='rca'
    )
    
    investigation_method = models.CharField(max_length=100, blank=True)
    five_whys = models.TextField(blank=True)
    contributing_factors = models.TextField(blank=True)
    lessons_learned = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Root Cause Analyses"


class KnownErrorDatabase(AuditModel):
    """Known Error Database (KEDB) entries"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='known_errors'
    )
    
    problem = models.OneToOneField(
        Problem,
        on_delete=models.CASCADE,
        related_name='kedb_entry',
        null=True,
        blank=True
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    error_code = models.CharField(max_length=50, unique=True)
    symptoms = models.TextField()
    workaround = models.TextField()
    permanent_solution = models.TextField(blank=True)
    
    # Effectiveness
    resolution_rate = models.FloatField(default=0)  # 0-100%
    
    class Meta:
        verbose_name_plural = "Known Error Databases"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization']),
            models.Index(fields=['error_code']),
        ]
    
    def __str__(self):
        return f"{self.error_code} - {self.title}"
