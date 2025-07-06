from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.utils import send_verification_email

User = get_user_model()

class Command(BaseCommand):
    help = 'Test email verification functionality with the new HTML template'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send verification to',
        )

    def handle(self, *args, **options):
        email = options['email']
        
        if not email:
            self.stdout.write(
                self.style.ERROR('Please provide an email address with --email')
            )
            return
        
        try:
            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'is_email_verified': False
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created new user: {user.email}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Found existing user: {user.email}')
                )
            
            # Send verification email
            self.stdout.write('Sending verification email...')
            success = send_verification_email(user)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS('✅ Email verification sent successfully!')
                )
                self.stdout.write(f'📧 Sent to: {user.email}')
                self.stdout.write('📄 Check your email for the new HTML template')
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Failed to send verification email')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {str(e)}')
            ) 