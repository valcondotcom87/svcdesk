"""
Changes Models - Change management process
"""
from django.db import models
from apps.core.models import TimeStampedModel, AuditModel


class ChangeType(models.TextChoices):
    """Types of changes (ITIL)"""
    STANDARD = 'standard', 'Standard Change'
    NORMAL = 'normal', 'Normal Change'
    EMERGENCY = 'emergency', 'Emergency Change'


class ChangeStatus(models.TextChoices):
    """Change status workflow"""
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    PENDING_APPROVAL = 'pending_approval', 'Pending Approval'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    SCHEDULED = 'scheduled', 'Scheduled'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    ROLLED_BACK = 'rolled_back', 'Rolled Back'


class ChangeImpactLevel(models.IntegerChoices):
    """Change impact assessment"""
    CRITICAL = 1, 'Critical'
    HIGH = 2, 'High'
    MEDIUM = 3, 'Medium'
    LOW = 4, 'Low'


class Change(AuditModel):
    """Change management - modifications to IT services"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='changes'
    )
    
    # Identifiers
    ticket_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Classification
    change_type = models.CharField(
        max_length=20,
        choices=ChangeType.choices,
        default=ChangeType.NORMAL
    )
    category = models.CharField(max_length=100, blank=True)
    
    # People
    requester = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='requested_changes'
    )
    implementation_owner = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='implementing_changes'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=ChangeStatus.choices,
        default=ChangeStatus.DRAFT,
        db_index=True
    )
    
    # Planning
    implementation_date = models.DateTimeField(null=True, blank=True)
    backout_date = models.DateTimeField(null=True, blank=True)
    estimated_duration_minutes = models.IntegerField(null=True, blank=True)
    
    # Impact & Risk
    impact_level = models.IntegerField(
        choices=ChangeImpactLevel.choices,
        default=ChangeImpactLevel.MEDIUM
    )
    affected_services = models.CharField(max_length=500, blank=True)
    risk_assessment = models.TextField(blank=True)
    risk_mitigation = models.TextField(blank=True)
    
    # Implementation
    implementation_plan = models.TextField(blank=True)
    backout_plan = models.TextField(blank=True)
    success_criteria = models.TextField(blank=True)
    test_results = models.TextField(blank=True)
    
    # Completion
    completed_date = models.DateTimeField(null=True, blank=True)
    actual_duration_minutes = models.IntegerField(null=True, blank=True)
    completion_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['ticket_number']),
            models.Index(fields=['implementation_date']),
        ]
    
    def __str__(self):
        return f"{self.ticket_number} - {self.title}"


class CABMember(TimeStampedModel):
    """Change Advisory Board (CAB) members"""
    change = models.ForeignKey(
        Change,
        on_delete=models.CASCADE,
        related_name='cab_members'
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='cab_memberships'
    )
    role = models.CharField(max_length=100)  # e.g., "Business Representative", "Technical Expert"
    is_mandatory = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['change', 'user']


class ChangeApproval(AuditModel):
    """CAB approvals for changes"""
    change = models.ForeignKey(
        Change,
        on_delete=models.CASCADE,
        related_name='approvals'
    )
    
    cab_member = models.ForeignKey(
        CABMember,
        on_delete=models.CASCADE,
        related_name='approvals'
    )
    
    # Decision
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('on_hold', 'On Hold'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comments = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['change', 'cab_member']
        ordering = ['created_at']


class ChangeImpactAnalysis(AuditModel):
    """Impact analysis of changes"""
    change = models.OneToOneField(
        Change,
        on_delete=models.CASCADE,
        related_name='impact_analysis'
    )
    
    affected_cis = models.CharField(max_length=500, blank=True)
    affected_incidents = models.IntegerField(default=0)
    estimated_downtime_minutes = models.IntegerField(default=0)
    estimated_users_impacted = models.IntegerField(default=0)
    
    dependency_analysis = models.TextField(blank=True)
    risk_score = models.IntegerField(default=5)  # 1-10


class ChangeLog(AuditModel):
    """Audit log for all change modifications"""
    change = models.ForeignKey(
        Change,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    
    action = models.CharField(max_length=100)  # Created, Updated, Status Changed, Approved, etc.
    field_changed = models.CharField(max_length=100, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
