from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from courses.models import (
    UserLevel, Achievement, UserAchievement,
    CulturalEvent, UserCulturalProgress,
    CommunityContribution, UserReward
)
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Test the gamification system with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting gamification system test...')

        # Create test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'password': 'testpass123'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created test user'))

        # Create user level
        user_level, created = UserLevel.objects.get_or_create(
            user=user,
            defaults={
                'level': 1,
                'experience_points': 0,
                'experience_to_next_level': 100,
                'clan': 'Hawiye',
                'region': 'Mogadishu',
                'language_preference': 'so'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created user level'))

        # Create cultural event
        event = CulturalEvent.objects.create(
            name='Eid al-Fitr Celebration',
            description='Join our Eid celebration and learn about Somali traditions',
            event_date=timezone.now().date() + timedelta(days=7),
            event_type='celebration',
            points_reward=100,
            is_active=True
        )
        self.stdout.write(self.style.SUCCESS('Created cultural event'))

        # Simulate user participation
        progress = UserCulturalProgress.objects.create(
            user=user,
            event=event,
            completed=True,
            completed_at=timezone.now(),
            points_earned=event.points_reward
        )
        self.stdout.write(self.style.SUCCESS('Created event progress'))

        # Add experience points
        user_level.add_experience(event.points_reward)
        self.stdout.write(
            self.style.SUCCESS(
                f'Added {event.points_reward} experience points. '
                f'Current level: {user_level.level}'
            )
        )

        # Create community contribution
        contribution = CommunityContribution.objects.create(
            user=user,
            contribution_type='cultural',
            description='Shared traditional Somali poetry',
            points_awarded=150,
            verified=True
        )
        self.stdout.write(self.style.SUCCESS('Created community contribution'))

        # Add more experience points
        user_level.add_experience(contribution.points_awarded)
        self.stdout.write(
            self.style.SUCCESS(
                f'Added {contribution.points_awarded} experience points. '
                f'Current level: {user_level.level}'
            )
        )

        # Create reward
        reward = UserReward.objects.create(
            user=user,
            reward_type='points',
            reward_name='Cultural Contribution',
            value=contribution.points_awarded
        )
        self.stdout.write(self.style.SUCCESS('Created reward'))

        # Check achievements
        achievements = Achievement.objects.filter(level_required__lte=user_level.level)
        for achievement in achievements:
            UserAchievement.objects.get_or_create(
                user=user,
                achievement=achievement
            )
            self.stdout.write(
                self.style.SUCCESS(f'Unlocked achievement: {achievement.name}')
            )

        # Print final stats
        self.stdout.write('\nFinal Stats:')
        self.stdout.write(f'User Level: {user_level.level}')
        self.stdout.write(f'Experience Points: {user_level.experience_points}')
        self.stdout.write(f'Experience to Next Level: {user_level.experience_to_next_level}')
        self.stdout.write(f'Total Rewards: {UserReward.objects.filter(user=user).count()}')
        self.stdout.write(f'Total Achievements: {UserAchievement.objects.filter(user=user).count()}')
        self.stdout.write(f'Cultural Events Participated: {UserCulturalProgress.objects.filter(user=user).count()}')
        self.stdout.write(f'Community Contributions: {CommunityContribution.objects.filter(user=user).count()}') 