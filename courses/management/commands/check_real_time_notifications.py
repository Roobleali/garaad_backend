from django.core.management.base import BaseCommand
from django.utils import timezone
from courses.services import NotificationService
from accounts.models import User
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check all users for real-time notifications and send them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Check notifications for a specific user ID',
        )
        parser.add_argument(
            '--force-send',
            action='store_true',
            help='Force send notifications even if recently sent',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        force_send = options.get('force_send')
        dry_run = options.get('dry_run')
        
        if dry_run:
            self.stdout.write("DRY RUN MODE - No emails will be sent")
        
        if user_id:
            # Check specific user
            try:
                user = User.objects.get(id=user_id)
                self.stdout.write(f"Checking notifications for user: {user.username} ({user.email})")
                self.check_user_notifications(user, force_send, dry_run)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User with ID {user_id} not found"))
        else:
            # Check all users
            users = User.objects.filter(is_active=True)
            self.stdout.write(f"Checking notifications for {users.count()} active users...")
            
            processed_count = 0
            for user in users:
                try:
                    if self.check_user_notifications(user, force_send, dry_run):
                        processed_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing user {user.id}: {e}"))
            
            self.stdout.write(
                self.style.SUCCESS(f"Processed notifications for {processed_count} users")
            )

    def check_user_notifications(self, user, force_send=False, dry_run=False):
        """
        Check and send real-time notifications for a specific user.
        """
        try:
            # Check for streak break
            streak_broken, streak_count = NotificationService.is_streak_broken(user)
            if streak_broken:
                self.stdout.write(f"  ✓ Streak broken for user {user.username} (streak: {streak_count})")
                if not dry_run:
                    NotificationService.send_streak_break_reminder(user, streak_count)
                return True
            
            # Check for inactivity
            inactive_days = NotificationService.get_inactivity_days(user)
            if inactive_days and inactive_days >= 1:
                self.stdout.write(f"  ✓ User {user.username} inactive for {inactive_days} days")
                if not dry_run:
                    NotificationService.send_inactivity_reminder(user)
                return True
            
            # Check for daily reminder (if user hasn't been active today)
            try:
                from api.models import Streak
                streak = Streak.objects.get(user=user)
                if streak.last_activity_date != timezone.now().date():
                    self.stdout.write(f"  ✓ Sending daily reminder to {user.username}")
                    if not dry_run:
                        NotificationService.send_daily_reminder_notification(user)
                    return True
            except Streak.DoesNotExist:
                pass
            
            # Run comprehensive check
            if not dry_run:
                NotificationService.check_and_send_real_time_reminders(user)
            
            return False
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error checking notifications for user {user.username}: {e}"))
            return False 