import pytest
from django.test import TestCase
from django.utils import timezone
from django.core import mail
from django.contrib.auth import get_user_model
from accounts.models import StudentProfile, User
from courses.models import UserNotification
from courses.services import NotificationService
import json

class TestNotificationGamification(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create student profile
        self.profile = StudentProfile.objects.create(
            user=self.user,
            preferred_study_time='morning',
            daily_goal_minutes=15,
            streak_charges=2,
            notification_preferences={
                'email_notifications': True,
                'streak_reminders': True,
                'achievement_notifications': True,
                'daily_goal_reminders': True,
                'league_updates': True
            },
            subjects='["Xisaab", "Saynis"]',
            proficiency_level='Beginner',
            study_frequency=5
        )

    def test_student_profile_creation(self):
        """Test student profile is created with correct defaults"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.preferred_study_time, 'morning')
        self.assertEqual(self.profile.daily_goal_minutes, 15)
        self.assertEqual(self.profile.streak_charges, 2)
        self.assertEqual(self.profile.get_subjects(), ["Xisaab", "Saynis"])

    def test_study_time_badges(self):
        """Test study time badges are returned correctly"""
        # Test morning badge
        self.profile.preferred_study_time = 'morning'
        self.profile.save()
        self.assertIn('يَعْلَمُونَ', self.profile.get_study_time_badge())

        # Test afternoon badge
        self.profile.preferred_study_time = 'afternoon'
        self.profile.save()
        self.assertIn('زِدْنِي عِلْمًا', self.profile.get_study_time_badge())

    def test_goal_badges(self):
        """Test goal badges are returned correctly"""
        # Test different goal minutes
        self.profile.daily_goal_minutes = 5
        self.profile.save()
        self.assertEqual(self.profile.get_goal_badge(), "Talaabo yar, guul weyn")

        self.profile.daily_goal_minutes = 20
        self.profile.save()
        self.assertEqual(self.profile.get_goal_badge(), "Waxbarasho joogto ah")

    def test_streak_charges(self):
        """Test streak charge functionality"""
        initial_charges = self.profile.streak_charges
        
        # Test using a streak charge
        self.assertTrue(self.profile.use_streak_charge())
        self.assertEqual(self.profile.streak_charges, initial_charges - 1)
        
        # Test adding streak charges
        self.profile.add_streak_charge(2)
        self.assertEqual(self.profile.streak_charges, initial_charges + 1)

    def test_notification_email_sending(self):
        """Test notification emails are sent correctly"""
        # Test daily goal reminder
        notification_service = NotificationService()
        reminder = notification_service.schedule_daily_reminder(self.user)
        
        # Force send the notification
        success = notification_service.send_notification_email(reminder)
        self.assertTrue(success)
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Waqtiga Waxbarashada!', mail.outbox[0].subject)
        self.assertIn(str(self.profile.daily_goal_minutes), mail.outbox[0].body)

    def test_notification_scheduling(self):
        """Test notification scheduling works correctly"""
        notification_service = NotificationService()
        reminder = notification_service.schedule_daily_reminder(self.user)
        
        # Check reminder is scheduled for correct time
        reminder_hour = self.profile.get_reminder_time()
        scheduled_time = reminder.scheduled_for
        
        self.assertEqual(scheduled_time.hour, reminder_hour)
        self.assertTrue(scheduled_time > timezone.now())

    def test_streak_reminder(self):
        """Test streak reminder notifications"""
        notification_service = NotificationService()
        success = notification_service.send_streak_reminder(
            user=self.user,
            streak_count=5,
            streak_charge=2
        )
        
        self.assertTrue(success)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('streak charges', mail.outbox[0].body)

    def test_achievement_notification(self):
        """Test achievement notifications"""
        notification_service = NotificationService()
        success = notification_service.send_achievement_notification(
            user=self.user,
            achievement={
                'name': 'First Lesson Complete',
                'description': 'Completed your first lesson'
            }
        )
        
        self.assertTrue(success)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Hambalyo!', mail.outbox[0].subject)

    def test_league_update_notification(self):
        """Test league update notifications"""
        notification_service = NotificationService()
        success = notification_service.send_league_update(
            user=self.user,
            league_position=1,
            league_name='Gold League'
        )
        
        self.assertTrue(success)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Warbixin Tartanka!', mail.outbox[0].subject) 