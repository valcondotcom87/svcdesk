"""
Core Models - Base models for inheritance
"""
import uuid
from django.db import models
from django.utils import timezone


class UUIDModel(models.Model):
    """
    Base model with UUID primary key
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    class Meta:
        abstract = True


class TimeStampedModel(UUIDModel):
    """
    Base model with created_at and updated_at timestamps
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteModel(TimeStampedModel):
    """
    Base model with soft delete functionality
    """
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True
    )
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """
        Soft delete - set deleted_at instead of actually deleting
        """
        self.deleted_at = timezone.now()
        self.save(using=using)
    
    def hard_delete(self):
        """
        Actually delete the record from database
        """
        super().delete()
    
    def restore(self):
        """
        Restore soft-deleted record
        """
        self.deleted_at = None
        self.save()


class AuditModel(SoftDeleteModel):
    """
    Base model with audit fields (created_by, updated_by)
    """
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        db_index=True
    )
    updated_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'
    )
    
    class Meta:
        abstract = True
