from django.core.management.base import BaseCommand
from courses.models import Category


class Command(BaseCommand):
    help = 'Enable community features on specific categories'

    def add_arguments(self, parser):
        parser.add_argument(
            'category_ids',
            nargs='+',
            type=str,
            help='Category IDs to enable community on (e.g., physics math ai)'
        )
        parser.add_argument(
            '--description',
            type=str,
            default='',
            help='Community description for these categories'
        )

    def handle(self, *args, **options):
        category_ids = options['category_ids']
        description = options['description']
        
        self.stdout.write('🚀 Enabling community features...\n')
        
        enabled_count = 0
        for category_id in category_ids:
            try:
                category = Category.objects.get(id=category_id)
                category.is_community_enabled = True
                if description:
                    category.community_description = description
                category.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Enabled community on: {category.title}')
                )
                enabled_count += 1
                
            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Category not found: {category_id}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Enabled community on {enabled_count} categories!')
        )
