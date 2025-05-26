from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from uuid import uuid4
from ..models import Streak, DailyActivity
from unittest.mock import patch

User = get_user_model()

class StreakModelTest(TestCase):
    def setUp(self):
        # Create test user with unique email and username
        unique_id = uuid4().hex[:8]
        self.user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
        # Create streak for user
        self.streak = Streak.objects.create(user=self.user)

    def test_initial_streak_state(self):
        """Test initial streak state"""
        self.assertEqual(self.streak.current_streak, 0)
        self.assertEqual(self.streak.max_streak, 0)
        self.assertEqual(self.streak.xp, 0)
        self.assertEqual(self.streak.daily_xp, 0)
        self.assertEqual(self.streak.current_energy, 3)
        self.assertEqual(self.streak.max_energy, 3)

    def test_first_activity(self):
        """Test first activity of the day"""
        self.streak.update_streak(problems_solved=3, lesson_ids=['lesson1'])
        
        self.assertEqual(self.streak.current_streak, 1)
        self.assertEqual(self.streak.max_streak, 1)
        self.assertEqual(self.streak.xp, 35)  # 20 XP for streak + 15 XP for 3 problems
        self.assertEqual(self.streak.daily_xp, 35)
        self.assertEqual(self.streak.current_energy, 2)  # Used 1 energy

    def test_consecutive_days(self):
        """Test maintaining streak on consecutive days"""
        # First day
        self.streak.update_streak(problems_solved=3, lesson_ids=['lesson1'])
        self.assertEqual(self.streak.current_streak, 1)
        
        # Simulate next day
        self.streak.last_activity_date = timezone.now().date() - timedelta(days=1)
        self.streak.save()
        
        # Second day
        self.streak.update_streak(problems_solved=3, lesson_ids=['lesson2'])
        self.assertEqual(self.streak.current_streak, 2)
        self.assertEqual(self.streak.xp, 70)  # 35 XP from first day + 35 XP from second day

    def test_missed_day(self):
        """Test streak reset after missing a day"""
        # First day
        self.streak.update_streak(problems_solved=3, lesson_ids=['lesson1'])
        
        # Simulate missing a day
        self.streak.last_activity_date = timezone.now().date() - timedelta(days=2)
        self.streak.save()
        
        # Activity after missing a day
        self.streak.update_streak(problems_solved=3, lesson_ids=['lesson2'])
        self.assertEqual(self.streak.current_streak, 1)  # Streak should reset to 1

    def test_milestone_xp(self):
        """Test XP rewards for milestone streaks"""
        # Give enough energy for 7 days
        self.streak.current_energy = 7
        self.streak.save()
        base_date = timezone.now().date() - timedelta(days=6)
        with patch('django.utils.timezone.now') as mock_now:
            for i in range(7):
                mock_now.return_value = timezone.datetime.combine(base_date + timedelta(days=i), timezone.datetime.min.time(), tzinfo=timezone.get_current_timezone())
                self.streak.last_activity_date = (base_date + timedelta(days=i-1)) if i > 0 else None
                self.streak.current_streak = i if i > 0 else 0
                self.streak.save()
                self.streak.update_streak(problems_solved=3, lesson_ids=[f'lesson{i+1}'])
                print(f"Day {i+1}: XP = {self.streak.xp}, Streak = {self.streak.current_streak}")
            self.assertEqual(self.streak.current_streak, 7)
            # 7 days: (20+15)*7 + 50 milestone = 245 + 50 = 295
            expected_xp = 35 * 7 + 50
            self.assertEqual(self.streak.xp, expected_xp)

    def test_energy_system(self):
        """Test energy regeneration and usage"""
        # Use all energy
        for _ in range(3):
            self.assertTrue(self.streak.use_energy())
        self.assertEqual(self.streak.current_energy, 0)
        
        # Try to use energy when none available
        self.assertFalse(self.streak.use_energy())
        
        # Simulate time passing (4 hours)
        self.streak.last_energy_update = timezone.now() - timedelta(hours=4)
        self.streak.save()
        
        # Check energy regeneration
        self.assertTrue(self.streak.update_energy())
        self.assertEqual(self.streak.current_energy, 1)

    def test_daily_xp_reset(self):
        """Test daily XP reset"""
        # Add some XP
        self.streak.award_xp(50, 'problem')
        self.assertEqual(self.streak.daily_xp, 50)
        
        # Simulate next day
        self.streak.last_xp_reset = timezone.now().date() - timedelta(days=1)
        self.streak.save()
        
        # Add more XP
        self.streak.award_xp(30, 'problem')
        self.assertEqual(self.streak.daily_xp, 30)  # Should reset and only show new XP
        self.assertEqual(self.streak.xp, 80)  # Total XP should accumulate

    def test_problem_xp_cap(self):
        """Test daily problem XP cap"""
        # Try to earn more than 20 XP from problems
        self.streak.update_streak(problems_solved=10, lesson_ids=['lesson1'])
        self.assertEqual(self.streak.daily_xp, 40)  # 20 XP for streak + 20 XP (capped) for problems

    def test_daily_activity_tracking(self):
        """Test daily activity recording"""
        self.streak.update_streak(problems_solved=3, lesson_ids=['lesson1'])
        
        # Check if daily activity was created
        activity = DailyActivity.objects.get(user=self.user, date=timezone.now().date())
        self.assertEqual(activity.problems_solved, 3)
        self.assertEqual(activity.lesson_ids, ['lesson1'])
        self.assertEqual(activity.status, 'complete') 