from django.core.management.base import BaseCommand
from django.utils import timezone
from courses.services import NotificationService
from courses.models import UserNotification
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sends scheduled notifications to users'

    def handle(self, *args, **options):
        try:
            # Process all scheduled notifications
            NotificationService.process_scheduled_notifications()
            
            # Clean up old notifications
            one_month_ago = timezone.now() - timezone.timedelta(days=30)
            old_notifications = UserNotification.objects.filter(
                created_at__lt=one_month_ago,
                is_sent=True
            )
            deleted_count = old_notifications.delete()[0]
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully processed notifications and cleaned up {deleted_count} old notifications'
                )
            )
            
        except Exception as e:
            logger.error(f"Error processing notifications: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Error processing notifications: {str(e)}')
            ) 