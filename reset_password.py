import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

try:
    user = User.objects.get(email='info@garaad.org')
    user.set_password('new_admin_password_123')
    user.save()
    print('Successfully reset password for info@garaad.org')
except User.DoesNotExist:
    print('User with email info@garaad.org does not exist')
except Exception as e:
    print(f'Error: {str(e)}') 