import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'accounts.apps.AccountsConfig',
    'api.apps.ApiConfig',
    'courses.apps.CoursesConfig',
    'leagues.apps.LeaguesConfig',
    'billing.apps.BillingConfig',  # Updated to use the new app name
]

# Waafipay Settings
WAAFIPAY_MERCHANT_ID = os.environ.get('WAAFIPAY_MERCHANT_ID', '')
WAAFIPAY_API_KEY = os.environ.get('WAAFIPAY_API_KEY', '')
WAAFIPAY_API_USER_ID = os.environ.get('WAAFIPAY_API_USER_ID', '')
WAAFIPAY_TEST_MODE = os.environ.get('WAAFIPAY_TEST_MODE', 'True') == 'True'
WAAFIPAY_LOCAL_AMOUNT = 19  # $19 for local users
WAAFIPAY_DIASPORA_AMOUNT = 49  # $49 for diaspora users 