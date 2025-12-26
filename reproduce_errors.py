import os
import django
import sys
from unittest.mock import MagicMock

# Mock non-app modules
sys.modules['resend'] = MagicMock()
sys.modules['decouple'] = MagicMock()
sys.modules['corsheaders'] = MagicMock()
sys.modules['corsheaders.middleware'] = MagicMock()

# Set up Django environment basic
sys.path.append('/Users/rooble/Documents/garaad_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
os.environ.setdefault('DJANGO_SECRET_KEY', 'temp-secret-key-for-verification')

from django.conf import settings
if not settings.configured:
    import garaad.settings as base_settings
    apps_to_remove = ['channels', 'daphne', 'whitenoise.runserver_nostatic', 'corsheaders']
    base_settings.INSTALLED_APPS = [app for app in base_settings.INSTALLED_APPS if app not in apps_to_remove]
    base_settings.DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}

django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from community.models import Post, Reaction
from courses.models import Category
import uuid

User = get_user_model()

def run_tests():
    client = Client()
    user = User.objects.create_user(username='testuser', email='test@test.com', password='password')
    client.force_login(user)

    print("\n--- Testing /api/community/profiles/me/ ---")
    response = client.get('/api/community/profiles/me/')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 500:
        print("REPRODUCED: /profiles/me/ returns 500")
    
    print("\n--- Testing /api/activity/update/ with empty request_id ---")
    response = client.post('/api/activity/update/', {'request_id': '', 'action_type': 'solve'}, content_type='application/json')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 400:
        print(f"REPRODUCED: update_activity with empty request_id returns 400. Response: {response.data}")

    print("\n--- Testing /api/activity/update/ with null request_id ---")
    response = client.post('/api/activity/update/', {'request_id': None, 'action_type': 'solve'}, content_type='application/json')
    print(f"Status Code: {response.status_code}")

if __name__ == '__main__':
    from django.core.management import call_command
    call_command('migrate', verbosity=0)
    run_tests()
