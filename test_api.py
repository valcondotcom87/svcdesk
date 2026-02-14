import requests

# Login
login_data = {
    'username': 'admin@itsm.local',
    'password': 'admin123456'
}

response = requests.post('http://127.0.0.1:8000/api/v1/auth/login/', json=login_data)
print(f"Login status: {response.status_code}")

if response.status_code == 200:
    token = response.json()['access']
    print(f"Token: {token[:50]}...")
    
    # Test AD configuration endpoint
    headers = {'Authorization': f'Bearer {token}'}
    ad_response = requests.get('http://127.0.0.1:8000/api/v1/users/ad-configuration/', headers=headers)
    
    print(f"\nAD Config endpoint status: {ad_response.status_code}")
    print(f"Response: {ad_response.text[:500]}")
else:
    print(f"Login failed: {response.text}")
