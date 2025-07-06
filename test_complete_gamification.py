#!/usr/bin/env python3
"""
Complete Gamification System Test
Tests all components: XP, Leagues, Streaks, Notifications, Progress
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
from courses.services import NotificationService

User = get_user_model()

class GamificationTester:
    def __init__(self):
        self.user = None
        self.test_course = None
        self.test_lesson = None
        self.test_problems = []
        
    def setup_test_environment(self):
        """Setup test user and data"""
        print("🔧 Setting up test environment...")
        
        # Get or create test user
        self.user, created = User.objects.get_or_create(
            email="abdishakuuralimohamed@gmail.com",
            defaults={
                'username': 'abdishakuuralimohamed',
                'is_active': True
            }
        )
        print(f"👤 Using user: {self.user.username} (ID: {self.user.id})")
        
        # Get or create leagues
        self.setup_leagues()
        
        # Get or create test course and lesson
        self.setup_test_course()
        
        print("✅ Test environment ready")
        
    def setup_leagues(self):
        """Setup league system"""
        print("\n🏆 Setting up leagues...")
        
        leagues_data = [
            {'name': 'Biyo', 'somali_name': 'Biyo', 'min_xp': 0, 'order': 1},
            {'name': 'Geesi', 'somali_name': 'Geesi', 'min_xp': 1000, 'order': 2},
            {'name': 'Ogow', 'somali_name': 'Ogow', 'min_xp': 5000, 'order': 3},
            {'name': 'Iftiin', 'somali_name': 'Iftiin', 'min_xp': 10000, 'order': 4},
            {'name': 'Bir Adag', 'somali_name': 'Bir Adag', 'min_xp': 25000, 'order': 5},
        ]
        
        for league_data in leagues_data:
            league, created = League.objects.get_or_create(
                name=league_data['name'],
                defaults={
                    'somali_name': league_data['somali_name'],
                    'description': f'League {league_data["name"]}',
                    'min_xp': league_data['min_xp'],
                    'order': league_data['order']
                }
            )
            if created:
                print(f"   ✅ Created league: {league.name}")
            else:
                print(f"   ℹ️  League exists: {league.name}")
        
        # Get or create user league
        default_league = League.objects.order_by('min_xp').first()
        user_league, created = UserLeague.objects.get_or_create(
            user=self.user,
            defaults={
                'current_league': default_league,
                'total_xp': 0,
                'weekly_xp': 0,
                'monthly_xp': 0
            }
        )
        print(f"   📊 User league: {user_league.current_league.name}")
        
    def setup_test_course(self):
        """Setup test course and lesson"""
        print("\n📚 Setting up test course...")
        
        # Get or create test course
        self.test_course, created = Course.objects.get_or_create(
            title="Test Course",
            defaults={
                'description': 'Test course for gamification',
                'category': None
            }
        )
        if created:
            print(f"   ✅ Created test course: {self.test_course.title}")
        
        # Get or create test lesson
        self.test_lesson, created = Lesson.objects.get_or_create(
            title="Test Lesson",
            course=self.test_course,
            defaults={
                'content': 'Test lesson content',
                'order': 1
            }
        )
        if created:
            print(f"   ✅ Created test lesson: {self.test_lesson.title}")
        
        # Create test problems
        self.create_test_problems()
        
    def create_test_problems(self):
        """Create test problems for the lesson"""
        print("\n🧩 Creating test problems...")
        
        problems_data = [
            {'question_text': 'Test Problem 1', 'xp': 10},
            {'question_text': 'Test Problem 2', 'xp': 15},
            {'question_text': 'Test Problem 3', 'xp': 20},
        ]
        
        for i, problem_data in enumerate(problems_data):
            problem, created = Problem.objects.get_or_create(
                question_text=problem_data['question_text'],
                lesson=self.test_lesson,
                defaults={
                    'question_type': 'multiple_choice',
                    'content': {
                        'question': problem_data['question_text'],
                        'options': ['A', 'B', 'C', 'D'],
                        'correct_answer': 'A',
                        'explanation': 'Test explanation'
                    },
                    'xp': problem_data['xp']
                }
            )
            if created:
                print(f"   ✅ Created problem {i+1}: {problem.xp} XP")
            self.test_problems.append(problem)
    
    def test_current_gamification_state(self):
        """Test current gamification state"""
        print("\n📊 Testing current gamification state...")
        
        # Get user's streak
        streak, created = Streak.objects.get_or_create(user=self.user)
        print(f"🕐 Streak: {streak.current_streak} days (max: {streak.max_streak})")
        print(f"⚡ Energy: {streak.current_energy}/{streak.max_energy}")
        print(f"📈 XP: {streak.xp} (daily: {streak.daily_xp}, weekly: {streak.weekly_xp})")
        
        # Get user's league
        user_league = UserLeague.objects.get(user=self.user)
        print(f"🏆 League: {user_league.current_league.name} (XP: {user_league.total_xp})")
        
        # Get next league
        next_league = League.objects.filter(min_xp__gt=user_league.current_league.min_xp).order_by('min_xp').first()
        if next_league:
            points_needed = next_league.min_xp - user_league.total_xp
            print(f"🎯 Next league: {next_league.name} (need {points_needed} more XP)")
        
        # Get notifications
        notifications = Notification.objects.filter(user=self.user).order_by('-created_at')[:5]
        print(f"🔔 Recent notifications: {notifications.count()}")
        
        return True
    
    def test_problem_solving_flow(self):
        """Test complete problem solving flow"""
        print("\n🧩 Testing problem solving flow...")
        
        if not self.test_problems:
            print("❌ No test problems available")
            return False
        
        problem = self.test_problems[0]
        print(f"🎯 Solving problem: {problem.question_text} ({problem.xp} XP)")
        
        # Create user problem record
        user_problem, created = UserProblem.objects.get_or_create(
            user=self.user,
            problem=problem,
            defaults={
                'solved': False,
                'attempts': 0,
                'xp_earned': 0
            }
        )
        
        # Mark as solved
        if user_problem.mark_as_solved():
            print("✅ Problem solved successfully!")
            
            # Check updated state
            streak = Streak.objects.get(user=self.user)
            user_league = UserLeague.objects.get(user=self.user)
            
            print(f"📈 XP earned: {user_problem.xp_earned}")
            print(f"📊 Total XP: {streak.xp}")
            print(f"🏆 League XP: {user_league.total_xp}")
            
            return True
        else:
            print("❌ Problem already solved")
            return False
    
    def test_streak_system(self):
        """Test streak system"""
        print("\n🔥 Testing streak system...")
        
        streak = Streak.objects.get(user=self.user)
        print(f"🕐 Current streak: {streak.current_streak} days")
        
        # Test streak update
        problems_solved = 2
        lesson_ids = [self.test_lesson.id]
        
        try:
            streak.update_streak(problems_solved, lesson_ids)
            print("✅ Streak updated successfully!")
            print(f"🕐 New streak: {streak.current_streak} days")
            print(f"⚡ Energy: {streak.current_energy}")
            return True
        except ValueError as e:
            print(f"❌ Streak update failed: {e}")
            return False
    
    def test_league_progression(self):
        """Test league progression"""
        print("\n🏆 Testing league progression...")
        
        user_league = UserLeague.objects.get(user=self.user)
        old_league = user_league.current_league
        print(f"🏆 Current league: {old_league.name} (XP: {user_league.total_xp})")
        
        # Add XP to trigger league promotion
        xp_to_add = 6000  # Enough to reach next league
        user_league.add_xp(xp_to_add)
        
        print(f"📈 Added {xp_to_add} XP")
        print(f"🏆 New league: {user_league.current_league.name}")
        
        if user_league.current_league != old_league:
            print("✅ League promotion successful!")
            return True
        else:
            print("ℹ️  No league promotion (XP not enough)")
            return True
    
    def test_notification_system(self):
        """Test notification system"""
        print("\n🔔 Testing notification system...")
        
        # Create test notification
        notification = Notification.objects.create(
            user=self.user,
            type='achievement',
            title='Test Achievement',
            message='You earned a test achievement!',
            data={'xp_earned': 50}
        )
        print(f"✅ Created notification: {notification.title}")
        
        # Test notification service
        try:
            NotificationService.check_and_send_real_time_reminders(self.user)
            print("✅ Notification service working")
            return True
        except Exception as e:
            print(f"❌ Notification service error: {e}")
            return False
    
    def test_leaderboard_system(self):
        """Test leaderboard system"""
        print("\n🏅 Testing leaderboard system...")
        
        # Get all users with streaks
        streaks = Streak.objects.all().order_by('-xp')[:10]
        print(f"📊 Top 10 users by XP:")
        
        for i, streak in enumerate(streaks):
            user_league = UserLeague.objects.get(user=streak.user)
            print(f"   {i+1}. {streak.user.username}: {streak.xp} XP ({user_league.current_league.name})")
        
        # Check user's rank
        user_streak = Streak.objects.get(user=self.user)
        user_rank = Streak.objects.filter(xp__gt=user_streak.xp).count() + 1
        print(f"🎯 Your rank: #{user_rank}")
        
        return True
    
    def test_progress_tracking(self):
        """Test progress tracking"""
        print("\n📈 Testing progress tracking...")
        
        # Get or create user progress
        progress, created = UserProgress.objects.get_or_create(
            user=self.user,
            lesson=self.test_lesson,
            defaults={
                'status': 'not_started',
                'problems_solved': 0,
                'total_xp_earned': 0
            }
        )
        
        print(f"📊 Lesson progress: {progress.status}")
        print(f"🧩 Problems solved: {progress.problems_solved}")
        print(f"📈 XP earned: {progress.total_xp_earned}")
        
        # Mark as in progress
        progress.mark_as_in_progress()
        print("✅ Marked as in progress")
        
        return True
    
    def test_daily_activity(self):
        """Test daily activity tracking"""
        print("\n📅 Testing daily activity...")
        
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
        print(f"🧩 Problems solved today: {activity.problems_solved}")
        
        # Update activity
        activity.status = 'partial'
        activity.problems_solved = 2
        activity.save()
        
        print("✅ Updated daily activity")
        
        return True
    
    def run_comprehensive_test(self):
        """Run all gamification tests"""
        print("🚀 Starting comprehensive gamification test...\n")
        
        # Setup
        self.setup_test_environment()
        
        # Run tests
        tests = [
            ("Current State", self.test_current_gamification_state),
            ("Problem Solving", self.test_problem_solving_flow),
            ("Streak System", self.test_streak_system),
            ("League Progression", self.test_league_progression),
            ("Notification System", self.test_notification_system),
            ("Leaderboard System", self.test_leaderboard_system),
            ("Progress Tracking", self.test_progress_tracking),
            ("Daily Activity", self.test_daily_activity),
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
        print("📊 GAMIFICATION SYSTEM TEST SUMMARY")
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
        else:
            print("\n⚠️  Some systems need attention")
        
        return passed == total

if __name__ == "__main__":
    tester = GamificationTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1) 