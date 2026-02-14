"""
SLA background tasks.
"""
from celery import shared_task
from django.utils import timezone

from apps.sla.models import SLABreach
from apps.incidents.models import Incident
from apps.service_requests.models import ServiceRequest


@shared_task
def check_sla_breaches():
    now = timezone.now()
    breached_incidents = Incident.objects.filter(
        sla_due_date__isnull=False,
        sla_due_date__lt=now,
        sla_breach=False,
    )
    breached_requests = ServiceRequest.objects.filter(
        sla_due_date__isnull=False,
        sla_due_date__lt=now,
        sla_breach=False,
    )

    for incident in breached_incidents:
        incident.sla_breach = True
        incident.save(update_fields=["sla_breach"])
        duration_minutes = int((now - incident.sla_due_date).total_seconds() / 60)
        SLABreach.objects.get_or_create(
            organization=incident.organization,
            incident=incident,
            defaults={
                "sla_policy": incident.sla_policy,
                "breach_type": "resolution",
                "target_time": incident.sla_due_date,
                "breached_at": now,
                "breach_duration_minutes": max(duration_minutes, 0),
            },
        )

    for request in breached_requests:
        request.sla_breach = True
        request.save(update_fields=["sla_breach"])
        duration_minutes = int((now - request.sla_due_date).total_seconds() / 60)
        SLABreach.objects.get_or_create(
            organization=request.organization,
            service_request=request,
            defaults={
                "sla_policy": request.sla_policy,
                "breach_type": "resolution",
                "target_time": request.sla_due_date,
                "breached_at": now,
                "breach_duration_minutes": max(duration_minutes, 0),
            },
        )

    return {
        "incident_breaches": breached_incidents.count(),
        "service_request_breaches": breached_requests.count(),
    }


@shared_task
def send_sla_warnings():
    now = timezone.now()
    warning_window = now + timezone.timedelta(minutes=60)

    incident_due = Incident.objects.filter(
        sla_due_date__isnull=False,
        sla_due_date__lte=warning_window,
        sla_due_date__gte=now,
        sla_breach=False,
    ).count()
    request_due = ServiceRequest.objects.filter(
        sla_due_date__isnull=False,
        sla_due_date__lte=warning_window,
        sla_due_date__gte=now,
        sla_breach=False,
    ).count()

    return {
        "incident_warnings": incident_due,
        "service_request_warnings": request_due,
    }


@shared_task
def auto_escalate_tickets():
    """Auto-escalate tickets based on SLA escalation rules"""
    from datetime import timedelta
    from apps.sla.models import SLAEscalation
    from django.core.mail import send_mail

    now = timezone.now()
    processed = 0

    try:
        # Get all escalation rules
        escalations = SLAEscalation.objects.select_related(
            "sla_policy", "escalate_to_team", "escalate_to_user"
        )

        for escalation in escalations:
            # Find unresolved tickets matching this policy
            incidents = Incident.objects.filter(
                sla_policy=escalation.sla_policy,
                status__in=["new", "assigned", "pending"],
                created_at__lte=now
                - timedelta(minutes=escalation.escalate_after_minutes),
            )

            for incident in incidents:
                # Check if already escalated to this level
                escalation_level = getattr(incident, "escalation_level", 0)
                if escalation_level >= escalation.level:
                    continue

                # Perform escalation
                incident.escalation_level = escalation.level
                incident.escalated_at = now
                incident.priority = max(1, incident.priority - 1)  # Increase priority
                incident.save(
                    update_fields=["escalation_level", "escalated_at", "priority"]
                )

                # Send notification to escalation recipient
                if escalation.escalate_to_team or escalation.escalate_to_user:
                    subject = (
                        f"[ESCALATION] Incident #{incident.ticket_number} - "
                        f"Level {escalation.level}"
                    )
                    message = f"""
                    SLA Escalation Alert - Level {escalation.level}
                    
                    Incident: #{incident.ticket_number}
                    Title: {incident.title}
                    Priority: {incident.priority}
                    Created: {incident.created_at}
                    
                    Action Required: {escalation.action_description or "Manual intervention required"}
                    """

                    recipients = []
                    if escalation.escalate_to_user and escalation.escalate_to_user.email:
                        recipients.append(escalation.escalate_to_user.email)
                    if escalation.escalate_to_team:
                        team_members = escalation.escalate_to_team.members.values_list(
                            "email", flat=True
                        )
                        recipients.extend(team_members)

                    if escalation.notify_managers:
                        managers = (
                            incident.organization.users.filter(
                                role__in=["manager", "admin"]
                            ).values_list("email", flat=True)
                        )
                        recipients.extend(managers)

                    if recipients:
                        try:
                            send_mail(
                                subject=subject,
                                message=message,
                                from_email="noreply@itsm.local",
                                recipient_list=list(set(recipients)),
                                fail_silently=False,
                            )
                        except Exception as mail_error:
                            print(f"Failed to send escalation email: {mail_error}")

                processed += 1

        escalated_requests = ServiceRequest.objects.filter(
            sla_due_date__isnull=False,
            sla_due_date__lt=now,
            sla_breach=True,
        )

        for request in escalated_requests:
            request.priority = 1
            request.save(update_fields=["priority"])
            processed += 1

        return {
            "escalated_incidents": processed,
            "status": "completed",
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


@shared_task
def calculate_sla_compliance():
    """Calculate monthly SLA compliance metrics"""
    from datetime import datetime
    from django.db.models import Count

    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    try:
        from apps.organizations.models import Organization

        organizations = Organization.objects.all()
        calculated = 0

        for org in organizations:
            total_incidents = Incident.objects.filter(
                organization=org, created_at__gte=month_start
            ).count()

            breached_incidents = SLABreach.objects.filter(
                organization=org, created_at__gte=month_start
            ).values("incident").distinct().count()

            if total_incidents > 0:
                compliance = ((total_incidents - breached_incidents) / total_incidents) * 100
            else:
                compliance = 100.0

            from apps.sla.models import SLAMetric

            metric, created = SLAMetric.objects.update_or_create(
                organization=org,
                year=now.year,
                month=now.month,
                defaults={
                    "total_incidents": total_incidents,
                    "breached_incidents": breached_incidents,
                    "compliance_percentage": compliance,
                    "is_compliant": compliance >= 95.0,
                },
            )

            calculated += 1

        return {
            "calculated": calculated,
            "status": "completed",
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }
