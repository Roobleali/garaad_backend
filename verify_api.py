import os
import django
from django.test import Client, override_settings
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

@override_settings(ALLOWED_HOSTS=['*'])
def verify():
    User = get_user_model()
    client = Client()
    
    # Create or get a test user
    test_user, created = User.objects.get_or_create(username='test_checker', email='checker@example.com')
    if created:
        test_user.set_password('checkpass123')
        test_user.save()
    
    client.force_login(test_user)
    
    endpoints = [
        ('/api/streaks/', 'GET'),
        ('/api/activity/update/', 'POST'),
        ('/api/community/posts/', 'GET'),
        ('/api/community/profiles/me/', 'GET'),
        ('/api/gamification/status/', 'GET'),
    ]
    
    print("\n🚀 Starting API Endpoint Verification...\n")
    
    all_passed = True
    for url, method in endpoints:
        print(f"📡 Testing {method} {url}...", end=" ", flush=True)
        try:
            if method == 'GET':
                response = client.get(url)
            else:
                # Basic empty payload for activity update
                response = client.post(url, data={}, content_type='application/json')
            
            if response.status_code in [200, 201, 400]: # 400 is fine for empty POST, 500 is the enemy
                print(f"✅ PASSED (Status: {response.status_code})")
            else:
                print(f"❌ FAILED (Status: {response.status_code})")
                if response.status_code == 500:
                    all_passed = False
                    # Print a snippet of the error if it's a 500
                    try:
                        print(f"   Error Detail: {response.json().get('detail', 'No detail provided')}")
                    except:
                        pass
        except Exception as e:
            print(f"💥 CRASHED: {e}")
            all_passed = False

    if all_passed:
        print("\n✨ ALL CRITICAL ENDPOINTS ARE STABLE! No 500 errors detected.")
    else:
        print("\n⚠️ SOME ENDPOINTS STILL HAVE ISSUES. Check the logs above.")

if __name__ == "__main__":
    verify()
