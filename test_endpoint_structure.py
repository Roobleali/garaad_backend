#!/usr/bin/env python3
"""
Test the generate-referral-code endpoint structure
"""
import os
import django

# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

from django.urls import reverse, resolve
from django.test import TestCase

def test_endpoint_structure():
    """Test that the endpoint is properly configured"""
    print("🔍 Testing Generate Referral Code Endpoint Structure...")
    
    # Test 1: Check if URL pattern exists
    print("\n1. Testing URL pattern...")
    try:
        # Try to resolve the URL
        resolver = resolve('/api/auth/generate-referral-code/')
        print(f"✅ URL pattern found: {resolver}")
        print(f"✅ View function: {resolver.func}")
        print(f"✅ URL name: {resolver.url_name}")
    except Exception as e:
        print(f"❌ URL pattern not found: {e}")
    
    # Test 2: Check if view function exists
    print("\n2. Testing view function...")
    try:
        from accounts.views import generate_referral_code_view
        print("✅ View function imported successfully")
        print(f"✅ Function name: {generate_referral_code_view.__name__}")
        print(f"✅ Function docstring: {generate_referral_code_view.__doc__}")
    except ImportError as e:
        print(f"❌ View function not found: {e}")
    
    # Test 3: Check URL configuration
    print("\n3. Testing URL configuration...")
    try:
        from accounts.urls import urlpatterns
        print("✅ URL patterns loaded successfully")
        
        # Find our endpoint
        generate_url = None
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name == 'generate_referral_code':
                generate_url = pattern
                break
        
        if generate_url:
            print("✅ Generate referral code URL pattern found")
            print(f"✅ Pattern: {generate_url}")
        else:
            print("❌ Generate referral code URL pattern not found")
            
    except Exception as e:
        print(f"❌ Error loading URL patterns: {e}")
    
    # Test 4: Check imports in views
    print("\n4. Testing view imports...")
    try:
        from accounts.views import generate_referral_code_view
        from rest_framework.decorators import api_view, permission_classes
        from rest_framework.permissions import IsAuthenticated
        from rest_framework.response import Response
        from rest_framework import status
        
        print("✅ All required imports available")
        
        # Check if view has proper decorators
        if hasattr(generate_referral_code_view, '__wrapped__'):
            print("✅ View has decorators")
        else:
            print("⚠️  View may not have proper decorators")
            
    except Exception as e:
        print(f"❌ Import error: {e}")
    
    print("\n🎉 Endpoint structure tests completed!")

if __name__ == "__main__":
    test_endpoint_structure() 