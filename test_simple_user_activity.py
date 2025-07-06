#!/usr/bin/env python3
"""
Simple test to verify user activity tracking without debouncing.
"""

import os
import sys
import django
from django.utils import timezone
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.middleware import UserActivityMiddleware

User = get_user_model()

def test_user_activity_without_debouncing():
    """Test user activity tracking by bypassing debouncing"""
    print("🔍 Testing user activity tracking...")
    
    try:
        # Find the user
        user = User.objects.get(email="abdishakuuralimohamed@gmail.com")
        print(f"👤 Found user: {user.username} (ID: {user.id})")
        print(f"📧 Email: {user.email}")
        
        # Get current state
        print(f"🕐 Current last_active: {user.last_active}")
        print(f"🕐 Current last_login: {user.last_login}")
        
        # Test 1: Direct middleware call (bypasses debouncing)
        print("\n🔧 Test 1: Direct middleware call...")
        middleware = UserActivityMiddleware(lambda req: None)
        
        # Force update by setting last_active to None first
        user.last_active = None
        user.save(update_fields=['last_active'])
        print(f"🕐 Set last_active to None")
        
        # Call middleware
        middleware._update_user_activity(user)
        
        # Check result
        user.refresh_from_db()
        print(f"🕐 last_active after middleware: {user.last_active}")
        
        if user.last_active:
            print("✅ Middleware updated last_active correctly!")
        else:
            print("❌ Middleware did not update last_active")
            return False
        
        # Test 2: Simulate activity after 6 minutes (should update)
        print("\n🔧 Test 2: Activity after 6 minutes...")
        old_time = user.last_active - timedelta(minutes=6)
        user.last_active = old_time
        user.save(update_fields=['last_active'])
        print(f"🕐 Set last_active to: {old_time}")
        
        # Call middleware again
        middleware._update_user_activity(user)
        
        # Check result
        user.refresh_from_db()
        print(f"🕐 last_active after 6-minute test: {user.last_active}")
        
        if user.last_active and user.last_active > old_time:
            print("✅ Middleware updated after 6 minutes correctly!")
        else:
            print("❌ Middleware did not update after 6 minutes")
            return False
        
        # Test 3: Simulate activity after 2 minutes (should NOT update due to debouncing)
        print("\n🔧 Test 3: Activity after 2 minutes (debouncing test)...")
        old_time = user.last_active - timedelta(minutes=2)
        user.last_active = old_time
        user.save(update_fields=['last_active'])
        print(f"🕐 Set last_active to: {old_time}")
        
        # Call middleware again
        middleware._update_user_activity(user)
        
        # Check result
        user.refresh_from_db()
        print(f"🕐 last_active after 2-minute test: {user.last_active}")
        
        if user.last_active == old_time:
            print("✅ Debouncing working correctly (no update after 2 minutes)!")
        else:
            print("❌ Debouncing not working (updated when it shouldn't)")
            return False
        
        print("\n🎉 All middleware tests passed!")
        return True
        
    except User.DoesNotExist:
        print(f"❌ User with email 'abdishakuuralimohamed@gmail.com' not found")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

def test_streak_integration():
    """Test that streaks are updated correctly"""
    print("\n🔍 Testing streak integration...")
    
    try:
        user = User.objects.get(email="abdishakuuralimohamed@gmail.com")
        
        # Import streak model
        from api.models import Streak
        
        # Get or create streak
        streak, created = Streak.objects.get_or_create(user=user)
        print(f"📊 Current streak: {streak.current_streak} days")
        print(f"📊 Max streak: {streak.max_streak} days")
        print(f"📅 Last activity date: {streak.last_activity_date}")
        
        # Test middleware update
        middleware = UserActivityMiddleware(lambda req: None)
        middleware._update_user_activity(user)
        
        # Check streak after
        streak.refresh_from_db()
        print(f"📊 Streak after middleware: {streak.current_streak} days")
        print(f"📅 Last activity date after: {streak.last_activity_date}")
        
        if streak.last_activity_date == timezone.now().date():
            print("✅ Streak integration working correctly!")
            return True
        else:
            print("❌ Streak integration not working")
            return False
            
    except Exception as e:
        print(f"❌ Error testing streak: {e}")
        return False

def test_daily_activity():
    """Test that daily activity records are created"""
    print("\n🔍 Testing daily activity...")
    
    try:
        user = User.objects.get(email="abdishakuuralimohamed@gmail.com")
        
        # Import daily activity model
        from api.models import DailyActivity
        
        today = timezone.now().date()
        
        # Check if daily activity exists
        try:
            activity = DailyActivity.objects.get(user=user, date=today)
            print(f"📊 Daily activity found:")
            print(f"   Status: {activity.status}")
            print(f"   Problems solved: {activity.problems_solved}")
            print(f"   Lesson IDs: {activity.lesson_ids}")
            print("✅ Daily activity integration working!")
            return True
        except DailyActivity.DoesNotExist:
            print("❌ Daily activity not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing daily activity: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting simple user activity tests...\n")
    
    # Run tests
    test1 = test_user_activity_without_debouncing()
    test2 = test_streak_integration()
    test3 = test_daily_activity()
    
    # Summary
    print("\n" + "="*50)
    print("📊 SIMPLE USER ACTIVITY TEST SUMMARY")
    print("="*50)
    print(f"✅ Middleware: {'PASS' if test1 else 'FAIL'}")
    print(f"✅ Streak Integration: {'PASS' if test2 else 'FAIL'}")
    print(f"✅ Daily Activity: {'PASS' if test3 else 'FAIL'}")
    
    all_passed = all([test1, test2, test3])
    
    if all_passed:
        print("\n🎉 All tests passed! Activity tracking is working correctly.")
        print("\n📋 Summary:")
        print("   - Middleware updates last_active correctly")
        print("   - Debouncing works (5-minute intervals)")
        print("   - Streak integration is functional")
        print("   - Daily activity tracking is working")
    else:
        print("\n⚠️  Some tests failed. Check the implementation.")
    
    sys.exit(0 if all_passed else 1) 