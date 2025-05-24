import pytest
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from courses.models import (
    Course, Lesson, UserProgress, UserLevel,
    UserReward, Achievement, UserAchievement, LeaderboardEntry
)
from courses.services import LearningProgressService

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def course(db):
    return Course.objects.create(
        title='Test Course',
        description='Test Description'
    )

@pytest.fixture
def lesson(db, course):
    return Lesson.objects.create(
        title='Test Lesson',
        description='Test Lesson Description',
        course=course
    )

@pytest.fixture
def achievement(db):
    return Achievement.objects.create(
        name='Test Achievement',
        description='Test Achievement Description',
        achievement_type='streak_milestone',
        level_required=1
    )

class TestLearningProgressService(TestCase):
    def test_process_lesson_completion(self, user, lesson):
        """Test basic lesson completion processing"""
        result = LearningProgressService.process_lesson_completion(
            user=user,
            lesson=lesson,
            score=100
        )
        
        # Check progress
        assert result['progress'].status == 'completed'
        assert result['progress'].score == 100
        
        # Check rewards
        assert result['rewards']['xp'] == 15  # Base 10 + Perfect score bonus 5
        assert result['rewards']['streak'] == 5  # Base streak points
        
        # Check user level
        user_level = UserLevel.objects.get(user=user)
        assert user_level.experience_points == 15
        
        # Check streak reward
        streak_reward = UserReward.objects.get(
            user=user,
            reward_type='streak'
        )
        assert streak_reward.value == 5

    def test_streak_multipliers(self, user, lesson):
        """Test streak multiplier system"""
        # Complete lessons for 3 consecutive days
        for days_ago in range(3):
            completion_date = timezone.now() - timedelta(days=days_ago)
            UserProgress.objects.create(
                user=user,
                lesson=lesson,
                status='completed',
                completed_at=completion_date
            )
        
        # Complete another lesson today
        result = LearningProgressService.process_lesson_completion(
            user=user,
            lesson=lesson,
            score=100
        )
        
        # Should get 1.5x multiplier for 3-day streak
        assert result['rewards']['streak'] == 7  # 5 * 1.5 rounded down
        assert result['rewards']['streak_days'] == 4

    def test_achievement_awarding(self, user, lesson, achievement):
        """Test achievement awarding system"""
        # Complete lessons for 3 consecutive days
        for days_ago in range(3):
            completion_date = timezone.now() - timedelta(days=days_ago)
            UserProgress.objects.create(
                user=user,
                lesson=lesson,
                status='completed',
                completed_at=completion_date
            )
        
        # Complete another lesson today
        result = LearningProgressService.process_lesson_completion(
            user=user,
            lesson=lesson,
            score=100
        )
        
        # Check if achievement was awarded
        assert len(result['achievements']) > 0
        assert any(a.id == achievement.id for a in result['achievements'])
        
        # Verify achievement was saved
        user_achievement = UserAchievement.objects.get(
            user=user,
            achievement=achievement
        )
        assert user_achievement is not None

    def test_leaderboard_update(self, user, lesson):
        """Test leaderboard update after lesson completion"""
        # Complete a lesson
        result = LearningProgressService.process_lesson_completion(
            user=user,
            lesson=lesson,
            score=100
        )
        
        # Check leaderboard entry
        leaderboard_entry = LeaderboardEntry.objects.get(
            user=user,
            time_period='weekly'
        )
        assert leaderboard_entry.points > 0

    def test_perfect_score_bonus(self, user, lesson):
        """Test perfect score bonus"""
        result = LearningProgressService.process_lesson_completion(
            user=user,
            lesson=lesson,
            score=100
        )
        
        # Should get perfect score bonus
        assert result['rewards']['xp'] == 15  # Base 10 + Perfect score bonus 5
        
        # Regular score should not get bonus
        result = LearningProgressService.process_lesson_completion(
            user=user,
            lesson=lesson,
            score=80
        )
        assert result['rewards']['xp'] == 10  # Only base XP

    def test_streak_break(self, user, lesson):
        """Test streak break after missing a day"""
        # Complete lessons for 2 consecutive days
        for days_ago in range(2):
            completion_date = timezone.now() - timedelta(days=days_ago)
            UserProgress.objects.create(
                user=user,
                lesson=lesson,
                status='completed',
                completed_at=completion_date
            )
        
        # Skip a day and complete another lesson
        completion_date = timezone.now() - timedelta(days=3)
        UserProgress.objects.create(
            user=user,
            lesson=lesson,
            status='completed',
            completed_at=completion_date
        )
        
        # Complete a lesson today
        result = LearningProgressService.process_lesson_completion(
            user=user,
            lesson=lesson,
            score=100
        )
        
        # Streak should be reset
        assert result['rewards']['streak_days'] == 1
        assert result['rewards']['streak'] == 5  # Base streak points 