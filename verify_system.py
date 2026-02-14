#!/usr/bin/env python3
"""
ITSM System - Verification Script
Verifies that all key endpoints are working
"""
import os
import json
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_project.settings')

import django
django.setup()

from rest_framework.test import APIClient
from apps.users.models import User, Organization
from django.test.utils import get_unique_databases_and_mirrors
from rest_framework import status

def banner(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def test_endpoint(method, endpoint, data=None, auth_token=None):
    """Test an endpoint and return results"""
    client = APIClient()
    host = os.getenv('SITE_DOMAIN', 'localhost')
    extra = {'HTTP_HOST': host}
    if auth_token:
        extra['HTTP_AUTHORIZATION'] = f'Bearer {auth_token}'
    
    try:
        if method == 'GET':
            response = client.get(endpoint, **extra)
        elif method == 'POST':
            response = client.post(endpoint, data=data, format='json', **extra)
        else:
            return {'status': 'error', 'message': f'Unsupported method: {method}'}
        
        success = response.status_code < 400
        return {
            'status': 'success' if success else 'failed',
            'code': response.status_code,
            'method': method,
            'endpoint': endpoint,
            'data': response.data if hasattr(response, 'data') else response.content.decode()[:100]
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def main():
    banner("🚀 ITSM SYSTEM VERIFICATION")
    print("Testing all core endpoints...\n")
    
    results = []
    
    # Test 1: Health Check
    print("1️⃣  Testing Health Check...")
    health = test_endpoint('GET', '/api/v1/health/')
    results.append(('Health Check', health))
    print(f"   Status: {health['code']} - {'✅ PASS' if health['status'] == 'success' else '❌ FAIL'}")
    
    # Test 2: Login
    print("\n2️⃣  Testing Login...")
    login = test_endpoint('POST', '/api/v1/auth/login/', {
        'username': 'admin@itsm.local',
        'password': 'admin123456'
    })
    results.append(('Login', login))
    print(f"   Status: {login['code']} - {'✅ PASS' if login['status'] == 'success' else '❌ FAIL'}")
    
    token = None
    if login['status'] == 'success' and isinstance(login['data'], dict):
        token = login['data'].get('access')
        print(f"   Token: {token[:20] if token else 'None'}...")
    
    # Test 3: Get Current User Profile
    if token:
        print("\n3️⃣  Testing Get Current User Profile...")
        profile = test_endpoint('GET', '/api/v1/users/me/', auth_token=token)
        results.append(('Get User Profile', profile))
        print(f"   Status: {profile['code']} - {'✅ PASS' if profile['status'] == 'success' else '❌ FAIL'}")
        if profile['status'] == 'success':
            data = profile['data']
            if isinstance(data, dict) and 'data' in data:
                print(f"   User: {data['data'].get('email', 'N/A')}")
    
    # Test 4: List Users
    if token:
        print("\n4️⃣  Testing List Users...")
        users = test_endpoint('GET', '/api/v1/users/', auth_token=token)
        results.append(('List Users', users))
        print(f"   Status: {users['code']} - {'✅ PASS' if users['status'] == 'success' else '❌ FAIL'}")
    
    # Test 5: List Teams
    if token:
        print("\n5️⃣  Testing List Teams...")
        teams = test_endpoint('GET', '/api/v1/teams/', auth_token=token)
        results.append(('List Teams', teams))
        print(f"   Status: {teams['code']} - {'✅ PASS' if teams['status'] == 'success' else '❌ FAIL'}")
    
    # Test 6: List Compliance Frameworks
    if token:
        print("\n6️⃣  Testing List Compliance Frameworks...")
        frameworks = test_endpoint('GET', '/api/v1/compliance/frameworks/', auth_token=token)
        results.append(('List Compliance Frameworks', frameworks))
        print(f"   Status: {frameworks['code']} - {'✅ PASS' if frameworks['status'] == 'success' else '❌ FAIL'}")
    
    # Summary
    banner("📊 VERIFICATION SUMMARY")
    
    passed = sum(1 for _, r in results if r['status'] == 'success')
    failed = sum(1 for _, r in results if r['status'] == 'failed')
    errors = sum(1 for _, r in results if r['status'] == 'error')
    
    print(f"Total Tests:    {len(results)}")
    print(f"✅ Passed:      {passed}")
    print(f"❌ Failed:      {failed}")
    print(f"⚠️  Errors:      {errors}\n")
    
    # Detailed results
    print("Detailed Results:")
    print("-" * 60)
    for name, result in results:
        status_icon = '✅' if result['status'] == 'success' else '❌' if result['status'] == 'failed' else '⚠️'
        print(f"{status_icon} {name:.<40} [{result['code']}]")
    
    # Final status
    banner("🎉 SYSTEM STATUS")
    
    if failed == 0 and errors == 0:
        print("✅ ALL TESTS PASSED!")
        print("\nSystem is ready for use:")
        print(f"  • Web Server: http://127.0.0.1:8000")
        print(f"  • Admin Panel: http://127.0.0.1:8000/admin/")
        print(f"  • API Docs: http://127.0.0.1:8000/api/docs/")
        print(f"  • ReDoc: http://127.0.0.1:8000/api/redoc/")
        print(f"\nAdmin Credentials:")
        print(f"  • Email: admin@itsm.local")
        print(f"  • Password: admin123456")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print(f"Failed: {failed}, Errors: {errors}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
