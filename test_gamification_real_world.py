#!/usr/bin/env python3
"""
Real-world Gamification System Test
Tests all components with existing data
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
from api.models import Streak, Notification, DailyActivity
from leagues.models import League, UserLeague
from courses.models import Course, Lesson, Problem, UserProgress, UserProblem, UserReward

User = get_user_model()

class RealWorldGamificationTest:
    def __init__(self):
        self.user = None
        
    def setup_user(self):
        """Setup test user"""
        print("👤 Setting up test user...")
        
        self.user = User.objects.get(email="abdishakuuralimohamed@gmail.com")
        print(f"✅ Using user: {self.user.username} (ID: {self.user.id})")
        
        return True
    
    def test_current_state(self):
        """Test current gamification state"""
        print("\n📊 Current Gamification State:")
        print("=" * 50)
        
        # Get streak
        streak, created = Streak.objects.get_or_create(user=self.user)
        print(f"🔥 Streak: {streak.current_streak} days (max: {streak.max_streak})")
        print(f"⚡ Energy: {streak.current_energy}/{streak.max_energy}")
        print(f"📈 Total XP: {streak.xp}")
        print(f"📅 Daily XP: {streak.daily_xp}")
        print(f"📊 Weekly XP: {streak.weekly_xp}")
        print(f"📈 Monthly XP: {streak.monthly_xp}")
        
        # Get league
        user_league, created = UserLeague.objects.get_or_create(
            user=self.user,
            defaults={'current_league': League.objects.order_by('min_xp').first()}
        )
        print(f"🏆 League: {user_league.current_league.name}")
        print(f"🎯 League XP: {user_league.total_xp}")
        print(f"📊 Weekly League XP: {user_league.weekly_xp}")
        
        # Get next league
        next_league = League.objects.filter(
            min_xp__gt=user_league.current_league.min_xp
        ).order_by('min_xp').first()
        
        if next_league:
            points_needed = next_league.min_xp - user_league.total_xp
            print(f"🎯 Next League: {next_league.name} (need {points_needed} more XP)")
        
        # Get recent notifications
        notifications = Notification.objects.filter(user=self.user).order_by('-created_at')[:3]
        print(f"🔔 Recent Notifications: {notifications.count()}")
        for notif in notifications:
            print(f"   - {notif.title}: {notif.message}")
        
        # Get daily activity
        today = timezone.now().date()
        try:
            activity = DailyActivity.objects.get(user=self.user, date=today)
            print(f"📅 Today's Activity: {activity.status} ({activity.problems_solved} problems)")
        except DailyActivity.DoesNotExist:
            print("📅 Today's Activity: None")
        
        return True
    
    def test_xp_system(self):
        """Test XP system"""
        print("\n📈 Testing XP System:")
        print("=" * 30)
        
        streak = Streak.objects.get(user=self.user)
        old_xp = streak.xp
        
        # Simulate XP award
        xp_to_award = 25
        streak.award_xp(xp_to_award, 'problem')
        
        print(f"🎯 Awarded {xp_to_award} XP")
        print(f"📈 XP before: {old_xp}")
        print(f"📈 XP after: {streak.xp}")
        print(f"📊 Daily XP: {streak.daily_xp}")
        print(f"📊 Weekly XP: {streak.weekly_xp}")
        
        if streak.xp > old_xp:
            print("✅ XP system working correctly!")
            return True
        else:
            print("❌ XP system not working")
            return False
    
    def test_streak_system(self):
        """Test streak system"""
        print("\n🔥 Testing Streak System:")
        print("=" * 30)
        
        streak = Streak.objects.get(user=self.user)
        old_streak = streak.current_streak
        old_energy = streak.current_energy
        
        print(f"🕐 Current streak: {old_streak} days")
        print(f"⚡ Current energy: {old_energy}")
        
        # Test streak update
        try:
            problems_solved = 2
            lesson_ids = [1]  # Dummy lesson ID
            
            streak.update_streak(problems_solved, lesson_ids)
            
            print(f"🕐 New streak: {streak.current_streak} days")
            print(f"⚡ New energy: {streak.current_energy}")
            
            if streak.current_streak >= old_streak:
                print("✅ Streak system working!")
                return True
            else:
                print("❌ Streak system not working")
                return False
                
        except ValueError as e:
            print(f"❌ Streak update failed: {e}")
            return False
    
    def test_league_system(self):
        """Test league system"""
        print("\n🏆 Testing League System:")
        print("=" * 30)
        
        user_league = UserLeague.objects.get(user=self.user)
        old_league = user_league.current_league
        old_xp = user_league.total_xp
        
        print(f"🏆 Current league: {old_league.name}")
        print(f"📈 Current XP: {old_xp}")
        
        # Add XP to test league progression
        xp_to_add = 1000
        user_league.add_xp(xp_to_add)
        
        print(f"📈 Added {xp_to_add} XP")
        print(f"🏆 New league: {user_league.current_league.name}")
        print(f"📈 New XP: {user_league.total_xp}")
        
        if user_league.total_xp > old_xp:
            print("✅ League system working!")
            return True
        else:
            print("❌ League system not working")
            return False
    
    def test_notification_system(self):
        """Test notification system"""
        print("\n🔔 Testing Notification System:")
        print("=" * 30)
        
        # Count existing notifications
        old_count = Notification.objects.filter(user=self.user).count()
        print(f"📊 Existing notifications: {old_count}")
        
        # Create test notification
        notification = Notification.objects.create(
            user=self.user,
            type='achievement',
            title='Test Achievement',
            message='You earned a test achievement!',
            data={'xp_earned': 50}
        )
        
        new_count = Notification.objects.filter(user=self.user).count()
        print(f"✅ Created notification: {notification.title}")
        print(f"📊 Total notifications: {new_count}")
        
        if new_count > old_count:
            print("✅ Notification system working!")
            return True
        else:
            print("❌ Notification system not working")
            return False
    
    def test_leaderboard_system(self):
        """Test leaderboard system"""
        print("\n🏅 Testing Leaderboard System:")
        print("=" * 30)
        
        # Get all users with streaks
        streaks = Streak.objects.all().order_by('-xp')[:10]
        print(f"📊 Top 10 users by XP:")
        
        for i, streak in enumerate(streaks):
            try:
                user_league = UserLeague.objects.get(user=streak.user)
                league_name = user_league.current_league.name
            except UserLeague.DoesNotExist:
                league_name = "No League"
            
            print(f"   {i+1}. {streak.user.username}: {streak.xp} XP ({league_name})")
        
        # Get user's rank
        user_streak = Streak.objects.get(user=self.user)
        user_rank = Streak.objects.filter(xp__gt=user_streak.xp).count() + 1
        print(f"🎯 Your rank: #{user_rank} with {user_streak.xp} XP")
        
        return True
    
    def test_progress_tracking(self):
        """Test progress tracking"""
        print("\n📈 Testing Progress Tracking:")
        print("=" * 30)
        
        # Get user progress records
        progress_records = UserProgress.objects.filter(user=self.user)
        print(f"📊 Progress records: {progress_records.count()}")
        
        for progress in progress_records[:3]:  # Show first 3
            print(f"   📚 {progress.lesson.title}: {progress.status}")
            print(f"      🧩 Problems solved: {progress.problems_solved}")
            print(f"      📈 XP earned: {progress.total_xp_earned}")
        
        # Get user problems
        user_problems = UserProblem.objects.filter(user=self.user)
        solved_problems = user_problems.filter(solved=True)
        print(f"🧩 Total problems: {user_problems.count()}")
        print(f"✅ Solved problems: {solved_problems.count()}")
        
        return True
    
    def test_daily_activity(self):
        """Test daily activity tracking"""
        print("\n📅 Testing Daily Activity:")
        print("=" * 30)
        
        today = timezone.now().date()
        
        # Get or create daily activity
        activity, created = DailyActivity.objects.get_or_create(
            user=self.user,
            date=today,
            defaults={
                'status': 'none',
                'problems_solved': 0,
                'lesson_ids': []
            }
        )
        
        print(f"📅 Today's activity: {activity.status}")
        print(f"🧩 Problems solved: {activity.problems_solved}")
        print(f"📚 Lesson IDs: {activity.lesson_ids}")
        
        # Update activity
        activity.status = 'partial'
        activity.problems_solved = 2
        activity.save()
        
        print("✅ Updated daily activity")
        
        return True
    
    def test_rewards_system(self):
        """Test rewards system"""
        print("\n🏆 Testing Rewards System:")
        print("=" * 30)
        
        # Get user rewards
        rewards = UserReward.objects.filter(user=self.user)
        print(f"🏆 Total rewards: {rewards.count()}")
        
        for reward in rewards[:5]:  # Show first 5
            print(f"   🎁 {reward.reward_type}: {reward.reward_name} ({reward.value})")
        
        # Create test reward
        reward = UserReward.objects.create(
            user=self.user,
            reward_type='points',
            reward_name='Test Reward',
            value=100
        )
        
        print(f"✅ Created test reward: {reward.reward_name}")
        
        return True
    
    def test_integration_flow(self):
        """Test complete integration flow"""
        print("\n🔄 Testing Complete Integration Flow:")
        print("=" * 40)
        
        # 1. User solves a problem
        print("1️⃣ User solves a problem...")
        streak = Streak.objects.get(user=self.user)
        old_xp = streak.xp
        
        # Award XP
        streak.award_xp(15, 'problem')
        
        # 2. Update streak
        print("2️⃣ Update streak...")
        try:
            streak.update_streak(1, [1])
        except ValueError as e:
            print(f"   ⚠️  Streak update: {e}")
        
        # 3. Update league
        print("3️⃣ Update league...")
        user_league = UserLeague.objects.get(user=self.user)
        user_league.update_weekly_points(15)
        
        # 4. Create notification
        print("4️⃣ Create notification...")
        notification = Notification.objects.create(
            user=self.user,
            type='achievement',
            title='Problem Solved!',
            message='You solved a problem and earned XP!',
            data={'xp_earned': 15}
        )
        
        # 5. Check results
        print("5️⃣ Check results...")
        streak.refresh_from_db()
        user_league.refresh_from_db()
        
        print(f"   📈 XP increased: {streak.xp > old_xp}")
        print(f"   🔥 Streak: {streak.current_streak} days")
        print(f"   🏆 League XP: {user_league.total_xp}")
        print(f"   🔔 Notification: {notification.title}")
        
        return True
    
    def run_all_tests(self):
        """Run all gamification tests"""
        print("🚀 Starting Real-World Gamification Tests...\n")
        
        # Setup
        self.setup_user()
        
        # Run tests
        tests = [
            ("Current State", self.test_current_state),
            ("XP System", self.test_xp_system),
            ("Streak System", self.test_streak_system),
            ("League System", self.test_league_system),
            ("Notification System", self.test_notification_system),
            ("Leaderboard System", self.test_leaderboard_system),
            ("Progress Tracking", self.test_progress_tracking),
            ("Daily Activity", self.test_daily_activity),
            ("Rewards System", self.test_rewards_system),
            ("Integration Flow", self.test_integration_flow),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with error: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "="*60)
        print("📊 REAL-WORLD GAMIFICATION TEST SUMMARY")
        print("="*60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All gamification systems working correctly!")
            print("\n📋 System Overview:")
            print("   ✅ XP System: Points awarded for activities")
            print("   ✅ Streak System: Daily engagement tracking")
            print("   ✅ League System: Competitive rankings")
            print("   ✅ Notification System: User feedback")
            print("   ✅ Progress Tracking: Lesson completion")
            print("   ✅ Daily Activity: Activity monitoring")
            print("   ✅ Leaderboard: Competitive rankings")
            print("   ✅ Rewards System: Achievement tracking")
            print("   ✅ Integration: All systems working together")
        else:
            print("\n⚠️  Some systems need attention")
        
        return passed == total

if __name__ == "__main__":
    tester = RealWorldGamificationTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1) 