# Django Settings Configuration for Compliance Module
# Add these settings to your Django settings.py file

"""
=== COMPLIANCE APP CONFIGURATION ===

Add to INSTALLED_APPS:
"""
INSTALLED_APPS = [
    # ... other apps ...
    'apps.compliance',
]

"""
=== DATABASE CONFIGURATION FOR AUDIT LOGGING ===

The compliance module requires a PostgreSQL database with proper indexing.
Ensure your database is configured for:
1. High-frequency write operations (audit logging)
2. Efficient querying with indexes
3. Optional: Table partitioning for audit logs older than 1 year
"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'itsm_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
        # Optional: Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

"""
=== SECURITY SETTINGS FOR COMPLIANCE ===
"""

# 1. ENCRYPTION AT REST
# Enable database-level encryption (PostgreSQL pgcrypto extension)
# psql> CREATE EXTENSION pgcrypto;

# 2. AUDIT LOG SETTINGS
COMPLIANCE_AUDIT_LOG_RETENTION_DAYS = 2555  # ~7 years for regulatory compliance
COMPLIANCE_AUDIT_LOG_BATCH_SIZE = 1000  # Batch size for audit log processing

# 3. IMMUTABLE LOG HASH CHAIN
COMPLIANCE_HASH_ALGORITHM = 'sha256'  # Use SHA-256 for hash chain
COMPLIANCE_VERIFY_HASH_CHAIN = True  # Verify chain integrity on retrieval

# 4. INCIDENT RESPONSE
COMPLIANCE_INCIDENT_ESCALATION_EMAIL = 'security-team@company.com'
COMPLIANCE_INCIDENT_CRITICAL_RESPONSE_SLA_MINUTES = 15
COMPLIANCE_INCIDENT_NORMAL_RESPONSE_SLA_MINUTES = 30

# 5. VULNERABILITY MANAGEMENT
COMPLIANCE_VULNERABILITY_SCAN_FREQUENCY = 'daily'  # daily, weekly, monthly
COMPLIANCE_VULNERABILITY_CRITICAL_REMEDIATION_DAYS = 3
COMPLIANCE_VULNERABILITY_HIGH_REMEDIATION_DAYS = 14
COMPLIANCE_VULNERABILITY_MEDIUM_REMEDIATION_DAYS = 30
COMPLIANCE_VULNERABILITY_LOW_REMEDIATION_DAYS = 90

# 6. COMPLIANCE CHECKPOINT
COMPLIANCE_CHECKPOINT_MINIMUM_SCORE = 80  # Minimum compliance score
COMPLIANCE_AUTO_SCHEDULE_QUARTERLY_CHECKPOINTS = True

"""
=== LOGGING CONFIGURATION ===
Configure Python logging for compliance module
"""

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/compliance.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/audit.log',
            'maxBytes': 1024 * 1024 * 50,  # 50MB
            'backupCount': 30,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'apps.compliance': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps.compliance.audit': {
            'handlers': ['audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

"""
=== MIDDLEWARE CONFIGURATION ===
Add compliance middleware for request/response logging
"""

MIDDLEWARE = [
    # ... other middleware ...
    'apps.compliance.middleware.AuditLoggingMiddleware',
]

"""
=== CELERY CONFIGURATION FOR ASYNC COMPLIANCE TASKS ===
Optional: For background compliance checks and reports
"""

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Compliance periodic tasks
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'check-compliance-status': {
        'task': 'apps.compliance.tasks.check_compliance_status',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    'verify-audit-chain': {
        'task': 'apps.compliance.tasks.verify_audit_chain_integrity',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'generate-compliance-report': {
        'task': 'apps.compliance.tasks.generate_monthly_report',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),  # 1st of month at midnight
    },
}

"""
=== REST FRAMEWORK CONFIGURATION ===
"""

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'compliance_audit': '10000/hour',  # Higher limit for audit logging
    }
}

"""
=== CORS CONFIGURATION ===
If using with separate frontend
"""

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://company.com",
]

"""
=== EMAIL CONFIGURATION FOR ALERTS ===
"""

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'

# Compliance alert emails
COMPLIANCE_ALERTS_EMAIL = 'compliance-alerts@company.com'
COMPLIANCE_CRITICAL_ALERT_RECIPIENTS = [
    'ciso@company.com',
    'compliance-officer@company.com',
]

"""
=== COMPLIANCE STANDARDS CONFIGURATION ===
Define which standards your organization complies with
"""

COMPLIANCE_FRAMEWORKS = {
    'ISO27001': {
        'name': 'ISO/IEC 27001:2022',
        'enabled': True,
        'audit_frequency': 'quarterly',
        'assessment_required': True,
    },
    'NIST_CSF': {
        'name': 'NIST Cybersecurity Framework',
        'enabled': True,
        'audit_frequency': 'quarterly',
        'assessment_required': True,
    },
    'GDPR': {
        'name': 'General Data Protection Regulation',
        'enabled': True,
        'audit_frequency': 'annual',
        'assessment_required': True,
    },
    'SOC2': {
        'name': 'System and Organization Controls 2',
        'enabled': True,
        'audit_frequency': 'annual',
        'assessment_required': True,
    },
    'ISO20000': {
        'name': 'ISO/IEC 20000 IT Service Management',
        'enabled': True,
        'audit_frequency': 'annual',
        'assessment_required': True,
    },
    'HIPAA': {
        'name': 'Health Insurance Portability and Accountability Act',
        'enabled': False,  # Enable if applicable
    },
}

"""
=== URLS CONFIGURATION ===
Add to main urls.py:

from django.urls import path, include

urlpatterns = [
    # ... other patterns ...
    path('api/compliance/', include('apps.compliance.urls')),
]
"""

"""
=== ENVIRONMENT VARIABLES ===
Set these in your .env file or environment:

DJANGO_SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=*.company.com
DATABASE_URL=postgresql://user:password@localhost:5432/itsm_db
COMPLIANCE_AUDIT_LOG_RETENTION_DAYS=2555
COMPLIANCE_HASH_ALGORITHM=sha256
COMPLIANCE_INCIDENT_ESCALATION_EMAIL=security@company.com
"""
