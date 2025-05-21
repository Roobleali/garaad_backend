from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from courses.models import (
    UserLevel, Achievement, UserAchievement,
    CulturalEvent, UserCulturalProgress,
    CommunityContribution, UserReward,
    DailyChallenge, UserChallengeProgress,
    LeaderboardEntry, UserNotification,
    Course, Lesson, UserProgress, Category, CourseEnrollment
)
from accounts.models import StudentProfile
from datetime import timedelta
import json

User = get_user_model()

class IntegratedGamificationTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create student profile
        self.student_profile = StudentProfile.objects.create(
            user=self.user,
            preferred_study_time='morning',
            daily_goal_minutes=30,
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
        
        # Create user level
        self.user_level = UserLevel.objects.create(
            user=self.user,
            level=1,
            experience_points=0,
            experience_to_next_level=100,
            clan='Hawiye',
            region='Mogadishu',
            language_preference='so'
        )

        # Create category
        self.category = Category.objects.create(
            id='test-category',
            title='Test Category',
            description='Test Category Description',
            image='test.jpg'
        )

        # Create course
        self.course = Course.objects.create(
            category=self.category,
            title='Test Course',
            description='Test Description',
            author_id='test-author',
            is_published=True
        )
        
        self.lesson = Lesson.objects.create(
            course=self.course,
            title='Test Lesson',
            lesson_number=1,
            estimated_time=30,
            is_published=True
        )

        # Create initial achievements
        self.achievements = [
            Achievement.objects.create(
                name='Level 1 Achievement',
                description='Reach level 1',
                icon='level-1',
                points_reward=100,
                level_required=1,
                achievement_type='level_milestone'
            ),
            Achievement.objects.create(
                name='Level 2 Achievement',
                description='Reach level 2',
                icon='level-2',
                points_reward=200,
                level_required=2,
                achievement_type='level_milestone'
            )
        ]

    def test_complete_gamification_flow(self):
        """Test all gamification components working together"""
        
        # 1. Complete a lesson
        # First enroll in the course
        CourseEnrollment.enroll_user(self.user, self.course)
        
        progress = UserProgress.objects.create(
            user=self.user,
            lesson=self.lesson,
            status='not_started'
        )
        progress.mark_as_completed()
        
        # Verify lesson completion rewards
        self.assertTrue(
            UserReward.objects.filter(
                user=self.user,
                reward_type='points',
                reward_name='Lesson Completion'
            ).exists()
        )
        
        # 2. Create and complete daily challenge
        challenge = DailyChallenge.objects.create(
            title='Daily Test',
            description='Test Challenge',
            challenge_date=timezone.now().date(),
            points_reward=50
        )
        
        challenge_progress = UserChallengeProgress.objects.create(
            user=self.user,
            challenge=challenge,
            completed=True,
            score=100
        )
        
        # Award challenge points
        reward = UserReward.award_challenge_completion(self.user, challenge, 100)
        self.assertIsNotNone(reward)
        
        # 3. Participate in cultural event
        event = CulturalEvent.objects.create(
            name='Test Cultural Event',
            description='Test Description',
            event_date=timezone.now().date(),
            event_type='celebration',
            points_reward=100,
            is_active=True
        )
        
        event_progress = UserCulturalProgress.objects.create(
            user=self.user,
            event=event,
            completed=True,
            completed_at=timezone.now(),
            points_earned=event.points_reward
        )
        
        # Add experience points for event
        self.user_level.add_experience(event.points_reward)
        
        # 4. Make community contribution
        contribution = CommunityContribution.objects.create(
            user=self.user,
            contribution_type='cultural',
            description='Test contribution',
            points_awarded=150,
            verified=True
        )
        
        # Add experience for contribution
        self.user_level.add_experience(contribution.points_awarded)
        
        # 5. Check achievements
        achievement = Achievement.objects.create(
            name='Test Achievement',
            description='Test Description',
            icon='test-icon',
            points_reward=200,
            level_required=1,
            achievement_type='challenge_completion'
        )
        
        user_achievement = UserAchievement.objects.create(
            user=self.user,
            achievement=achievement
        )
        
        # Create achievement notification
        notification = UserNotification.create_achievement_notification(
            self.user, 
            achievement  # Pass the achievement object directly
        )
        
        # 6. Verify leaderboard updates
        LeaderboardEntry.update_points(self.user)
        
        # Final verification
        self.assertGreater(self.user_level.level, 1)  # Should have leveled up
        self.assertTrue(UserReward.objects.filter(user=self.user).exists())
        self.assertTrue(UserAchievement.objects.filter(user=self.user).exists())
        self.assertTrue(UserNotification.objects.filter(user=self.user).exists())
        self.assertTrue(LeaderboardEntry.objects.filter(user=self.user).exists())
        
        # Verify total points on leaderboard
        leaderboard_entry = LeaderboardEntry.objects.get(
            user=self.user,
            time_period='all_time'
        )
        expected_points = sum(
            reward.value for reward in 
            UserReward.objects.filter(user=self.user, reward_type='points')
        )
        self.assertEqual(leaderboard_entry.points, expected_points)

    def test_streak_system(self):
        """Test streak maintenance and rewards"""
        # Create streak rewards for 3 consecutive days
        for i in range(3):
            UserReward.objects.create(
                user=self.user,
                reward_type='streak',
                reward_name=f'Day {i+1} Streak',
                value=i+1,
                awarded_at=timezone.now() - timedelta(days=i)
            )
        
        # Verify streak count
        latest_streak = UserReward.objects.filter(
            user=self.user,
            reward_type='streak'
        ).order_by('-awarded_at').first()
        
        self.assertEqual(latest_streak.value, 3)
        
        # Create streak reminder notification
        notification = UserNotification.objects.create(
            user=self.user,
            notification_type='streak_reminder',
            title='Ilaaligaaga Waxbarashada!',
            message=f'Waxaa kuu hadhay {latest_streak.value} maalmood oo aad ilaalisid. Soo gal maanta oo dhammaystir casharkaaga!',
            scheduled_for=timezone.now() + timedelta(hours=1)
        )
        
        self.assertTrue(notification.scheduled_for > timezone.now())

    def test_level_progression(self):
        """Test level progression and rewards"""
        initial_level = self.user_level.level
        
        # Add significant experience points
        self.user_level.add_experience(500)
        
        # Verify level up occurred
        self.assertGreater(self.user_level.level, initial_level)
        
        # Verify level-up achievements
        achievements = Achievement.objects.filter(
            level_required__lte=self.user_level.level,
            achievement_type='level_milestone'
        )
        
        for achievement in achievements:
            UserAchievement.objects.get_or_create(
                user=self.user,
                achievement=achievement
            )
        
        # Verify achievements were created
        self.assertTrue(
            UserAchievement.objects.filter(
                user=self.user,
                achievement__achievement_type='level_milestone'
            ).exists()
        ) 