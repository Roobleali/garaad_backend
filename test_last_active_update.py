#!/usr/bin/env python3
"""
Test script to verify last_active field is being updated.
Run this after a user logs in to check if the field is being set.
"""

import os
import sys
import django
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.middleware import UserActivityMiddleware

User = get_user_model()

def test_last_active_update():
    """Test if last_active field is being updated"""
    print("🔍 Testing last_active field update...")
    
    # Get a user (replace with actual user ID or username)
    try:
        # Try to get the first active user
        user = User.objects.filter(is_active=True).first()
        if not user:
            print("❌ No active users found. Please create a user first.")
            return False
        
        print(f"👤 Testing with user: {user.username} (ID: {user.id})")
        print(f"📅 Current time: {timezone.now()}")
        print(f"🕐 User last_active before: {user.last_active}")
        print(f"🕐 User last_login: {user.last_login}")
        
        # Test middleware update
        middleware = UserActivityMiddleware(lambda req: None)
        middleware._update_user_activity(user)
        
        # Refresh user from database
        user.refresh_from_db()
        
        print(f"🕐 User last_active after: {user.last_active}")
        
        if user.last_active:
            print("✅ last_active field is being updated correctly!")
            print(f"   Updated at: {user.last_active}")
            return True
        else:
            print("❌ last_active field is not being updated")
            return False
            
    except Exception as e:
        print(f"❌ Error testing last_active update: {e}")
        return False

def test_user_by_username(username):
    """Test a specific user by username"""
    print(f"🔍 Testing last_active for user: {username}")
    
    try:
        user = User.objects.get(username=username)
        print(f"👤 Found user: {user.username} (ID: {user.id})")
        print(f"🕐 Current last_active: {user.last_active}")
        
        # Test middleware update
        middleware = UserActivityMiddleware(lambda req: None)
        middleware._update_user_activity(user)
        
        # Refresh user from database
        user.refresh_from_db()
        
        print(f"🕐 Updated last_active: {user.last_active}")
        
        if user.last_active:
            print("✅ last_active field updated successfully!")
            return True
        else:
            print("❌ last_active field not updated")
            return False
            
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing last_active field update...\n")
    
    # Test with any active user
    success1 = test_last_active_update()
    
    # If you know a specific username, uncomment and modify this line:
    # success2 = test_user_by_username("your_username_here")
    
    print("\n" + "="*50)
    if success1:
        print("✅ last_active field is working correctly!")
        print("\n📋 Next steps:")
        print("   - Test login flow")
        print("   - Test API endpoints")
        print("   - Verify middleware is working")
    else:
        print("❌ last_active field is not working")
        print("\n🔧 Troubleshooting:")
        print("   - Check if middleware is loaded")
        print("   - Check database connection")
        print("   - Check user authentication")
    
    sys.exit(0 if success1 else 1) 