from django.db import models
from apps.core.models import AuditModel


class KnowledgeArticle(AuditModel):
    """Knowledge base article with lifecycle status."""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
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
        related_name='knowledge_articles'
    )
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    content = models.TextField()
    category = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_articles'
    )
    tags = models.TextField(blank=True)
    csf_function = models.CharField(
        max_length=20,
        choices=CSF_FUNCTION_CHOICES,
        default='identify'
    )
    csf_category = models.CharField(max_length=100, blank=True)
    iso_control = models.CharField(max_length=100, blank=True)
    nist_control = models.CharField(max_length=100, blank=True)
    review_notes = models.TextField(blank=True)
    version = models.IntegerField(default=1)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'category']),
            models.Index(fields=['-updated_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.status})"
