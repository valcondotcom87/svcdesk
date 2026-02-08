from django.apps import AppConfig


class ComplianceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.compliance'
    verbose_name = 'Compliance Management'

    def ready(self):
        """Initialize compliance signals when app is ready"""
        import apps.compliance.signals  # noqa: F401
