#!/usr/bin/env python3
"""
Test script to verify CORS settings are working properly
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

def test_cors_settings():
    """Test CORS settings configuration"""
    print("🔍 Testing CORS Settings...")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"CORS_ALLOW_CREDENTIALS: {getattr(settings, 'CORS_ALLOW_CREDENTIALS', 'Not set')}")
    print(f"CORS_ALLOW_ALL_ORIGINS: {getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', 'Not set')}")
    print(f"CORS_ALLOWED_ORIGINS: {getattr(settings, 'CORS_ALLOWED_ORIGINS', 'Not set')}")
    print(f"CORS_ALLOW_METHODS: {getattr(settings, 'CORS_ALLOW_METHODS', 'Not set')}")
    print(f"CORS_ALLOW_HEADERS: {getattr(settings, 'CORS_ALLOW_HEADERS', 'Not set')}")
    
    # Check middleware order
    middleware = settings.MIDDLEWARE
    cors_index = None
    for i, middleware_name in enumerate(middleware):
        if 'corsheaders' in middleware_name:
            cors_index = i
            break
    
    if cors_index is not None:
        print(f"✅ CORS middleware found at position {cors_index}")
        if cors_index == 0:
            print("✅ CORS middleware is at the top (correct)")
        else:
            print(f"⚠️  CORS middleware should be at position 0, but is at {cors_index}")
    else:
        print("❌ CORS middleware not found in MIDDLEWARE")
    
    # Test specific origins
    test_origins = [
        'http://localhost:3000',
        'https://api.garaad.org',
        'https://garaad.org'
    ]
    
    print("\n🔍 Testing specific origins:")
    for origin in test_origins:
        if hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS') and settings.CORS_ALLOW_ALL_ORIGINS:
            print(f"✅ {origin} - Allowed (CORS_ALLOW_ALL_ORIGINS=True)")
        elif hasattr(settings, 'CORS_ALLOWED_ORIGINS') and origin in settings.CORS_ALLOWED_ORIGINS:
            print(f"✅ {origin} - Explicitly allowed")
        else:
            print(f"❌ {origin} - Not allowed")

if __name__ == '__main__':
    test_cors_settings() 