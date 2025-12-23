from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from community.models import Campus, Room, UserCommunityProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up initial community data with campuses and rooms'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all community data before creating new data',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('🗑️  Resetting community data...')
            Campus.objects.all().delete()
            UserCommunityProfile.objects.all().delete()
            self.stdout.write(self.style.WARNING('All community data has been reset.'))

        self.stdout.write('🚀 Setting up community system...')
        
        with transaction.atomic():
            # Create campuses
            campuses_data = [
                {
                    'name': 'Fiisigis (Physics)',
                    'description': 'Baro sharciyada dabeecadda iyo koonka.',
                    'subject_tag': 'physics',
                    'icon': '⚛️',
                    'color_code': '#3B82F6'
                },
                {
                    'name': 'Xisaab (Math)',
                    'description': 'Baro luuqadda lambarrada iyo fekerka mantiqiga ah.',
                    'subject_tag': 'math',
                    'icon': '📐',
                    'color_code': '#10B981'
                },
                {
                    'name': 'Qarsoodiga (Crypto)',
                    'description': 'Wax ka baro blockchain iyo lacagaha dijitaalka ah.',
                    'subject_tag': 'crypto',
                    'icon': '₿',
                    'color_code': '#F59E0B'
                },
                {
                    'name': 'Bayooloji (Biology)',
                    'description': 'Baro nolosha iyo noolaha.',
                    'subject_tag': 'biology',
                    'icon': '🧬',
                    'color_code': '#8B5CF6'
                }
            ]

            created_campuses = []
            for campus_data in campuses_data:
                campus, created = Campus.objects.get_or_create(
                    subject_tag=campus_data['subject_tag'],
                    defaults=campus_data
                )
                created_campuses.append(campus)
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Created campus: {campus.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'ℹ️  Campus already exists: {campus.name}')
                    )

            # Create default rooms for each campus
            room_types_data = [
                {
                    'name': 'sheeko-guud',
                    'description': 'Doodyo guud oo ku saabsan mawduuca',
                    'room_type': 'chat',
                    'icon': 'hashtag',
                    'order': 10
                },
                {
                    'name': 'waxbarasho',
                    'description': 'Waxbarasho wadajir ah iyo caawimo',
                    'room_type': 'study',
                    'icon': 'graduation-cap',
                    'order': 20
                },
                {
                    'name': 'ogeysiisyada',
                    'description': 'Ogeysiisyo muhiim ah',
                    'room_type': 'announcement',
                    'icon': 'megaphone',
                    'order': 0
                }
            ]

            total_rooms_created = 0
            for campus in created_campuses:
                for room_data in room_types_data:
                    room_info = room_data.copy()
                    room_info['campus'] = campus
                    
                    room, created = Room.objects.get_or_create(
                        campus=campus,
                        name=room_data['name'],
                        defaults=room_info
                    )
                    
                    if created:
                        total_rooms_created += 1

            self.stdout.write(
                self.style.SUCCESS(f'✅ Created {total_rooms_created} rooms across all campuses')
            )

            # Create community profiles for existing users
            users_count = 0
            for user in User.objects.all():
                profile, created = UserCommunityProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'community_points': 0,
                        'badge_level': 'dhalinyaro',
                        'preferred_language': 'so'
                    }
                )
                if created:
                    users_count += 1

            self.stdout.write(
                self.style.SUCCESS(f'✅ Created community profiles for {users_count} users')
            )

        self.stdout.write('\n🎉 Community system setup completed successfully!')
        self.stdout.write('\n📊 Summary:')
        self.stdout.write(f'   • Campuses: {Campus.objects.count()}')
        self.stdout.write(f'   • Rooms: {Room.objects.count()}')
        self.stdout.write(f'   • User Profiles: {UserCommunityProfile.objects.count()}')
        
        self.stdout.write('\n🚀 Next steps:')
        self.stdout.write('   1. Users can now join campuses through the API')
        self.stdout.write('   2. Create posts and comments in rooms')
        self.stdout.write('   3. Like content and earn points')
        self.stdout.write('   4. Check the admin panel for moderation tools')
        
        self.stdout.write('\n📚 Available API endpoints:')
        self.stdout.write('   • GET /api/community/api/campuses/ - List all campuses')
        self.stdout.write('   • POST /api/community/api/campuses/{slug}/join/ - Join a campus')
        self.stdout.write('   • GET /api/community/api/campuses/{slug}/rooms/ - Get campus rooms')
        self.stdout.write('   • POST /api/community/api/posts/ - Create a new post')
        self.stdout.write('   • POST /api/community/api/comments/ - Add a comment')
        self.stdout.write('   • GET /api/community/api/profiles/me/ - Get user profile')
        self.stdout.write('   • GET /api/community/api/notifications/ - Get notifications') 