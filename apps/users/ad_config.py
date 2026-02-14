"""
Active Directory Configuration Model
"""
from django.db import models
from apps.core.models import TimeStampedModel, AuditModel


class ADConfiguration(AuditModel):
    """Active Directory sync configuration"""
    
    organization = models.OneToOneField(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='ad_configuration',
        help_text="One AD config per organization"
    )
    
    # Connection Settings
    server_name = models.CharField(
        max_length=255,
        help_text="AD Server hostname or IP (e.g., 192.168.1.10 or ad.company.local)"
    )
    server_port = models.IntegerField(
        default=389,
        help_text="LDAP port (389 for plain, 636 for SSL)"
    )
    use_ssl = models.BooleanField(
        default=False,
        help_text="Enable SSL/TLS for secure connection"
    )
    
    # Authentication
    bind_username = models.CharField(
        max_length=255,
        help_text="Service account username (e.g., CN=admin,DC=company,DC=com)"
    )
    bind_password = models.CharField(
        max_length=500,
        help_text="Service account password"
    )
    
    # Search Base
    search_base = models.CharField(
        max_length=255,
        help_text="Base DN for user search (e.g., OU=Users,DC=company,DC=com)"
    )
    search_filter = models.CharField(
        max_length=255,
        default='(objectClass=user)',
        help_text="LDAP filter for users (default: (objectClass=user))"
    )
    
    # Attribute Mapping
    username_attribute = models.CharField(
        max_length=50,
        default='sAMAccountName',
        help_text="AD attribute for username (typically sAMAccountName)"
    )
    email_attribute = models.CharField(
        max_length=50,
        default='mail',
        help_text="AD attribute for email (typically mail)"
    )
    first_name_attribute = models.CharField(
        max_length=50,
        default='givenName',
        help_text="AD attribute for first name (typically givenName)"
    )
    last_name_attribute = models.CharField(
        max_length=50,
        default='sn',
        help_text="AD attribute for last name (typically sn)"
    )
    phone_attribute = models.CharField(
        max_length=50,
        default='telephoneNumber',
        help_text="AD attribute for phone (typically telephoneNumber)"
    )
    
    # Group Mapping
    group_base = models.CharField(
        max_length=255,
        blank=True,
        help_text="Base DN for group search (e.g., OU=Groups,DC=company,DC=com)"
    )
    group_member_attribute = models.CharField(
        max_length=50,
        default='member',
        help_text="Attribute that contains group members (typically member or memberUid)"
    )
    
    # Sync Settings
    auto_create_users = models.BooleanField(
        default=True,
        help_text="Automatically create users found in AD"
    )
    auto_update_users = models.BooleanField(
        default=True,
        help_text="Automatically update user info from AD"
    )
    auto_disable_missing_users = models.BooleanField(
        default=False,
        help_text="Disable users not found in AD during sync"
    )
    
    # Status
    is_enabled = models.BooleanField(
        default=True,
        help_text="Enable/disable AD sync"
    )
    last_sync_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of last successful sync"
    )
    last_sync_status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('running', 'Running'),
            ('success', 'Success'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    last_sync_error = models.TextField(
        blank=True,
        help_text="Error message from last sync (if failed)"
    )
    
    class Meta:
        verbose_name = "AD Configuration"
        verbose_name_plural = "AD Configurations"
    
    def __str__(self):
        return f"AD Config - {self.organization.name}"
    
    @property
    def is_configured(self):
        """Check if AD is properly configured"""
        return bool(
            self.server_name and
            self.bind_username and
            self.bind_password and
            self.search_base
        )
    
    @property
    def connection_string(self):
        """Get LDAP connection string"""
        protocol = 'ldaps' if self.use_ssl else 'ldap'
        return f"{protocol}://{self.server_name}:{self.server_port}"
