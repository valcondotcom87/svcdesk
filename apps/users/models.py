"""
Users Models - Custom User Model with RBAC
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from apps.core.models import UUIDModel, TimeStampedModel


class UserManager(BaseUserManager):
    """
    Custom user manager
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user
        """
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class Organization(TimeStampedModel):
    """
    Organization model for multi-tenancy
    """
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=100, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    settings = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'organizations'
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class User(TimeStampedModel, AbstractBaseUser, PermissionsMixin):
    """
    Custom User model
    """
    ROLE_CHOICES = [
        ('end_user', 'End User'),
        ('agent', 'Agent'),
        ('manager', 'Manager'),
        ('admin', 'Administrator'),
    ]
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='end_user')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # MFA
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=255, blank=True)
    
    # Security
    last_login = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between
        """
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username
    
    def get_short_name(self):
        """
        Return the short name for the user
        """
        return self.first_name or self.username
    
    def is_locked(self):
        """
        Check if user account is locked
        """
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False
    
    def lock_account(self, duration_minutes=30):
        """
        Lock user account for specified duration
        """
        self.locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save(update_fields=['locked_until'])
    
    def unlock_account(self):
        """
        Unlock user account
        """
        self.locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['locked_until', 'failed_login_attempts'])


class Team(TimeStampedModel):
    """
    Team model for grouping users
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='teams'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    team_lead = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_teams'
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'teams'
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TeamMember(UUIDModel):
    """
    Team membership model
    """
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('lead', 'Team Lead'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'team_members'
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'
        unique_together = ['team', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.team.name}"


class Role(TimeStampedModel):
    """
    Role model for RBAC
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=list)
    is_system_role = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserRole(UUIDModel):
    """
    User-Role assignment model
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_users')
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles'
    )
    
    class Meta:
        db_table = 'user_roles'
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        unique_together = ['user', 'role']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role.name}"
