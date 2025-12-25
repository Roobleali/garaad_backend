import os
import django
from django.test import Client, override_settings
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

@override_settings(ALLOWED_HOSTS=['*'], SECURE_SSL_REDIRECT=False)
def verify():
    User = get_user_model()
    client = Client()
    
    # Create or get a test user
    username = 'test_checker_v3'
    test_user, created = User.objects.get_or_create(username=username, defaults={'email': 'checker_v3@example.com'})
    if created:
        test_user.set_password('checkpass123')
        test_user.save()
    
    # Simple manual login to ensure session is set
    client.force_login(test_user)
    
    endpoints = [
        ('/api/streaks/', 'GET'),
        ('/api/activity/update/', 'POST'),
        ('/api/community/posts/', 'GET'),
        ('/api/community/profiles/me/', 'GET'),
        ('/api/gamification/status/', 'GET'),
    ]
    
    print("\n🚀 Starting API Endpoint Verification (v3 - UUID & Auth Fix)...\n")
    
    all_passed = True
    for url, method in endpoints:
        print(f"📡 Testing {method} {url}...", end=" ", flush=True)
        try:
            if method == 'GET':
                response = client.get(url, follow=True)
            else:
                response = client.post(url, data={}, content_type='application/json', follow=True)
            
            final_status = response.status_code
            # 200/201 are success. 
            # 400 is acceptable for empty POST on some endpoints.
            # 401 means our force_login failed to persist.
            # 500 is a crash.
            if final_status in [200, 201]:
                print(f"✅ PASSED (Status: {final_status})")
            elif final_status == 400:
                print(f"⚠️ WARN (Status: {final_status} - Payload empty but endpoint alive)")
            else:
                print(f"❌ FAILED (Status: {final_status})")
                all_passed = False
                if final_status == 500:
                    try:
                        # Try to print more info if possible
                        print(f"   Error: {response.content[:200]}")
                    except: pass
        except Exception as e:
            print(f"💥 CRASHED: {e}")
            all_passed = False

    if all_passed:
        print("\n✨ ALL CRITICAL ENDPOINTS ARE STABLE! No 500 errors detected.")
    else:
        print("\n⚠️ SOME ENDPOINTS STILL HAVE ISSUES. Check the logs above.")

if __name__ == "__main__":
    verify()
