import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "itsm_project.settings")

import django

django.setup()

from django.db.models.signals import post_delete
from django.apps import apps as django_apps
from apps.organizations.models import Organization as OrgsOrganization
from apps.users.models import User as UsersUser, Organization as UsersOrganization
from apps.knowledge.models import KnowledgeArticle
from apps.compliance.signals import log_user_deletion, log_incident_deletion
from apps.incidents.models import Incident
from apps.service_requests.models import ServiceRequest, ServiceCategory, Service
from apps.changes.models import Change
from apps.cmdb.models import ConfigurationItem, CICategory
from apps.assets.models import AssetCategory, Asset
from apps.workflows.models import Workflow, WorkflowStep
from apps.organizations.models import Department, DepartmentMember
from apps.sla.models import SLAPolicy, SLATarget


def cleanup_demo_records():
    demo_emails = ["enduser@itsm.local", "engineer@itsm.local"]
    demo_usernames = ["enduser", "engineer"]

    demo_users = UsersUser.objects.filter(email__in=demo_emails) | UsersUser.objects.filter(username__in=demo_usernames)
    demo_user_ids = list(demo_users.values_list("id", flat=True))
    demo_org = OrgsOrganization.objects.filter(slug="demo-org").first()

    deleted_audit_logs = []
    if demo_user_ids:
        for model in django_apps.get_models():
            if model._meta.app_label in ("audit", "audit_logs", "compliance") or model.__name__ in ("ImmutableAuditLog", "AuditLog"):
                field_names = {field.name for field in model._meta.fields}
                if "user" in field_names:
                    deleted_audit_logs.append((model.__name__, model.objects.filter(user_id__in=demo_user_ids).delete()))

    previous_receivers = list(post_delete.receivers)
    post_delete.receivers.clear()
    deleted_users = demo_users.delete()
    post_delete.receivers = previous_receivers

    deleted_orgs = None
    deleted_users_org = None
    if demo_org:
        deleted_incidents = Incident.objects.filter(ticket_number__in=[
            "INC-1001",
            "INC-1002",
            "INC-1003",
            "INC-1004",
            "INC-1005",
        ]).delete()
        deleted_service_requests = ServiceRequest.objects.filter(ticket_number__in=[
            "SR-2001",
            "SR-2002",
            "SR-2003",
        ]).delete()
        deleted_services = Service.objects.filter(name__in=[
            "Account Reset",
            "Laptop Provision",
            "VPN Setup",
            "Email Setup",
        ]).delete()
        deleted_service_categories = ServiceCategory.objects.filter(name__in=[
            "IT Services",
            "Hardware",
            "Software",
            "Network",
        ]).delete()
        deleted_cis = ConfigurationItem.objects.filter(ci_number__in=[
            "CI-1001",
            "CI-1002",
            "CI-1003",
            "CI-1004",
        ]).delete()
        deleted_ci_categories = CICategory.objects.filter(name="Servers", organization=demo_org).delete()
        deleted_assets = Asset.objects.filter(asset_tag__in=[
            "AST-LAP-001",
            "AST-SRV-002",
            "AST-NET-003",
            "AST-SEC-004",
        ]).delete()
        deleted_asset_categories = AssetCategory.objects.filter(name__in=[
            "Laptop",
            "Server",
            "Network",
            "Security",
        ]).delete()
        deleted_changes = Change.objects.filter(ticket_number__in=[
            "CHG-3001",
            "CHG-3002",
            "CHG-3003",
        ]).delete()
        deleted_workflow_steps = WorkflowStep.objects.filter(workflow__organization=demo_org).delete()
        deleted_workflows = Workflow.objects.filter(organization=demo_org).delete()
        deleted_department_members = DepartmentMember.objects.filter(department__organization=demo_org).delete()
        deleted_departments = Department.objects.filter(organization=demo_org).delete()
        deleted_sla_targets = SLATarget.objects.filter(sla_policy__organization=demo_org).delete()
        deleted_sla_policies = SLAPolicy.objects.filter(organization=demo_org, name="Standard SLA").delete()

        print("Deleted demo incidents:", deleted_incidents)
        print("Deleted demo service requests:", deleted_service_requests)
        print("Deleted demo services:", deleted_services)
        print("Deleted demo service categories:", deleted_service_categories)
        print("Deleted demo configuration items:", deleted_cis)
        print("Deleted demo CI categories:", deleted_ci_categories)
        print("Deleted demo assets:", deleted_assets)
        print("Deleted demo asset categories:", deleted_asset_categories)
        print("Deleted demo changes:", deleted_changes)
        print("Deleted demo workflow steps:", deleted_workflow_steps)
        print("Deleted demo workflows:", deleted_workflows)
        print("Deleted demo department members:", deleted_department_members)
        print("Deleted demo departments:", deleted_departments)
        print("Deleted demo SLA targets:", deleted_sla_targets)
        print("Deleted demo SLA policies:", deleted_sla_policies)

    demo_users_org = UsersOrganization.objects.filter(domain="demo-org").first()
    if demo_users_org:
        non_demo_users = UsersUser.objects.filter(organization=demo_users_org).exclude(
            email__in=demo_emails
        )
        if non_demo_users.exists():
            print("Skipped deleting users organization due to non-demo users.")
        else:
            deleted_users_org = demo_users_org.delete()

    if demo_org:
        deleted_orgs = demo_org.delete()

    deleted_articles = KnowledgeArticle.objects.filter(
        title__in=[
            "VPN Onboarding Guide",
            "Email Performance Tuning",
        ]
    ).delete()

    print("Deleted demo audit logs:", deleted_audit_logs)
    print("Deleted demo users:", deleted_users)
    print("Deleted demo users org:", deleted_users_org)
    print("Deleted demo orgs:", deleted_orgs)
    print("Deleted demo knowledge articles:", deleted_articles)


if __name__ == "__main__":
    cleanup_demo_records()
    print("Demo data cleanup complete.")
