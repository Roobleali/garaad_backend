from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Reset admin password for a specific email'

    def handle(self, *args, **options):
        try:
            user = User.objects.get(email='info@garaad.org')
            user.set_password('new_admin_password_123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Successfully reset password for info@garaad.org'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User with email info@garaad.org does not exist'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}')) 