from django.core.management.base import BaseCommand
from courses.models import Achievement

class Command(BaseCommand):
    help = 'Creates initial achievements for the platform'

    def handle(self, *args, **kwargs):
        achievements = [
            {
                'name': 'Dhalasho Cusub',
                'description': 'Complete your first daily challenge',
                'icon': 'first-challenge',
                'points_reward': 50,
                'level_required': 1,
                'achievement_type': 'challenge_completion'
            },
            {
                'name': 'Maalintii Axad',
                'description': 'Complete 7 daily challenges',
                'icon': 'weekly-master',
                'points_reward': 200,
                'level_required': 5,
                'achievement_type': 'challenge_completion'
            },
            {
                'name': 'Bil Cusub',
                'description': 'Complete 30 daily challenges',
                'icon': 'monthly-master',
                'points_reward': 500,
                'level_required': 10,
                'achievement_type': 'challenge_completion'
            },
            {
                'name': 'Aqoon Badan',
                'description': 'Get a perfect score on any challenge',
                'icon': 'perfect-score',
                'points_reward': 100,
                'level_required': 1,
                'achievement_type': 'perfect_score'
            },
            {
                'name': 'Horumarinta',
                'description': 'Join the platform during its first month',
                'icon': 'early-adopter',
                'points_reward': 1000,
                'level_required': 1,
                'achievement_type': 'early_adopter'
            },
            {
                'name': 'Xirfadle',
                'description': 'Reach level 5',
                'icon': 'level-5',
                'points_reward': 200,
                'level_required': 5,
                'achievement_type': 'level_milestone'
            },
            {
                'name': 'Aqoonyahan',
                'description': 'Reach level 10',
                'icon': 'level-10',
                'points_reward': 500,
                'level_required': 10,
                'achievement_type': 'level_milestone'
            },
            {
                'name': 'Maalim',
                'description': 'Reach level 20',
                'icon': 'level-20',
                'points_reward': 1000,
                'level_required': 20,
                'achievement_type': 'level_milestone'
            },
            {
                'name': 'Aqoon Farxad',
                'description': 'Complete your first course',
                'icon': 'course-master',
                'points_reward': 300,
                'level_required': 3,
                'achievement_type': 'course_completion'
            },
            {
                'name': 'Dedication',
                'description': 'Maintain a 7-day learning streak',
                'icon': 'streak-master',
                'points_reward': 150,
                'level_required': 2,
                'achievement_type': 'streak_milestone'
            },
            {
                'name': 'Xeerka',
                'description': 'Follow all community guidelines for a month',
                'icon': 'community-respect',
                'points_reward': 200,
                'level_required': 3,
                'achievement_type': 'community'
            },
            {
                'name': 'Wadaag',
                'description': 'Help 5 other learners complete their challenges',
                'icon': 'helping-others',
                'points_reward': 250,
                'level_required': 4,
                'achievement_type': 'community'
            },
            {
                'name': 'Maanso',
                'description': 'Create and share educational content',
                'icon': 'content-creator',
                'points_reward': 300,
                'level_required': 5,
                'achievement_type': 'content'
            },
            {
                'name': 'Dhaqan',
                'description': 'Complete a course about Somali culture and traditions',
                'icon': 'culture',
                'points_reward': 400,
                'level_required': 6,
                'achievement_type': 'culture'
            }
        ]

        for achievement_data in achievements:
            Achievement.objects.get_or_create(
                name=achievement_data['name'],
                defaults=achievement_data
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created achievement "{achievement_data["name"]}"'
                )
            ) 