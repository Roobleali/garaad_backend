from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from courses.models import (
    UserLevel, Achievement, UserAchievement,
    CulturalEvent, UserCulturalProgress,
    CommunityContribution, UserReward
)
from datetime import timedelta

User = get_user_model()

class GamificationTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
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
        
        # Create test achievement
        self.achievement = Achievement.objects.create(
            name='Dhalasho Cusub',
            description='Complete your first daily challenge',
            icon='first-challenge',
            points_reward=50,
            level_required=1,
            achievement_type='challenge_completion'
        )
        
        # Create test cultural event
        self.cultural_event = CulturalEvent.objects.create(
            name='Eid al-Fitr Celebration',
            description='Join our Eid celebration and learn about Somali traditions',
            event_date=timezone.now().date() + timedelta(days=7),
            event_type='celebration',
            points_reward=100,
            is_active=True
        )

    def test_user_level_progression(self):
        """Test user level progression system"""
        # Add experience points
        self.user_level.add_experience(150)
        
        # Check level up
        self.assertEqual(self.user_level.level, 2)
        self.assertEqual(self.user_level.experience_points, 50)
        self.assertEqual(self.user_level.experience_to_next_level, 150)

    def test_achievement_system(self):
        """Test achievement system"""
        # Create user achievement
        user_achievement = UserAchievement.objects.create(
            user=self.user,
            achievement=self.achievement
        )
        
        # Verify achievement
        self.assertEqual(user_achievement.achievement, self.achievement)
        self.assertEqual(user_achievement.user, self.user)

    def test_cultural_event_participation(self):
        """Test cultural event participation"""
        # Create user progress for event
        progress = UserCulturalProgress.objects.create(
            user=self.user,
            event=self.cultural_event,
            completed=True,
            completed_at=timezone.now(),
            points_earned=self.cultural_event.points_reward
        )
        
        # Verify progress
        self.assertTrue(progress.completed)
        self.assertEqual(progress.points_earned, self.cultural_event.points_reward)

    def test_community_contribution(self):
        """Test community contribution system"""
        # Create contribution
        contribution = CommunityContribution.objects.create(
            user=self.user,
            contribution_type='cultural',
            description='Shared traditional Somali poetry',
            points_awarded=150,
            verified=True
        )
        
        # Verify contribution
        self.assertEqual(contribution.points_awarded, 150)
        self.assertTrue(contribution.verified)

    def test_reward_system(self):
        """Test reward system"""
        # Create reward
        reward = UserReward.objects.create(
            user=self.user,
            reward_type='points',
            reward_name='Cultural Contribution',
            value=150
        )
        
        # Verify reward
        self.assertEqual(reward.value, 150)
        self.assertEqual(reward.reward_type, 'points')

    def test_integrated_gamification_flow(self):
        """Test complete gamification flow"""
        # 1. User participates in cultural event
        progress = UserCulturalProgress.objects.create(
            user=self.user,
            event=self.cultural_event,
            completed=True,
            completed_at=timezone.now(),
            points_earned=self.cultural_event.points_reward
        )
        
        # 2. Add experience points
        self.user_level.add_experience(self.cultural_event.points_reward)
        
        # 3. Create reward
        reward = UserReward.objects.create(
            user=self.user,
            reward_type='points',
            reward_name='Cultural Event Participation',
            value=self.cultural_event.points_reward
        )
        
        # 4. Check if achievement is unlocked
        if self.user_level.level >= self.achievement.level_required:
            user_achievement = UserAchievement.objects.create(
                user=self.user,
                achievement=self.achievement
            )
        
        # Verify final state
        self.assertTrue(progress.completed)
        self.assertEqual(reward.value, self.cultural_event.points_reward)
        self.assertTrue(UserAchievement.objects.filter(
            user=self.user,
            achievement=self.achievement
        ).exists()) 