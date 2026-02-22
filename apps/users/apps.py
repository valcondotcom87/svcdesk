"""
Users App Configuration
"""
import os
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Users'

    def ready(self):
        if os.getenv('AD_SYNC_ENABLED', 'False') != 'True':
            return

        try:
            from django_celery_beat.models import CrontabSchedule, PeriodicTask
        except Exception:
            return

        cron_expr = os.getenv('AD_SYNC_CRON', '0 * * * *')
        parts = cron_expr.split()
        if len(parts) != 5:
            return

        minute, hour, day_of_month, month_of_year, day_of_week = parts
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=minute,
            hour=hour,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
            day_of_week=day_of_week,
        )

        PeriodicTask.objects.update_or_create(
            name='AD Sync Users',
            defaults={
                'crontab': schedule,
                'task': 'apps.users.tasks.sync_ad_users',
                'enabled': True,
            },
        )
