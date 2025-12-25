import os
import django
from django.test import Client, override_settings
from django.contrib.auth import get_user_model
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

@override_settings(ALLOWED_HOSTS=['*'], SECURE_SSL_REDIRECT=False)
def verify():
    from rest_framework_simplejwt.tokens import RefreshToken
    User = get_user_model()
    client = Client()
    
    # Create or get a test user
    username = 'api_verifier_jwt'
    test_user, created = User.objects.get_or_create(username=username, defaults={'email': 'verifier@example.com'})
    if created:
        test_user.set_password('checkpass123')
        test_user.save()
    
    # Generate JWT Token
    refresh = RefreshToken.for_user(test_user)
    access_token = str(refresh.access_token)
    auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
    
    endpoints = [
        ('/api/streaks/', 'GET'),
        ('/api/activity/update/', 'POST'),
        ('/api/community/posts/', 'GET'),
        ('/api/community/profiles/me/', 'GET'),
        ('/api/gamification/status/', 'GET'),
    ]
    
    print("\n🚀 Starting API Endpoint Verification (v4 - JWT Authentication)...\n")
    print(f"🔑 Authenticated as: {username}")
    
    all_passed = True
    for url, method in endpoints:
        print(f"📡 Testing {method} {url}...", end=" ", flush=True)
        try:
            if method == 'GET':
                response = client.get(url, follow=True, **auth_headers)
            else:
                # Basic empty payload for activity update
                response = client.post(url, data={}, content_type='application/json', follow=True, **auth_headers)
            
            final_status = response.status_code
            if final_status in [200, 201]:
                print(f"✅ PASSED (Status: {final_status})")
            elif final_status == 400:
                print(f"⚠️ WARN (Status: {final_status} - Payload empty but endpoint alive)")
            elif final_status == 401:
                print(f"❌ FAILED (Status: {final_status} - Unauthorized despite JWT)")
                all_passed = False
            else:
                print(f"❌ FAILED (Status: {final_status})")
                all_passed = False
                if final_status == 500:
                    try:
                        print(f"   Error: {response.content[:200]}")
                    except: pass
        except Exception as e:
            print(f"💥 CRASHED: {e}")
            all_passed = False

    if all_passed:
        print("\n✨ ALL CRITICAL ENDPOINTS ARE STABLE! No 500/401 errors detected.")
    else:
        print("\n⚠️ SOME ENDPOINTS STILL HAVE ISSUES. Check the logs above.")

if __name__ == "__main__":
    verify()
