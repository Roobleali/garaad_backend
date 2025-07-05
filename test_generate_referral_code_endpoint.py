#!/usr/bin/env python3
"""
Test script to verify the generate-referral-code endpoint
"""
import os
import django
import requests
import json
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

def test_generate_referral_code_endpoint():
    """Test the generate-referral-code endpoint"""
    print("🔍 Testing Generate Referral Code Endpoint...")
    
    # Base URL
    base_url = "http://localhost:8000"
    
    # Test 1: Test endpoint exists
    print("\n1. Testing endpoint availability...")
    try:
        response = requests.post(f"{base_url}/api/auth/generate-referral-code/")
        print(f"✅ Endpoint exists (status: {response.status_code})")
        print(f"✅ Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running. Please start the server with: python manage.py runserver 8000")
        return
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return
    
    # Test 2: Test authentication requirement
    print("\n2. Testing authentication requirement...")
    try:
        response = requests.post(f"{base_url}/api/auth/generate-referral-code/")
        if response.status_code == 401:
            print("✅ Authentication required (expected)")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
    
    # Test 3: Test with authentication
    print("\n3. Testing with authentication...")
    try:
        from accounts.models import User
        
        # Create a test user without referral code
        test_user = User.objects.create_user(
            username=f"testuser_{os.urandom(4).hex()}",
            email=f"test{os.urandom(4).hex()}@example.com",
            password="testpass123",
            age=25
        )
        
        # Clear referral code
        test_user.referral_code = ""
        test_user.save()
        
        print(f"✅ Created test user: {test_user.username}")
        print(f"✅ User has no referral code: {test_user.referral_code == ''}")
        
        # Get JWT token for the user
        login_response = requests.post(f"{base_url}/api/auth/signin/", json={
            "email": test_user.email,
            "password": "testpass123"
        })
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access')
            
            if access_token:
                print("✅ Got access token")
                
                # Test generate referral code with authentication
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.post(f"{base_url}/api/auth/generate-referral-code/", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    print("✅ Successfully generated referral code")
                    print(f"✅ New referral code: {data.get('referral_code')}")
                    print(f"✅ Message: {data.get('message')}")
                    
                    # Verify the code was saved
                    test_user.refresh_from_db()
                    print(f"✅ User referral code updated: {test_user.referral_code}")
                    
                else:
                    print(f"❌ Failed to generate referral code: {response.status_code}")
                    print(f"❌ Response: {response.text}")
            else:
                print("❌ No access token in response")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"❌ Response: {login_response.text}")
        
        # Clean up
        test_user.delete()
        print("✅ Test user cleaned up")
        
    except Exception as e:
        print(f"❌ Error in test 3: {e}")
    
    # Test 4: Test with user who already has referral code
    print("\n4. Testing with user who already has referral code...")
    try:
        from accounts.models import User
        
        # Create a test user with referral code
        test_user = User.objects.create_user(
            username=f"testuser2_{os.urandom(4).hex()}",
            email=f"test2{os.urandom(4).hex()}@example.com",
            password="testpass123",
            age=25
        )
        
        print(f"✅ Created test user: {test_user.username}")
        print(f"✅ User has referral code: {test_user.referral_code}")
        
        # Get JWT token for the user
        login_response = requests.post(f"{base_url}/api/auth/signin/", json={
            "email": test_user.email,
            "password": "testpass123"
        })
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access')
            
            if access_token:
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.post(f"{base_url}/api/auth/generate-referral-code/", headers=headers)
                
                if response.status_code == 400:
                    data = response.json()
                    print("✅ Correctly rejected user with existing referral code")
                    print(f"✅ Error message: {data.get('error')}")
                    print(f"✅ Existing referral code: {data.get('referral_code')}")
                else:
                    print(f"⚠️  Unexpected response: {response.status_code}")
                    print(f"⚠️  Response: {response.text}")
            else:
                print("❌ No access token in response")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
        
        # Clean up
        test_user.delete()
        print("✅ Test user cleaned up")
        
    except Exception as e:
        print(f"❌ Error in test 4: {e}")
    
    print("\n🎉 Generate referral code endpoint tests completed!")

if __name__ == "__main__":
    test_generate_referral_code_endpoint() 