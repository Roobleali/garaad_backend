"""
Production settings for Garaad backend.
This file contains production-specific settings that override the base settings.
"""

import os
from .settings import *

# Production-specific settings
DEBUG = False

# Security settings for production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Production allowed hosts
ALLOWED_HOSTS = [
    'api.garaad.org',
    'garaad-backend-production.up.railway.app',
    'garaad-backend-development.up.railway.app',
    '127.0.0.1',
    'localhost',
    '0.0.0.0',
]

# Production CORS settings
CORS_ALLOWED_ORIGINS = [
    'https://garaad.org',
    'https://www.garaad.org',
    'https://api.garaad.org',
    'http://localhost:3000',  # For development testing
    'http://127.0.0.1:3000'   # For development testing
]

# Disable CORS allow all origins in production
CORS_ALLOW_ALL_ORIGINS = False

# Production logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'community': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'courses': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Static files configuration for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Database connection pooling for production
DATABASES = {
    'default': dj_database_url.parse(
        os.getenv('DATABASE_URL', 'postgresql://postgres.icbgyzaihxqcfjzwllll:Garaad%233344@aws-0-us-east-1.pooler.supabase.com:5432/postgres'),
        conn_max_age=600,
        ssl_require=True
    )
}

# Cache configuration for production (if needed)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.resend.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'noreply@garaad.org')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

# Site URLs for production
SITE_URL = 'https://garaad.org'
FRONTEND_URL = 'https://garaad.org' 