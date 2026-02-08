#!/usr/bin/env python3
"""
Quick system verification using HTTP requests
"""
import requests
import urllib3
import json
import sys

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()

def banner(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def test_api(method, url, data=None, token=None):
    """Test API endpoint"""
    headers = {
        'Content-Type': 'application/json'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        # Ensure HTTP, not HTTPS
        url = url.replace('https://', 'http://')
        
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=5, verify=False)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=5, verify=False)
        else:
            return None
        
        return response
    except Exception as e:
        print(f"   Error: {str(e)[:80]}")
        return None

def main():
    banner("🚀 ITSM SYSTEM - VERIFICATION TEST")
    
    base_url = "http://127.0.0.1:8000"
    results = []
    token = None
    
    # Test 1: Health Check
    print("1️⃣  Health Check...")
    resp = test_api('GET', f"{base_url}/api/v1/health/")
    if resp and resp.status_code == 200:
        print(f"   ✅ PASS [200] - System is healthy")
        results.append(True)
    else:
        code = resp.status_code if resp else 'N/A'
        print(f"   ❌ FAIL [{code}]")
        results.append(False)
    
    # Test 2: Login
    print("\n2️⃣  Login Endpoint...")
    resp = test_api('POST', f"{base_url}/api/v1/auth/login/", {
        'username': 'admin@itsm.local',
        'password': 'admin123456'
    })
    if resp and resp.status_code == 200:
        data = resp.json()
        token = data.get('access')
        email = data.get('user', {}).get('email')
        print(f"   ✅ PASS [200]")
        print(f"   User: {email}")
        print(f"   Token: {token[:30] if token else 'None'}...")
        results.append(True)
    else:
        code = resp.status_code if resp else 'N/A'
        print(f"   ❌ FAIL [{code}]")
        if resp:
            print(f"   Response: {resp.text[:100]}")
        results.append(False)
    
    # Test 3: Get User Profile
    if token:
        print("\n3️⃣  Get Current User Profile...")
        resp = test_api('GET', f"{base_url}/api/v1/users/me/", token=token)
        if resp and resp.status_code == 200:
            data = resp.json()
            email = data.get('data', {}).get('email')
            print(f"   ✅ PASS [200]")
            print(f"   Email: {email}")
            results.append(True)
        else:
            code = resp.status_code if resp else 'N/A'
            print(f"   ❌ FAIL [{code}]")
            results.append(False)
    
    # Test 4: List Users
    if token:
        print("\n4️⃣  List Users...")
        resp = test_api('GET', f"{base_url}/api/v1/users/", token=token)
        if resp and resp.status_code == 200:
            data = resp.json()
            count = len(data.get('results', []))
            print(f"   ✅ PASS [200]")
            print(f"   Total Users: {count}")
            results.append(True)
        else:
            code = resp.status_code if resp else 'N/A'
            print(f"   ❌ FAIL [{code}]")
            results.append(False)
    
    # Test 5: List Teams
    if token:
        print("\n5️⃣  List Teams...")
        resp = test_api('GET', f"{base_url}/api/v1/teams/", token=token)
        if resp and resp.status_code == 200:
            data = resp.json()
            # Handle different response formats
            if isinstance(data, dict):
                count = len(data.get('results', []))
            else:
                count = len(data)
            print(f"   ✅ PASS [200]")
            print(f"   Total Teams: {count}")
            results.append(True)
        else:
            code = resp.status_code if resp else 'N/A'
            print(f"   ❌ FAIL [{code}]")
            results.append(False)
    
    # Test 6: List Compliance Frameworks
    if token:
        print("\n6️⃣  List Compliance Frameworks...")
        resp = test_api('GET', f"{base_url}/api/v1/compliance/frameworks/", token=token)
        if resp and resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict):
                count = len(data.get('results', []))
            else:
                count = len(data)
            print(f"   ✅ PASS [200]")
            print(f"   Total Frameworks: {count}")
            results.append(True)
        else:
            code = resp.status_code if resp else 'N/A'
            print(f"   ❌ FAIL [{code}]")
            results.append(False)
    
    # Test 7: Admin Panel
    print("\n7️⃣  Admin Panel...")
    resp = test_api('GET', f"{base_url}/admin/")
    if resp and resp.status_code < 400:
        print(f"   ✅ PASS [{resp.status_code}]")
        results.append(True)
    else:
        code = resp.status_code if resp else 'N/A'
        print(f"   ❌ FAIL [{code}]")
        results.append(False)
    
    # Summary
    banner("📊 VERIFICATION SUMMARY")
    
    passed = sum(results)
    failed = len(results) - passed
    
    print(f"Total Tests:    {len(results)}")
    print(f"✅ Passed:      {passed}")
    print(f"❌ Failed:      {failed}\n")
    
    # Final status
    if failed == 0:
        banner("✅ SYSTEM READY FOR USE")
        print("\n🎉 All endpoints verified and working!\n")
        print("Access Information:")
        print("-" * 60)
        print(f"  Web Server:     http://127.0.0.1:8000/")
        print(f"  Admin Panel:    http://127.0.0.1:8000/admin/")
        print(f"  API Swagger:    http://127.0.0.1:8000/api/docs/")
        print(f"  API ReDoc:      http://127.0.0.1:8000/api/redoc/")
        print(f"\nAdmin Credentials:")
        print(f"  Email:          admin@itsm.local")
        print(f"  Password:       admin123456")
        print(f"\nTest Credentials:")
        print(f"  Email:          user@example.com")
        print(f"  Password:       userpass123")
        print("\n" + "="*60)
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the responses above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
