"""
Celery configuration for ITSM project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_project.settings')

app = Celery('itsm_project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    # Check SLA breaches every 5 minutes
    'check-sla-breaches': {
        'task': 'apps.sla.tasks.check_sla_breaches',
        'schedule': crontab(minute='*/5'),
    },
    # Auto-escalate tickets every 10 minutes
    'auto-escalate-tickets': {
        'task': 'apps.tickets.tasks.auto_escalate_tickets',
        'schedule': crontab(minute='*/10'),
    },
    # Send SLA warning notifications every 15 minutes
    'send-sla-warnings': {
        'task': 'apps.sla.tasks.send_sla_warnings',
        'schedule': crontab(minute='*/15'),
    },
    # Generate daily reports at 6 AM
    'generate-daily-reports': {
        'task': 'apps.reports.tasks.generate_daily_reports',
        'schedule': crontab(hour=6, minute=0),
    },
    # Clean up old notifications daily at 2 AM
    'cleanup-old-notifications': {
        'task': 'apps.notifications.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=2, minute=0),
    },
    # Archive old tickets monthly on 1st at 3 AM
    'archive-old-tickets': {
        'task': 'apps.tickets.tasks.archive_old_tickets',
        'schedule': crontab(day_of_month=1, hour=3, minute=0),
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')
