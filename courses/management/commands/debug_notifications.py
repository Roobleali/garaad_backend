from django.core.management.base import BaseCommand
from django.utils import timezone
from courses.models import UserNotification
from courses.services import NotificationService
from accounts.models import User
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Debug notification issues and test email sending'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-email',
            action='store_true',
            help='Test email sending to a specific user',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to test email sending with',
        )
        parser.add_argument(
            '--fix-scheduled',
            action='store_true',
            help='Fix notifications scheduled in the past',
        )

    def handle(self, *args, **options):
        now = timezone.now()
        
        self.stdout.write(f"Current time: {now}")
        self.stdout.write(f"Current timezone: {timezone.get_current_timezone()}")
        
        # Show notification statistics
        total_notifications = UserNotification.objects.count()
        unsent_notifications = UserNotification.objects.filter(is_sent=False).count()
        due_notifications = UserNotification.objects.filter(
            is_sent=False,
            scheduled_for__lte=now
        ).count()
        past_notifications = UserNotification.objects.filter(
            scheduled_for__lt=now
        ).count()
        
        self.stdout.write(f"Total notifications: {total_notifications}")
        self.stdout.write(f"Unsent notifications: {unsent_notifications}")
        self.stdout.write(f"Due notifications: {due_notifications}")
        self.stdout.write(f"Past scheduled notifications: {past_notifications}")
        
        # Show recent notifications
        recent_notifications = UserNotification.objects.order_by('-created_at')[:10]
        self.stdout.write("\nRecent notifications:")
        for notification in recent_notifications:
            status = "SENT" if notification.is_sent else "PENDING"
            scheduled_info = f" (scheduled for {notification.scheduled_for})" if notification.scheduled_for else ""
            self.stdout.write(f"  - {notification.user.username}: {notification.notification_type} - {status}{scheduled_info}")
        
        # Fix notifications scheduled in the past
        if options['fix_scheduled']:
            past_notifications = UserNotification.objects.filter(
                is_sent=False,
                scheduled_for__lt=now
            )
            fixed_count = 0
            for notification in past_notifications:
                # Reschedule for 5 minutes from now
                notification.scheduled_for = now + timezone.timedelta(minutes=5)
                notification.save()
                fixed_count += 1
            self.stdout.write(f"Fixed {fixed_count} notifications scheduled in the past")
        
        # Test email sending
        if options['test_email']:
            if options['user_id']:
                try:
                    user = User.objects.get(id=options['user_id'])
                    self.stdout.write(f"Testing email sending for user: {user.username} ({user.email})")
                    
                    # Create a test notification
                    test_notification = UserNotification.objects.create(
                        user=user,
                        notification_type='daily_goal',
                        title='Test Notification',
                        message='This is a test notification to verify email sending.',
                        scheduled_for=now
                    )
                    
                    # Try to send the email
                    success = NotificationService.send_notification_email(test_notification)
                    
                    if success:
                        self.stdout.write(self.style.SUCCESS("Test email sent successfully!"))
                    else:
                        self.stdout.write(self.style.ERROR("Test email failed to send"))
                        
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"User with ID {options['user_id']} not found"))
            else:
                self.stdout.write(self.style.ERROR("Please provide --user-id when using --test-email"))
        
        # Show due notifications details
        if due_notifications > 0:
            self.stdout.write(f"\nDue notifications details:")
            for notification in UserNotification.objects.filter(
                is_sent=False,
                scheduled_for__lte=now
            )[:5]:  # Show first 5
                self.stdout.write(f"  - ID: {notification.id}, User: {notification.user.username}, Type: {notification.notification_type}, Scheduled: {notification.scheduled_for}") 