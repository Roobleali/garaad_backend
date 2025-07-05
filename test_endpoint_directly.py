#!/usr/bin/env python3
"""
Test the generate-referral-code endpoint directly in Django
"""
import os
import django

# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

# Now import Django and DRF modules
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_generate_referral_code_endpoint():
    """Test the generate-referral-code endpoint directly"""
    print("🔍 Testing Generate Referral Code Endpoint Directly...")
    
    # Create a test user without referral code
    test_user = User.objects.create_user(
        username="testuser_no_code",
        email="testnocode@example.com",
        password="testpass123",
        age=25
    )
    
    # Clear referral code
    test_user.referral_code = ""
    test_user.save()
    
    print(f"✅ Created test user: {test_user.username}")
    print(f"✅ User has no referral code: {test_user.referral_code == ''}")
    
    # Create JWT token
    refresh = RefreshToken.for_user(test_user)
    access_token = str(refresh.access_token)
    
    print(f"✅ Generated access token: {access_token[:20]}...")
    
    # Test the endpoint
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Test 1: Generate referral code for user without one
    print("\n1. Testing generate referral code for user without one...")
    response = client.post('/api/auth/generate-referral-code/')
    
    print(f"✅ Response status: {response.status_code}")
    print(f"✅ Response data: {response.data}")
    
    if response.status_code == 200:
        print("✅ Successfully generated referral code")
        test_user.refresh_from_db()
        print(f"✅ User referral code updated: {test_user.referral_code}")
    else:
        print(f"❌ Failed to generate referral code: {response.status_code}")
        print(f"❌ Response: {response.data}")
    
    # Test 2: Try to generate again (should fail)
    print("\n2. Testing generate referral code for user who already has one...")
    response = client.post('/api/auth/generate-referral-code/')
    
    print(f"✅ Response status: {response.status_code}")
    print(f"✅ Response data: {response.data}")
    
    if response.status_code == 400:
        print("✅ Correctly rejected user with existing referral code")
    else:
        print(f"⚠️  Unexpected response: {response.status_code}")
    
    # Test 3: Test without authentication
    print("\n3. Testing without authentication...")
    client.credentials()  # Remove authentication
    response = client.post('/api/auth/generate-referral-code/')
    
    print(f"✅ Response status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Correctly requires authentication")
    else:
        print(f"⚠️  Unexpected response: {response.status_code}")
    
    # Clean up
    test_user.delete()
    print("\n✅ Test user cleaned up")
    
    print("\n🎉 Generate referral code endpoint tests completed!")

if __name__ == "__main__":
    test_generate_referral_code_endpoint() 