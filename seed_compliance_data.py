#!/usr/bin/env python
"""
Seed compliance data with realistic frameworks, requirements, and sample data
"""
import os
import django
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_project.settings')
django.setup()

from apps.compliance.models import (
    ComplianceFramework,
    ComplianceRequirement,
    IncidentResponsePlan,
    VulnerabilityTracking,
    ComplianceCheckpoint
)
from apps.users.models import User, Organization

def create_sample_data():
    """Create sample compliance data"""
    
    # Ensure organization exists
    org, created = Organization.objects.get_or_create(
        name='Main Organization',
        defaults={
            'slug': 'main-organization',
            'description': 'Primary organization for compliance management',
            'email': 'compliance@main.local',
            'is_active': True,
            'subscription_tier': 'enterprise'
        }
    )
    if created:
        print(f"Created organization: {org.name}")
    
    # Ensure admin user exists
    admin, _ = User.objects.get_or_create(
        email='admin@itsm.local',
        defaults={
            'username': 'admin',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
            'organization': org
        }
    )
    
    frameworks_data = [
        {
            'name': 'ISO 27001',
            'description': 'Information Security Management System (ISMS) - International standard',
            'version': '2022',
            'compliance_level': 'HIGH',
            'owner': admin,
            'organization': org,
            'requirements_data': [
                {'name': 'Information security policies', 'description': 'Define and implement information security policies'},
                {'name': 'Access control', 'description': 'Implement least privilege and access controls'},
                {'name': 'Cryptography', 'description': 'Protect sensitive data with encryption'},
                {'name': 'Physical security', 'description': 'Control physical access to facilities'},
                {'name': 'Incident management', 'description': 'Establish incident response procedures'},
            ]
        },
        {
            'name': 'PCI-DSS',
            'description': 'Payment Card Industry Data Security Standard - Protect cardholder data',
            'version': '3.2.1',
            'compliance_level': 'CRITICAL',
            'owner': admin,
            'organization': org,
            'requirements_data': [
                {'name': 'Network security', 'description': 'Install and maintain firewall configuration'},
                {'name': 'Cardholder data protection', 'description': 'Protect stored cardholder data'},
                {'name': 'Vulnerability management', 'description': 'Maintain secure systems and networks'},
                {'name': 'Access control', 'description': 'Restrict access by business need'},
                {'name': 'Monitoring and testing', 'description': 'Regularly test security systems'},
            ]
        },
        {
            'name': 'HIPAA',
            'description': 'Health Insurance Portability and Accountability Act - Protect PHI',
            'version': '2013',
            'compliance_level': 'CRITICAL',
            'owner': admin,
            'organization': org,
            'requirements_data': [
                {'name': 'Administrative safeguards', 'description': 'Implement administrative security measures'},
                {'name': 'Physical safeguards', 'description': 'Protect facilities and devices'},
                {'name': 'Technical safeguards', 'description': 'Implement technical security measures'},
                {'name': 'Breach notification', 'description': 'Report security breaches appropriately'},
                {'name': 'Audit controls', 'description': 'Record and examine activity'},
            ]
        },
        {
            'name': 'GDPR',
            'description': 'General Data Protection Regulation - Protect personal data',
            'version': '2016',
            'compliance_level': 'HIGH',
            'owner': admin,
            'organization': org,
            'requirements_data': [
                {'name': 'Data protection officer', 'description': 'Appoint DPO if required'},
                {'name': 'Data minimization', 'description': 'Collect only necessary data'},
                {'name': 'Data subject rights', 'description': 'Provide access and deletion rights'},
                {'name': 'Privacy by design', 'description': 'Implement privacy in system design'},
                {'name': 'Data protection impact', 'description': 'Conduct DPIA for high-risk processing'},
            ]
        },
        {
            'name': 'SOC 2',
            'description': 'Service Organization Control 2 - Security, availability, integrity',
            'version': 'Type II',
            'compliance_level': 'MEDIUM',
            'owner': admin,
            'organization': org,
            'requirements_data': [
                {'name': 'Security controls', 'description': 'Implement security controls'},
                {'name': 'Availability', 'description': 'Ensure system availability'},
                {'name': 'Processing integrity', 'description': 'Ensure accurate data processing'},
                {'name': 'Confidentiality', 'description': 'Protect confidential information'},
                {'name': 'Audit and monitoring', 'description': 'Maintain audit logs'},
            ]
        }
    ]
    
    created_count = 0
    for fw_data in frameworks_data:
        requirements_data = fw_data.pop('requirements_data')
        
        framework, created = ComplianceFramework.objects.get_or_create(
            name=fw_data['name'],
            organization=fw_data['organization'],
            defaults=fw_data
        )
        
        if created:
            created_count += 1
            print(f"Created framework: {framework.name}")
            
            # Create requirements for this framework
            for req_data in requirements_data:
                requirement, _ = ComplianceRequirement.objects.get_or_create(
                    framework=framework,
                    name=req_data['name'],
                    defaults={
                        'description': req_data['description'],
                        'status': 'PENDING',
                        'priority': 'HIGH' if framework.compliance_level in ['CRITICAL', 'HIGH'] else 'MEDIUM',
                        'owner': admin,
                        'target_date': datetime.now() + timedelta(days=90),
                        'compliance_percentage': 0
                    }
                )
                if _:
                    print(f"  - Added requirement: {requirement.name}")
    
    # Create incident response plans
    irp_data = [
        {
            'name': 'Data Breach Response',
            'description': 'Procedure for responding to data breaches',
            'framework': ComplianceFramework.objects.filter(name='ISO 27001').first(),
        },
        {
            'name': 'Ransomware Response',
            'description': 'Procedure for responding to ransomware attacks',
            'framework': ComplianceFramework.objects.filter(name='PCI-DSS').first(),
        },
        {
            'name': 'PHI Breach Response',
            'description': 'Procedure for PHI security breaches',
            'framework': ComplianceFramework.objects.filter(name='HIPAA').first(),
        }
    ]
    
    for irp in irp_data:
        plan, created = IncidentResponsePlan.objects.get_or_create(
            name=irp['name'],
            framework=irp['framework'],
            defaults={
                'description': irp['description'],
                'owner': admin,
                'status': 'ACTIVE',
                'response_time_hours': 4,
                'escalation_contacts': 'security-team@company.com, ciso@company.com'
            }
        )
        if created:
            created_count += 1
            print(f"Created incident plan: {plan.name}")
    
    # Create vulnerability tracking
    vuln_data = [
        {
            'title': 'Unpatched Windows Server',
            'description': 'Multiple servers missing critical security patches',
            'severity': 'CRITICAL',
            'framework': ComplianceFramework.objects.filter(name='PCI-DSS').first(),
        },
        {
            'title': 'Weak password policy',
            'description': 'Password policy does not meet HIPAA requirements',
            'severity': 'HIGH',
            'framework': ComplianceFramework.objects.filter(name='HIPAA').first(),
        },
        {
            'title': 'Missing encryption',
            'description': 'Database encryption not enabled for sensitive data',
            'severity': 'HIGH',
            'framework': ComplianceFramework.objects.filter(name='ISO 27001').first(),
        }
    ]
    
    for vuln in vuln_data:
        vulnerability, created = VulnerabilityTracking.objects.get_or_create(
            title=vuln['title'],
            framework=vuln['framework'],
            defaults={
                'description': vuln['description'],
                'severity': vuln['severity'],
                'status': 'OPEN',
                'owner': admin,
                'found_date': datetime.now() - timedelta(days=30),
                'target_remediation_date': datetime.now() + timedelta(days=60),
                'remediation_cost': Decimal('5000.00') if vuln['severity'] == 'CRITICAL' else Decimal('2000.00')
            }
        )
        if created:
            created_count += 1
            print(f"Created vulnerability: {vulnerability.title}")
    
    # Create compliance checkpoints
    checkpoint_data = [
        {
            'name': 'Q1 Security Audit',
            'description': 'Quarterly security audit and assessment',
            'requirement': ComplianceRequirement.objects.filter(name='Access control').first(),
            'scheduled_date': datetime.now() + timedelta(days=45),
        },
        {
            'name': 'Annual Compliance Review',
            'description': 'Annual comprehensive compliance review',
            'requirement': ComplianceRequirement.objects.filter(name='Audit controls').first(),
            'scheduled_date': datetime.now() + timedelta(days=180),
        },
        {
            'name': 'Vulnerability Assessment',
            'description': 'Regular vulnerability scanning and assessment',
            'requirement': ComplianceRequirement.objects.filter(name__icontains='vulnerability').first(),
            'scheduled_date': datetime.now() + timedelta(days=30),
        }
    ]
    
    for checkpoint in checkpoint_data:
        req = checkpoint.pop('requirement')
        cp, created = ComplianceCheckpoint.objects.get_or_create(
            name=checkpoint['name'],
            requirement=req,
            defaults={
                'description': checkpoint['description'],
                'scheduled_date': checkpoint['scheduled_date'],
                'owner': admin,
                'status': 'SCHEDULED',
                'completion_percentage': 0
            }
        )
        if created:
            created_count += 1
            print(f"Created checkpoint: {cp.name}")
    
    return created_count

if __name__ == '__main__':
    print("Starting compliance data seeding...\n")
    count = create_sample_data()
    print(f"\n✓ Successfully seeded {count} new compliance records")
    print("\nSample data includes:")
    print("  - 5 compliance frameworks (ISO 27001, PCI-DSS, HIPAA, GDPR, SOC 2)")
    print("  - 25 compliance requirements")
    print("  - 3 incident response plans")
    print("  - 3 vulnerability tracking records")
    print("  - 3 compliance checkpoints")
