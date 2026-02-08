"""
Users Tests
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest import skip
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import Organization, Team, Role

User = get_user_model()


class UserModelTest(TestCase):
    """
    Test User model
    """
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name='Test Organization',
            domain='test.com'
        )
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            organization=self.organization
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass123'
        )
        
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.role, 'admin')
    
    def test_user_full_name(self):
        """Test get_full_name method"""
        user = User.objects.create_user(
            email='john@example.com',
            username='john',
            password='pass123',
            first_name='John',
            last_name='Doe'
        )
        
        self.assertEqual(user.get_full_name(), 'John Doe')
    
    def test_user_lock_unlock(self):
        """Test account locking"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='pass123'
        )
        
        # Lock account
        user.lock_account(duration_minutes=30)
        self.assertTrue(user.is_locked())
        
        # Unlock account
        user.unlock_account()
        self.assertFalse(user.is_locked())
        self.assertEqual(user.failed_login_attempts, 0)



class UserAPITest(APITestCase):
    """
    Test User API endpoints
    """
    
    def setUp(self):
        self.client = APIClient()
        self.organization = Organization.objects.create(
            name='Test Organization',
            domain='test.com'
        )
        
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            organization=self.organization
        )
        
        # Create regular user
        self.user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='userpass123',
            organization=self.organization,
            role='end_user'
        )
    
    def test_login(self):
        """Test user login"""
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'admin@example.com',
            'password': 'adminpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'admin@example.com',
            'password': 'wrongpassword'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_user_profile(self):
        """Test getting current user profile"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/users/me/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['email'], 'user@example.com')
    
    def test_list_users_as_admin(self):
        """Test listing users as admin"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/users/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)
    
    def test_create_user_as_admin(self):
        """Test creating user as admin"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/v1/users/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPass@123456',
            'password_confirm': 'NewPass@123456',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'agent',
            'organization': str(self.organization.id)
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['email'], 'newuser@example.com')
    
    def test_change_password(self):
        """Test changing password"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/v1/users/change_password/', {
            'old_password': 'userpass123',
            'new_password': 'NewPassword@456',
            'new_password_confirm': 'NewPassword@456'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify new password works
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword@456'))



class TeamAPITest(APITestCase):
    """
    Test Team API endpoints
    """
    
    def setUp(self):
        self.client = APIClient()
        self.organization = Organization.objects.create(
            name='Test Organization'
        )
        
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            organization=self.organization
        )
        
        self.team = Team.objects.create(
            name='Support Team',
            organization=self.organization,
            team_lead=self.admin_user
        )
    
    def test_list_teams(self):
        """Test listing teams"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/teams/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_create_team(self):
        """Test creating team"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/v1/teams/', {
            'name': 'Development Team',
            'description': 'Software development team',
            'organization': str(self.organization.id),
            'team_lead': str(self.admin_user.id)
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_add_team_member(self):
        """Test adding member to team"""
        user = User.objects.create_user(
            email='member@example.com',
            username='member',
            password='pass123',
            organization=self.organization
        )
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            f'/api/v1/teams/{self.team.id}/add_member/',
            {
                'user_id': str(user.id),
                'role': 'member'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(response.data['data']['user']), str(user.id))
