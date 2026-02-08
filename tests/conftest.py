"""
Test configuration and fixtures
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models import Organization, Team, Department
from apps.incidents.models import Incident


User = get_user_model()


@pytest.fixture
def api_client():
    """Provide API client for tests"""
    return APIClient()


@pytest.fixture
def organization():
    """Create a test organization"""
    return Organization.objects.create(
        name='Test Organization',
        code='TEST-ORG',
        slug='test-org',
        email='test@org.com'
    )


@pytest.fixture
def user(organization):
    """Create a test user"""
    user = User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User',
        organization=organization,
        user_type='staff'
    )
    return user


@pytest.fixture
def superuser(organization):
    """Create a test superuser"""
    user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        organization=organization
    )
    return user


@pytest.fixture
def authenticated_user(user):
    """Provide authenticated user with token"""
    refresh = RefreshToken.for_user(user)
    return {
        'user': user,
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh)
    }


@pytest.fixture
def authenticated_client(api_client, authenticated_user):
    """Provide API client with authentication"""
    api_client.credentials(
        HTTP_AUTHORIZATION=f'Bearer {authenticated_user["access_token"]}'
    )
    api_client.user = authenticated_user['user']
    return api_client


@pytest.fixture
def admin_authenticated_client(api_client, superuser):
    """Provide authenticated admin client"""
    refresh = RefreshToken.for_user(superuser)
    api_client.credentials(
        HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}'
    )
    api_client.user = superuser
    return api_client


@pytest.fixture
def department(organization):
    """Create a test department"""
    return Department.objects.create(
        organization=organization,
        name='IT Department',
        description='Information Technology'
    )


@pytest.fixture
def team(organization, department, user):
    """Create a test team"""
    team = Team.objects.create(
        organization=organization,
        department=department,
        name='Support Team',
        description='Technical Support'
    )
    team.members.add(user)
    return team


@pytest.fixture
def incident(organization, user):
    """Create a test incident"""
    return Incident.objects.create(
        organization=organization,
        ticket_number='TEST-INC-00001',
        title='Test Incident',
        description='This is a test incident',
        requester=user,
        assigned_to=user,
        priority='high',
        urgency='high',
        impact='high',
        status='open',
        created_by=user
    )


@pytest.fixture
def incident_list(organization, user):
    """Create multiple test incidents"""
    incidents = []
    for i in range(5):
        incident = Incident.objects.create(
            organization=organization,
            ticket_number=f'TEST-INC-{i:05d}',
            title=f'Test Incident {i}',
            description=f'Test incident description {i}',
            requester=user,
            assigned_to=user,
            priority=['low', 'medium', 'high', 'critical', 'urgent'][i],
            urgency=['low', 'medium', 'high', 'critical', 'urgent'][i],
            impact=['low', 'medium', 'high', 'critical', 'urgent'][i],
            status=['open', 'assigned', 'in_progress', 'resolved', 'closed'][i],
            created_by=user
        )
        incidents.append(incident)
    return incidents


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Configure Django database for tests"""
    with django_db_blocker.unblock():
        pass


# Pytest markers for test categorization
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "serializer: mark test as serializer test")
    config.addinivalue_line("markers", "viewset: mark test as viewset test")
    config.addinivalue_line("markers", "auth: mark test as authentication test")
    config.addinivalue_line("markers", "permission: mark test as permission test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
