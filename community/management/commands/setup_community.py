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
            # Create campuses with Somali names
            campuses_data = [
                {
                    'name': 'Physics Campus',
                    'name_somali': 'Campus Fiisigis',
                    'description': 'Explore the fundamental laws of nature and the universe.',
                    'description_somali': 'Baadh sharciyada asaasiga ah ee dabeecadda iyo koonka.',
                    'subject_tag': 'physics',
                    'icon': '⚛️',
                    'color_code': '#3B82F6'
                },
                {
                    'name': 'Mathematics Campus',
                    'name_somali': 'Campus Xisaab',
                    'description': 'Master the language of numbers and logical reasoning.',
                    'description_somali': 'Ka talisid luuqadda lambarrada iyo fekerka mantiqiga ah.',
                    'subject_tag': 'math',
                    'icon': '📐',
                    'color_code': '#10B981'
                },
                {
                    'name': 'Cryptocurrency Campus',
                    'name_somali': 'Campus Qarsoodiga',
                    'description': 'Learn about blockchain technology and digital currencies.',
                    'description_somali': 'Wax ka baro tignoolajiyada blockchain iyo lacagaha dijitaalka ah.',
                    'subject_tag': 'crypto',
                    'icon': '₿',
                    'color_code': '#F59E0B'
                },
                {
                    'name': 'Biology Campus',
                    'name_somali': 'Campus Bayooloji',
                    'description': 'Discover the wonders of life and living organisms.',
                    'description_somali': 'Ogaada yaabka nolosha iyo noolasha.',
                    'subject_tag': 'biology',
                    'icon': '🧬',
                    'color_code': '#8B5CF6'
                },
                {
                    'name': 'Chemistry Campus',
                    'name_somali': 'Campus Kimistar',
                    'description': 'Explore the composition and properties of matter.',
                    'description_somali': 'Baadh halbeegga iyo sifooyinka maadada.',
                    'subject_tag': 'chemistry',
                    'icon': '🧪',
                    'color_code': '#EF4444'
                },
                {
                    'name': 'History Campus',
                    'name_somali': 'Campus Taariikh',
                    'description': 'Journey through time and learn from the past.',
                    'description_somali': 'Safar dhex mara waqtiga oo wax ka baro wixii hore.',
                    'subject_tag': 'history',
                    'icon': '📜',
                    'color_code': '#92400E'
                },
                {
                    'name': 'Literature Campus',
                    'name_somali': 'Campus Suugaan',
                    'description': 'Explore the beauty of language and storytelling.',
                    'description_somali': 'Baadh quruxda luuqadda iyo sheekooyin-sheegista.',
                    'subject_tag': 'literature',
                    'icon': '📚',
                    'color_code': '#DC2626'
                },
                {
                    'name': 'Technology Campus',
                    'name_somali': 'Campus Tignoolajiyada',
                    'description': 'Stay ahead with the latest in technology and innovation.',
                    'description_somali': 'Ka hor joog tignoolajiyada cusub iyo hal-abuurka.',
                    'subject_tag': 'technology',
                    'icon': '💻',
                    'color_code': '#1F2937'
                },
                {
                    'name': 'Business Campus',
                    'name_somali': 'Campus Ganacsi',
                    'description': 'Learn entrepreneurship and business strategies.',
                    'description_somali': 'Baro ganacsatada iyo xeeladaha ganacsiga.',
                    'subject_tag': 'business',
                    'icon': '💼',
                    'color_code': '#059669'
                },
                {
                    'name': 'Islamic Studies Campus',
                    'name_somali': 'Campus Casharo Diinta',
                    'description': 'Deepen your understanding of Islamic teachings.',
                    'description_somali': 'Korkari fahamkaaga casharka Islaamka.',
                    'subject_tag': 'islamic_studies',
                    'icon': '🕌',
                    'color_code': '#047857'
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
                        self.style.SUCCESS(f'✅ Created campus: {campus.name_somali}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'ℹ️  Campus already exists: {campus.name_somali}')
                    )

            # Create default rooms for each campus
            room_types_data = [
                {
                    'name': 'General Discussion',
                    'name_somali': 'Doodka Guud',
                    'description': 'General discussions about the subject',
                    'description_somali': 'Doodyo guud oo ku saabsan mawduuca',
                    'room_type': 'general'
                },
                {
                    'name': 'Study Group',
                    'name_somali': 'Kooxda Waxbarashada',
                    'description': 'Collaborative study sessions and homework help',
                    'description_somali': 'Waxbarasho wadajir ah iyo caawinta hawlaha guriga',
                    'room_type': 'study'
                },
                {
                    'name': 'Q&A Help',
                    'name_somali': 'Su\'aalaha iyo Jawaabaha',
                    'description': 'Ask questions and get help from the community',
                    'description_somali': 'Weydiis su\'aalo oo ka hel caawimo bulshada',
                    'room_type': 'help'
                },
                {
                    'name': 'Announcements',
                    'name_somali': 'Ogeysiisyada',
                    'description': 'Important announcements and updates',
                    'description_somali': 'Ogeysiisyo muhiim ah iyo cusbooneysiinta',
                    'room_type': 'announcements'
                },
                {
                    'name': 'Social Chat',
                    'name_somali': 'Sheeko Bulshada',
                    'description': 'Casual conversations and community building',
                    'description_somali': 'Sheeko fudud iyo dhismaha bulshada',
                    'room_type': 'social'
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