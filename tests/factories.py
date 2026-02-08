"""
Factory Boy factories for model creation in tests
"""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

from apps.core.models import Organization, Department, Team, CustomUser
from apps.incidents.models import Incident, IncidentComment
from apps.service_requests.models import ServiceCategory, Service, ServiceRequest
from apps.problems.models import Problem
from apps.changes.models import Change
from apps.cmdb.models import CICategory, CI
from apps.sla.models import SLAPolicy
from apps.surveys.models import Survey, Feedback
from apps.assets.models import Asset, AssetCategory


User = get_user_model()


class OrganizationFactory(DjangoModelFactory):
    """Factory for Organization model"""
    class Meta:
        model = Organization
    
    name = factory.Sequence(lambda n: f'Organization {n}')
    code = factory.Sequence(lambda n: f'ORG{n:03d}')
    slug = factory.Sequence(lambda n: f'org-{n}')
    email = factory.Sequence(lambda n: f'org{n}@example.com')
    is_active = True


class CustomUserFactory(DjangoModelFactory):
    """Factory for CustomUser model"""
    class Meta:
        model = CustomUser
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.PostGeneration(lambda obj, create, extracted, **kwargs: 
                                     obj.set_password(extracted or 'testpass123'))
    organization = factory.SubFactory(OrganizationFactory)
    user_type = 'staff'
    is_active = True


class DepartmentFactory(DjangoModelFactory):
    """Factory for Department model"""
    class Meta:
        model = Department
    
    organization = factory.SubFactory(OrganizationFactory)
    name = factory.Sequence(lambda n: f'Department {n}')
    description = factory.Faker('text', max_nb_chars=50)


class TeamFactory(DjangoModelFactory):
    """Factory for Team model"""
    class Meta:
        model = Team
    
    organization = factory.SubFactory(OrganizationFactory)
    department = factory.SubFactory(DepartmentFactory, organization=factory.SelfAttribute('..organization'))
    name = factory.Sequence(lambda n: f'Team {n}')
    description = factory.Faker('text', max_nb_chars=50)


class IncidentFactory(DjangoModelFactory):
    """Factory for Incident model"""
    class Meta:
        model = Incident
    
    organization = factory.SubFactory(OrganizationFactory)
    ticket_number = factory.Sequence(lambda n: f'INC-{n:05d}')
    title = factory.Faker('title')
    description = factory.Faker('text')
    requester = factory.SubFactory(CustomUserFactory, organization=factory.SelfAttribute('..organization'))
    assigned_to = factory.SubFactory(CustomUserFactory, organization=factory.SelfAttribute('..organization'))
    priority = 'medium'
    urgency = 'medium'
    impact = 'medium'
    status = 'open'
    created_by = factory.SubFactory(CustomUserFactory, organization=factory.SelfAttribute('..organization'))


class IncidentCommentFactory(DjangoModelFactory):
    """Factory for IncidentComment model"""
    class Meta:
        model = IncidentComment
    
    incident = factory.SubFactory(IncidentFactory)
    text = factory.Faker('text')
    is_internal = False
    created_by = factory.SubFactory(CustomUserFactory, organization=factory.SelfAttribute('..incident.organization'))


class ServiceCategoryFactory(DjangoModelFactory):
    """Factory for ServiceCategory model"""
    class Meta:
        model = ServiceCategory
    
    organization = factory.SubFactory(OrganizationFactory)
    name = factory.Faker('title')
    description = factory.Faker('text', max_nb_chars=50)
    is_active = True


class ServiceFactory(DjangoModelFactory):
    """Factory for Service model"""
    class Meta:
        model = Service
    
    organization = factory.SubFactory(OrganizationFactory)
    category = factory.SubFactory(ServiceCategoryFactory, organization=factory.SelfAttribute('..organization'))
    name = factory.Faker('title')
    description = factory.Faker('text')
    owner = factory.SubFactory(CustomUserFactory, organization=factory.SelfAttribute('..organization'))
    is_active = True


class ServiceRequestFactory(DjangoModelFactory):
    """Factory for ServiceRequest model"""
    class Meta:
        model = ServiceRequest
    
    organization = factory.SubFactory(OrganizationFactory)
    request_number = factory.Sequence(lambda n: f'SR-{n:05d}')
    title = factory.Faker('title')
    description = factory.Faker('text')
    requester = factory.SubFactory(CustomUserFactory, organization=factory.SelfAttribute('..organization'))
    category = factory.SubFactory(ServiceCategoryFactory, organization=factory.SelfAttribute('..organization'))
    status = 'open'
    priority = 'medium'
    created_by = factory.SubFactory(CustomUserFactory, organization=factory.SelfAttribute('..organization'))


class ProblemFactory(DjangoModelFactory):
    """Factory for Problem model"""
    class Meta:
        model = Problem
    
    organization = factory.SubFactory(OrganizationFactory)
    problem_number = factory.Sequence(lambda n: f'PRB-{n:05d}')
    title = factory.Faker('title')
    description = factory.Faker('text')
    owner = factory.SubFactory(CustomUserFactory, organization=factory.SelfAttribute('..organization'))
    status = 'open'
    priority = 'medium'
    created_by = factory.SubFactory(CustomUserFactory, organization=factory.SelfAttribute('..organization'))


class ChangeFactory(DjangoModelFactory):
    """Factory for Change model"""
    class Meta:
        model = Change
    
    organization = factory.SubFactory(OrganizationFactory)
    change_number = factory.Sequence(lambda n: f'CHG-{n:05d}')
    title = factory.Faker('title')
    description = factory.Faker('text')
    initiator = factory.SubFactory(CustomUserFactory, organization=factory.SelfAttribute('..organization'))
    change_type = 'standard'
    status = 'open'
    priority = 'medium'
    created_by = factory.SubFactory(CustomUserFactory, organization=factory.SelfAttribute('..organization'))


class CICategoryFactory(DjangoModelFactory):
    """Factory for CICategory model"""
    class Meta:
        model = CICategory
    
    name = factory.Faker('title')
    description = factory.Faker('text', max_nb_chars=50)
    is_active = True


class CIFactory(DjangoModelFactory):
    """Factory for CI model"""
    class Meta:
        model = CI
    
    organization = factory.SubFactory(OrganizationFactory)
    name = factory.Faker('title')
    description = factory.Faker('text')
    category = factory.SubFactory(CICategoryFactory)
    serial_number = factory.Sequence(lambda n: f'SN-{n:05d}')
    status = 'active'
    created_by = factory.SubFactory(CustomUserFactory, organization=factory.SelfAttribute('..organization'))


class SLAPolicyFactory(DjangoModelFactory):
    """Factory for SLAPolicy model"""
    class Meta:
        model = SLAPolicy
    
    organization = factory.SubFactory(OrganizationFactory)
    name = factory.Faker('title')
    description = factory.Faker('text')
    coverage_type = 'business_hours'
    is_active = True


class SurveyFactory(DjangoModelFactory):
    """Factory for Survey model"""
    class Meta:
        model = Survey
    
    organization = factory.SubFactory(OrganizationFactory)
    title = factory.Faker('title')
    description = factory.Faker('text')
    survey_type = 'satisfaction'
    is_active = True


class FeedbackFactory(DjangoModelFactory):
    """Factory for Feedback model"""
    class Meta:
        model = Feedback
    
    organization = factory.SubFactory(OrganizationFactory)
    provider = factory.SubFactory(CustomUserFactory, organization=factory.SelfAttribute('..organization'))
    feedback_text = factory.Faker('text')
    rating = 4


class AssetCategoryFactory(DjangoModelFactory):
    """Factory for AssetCategory model"""
    class Meta:
        model = AssetCategory
    
    name = factory.Faker('title')
    description = factory.Faker('text', max_nb_chars=50)
    is_active = True


class AssetFactory(DjangoModelFactory):
    """Factory for Asset model"""
    class Meta:
        model = Asset
    
    organization = factory.SubFactory(OrganizationFactory)
    name = factory.Faker('title')
    description = factory.Faker('text')
    category = factory.SubFactory(AssetCategoryFactory)
    asset_tag = factory.Sequence(lambda n: f'AST-{n:05d}')
    status = 'active'
    current_owner = factory.SubFactory(CustomUserFactory, organization=factory.SelfAttribute('..organization'))
