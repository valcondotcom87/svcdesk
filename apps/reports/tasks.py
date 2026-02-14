"""
Report generation tasks.
"""
from celery import shared_task
from django.utils import timezone

from apps.reports.models import Report, ReportExecution


@shared_task
def generate_daily_reports():
    now = timezone.now()
    reports = Report.objects.filter(is_active=True, frequency="daily")
    created = 0

    for report in reports:
        ReportExecution.objects.create(
            report=report,
            executed_at=now,
            data_json={},
        )
        created += 1

    return {"created": created}
