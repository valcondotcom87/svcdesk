#!/usr/bin/env python3
"""
System verification using urllib (no SSL issues)
"""
import urllib.request
import urllib.error
import json

def banner(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def test_api(method, url, data=None, token=None):
    """Test API endpoint using urllib"""
    headers = {
        'Content-Type': 'application/json'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        if method == 'POST' and data:
            req_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=req_data, headers=headers, method='POST')
        else:
            req = urllib.request.Request(url, headers=headers, method='GET' if method == 'GET' else 'POST')
        
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.status
            body = response.read().decode('utf-8')
            return status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return None, str(e)

def main():
    banner("🚀 ITSM SYSTEM - VERIFICATION TEST")
    
    base_url = "http://127.0.0.1:8000"
    results = []
    token = None
    
    # Test 1: Health Check
    print("1️⃣  Health Check...")
    status, body = test_api('GET', f"{base_url}/api/v1/health/")
    if status == 200:
        print(f"   ✅ PASS [200] - System healthy")
        results.append(True)
    else:
        print(f"   ❌ FAIL [{status}]")
        results.append(False)
    
    # Test 2: Login
    print("\n2️⃣  Login...")
    status, body = test_api('POST', f"{base_url}/api/v1/auth/login/", {
        'username': 'admin@itsm.local',
        'password': 'admin123456'
    })
    if status == 200:
        try:
            data = json.loads(body)
            token = data.get('access')
            email = data.get('user', {}).get('email', 'N/A')
            print(f"   ✅ PASS [200]")
            print(f"      User: {email}")
            print(f"      Token: {token[:30] if token else 'None'}...")
            results.append(True)
        except:
            print(f"   ❌ Error parsing response")
            results.append(False)
    else:
        print(f"   ❌ FAIL [{status}]")
        results.append(False)
    
    # Test 3: Get User Profile
    if token:
        print("\n3️⃣  Get User Profile...")
        status, body = test_api('GET', f"{base_url}/api/v1/users/me/", token=token)
        if status == 200:
            try:
                data = json.loads(body)
                email = data.get('data', {}).get('email', 'N/A')
                print(f"   ✅ PASS [200] - User: {email}")
                results.append(True)
            except:
                print(f"   ❌ Error parsing")
                results.append(False)
        else:
            print(f"   ❌ FAIL [{status}]")
            results.append(False)
    
    # Test 4: List Users
    if token:
        print("\n4️⃣  List Users...")
        status, body = test_api('GET', f"{base_url}/api/v1/users/", token=token)
        if status == 200:
            try:
                data = json.loads(body)
                count = len(data.get('results', []))
                print(f"   ✅ PASS [200] - Total: {count} users")
                results.append(True)
            except:
                print(f"   ❌ Error parsing")
                results.append(False)
        else:
            print(f"   ❌ FAIL [{status}]")
            results.append(False)
    
    # Test 5: List Teams
    if token:
        print("\n5️⃣  List Teams...")
        status, body = test_api('GET', f"{base_url}/api/v1/teams/", token=token)
        if status == 200:
            print(f"   ✅ PASS [200]")
            results.append(True)
        else:
            print(f"   ❌ FAIL [{status}]")
            results.append(False)
    
    # Test 6: List Compliance Frameworks
    if token:
        print("\n6️⃣  List Compliance Frameworks...")
        status, body = test_api('GET', f"{base_url}/api/v1/compliance/frameworks/", token=token)
        if status == 200:
            try:
                data = json.loads(body)
                count = len(data.get('results', []))
                print(f"   ✅ PASS [200] - Frameworks: {count}")
                results.append(True)
            except:
                print(f"   ❌ Error parsing")
                results.append(False)
        else:
            print(f"   ❌ FAIL [{status}]")
            results.append(False)
    
    # Test 7: Admin Panel
    print("\n7️⃣  Admin Panel...")
    status, body = test_api('GET', f"{base_url}/admin/")
    if status and status < 400:
        print(f"   ✅ PASS [{status}]")
        results.append(True)
    else:
        print(f"   ❌ FAIL [{status}]")
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
        print("\n✨ System is ready for end-user use!")
        return 0
    else:
        print("\n⚠️  Some tests failed.")
        print("Check if server is running: python manage.py runserver 0.0.0.0:8000")
        return 1

if __name__ == '__main__':
    main()
