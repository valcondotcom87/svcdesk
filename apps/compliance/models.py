from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import URLValidator, MinValueValidator, MaxValueValidator
from datetime import timedelta
from django.utils import timezone
import hashlib
import json

User = get_user_model()


class ComplianceFramework(models.Model):
    """
    Compliance frameworks yang diimplementasikan (ISO 27001, NIST, GDPR, SOC2, etc)
    """
    FRAMEWORK_CHOICES = [
        ('ISO27001', 'ISO/IEC 27001:2022 - Information Security Management'),
        ('ISO9001', 'ISO/IEC 9001:2015 - Quality Management System'),
        ('ISO20000', 'ISO/IEC 20000:2018 - IT Service Management'),
        ('NIST_CSF', 'NIST Cybersecurity Framework'),
        ('NIST_800_53', 'NIST SP 800-53 - Security Controls'),
        ('NIST_800_171', 'NIST SP 800-171 - Contractor Systems'),
        ('SOC2', 'SOC 2 - Service Organization Control'),
        ('GDPR', 'GDPR - General Data Protection Regulation'),
        ('HIPAA', 'HIPAA - Health Insurance Portability'),
        ('PCI_DSS', 'PCI-DSS - Payment Card Industry'),
    ]
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('implemented', 'Implemented'),
        ('certified', 'Certified'),
        ('expired', 'Expired'),
    ]

    framework = models.CharField(
        max_length=20,
        choices=FRAMEWORK_CHOICES,
        unique=True,
        verbose_name=_('Framework')
    )
    description = models.TextField(
        verbose_name=_('Description'),
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        verbose_name=_('Status')
    )
    version = models.CharField(
        max_length=50,
        verbose_name=_('Version'),
        blank=True
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name=_('Organization')
    )
    target_date = models.DateField(
        verbose_name=_('Target Compliance Date'),
        null=True,
        blank=True
    )
    certification_date = models.DateField(
        verbose_name=_('Certification Date'),
        null=True,
        blank=True
    )
    expiry_date = models.DateField(
        verbose_name=_('Expiry Date'),
        null=True,
        blank=True
    )
    responsible_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Responsible Person'),
        related_name='compliance_frameworks'
    )
    progress_percentage = models.IntegerField(
        default=0,
        verbose_name=_('Progress Percentage'),
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Compliance Framework')
        verbose_name_plural = _('Compliance Frameworks')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.get_framework_display()} - {self.status}"


class ComplianceRequirement(models.Model):
    """
    Individual requirements untuk setiap compliance framework
    """
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('implemented', 'Implemented'),
        ('verified', 'Verified'),
        ('non_applicable', 'Non-Applicable'),
    ]

    framework = models.ForeignKey(
        ComplianceFramework,
        on_delete=models.CASCADE,
        related_name='requirements',
        verbose_name=_('Framework')
    )
    requirement_id = models.CharField(
        max_length=50,
        verbose_name=_('Requirement ID'),
        help_text="e.g., A.8.1.1 for ISO 27001"
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('Title')
    )
    description = models.TextField(
        verbose_name=_('Description')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started',
        verbose_name=_('Status')
    )
    implementation_evidence = models.TextField(
        verbose_name=_('Implementation Evidence'),
        blank=True,
        help_text="Document/proof of implementation"
    )
    responsible_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Responsible Person')
    )
    due_date = models.DateField(
        verbose_name=_('Due Date'),
        null=True,
        blank=True
    )
    completion_date = models.DateField(
        verbose_name=_('Completion Date'),
        null=True,
        blank=True
    )
    related_control = models.CharField(
        max_length=100,
        verbose_name=_('Related Control/Document'),
        blank=True
    )
    risk_if_not_implemented = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
        default='medium',
        verbose_name=_('Risk Level')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Compliance Requirement')
        verbose_name_plural = _('Compliance Requirements')
        unique_together = ['framework', 'requirement_id']
        ordering = ['requirement_id']

    def __str__(self):
        return f"{self.requirement_id} - {self.title}"


class ImmutableAuditLog(models.Model):
    """
    Tamper-proof audit trail untuk compliance
    - Setiap log memiliki hash yang mencegah modifikasi
    - Chaining dengan log sebelumnya untuk deteksi manipulasi
    """
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('download', 'Download'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('approval', 'Approval'),
        ('rejection', 'Rejection'),
        ('access_granted', 'Access Granted'),
        ('access_revoked', 'Access Revoked'),
        ('config_change', 'Configuration Change'),
        ('security_event', 'Security Event'),
    ]

    # Core audit information
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        verbose_name=_('Action')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_('User'),
        related_name='compliance_audit_logs'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Timestamp'),
        db_index=True
    )
    
    # Object information
    content_type = models.CharField(
        max_length=100,
        verbose_name=_('Content Type'),
        help_text="e.g., Ticket, User, Incident"
    )
    object_id = models.CharField(
        max_length=100,
        verbose_name=_('Object ID')
    )
    object_repr = models.CharField(
        max_length=255,
        verbose_name=_('Object Representation')
    )
    
    # Change details
    changes_made = models.JSONField(
        verbose_name=_('Changes Made'),
        default=dict,
        blank=True,
        help_text="JSON format: {field: {old: value, new: value}}"
    )
    old_values = models.JSONField(
        verbose_name=_('Old Values'),
        default=dict,
        blank=True
    )
    new_values = models.JSONField(
        verbose_name=_('New Values'),
        default=dict,
        blank=True
    )
    
    # Request information
    ip_address = models.GenericIPAddressField(
        verbose_name=_('IP Address'),
        null=True,
        blank=True
    )
    user_agent = models.TextField(
        verbose_name=_('User Agent'),
        blank=True
    )
    
    # Compliance & Security
    severity = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
        default='low',
        verbose_name=_('Severity')
    )
    compliance_relevant = models.BooleanField(
        default=True,
        verbose_name=_('Compliance Relevant'),
        help_text="Is this log relevant for compliance/audit?"
    )
    
    # Tamper-proof hash chain
    data_hash = models.CharField(
        max_length=64,
        verbose_name=_('SHA-256 Hash'),
        editable=False,
        db_index=True
    )
    previous_hash = models.CharField(
        max_length=64,
        verbose_name=_('Previous Log Hash'),
        editable=False,
        blank=True
    )
    hash_chain_valid = models.BooleanField(
        default=True,
        verbose_name=_('Hash Chain Valid'),
        editable=False
    )
    
    # Metadata
    description = models.TextField(
        verbose_name=_('Description'),
        blank=True
    )
    reason = models.TextField(
        verbose_name=_('Reason for Action'),
        blank=True
    )
    approval_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending',
        verbose_name=_('Approval Status')
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_audit_logs',
        verbose_name=_('Approved By')
    )
    
    class Meta:
        verbose_name = _('Immutable Audit Log')
        verbose_name_plural = _('Immutable Audit Logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['severity', '-timestamp']),
        ]

    def save(self, *args, **kwargs):
        """Generate hash chain before saving"""
        if not self.pk:  # Only on creation
            # Get previous log for this user
            previous_log = ImmutableAuditLog.objects.filter(
                user=self.user
            ).order_by('-timestamp').first()
            
            self.previous_hash = previous_log.data_hash if previous_log else ''
            
            # Create data string for hashing
            data_to_hash = f"{self.user_id}{self.timestamp}{self.action}{self.content_type}{self.object_id}{self.previous_hash}"
            self.data_hash = hashlib.sha256(data_to_hash.encode()).hexdigest()
            
            # Verify chain is valid
            if previous_log:
                self.hash_chain_valid = previous_log.hash_chain_valid
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.action} - {self.object_repr} by {self.user} at {self.timestamp}"

    @classmethod
    def log_action(cls, user, action, content_type, object_id, object_repr, 
                  changes=None, ip_address=None, user_agent=None, severity='low',
                  description='', reason='', **kwargs):
        """
        Convenience method to create audit log
        """
        # Ensure non-nullable text fields are not passed as None
        if ip_address is None:
            ip_address = ''
        if user_agent is None:
            user_agent = ''

        return cls.objects.create(
            user=user,
            action=action,
            content_type=content_type,
            object_id=str(object_id),
            object_repr=str(object_repr),
            changes_made=changes or {},
            ip_address=ip_address,
            user_agent=user_agent,
            severity=severity,
            description=description,
            reason=reason,
            **kwargs
        )


class IncidentResponsePlan(models.Model):
    """
    Formal incident response procedures (ISO 27035, NIST IR)
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]

    SEVERITY_LEVELS = [
        ('low', 'Low - User Impact'),
        ('medium', 'Medium - Department Impact'),
        ('high', 'High - Multiple Departments'),
        ('critical', 'Critical - Enterprise Wide'),
    ]

    name = models.CharField(
        max_length=255,
        verbose_name=_('Plan Name')
    )
    description = models.TextField(
        verbose_name=_('Description')
    )
    incident_type = models.CharField(
        max_length=100,
        verbose_name=_('Incident Type'),
        help_text="e.g., Data Breach, System Outage, Security Attack"
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_LEVELS,
        verbose_name=_('Severity Level')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_('Status')
    )

    # Response procedures
    detection_procedures = models.TextField(
        verbose_name=_('Detection Procedures'),
        help_text="How to detect this type of incident"
    )
    initial_response = models.TextField(
        verbose_name=_('Initial Response'),
        help_text="Immediate actions to take"
    )
    escalation_path = models.TextField(
        verbose_name=_('Escalation Path'),
        help_text="Who to contact and in what order"
    )
    investigation_steps = models.TextField(
        verbose_name=_('Investigation Steps'),
        help_text="Step-by-step investigation procedures"
    )
    recovery_procedures = models.TextField(
        verbose_name=_('Recovery Procedures'),
        help_text="How to recover from incident"
    )
    communication_template = models.TextField(
        verbose_name=_('Communication Template'),
        blank=True,
        help_text="Template for incident notifications"
    )
    post_incident_review = models.TextField(
        verbose_name=_('Post-Incident Review'),
        blank=True,
        help_text="Lessons learned process"
    )

    # Contacts
    primary_contact = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='primary_incident_plans',
        verbose_name=_('Primary Contact')
    )
    secondary_contacts = models.TextField(
        verbose_name=_('Secondary Contacts'),
        blank=True,
        help_text="JSON list of contact details"
    )

    # Timeline
    sla_detection = models.DurationField(
        default=timedelta(minutes=15),
        verbose_name=_('SLA - Detection Time')
    )
    sla_response = models.DurationField(
        default=timedelta(minutes=30),
        verbose_name=_('SLA - Response Time')
    )
    sla_resolution = models.DurationField(
        default=timedelta(hours=4),
        verbose_name=_('SLA - Resolution Time')
    )

    # Version & approval
    version = models.IntegerField(
        default=1,
        verbose_name=_('Version')
    )
    last_reviewed = models.DateField(
        verbose_name=_('Last Reviewed'),
        auto_now=True
    )
    next_review_date = models.DateField(
        verbose_name=_('Next Review Date'),
        null=True,
        blank=True
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_incident_plans',
        verbose_name=_('Approved By')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Incident Response Plan')
        verbose_name_plural = _('Incident Response Plans')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} ({self.severity})"


class VulnerabilityTracking(models.Model):
    """
    Track vulnerabilities dan remediation (untuk NIST, ISO 27001)
    """
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('acknowledged', 'Acknowledged'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('accepted_risk', 'Accepted Risk'),
        ('closed', 'Closed'),
    ]

    vulnerability_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Vulnerability ID'),
        help_text="CVE, internal ID, or scan ID"
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('Title')
    )
    description = models.TextField(
        verbose_name=_('Description')
    )
    affected_system = models.CharField(
        max_length=255,
        verbose_name=_('Affected System/Component')
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        verbose_name=_('Severity')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        verbose_name=_('Status')
    )

    # Discovery
    discovery_date = models.DateField(
        verbose_name=_('Discovery Date'),
        auto_now_add=True
    )
    discovered_by = models.CharField(
        max_length=100,
        verbose_name=_('Discovered By'),
        help_text="Scanner, tool, or person name"
    )
    scan_tool = models.CharField(
        max_length=100,
        verbose_name=_('Scan Tool'),
        blank=True,
        help_text="e.g., Trivy, Bandit, Nessus"
    )
    cve_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('CVE Reference')
    )

    # Impact & Risk
    business_impact = models.TextField(
        verbose_name=_('Business Impact'),
        blank=True
    )
    remediation_effort = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium',
        verbose_name=_('Remediation Effort')
    )

    # Remediation
    remediation_plan = models.TextField(
        verbose_name=_('Remediation Plan'),
        blank=True
    )
    responsible_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vulnerabilities',
        verbose_name=_('Responsible Person')
    )
    target_remediation_date = models.DateField(
        verbose_name=_('Target Remediation Date'),
        null=True,
        blank=True
    )
    actual_remediation_date = models.DateField(
        verbose_name=_('Actual Remediation Date'),
        null=True,
        blank=True
    )

    # Risk Acceptance (if not fixing)
    risk_acceptance_justification = models.TextField(
        verbose_name=_('Risk Acceptance Justification'),
        blank=True,
        help_text="If accepting risk, explain why"
    )
    accepted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accepted_vulnerabilities',
        verbose_name=_('Accepted By')
    )
    acceptance_date = models.DateField(
        verbose_name=_('Acceptance Date'),
        null=True,
        blank=True
    )
    acceptance_expiry = models.DateField(
        verbose_name=_('Acceptance Expiry Date'),
        null=True,
        blank=True
    )

    # Notes
    internal_notes = models.TextField(
        verbose_name=_('Internal Notes'),
        blank=True
    )
    verification_steps = models.TextField(
        verbose_name=_('Verification Steps'),
        blank=True,
        help_text="How to verify the fix"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Vulnerability Tracking')
        verbose_name_plural = _('Vulnerability Tracking')
        ordering = ['-discovery_date']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['-discovery_date']),
        ]

    def __str__(self):
        return f"{self.vulnerability_id} - {self.title}"


class ComplianceCheckpoint(models.Model):
    """
    Regular compliance checkpoints & assessments
    """
    CHECKPOINT_TYPE = [
        ('quarterly', 'Quarterly Review'),
        ('annual', 'Annual Audit'),
        ('incident_review', 'Incident Review'),
        ('control_testing', 'Control Testing'),
        ('vulnerability_scan', 'Vulnerability Scan'),
        ('access_review', 'Access Review'),
        ('policy_review', 'Policy Review'),
        ('procedure_review', 'Procedure Review'),
    ]

    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed - Remediation Required'),
    ]

    checkpoint_type = models.CharField(
        max_length=50,
        choices=CHECKPOINT_TYPE,
        verbose_name=_('Checkpoint Type')
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('Checkpoint Name')
    )
    description = models.TextField(
        verbose_name=_('Description'),
        blank=True
    )
    frameworks = models.ManyToManyField(
        ComplianceFramework,
        verbose_name=_('Applicable Frameworks')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        verbose_name=_('Status')
    )

    # Scheduling
    planned_date = models.DateField(
        verbose_name=_('Planned Date')
    )
    actual_completion_date = models.DateField(
        verbose_name=_('Actual Completion Date'),
        null=True,
        blank=True
    )
    frequency = models.CharField(
        max_length=50,
        verbose_name=_('Frequency'),
        help_text="e.g., Quarterly, Annual, Monthly"
    )

    # Execution
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_checkpoints',
        verbose_name=_('Assigned To')
    )
    findings = models.TextField(
        verbose_name=_('Findings'),
        blank=True
    )
    issues_identified = models.IntegerField(
        default=0,
        verbose_name=_('Issues Identified')
    )
    issues_resolved = models.IntegerField(
        default=0,
        verbose_name=_('Issues Resolved')
    )

    # Results
    compliance_score = models.IntegerField(
        default=0,
        verbose_name=_('Compliance Score (%)'),
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    evidence_attached = models.URLField(
        verbose_name=_('Evidence Link'),
        blank=True,
        help_text="Link to detailed report/evidence"
    )
    remediation_required = models.BooleanField(
        default=False,
        verbose_name=_('Remediation Required')
    )
    remediation_deadline = models.DateField(
        verbose_name=_('Remediation Deadline'),
        null=True,
        blank=True
    )

    # Notes
    notes = models.TextField(
        verbose_name=_('Notes'),
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Compliance Checkpoint')
        verbose_name_plural = _('Compliance Checkpoints')
        ordering = ['-planned_date']

    def __str__(self):
        return f"{self.name} - {self.planned_date}"
