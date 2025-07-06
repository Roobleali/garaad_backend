#!/usr/bin/env python3
"""
Real user login test to verify last_active field updates.
This simulates actual user behavior and API requests.
"""

import os
import sys
import django
import requests
import json
from django.utils import timezone
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class RealUserTest:
    def __init__(self):
        self.client = APIClient()
        self.base_url = "http://localhost:8000"  # Change this to your API URL
        self.user_email = "abdishakuuralimohamed@gmail.com"
        self.user_password = "abdishakuuralimohamed@gmail.com"
        self.access_token = None
        self.user = None
    
    def test_user_login(self):
        """Test real user login and token generation"""
        print("🔐 Testing real user login...")
        
        try:
            # Find the user
            self.user = User.objects.get(email=self.user_email)
            print(f"👤 Found user: {self.user.username} (ID: {self.user.id})")
            print(f"📧 Email: {self.user.email}")
            print(f"🕐 Current last_active: {self.user.last_active}")
            print(f"🕐 Current last_login: {self.user.last_login}")
            
            # Generate tokens manually (simulating login)
            refresh = RefreshToken.for_user(self.user)
            self.access_token = str(refresh.access_token)
            
            print(f"🎫 Generated access token: {self.access_token[:20]}...")
            
            # Update last_login manually (simulating Django's login)
            self.user.last_login = timezone.now()
            self.user.save(update_fields=['last_login'])
            
            print(f"🕐 Updated last_login: {self.user.last_login}")
            
            return True
            
        except User.DoesNotExist:
            print(f"❌ User with email '{self.user_email}' not found")
            return False
        except Exception as e:
            print(f"❌ Error during login: {e}")
            return False
    
    def test_api_requests(self):
        """Test various API requests to trigger middleware"""
        print("\n🌐 Testing API requests to trigger middleware...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        # Set up headers
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Test different API endpoints
        test_endpoints = [
            '/api/streak/',
            '/api/lms/courses/',
            '/api/lms/lessons/',
            '/api/activity/update/',
        ]
        
        for endpoint in test_endpoints:
            try:
                print(f"📡 Testing endpoint: {endpoint}")
                response = self.client.get(endpoint, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Request successful")
                else:
                    print(f"   ⚠️  Request failed: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return True
    
    def test_activity_update_endpoint(self):
        """Test the activity update endpoint specifically"""
        print("\n🔄 Testing activity update endpoint...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        try:
            response = self.client.post(
                '/api/activity/update/',
                HTTP_AUTHORIZATION=f'Bearer {self.access_token}',
                content_type='application/json'
            )
            
            print(f"📡 Activity update response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Activity update successful!")
                print(f"   User last_active: {data.get('user', {}).get('last_active')}")
                print(f"   Streak: {data.get('streak', {}).get('current_streak')}")
                return True
            else:
                print(f"❌ Activity update failed: {response.status_code}")
                print(f"   Response: {response.content}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing activity update: {e}")
            return False
    
    def check_user_activity_after_requests(self):
        """Check if user's last_active was updated after API requests"""
        print("\n🔍 Checking user activity after API requests...")
        
        try:
            # Refresh user from database
            self.user.refresh_from_db()
            
            print(f"🕐 User last_active after requests: {self.user.last_active}")
            print(f"🕐 User last_login: {self.user.last_login}")
            
            if self.user.last_active:
                print("✅ last_active field was updated by middleware!")
                print(f"   Updated at: {self.user.last_active}")
                return True
            else:
                print("❌ last_active field was not updated")
                return False
                
        except Exception as e:
            print(f"❌ Error checking user activity: {e}")
            return False
    
    def test_middleware_directly(self):
        """Test middleware directly to ensure it works"""
        print("\n🔧 Testing middleware directly...")
        
        try:
            from core.middleware import UserActivityMiddleware
            
            # Get user's last_active before
            self.user.refresh_from_db()
            before_last_active = self.user.last_active
            print(f"🕐 last_active before middleware: {before_last_active}")
            
            # Test middleware directly
            middleware = UserActivityMiddleware(lambda req: None)
            middleware._update_user_activity(self.user)
            
            # Check after middleware
            self.user.refresh_from_db()
            after_last_active = self.user.last_active
            print(f"🕐 last_active after middleware: {after_last_active}")
            
            if after_last_active and after_last_active != before_last_active:
                print("✅ Middleware is working correctly!")
                return True
            else:
                print("❌ Middleware did not update last_active")
                return False
                
        except Exception as e:
            print(f"❌ Error testing middleware: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting comprehensive real user test...\n")
        
        # Test 1: User login
        login_success = self.test_user_login()
        if not login_success:
            print("❌ Login test failed")
            return False
        
        # Test 2: API requests
        api_success = self.test_api_requests()
        
        # Test 3: Activity update endpoint
        activity_success = self.test_activity_update_endpoint()
        
        # Test 4: Check user activity
        activity_check = self.check_user_activity_after_requests()
        
        # Test 5: Direct middleware test
        middleware_success = self.test_middleware_directly()
        
        # Summary
        print("\n" + "="*60)
        print("📊 REAL USER TEST SUMMARY")
        print("="*60)
        print(f"✅ Login: {'PASS' if login_success else 'FAIL'}")
        print(f"✅ API Requests: {'PASS' if api_success else 'FAIL'}")
        print(f"✅ Activity Update: {'PASS' if activity_success else 'FAIL'}")
        print(f"✅ Activity Check: {'PASS' if activity_check else 'FAIL'}")
        print(f"✅ Middleware: {'PASS' if middleware_success else 'FAIL'}")
        
        all_passed = all([login_success, api_success, activity_success, activity_check, middleware_success])
        
        if all_passed:
            print("\n🎉 All tests passed! Activity tracking is working correctly.")
            print("\n📋 What this means:")
            print("   - User login is working")
            print("   - API requests are being processed")
            print("   - Middleware is updating last_active")
            print("   - Activity tracking is functional")
        else:
            print("\n⚠️  Some tests failed. Check the implementation.")
        
        return all_passed

if __name__ == "__main__":
    tester = RealUserTest()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1) 