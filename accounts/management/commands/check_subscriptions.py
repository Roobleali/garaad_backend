from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from api.models import Notification

class Command(BaseCommand):
    help = 'Check and update subscription statuses for all users'

    def handle(self, *args, **options):
        # Get all premium users
        premium_users = User.objects.filter(is_premium=True)
        expired_count = 0
        
        for user in premium_users:
            if not user.is_subscription_active():
                # Update user's premium status
                user.is_premium = False
                user.save()
                expired_count += 1
                
                # Create notification for expired subscription
                Notification.objects.create(
                    user=user,
                    type='reminder',
                    title='Xasuuso Premium-kaaga',
                    message='Premium-kaaga wuu dhacay. Dib u noqo si aad u hesho dhammaan awoodaha.',
                    data={
                        'premium_status': False,
                        'subscription_type': user.subscription_type,
                        'subscription_end_date': user.subscription_end_date.isoformat() if user.subscription_end_date else None
                    }
                )
                
                self.stdout.write(f"Subscription expired for user: {user.email}")
        
        self.stdout.write(self.style.SUCCESS(f'Successfully checked subscriptions. {expired_count} subscriptions expired.')) 