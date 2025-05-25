from django.core.management.base import BaseCommand
from leagues.models import League

class Command(BaseCommand):
    help = 'Initialize league levels with Somali cultural names'

    def handle(self, *args, **kwargs):
        leagues = [
            {
                'name': 'Biyo',
                'somali_name': 'Biyo',
                'description': 'The first step in your learning journey',
                'min_xp': 0,
                'order': 1
            },
            {
                'name': 'Geesi',
                'somali_name': 'Geesi',
                'description': 'A hero in learning',
                'min_xp': 1000,
                'order': 2
            },
            {
                'name': 'Ogow',
                'somali_name': 'Ogow',
                'description': 'A knowledgeable learner',
                'min_xp': 2500,
                'order': 3
            },
            {
                'name': 'Iftiin',
                'somali_name': 'Iftiin',
                'description': 'Bringing light to others',
                'min_xp': 5000,
                'order': 4
            },
            {
                'name': 'Bir Adag',
                'somali_name': 'Bir Adag',
                'description': 'Strong and resilient in learning',
                'min_xp': 10000,
                'order': 5
            },
            {
                'name': 'Ugaas',
                'somali_name': 'Ugaas',
                'description': 'A leader in knowledge',
                'min_xp': 20000,
                'order': 6
            },
            {
                'name': 'Abwaan',
                'somali_name': 'Abwaan',
                'description': 'A scholar and poet of learning',
                'min_xp': 35000,
                'order': 7
            },
            {
                'name': 'Ilbax',
                'somali_name': 'Ilbax',
                'description': 'Civilized and cultured in knowledge',
                'min_xp': 50000,
                'order': 8
            },
            {
                'name': 'Guuleyste',
                'somali_name': 'Guuleyste',
                'description': 'An achiever in learning',
                'min_xp': 75000,
                'order': 9
            },
            {
                'name': 'Farsamo-yahan',
                'somali_name': 'Farsamo-yahan',
                'description': 'A genius in knowledge',
                'min_xp': 100000,
                'order': 10
            }
        ]

        for league_data in leagues:
            League.objects.get_or_create(
                name=league_data['name'],
                defaults=league_data
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created league "{league_data["name"]}"')
            ) 