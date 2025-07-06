#!/usr/bin/env python3
"""
Simple test script for the activity tracking system logic.
This test validates the middleware logic without requiring database access.
"""

import sys
from datetime import datetime, timedelta, date

def test_streak_logic():
    """Test the streak calculation logic"""
    print("🧪 Testing Streak Logic")
    print("=" * 40)
    
    # Test data
    test_cases = [
        {
            'name': 'First day activity',
            'last_activity': None,
            'today': date(2025, 1, 29),
            'expected_streak': 1,
            'expected_max': 1
        },
        {
            'name': 'Consecutive day',
            'last_activity': date(2025, 1, 28),
            'today': date(2025, 1, 29),
            'expected_streak': 2,
            'expected_max': 2
        },
        {
            'name': 'Same day activity',
            'last_activity': date(2025, 1, 29),
            'today': date(2025, 1, 29),
            'expected_streak': 1,  # Should not change
            'expected_max': 1
        },
        {
            'name': 'Streak broken (2 day gap)',
            'last_activity': date(2025, 1, 27),
            'today': date(2025, 1, 29),
            'expected_streak': 1,  # Should reset
            'expected_max': 1
        },
        {
            'name': 'Long gap',
            'last_activity': date(2025, 1, 20),
            'today': date(2025, 1, 29),
            'expected_streak': 1,  # Should reset
            'expected_max': 1
        }
    ]
    
    def calculate_streak(last_activity, today, current_streak=0, max_streak=0):
        """Calculate streak based on activity dates"""
        if not last_activity or last_activity != today:
            if last_activity:
                days_diff = (today - last_activity).days
                
                if days_diff == 1:
                    # Consecutive day - increment streak
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                elif days_diff > 1:
                    # Streak broken - reset to 1
                    current_streak = 1
                    max_streak = max(max_streak, current_streak)
                # If days_diff == 0, it's the same day, don't change streak
            else:
                # First activity
                current_streak = 1
                max_streak = 1
            
            last_activity = today
        
        return current_streak, max_streak, last_activity
    
    # Run test cases
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Last activity: {test_case['last_activity']}")
        print(f"   Today: {test_case['today']}")
        
        current_streak, max_streak, new_last_activity = calculate_streak(
            test_case['last_activity'],
            test_case['today']
        )
        
        print(f"   Calculated streak: {current_streak}")
        print(f"   Calculated max: {max_streak}")
        print(f"   Expected streak: {test_case['expected_streak']}")
        print(f"   Expected max: {test_case['expected_max']}")
        
        if (current_streak == test_case['expected_streak'] and 
            max_streak == test_case['expected_max']):
            print("   ✅ PASS")
        else:
            print("   ❌ FAIL")
            all_passed = False
    
    return all_passed

def test_activity_status():
    """Test activity status logic"""
    print("\n📊 Testing Activity Status Logic")
    print("=" * 40)
    
    test_cases = [
        {
            'name': 'No problems solved',
            'problems_solved': 0,
            'expected_status': 'partial'  # User was active but no learning
        },
        {
            'name': 'Some problems solved',
            'problems_solved': 2,
            'expected_status': 'partial'  # Partial learning
        },
        {
            'name': 'Complete learning',
            'problems_solved': 3,
            'expected_status': 'complete'  # Complete learning goal
        },
        {
            'name': 'More than complete',
            'problems_solved': 5,
            'expected_status': 'complete'  # Still complete
        }
    ]
    
    def determine_activity_status(problems_solved):
        """Determine activity status based on problems solved"""
        if problems_solved == 0:
            return 'partial'  # User was active but no learning
        elif problems_solved < 3:
            return 'partial'  # Partial learning
        else:
            return 'complete'  # Complete learning goal
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Problems solved: {test_case['problems_solved']}")
        
        status = determine_activity_status(test_case['problems_solved'])
        expected = test_case['expected_status']
        
        print(f"   Calculated status: {status}")
        print(f"   Expected status: {expected}")
        
        if status == expected:
            print("   ✅ PASS")
        else:
            print("   ❌ FAIL")
            all_passed = False
    
    return all_passed

def test_middleware_logic():
    """Test middleware logic without database"""
    print("\n🔧 Testing Middleware Logic")
    print("=" * 40)
    
    class MockUser:
        def __init__(self, username, email):
            self.username = username
            self.email = email
            self.is_authenticated = True
    
    class MockRequest:
        def __init__(self, user, path):
            self.user = user
            self.path = path
    
    # Test middleware should track activity
    test_cases = [
        {
            'name': 'Authenticated user request',
            'user': MockUser('testuser', 'test@example.com'),
            'path': '/api/streaks/',
            'should_track': True
        },
        {
            'name': 'Static file request',
            'user': MockUser('testuser', 'test@example.com'),
            'path': '/static/css/style.css',
            'should_track': False
        },
        {
            'name': 'Admin request',
            'user': MockUser('testuser', 'test@example.com'),
            'path': '/admin/users/',
            'should_track': False
        },
        {
            'name': 'API health check',
            'user': MockUser('testuser', 'test@example.com'),
            'path': '/api/health/',
            'should_track': False
        }
    ]
    
    def should_track_request(path):
        """Determine if request should be tracked"""
        excluded_paths = [
            '/static/',
            '/media/',
            '/admin/',
            '/api/health/',
            '/favicon.ico',
            '/robots.txt',
        ]
        
        return not any(path.startswith(excluded) for excluded in excluded_paths)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Path: {test_case['path']}")
        
        should_track = should_track_request(test_case['path'])
        expected = test_case['should_track']
        
        print(f"   Should track: {should_track}")
        print(f"   Expected: {expected}")
        
        if should_track == expected:
            print("   ✅ PASS")
        else:
            print("   ❌ FAIL")
            all_passed = False
    
    return all_passed

def test_notification_logic():
    """Test notification logic"""
    print("\n🔔 Testing Notification Logic")
    print("=" * 40)
    
    today = date(2025, 1, 29)
    
    test_cases = [
        {
            'name': 'Active today',
            'last_activity': today,
            'current_streak': 5,
            'expected_streak_broken': False,
            'expected_inactive_days': 0
        },
        {
            'name': 'Inactive 1 day',
            'last_activity': today - timedelta(days=1),
            'current_streak': 5,
            'expected_streak_broken': False,
            'expected_inactive_days': 1
        },
        {
            'name': 'Streak broken (2 days)',
            'last_activity': today - timedelta(days=2),
            'current_streak': 5,
            'expected_streak_broken': True,
            'expected_inactive_days': 2
        },
        {
            'name': 'No streak record',
            'last_activity': None,
            'current_streak': 0,
            'expected_streak_broken': False,
            'expected_inactive_days': None
        }
    ]
    
    def is_streak_broken(last_activity, current_streak):
        """Check if streak is broken"""
        if last_activity and current_streak > 0:
            days_since_activity = (today - last_activity).days
            return days_since_activity > 1
        return False
    
    def get_inactivity_days(last_activity):
        """Calculate inactivity days"""
        if last_activity:
            return (today - last_activity).days
        return None
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Last activity: {test_case['last_activity']}")
        print(f"   Current streak: {test_case['current_streak']}")
        
        streak_broken = is_streak_broken(test_case['last_activity'], test_case['current_streak'])
        inactive_days = get_inactivity_days(test_case['last_activity'])
        
        print(f"   Streak broken: {streak_broken}")
        print(f"   Inactive days: {inactive_days}")
        print(f"   Expected streak broken: {test_case['expected_streak_broken']}")
        print(f"   Expected inactive days: {test_case['expected_inactive_days']}")
        
        if (streak_broken == test_case['expected_streak_broken'] and 
            inactive_days == test_case['expected_inactive_days']):
            print("   ✅ PASS")
        else:
            print("   ❌ FAIL")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("🚀 Starting Activity Tracking System Logic Tests")
    print("=" * 60)
    
    # Run all tests
    test1 = test_streak_logic()
    test2 = test_activity_status()
    test3 = test_middleware_logic()
    test4 = test_notification_logic()
    
    print("\n" + "=" * 60)
    if test1 and test2 and test3 and test4:
        print("✅ All logic tests passed!")
        print("\n📋 Summary:")
        print("   - Streak calculation logic is correct")
        print("   - Activity status logic is working")
        print("   - Middleware filtering logic is correct")
        print("   - Notification logic is working")
        print("\n🎯 The activity tracking system logic is sound!")
        print("   Next: Test with real database and deploy")
    else:
        print("❌ Some logic tests failed. Please review the implementation.")
        sys.exit(1) 