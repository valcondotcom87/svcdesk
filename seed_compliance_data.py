#!/usr/bin/env python
"""
Seed compliance data aligned to current compliance models.
"""
import os
from datetime import datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "itsm_project.settings")

import django

django.setup()

from apps.compliance.models import (
    ComplianceFramework,
    ComplianceRequirement,
    IncidentResponsePlan,
    VulnerabilityTracking,
    ComplianceCheckpoint,
)
from apps.organizations.models import Organization
from apps.users.models import User


def get_or_create_org():
    org, _ = Organization.objects.get_or_create(
        slug="main-org",
        defaults={
            "name": "Main Organization",
            "description": "Primary organization for compliance management",
            "email": "compliance@main.local",
            "phone": "+62-21-555-0102",
            "address": "Jakarta",
            "city": "Jakarta",
            "country": "Indonesia",
            "subscription_tier": "enterprise",
        },
    )
    return org


def get_admin_user():
    admin = User.objects.filter(email="admin@itsm.local").first()
    if not admin:
        admin = User.objects.create_superuser(
            email="admin@itsm.local",
            username="admin",
            password="admin123456",
            first_name="Admin",
            last_name="User",
        )
    return admin


def seed_frameworks(org, admin):
    frameworks = [
        {
            "framework": "ISO27001",
            "description": "Information Security Management System",
            "version": "2022",
            "status": "in_progress",
        },
        {
            "framework": "ISO20000",
            "description": "IT Service Management System",
            "version": "2018",
            "status": "in_progress",
        },
        {
            "framework": "ISO9001",
            "description": "Quality Management System",
            "version": "2015",
            "status": "planned",
        },
        {
            "framework": "SOC2",
            "description": "Service Organization Control 2",
            "version": "Type II",
            "status": "planned",
        },
        {
            "framework": "GDPR",
            "description": "General Data Protection Regulation",
            "version": "2016",
            "status": "in_progress",
        },
    ]

    created = 0
    framework_objs = {}
    for entry in frameworks:
        obj, is_new = ComplianceFramework.objects.get_or_create(
            framework=entry["framework"],
            defaults={
                "description": entry["description"],
                "version": entry["version"],
                "status": entry["status"],
                "organization": org,
                "responsible_person": admin,
                "progress_percentage": 0,
            },
        )
        framework_objs[entry["framework"]] = obj
        if is_new:
            created += 1
            print(f"Created framework: {obj.get_framework_display()}")
        else:
            print(f"Framework exists: {obj.get_framework_display()}")

    return framework_objs, created


def seed_requirements(frameworks, admin):
    requirements = {
        "ISO27001": [
            ("A.5.1", "Information security policies"),
            ("A.5.15", "Access control"),
            ("A.8.24", "Cryptography"),
        ],
        "ISO20000": [
            ("8.2", "Incident management"),
            ("8.5", "Change enablement"),
            ("8.6", "Service level management"),
        ],
        "ISO9001": [
            ("7.5", "Documented information"),
            ("9.1", "Monitoring, measurement, analysis"),
        ],
        "SOC2": [
            ("CC6.1", "Logical access controls"),
            ("CC7.2", "Security incident response"),
        ],
        "GDPR": [
            ("Art.32", "Security of processing"),
            ("Art.33", "Breach notification"),
        ],
    }

    created = 0
    for fw_key, req_list in requirements.items():
        framework = frameworks.get(fw_key)
        if not framework:
            continue
        for req_id, title in req_list:
            req, is_new = ComplianceRequirement.objects.get_or_create(
                framework=framework,
                requirement_id=req_id,
                defaults={
                    "title": title,
                    "description": f"Requirement for {framework.get_framework_display()}: {title}",
                    "status": "not_started",
                    "responsible_person": admin,
                    "due_date": datetime.utcnow().date() + timedelta(days=90),
                    "risk_if_not_implemented": "high",
                },
            )
            if is_new:
                created += 1
                print(f"Added requirement: {req.requirement_id} - {req.title}")
    return created


def seed_incident_plans(admin):
    plans = [
        {
            "name": "Data Breach Response",
            "description": "Response plan for data breaches",
            "incident_type": "Data Breach",
            "severity": "critical",
        },
        {
            "name": "Service Outage Response",
            "description": "Response plan for major service outages",
            "incident_type": "System Outage",
            "severity": "high",
        },
    ]

    created = 0
    for plan in plans:
        obj, is_new = IncidentResponsePlan.objects.get_or_create(
            name=plan["name"],
            defaults={
                "description": plan["description"],
                "incident_type": plan["incident_type"],
                "severity": plan["severity"],
                "status": "active",
                "detection_procedures": "Monitor alerts and SIEM notifications.",
                "initial_response": "Triage, contain, and notify stakeholders.",
                "escalation_path": "SOC -> IT Manager -> Executive",
                "investigation_steps": "Collect logs, identify root cause, validate scope.",
                "recovery_procedures": "Restore services and validate integrity.",
                "post_incident_review": "Conduct PIR within 5 business days.",
                "primary_contact": admin,
            },
        )
        if is_new:
            created += 1
            print(f"Created incident response plan: {obj.name}")
    return created


def seed_vulnerabilities(admin):
    vulns = [
        {
            "vulnerability_id": "VULN-1001",
            "title": "Unpatched web server",
            "description": "Critical patch missing on public web server.",
            "affected_system": "Web Server Cluster",
            "severity": "critical",
            "discovered_by": "Nessus",
        },
        {
            "vulnerability_id": "VULN-1002",
            "title": "Weak password policy",
            "description": "Password policy does not meet compliance baseline.",
            "affected_system": "Identity Service",
            "severity": "high",
            "discovered_by": "Internal audit",
        },
    ]

    created = 0
    for item in vulns:
        obj, is_new = VulnerabilityTracking.objects.get_or_create(
            vulnerability_id=item["vulnerability_id"],
            defaults={
                "title": item["title"],
                "description": item["description"],
                "affected_system": item["affected_system"],
                "severity": item["severity"],
                "status": "open",
                "discovered_by": item["discovered_by"],
                "remediation_effort": "high" if item["severity"] == "critical" else "medium",
                "responsible_person": admin,
                "target_remediation_date": datetime.utcnow().date() + timedelta(days=45),
                "business_impact": "Potential service disruption and compliance risk.",
            },
        )
        if is_new:
            created += 1
            print(f"Created vulnerability: {obj.vulnerability_id}")
    return created


def seed_checkpoints(frameworks, admin):
    checkpoints = [
        {
            "checkpoint_type": "quarterly",
            "name": "Q1 Security Audit",
            "description": "Quarterly security audit and assessment",
            "frameworks": ["ISO27001", "SOC2"],
            "planned_date": datetime.utcnow().date() + timedelta(days=45),
            "frequency": "Quarterly",
        },
        {
            "checkpoint_type": "annual",
            "name": "Annual Compliance Review",
            "description": "Annual compliance review",
            "frameworks": ["ISO20000", "ISO9001"],
            "planned_date": datetime.utcnow().date() + timedelta(days=120),
            "frequency": "Annual",
        },
        {
            "checkpoint_type": "vulnerability_scan",
            "name": "Vulnerability Assessment",
            "description": "Regular vulnerability scanning",
            "frameworks": ["ISO27001", "GDPR"],
            "planned_date": datetime.utcnow().date() + timedelta(days=30),
            "frequency": "Monthly",
        },
    ]

    created = 0
    for entry in checkpoints:
        obj, is_new = ComplianceCheckpoint.objects.get_or_create(
            checkpoint_type=entry["checkpoint_type"],
            name=entry["name"],
            planned_date=entry["planned_date"],
            defaults={
                "description": entry["description"],
                "frequency": entry["frequency"],
                "status": "planned",
                "assigned_to": admin,
                "compliance_score": 0,
            },
        )
        if is_new:
            created += 1
            print(f"Created checkpoint: {obj.name}")
        obj.frameworks.set([
            frameworks[key]
            for key in entry["frameworks"]
            if key in frameworks
        ])
    return created


def main():
    print("Starting compliance data seeding...\n")

    org = get_or_create_org()
    admin = get_admin_user()

    framework_map, fw_created = seed_frameworks(org, admin)
    req_created = seed_requirements(framework_map, admin)
    plan_created = seed_incident_plans(admin)
    vuln_created = seed_vulnerabilities(admin)
    checkpoint_created = seed_checkpoints(framework_map, admin)

    total_created = fw_created + req_created + plan_created + vuln_created + checkpoint_created

    print("\nSeeding summary:")
    print(f"  Frameworks created: {fw_created}")
    print(f"  Requirements created: {req_created}")
    print(f"  Incident plans created: {plan_created}")
    print(f"  Vulnerabilities created: {vuln_created}")
    print(f"  Checkpoints created: {checkpoint_created}")
    print(f"\nTotal new records: {total_created}")


if __name__ == "__main__":
    main()
