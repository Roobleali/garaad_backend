#!/usr/bin/env python3
"""
Test script for the new activity tracking system.
This script tests the last_active field integration and middleware functionality.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
from django.test import RequestFactory
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

from core.middleware import UserActivityMiddleware, SessionActivityMiddleware
from api.models import Streak, DailyActivity
from courses.services import NotificationService

User = get_user_model()

def test_last_active_field():
    """Test that the last_active field is working correctly"""
    print("🔍 Testing last_active field...")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='test_activity_user',
        defaults={
            'email': 'test@example.com',
            'is_active': True
        }
    )
    
    print(f"  Using user: {user.username} (ID: {user.id})")
    print(f"  Initial last_active: {user.last_active}")
    print(f"  Initial last_login: {user.last_login}")
    
    # Test middleware update
    factory = RequestFactory()
    request = factory.get('/api/test/')
    request.user = user
    
    middleware = UserActivityMiddleware(lambda req: None)
    middleware._update_user_activity(user)
    
    # Refresh user from database
    user.refresh_from_db()
    
    print(f"  After middleware update:")
    print(f"    last_active: {user.last_active}")
    print(f"    last_login: {user.last_login}")
    
    if user.last_active:
        print("  ✅ last_active field is working correctly")
        return True
    else:
        print("  ❌ last_active field is not being updated")
        return False

def test_streak_integration():
    """Test that streaks work with the new last_active field"""
    print("\n🔍 Testing streak integration...")
    
    user = User.objects.get(username='test_activity_user')
    
    # Check streak before
    streak, created = Streak.objects.get_or_create(user=user)
    print(f"  Initial streak: {streak.current_streak} days")
    print(f"  Last activity date: {streak.last_activity_date}")
    
    # Simulate activity
    factory = RequestFactory()
    request = factory.get('/api/test/')
    request.user = user
    
    middleware = UserActivityMiddleware(lambda req: None)
    middleware._update_user_activity(user)
    
    # Check streak after
    streak.refresh_from_db()
    user.refresh_from_db()
    
    print(f"  After activity:")
    print(f"    Current streak: {streak.current_streak} days")
    print(f"    Last activity date: {streak.last_activity_date}")
    print(f"    User last_active: {user.last_active}")
    
    if streak.last_activity_date == timezone.now().date():
        print("  ✅ Streak integration is working correctly")
        return True
    else:
        print("  ❌ Streak integration is not working")
        return False

def test_notification_service():
    """Test that notification service uses last_active correctly"""
    print("\n🔍 Testing notification service...")
    
    user = User.objects.get(username='test_activity_user')
    
    # Test is_user_active_today
    is_active = NotificationService.is_user_active_today(user)
    print(f"  User active today: {is_active}")
    
    # Test get_inactivity_days
    inactive_days = NotificationService.get_inactivity_days(user)
    print(f"  Inactive days: {inactive_days}")
    
    # Test is_streak_broken
    streak_broken, streak_count = NotificationService.is_streak_broken(user)
    print(f"  Streak broken: {streak_broken}, Count: {streak_count}")
    
    if inactive_days is not None:
        print("  ✅ Notification service is working correctly")
        return True
    else:
        print("  ❌ Notification service has issues")
        return False

def test_daily_activity():
    """Test that daily activity records are created correctly"""
    print("\n🔍 Testing daily activity...")
    
    user = User.objects.get(username='test_activity_user')
    today = timezone.now().date()
    
    # Check if daily activity exists
    try:
        activity = DailyActivity.objects.get(user=user, date=today)
        print(f"  Daily activity found:")
        print(f"    Status: {activity.status}")
        print(f"    Problems solved: {activity.problems_solved}")
        print(f"    Lesson IDs: {activity.lesson_ids}")
        print("  ✅ Daily activity is working correctly")
        return True
    except DailyActivity.DoesNotExist:
        print("  ❌ Daily activity not found")
        return False

def test_api_endpoint():
    """Test the activity update API endpoint"""
    print("\n🔍 Testing API endpoint...")
    
    user = User.objects.get(username='test_activity_user')
    
    # Simulate API request
    factory = RequestFactory()
    request = factory.post('/api/activity/update/')
    request.user = user
    
    # Import and test the view
    from api.views import update_activity
    from rest_framework.test import force_authenticate
    
    force_authenticate(request, user=user)
    
    try:
        response = update_activity(request)
        print(f"  Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            print(f"  Success: {data.get('success')}")
            print(f"  User last_active: {data.get('user', {}).get('last_active')}")
            print(f"  Streak: {data.get('streak', {}).get('current_streak')}")
            print("  ✅ API endpoint is working correctly")
            return True
        else:
            print(f"  ❌ API endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ API endpoint error: {e}")
        return False

def test_middleware_integration():
    """Test that middleware is properly integrated"""
    print("\n🔍 Testing middleware integration...")
    
    # Check if middleware is in settings
    try:
        from garaad.settings import MIDDLEWARE
        middleware_classes = [m.split('.')[-1] for m in MIDDLEWARE]
        
        print(f"  Middleware classes: {middleware_classes}")
        
        if 'UserActivityMiddleware' in middleware_classes:
            print("  ✅ UserActivityMiddleware is configured")
            return True
        else:
            print("  ❌ UserActivityMiddleware is not configured")
            return False
    except Exception as e:
        print(f"  ❌ Error checking middleware: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("🚀 Starting comprehensive activity tracking test...\n")
    
    tests = [
        ("Last Active Field", test_last_active_field),
        ("Streak Integration", test_streak_integration),
        ("Notification Service", test_notification_service),
        ("Daily Activity", test_daily_activity),
        ("API Endpoint", test_api_endpoint),
        ("Middleware Integration", test_middleware_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Activity tracking system is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 