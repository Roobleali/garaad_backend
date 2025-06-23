from django.core.management.base import BaseCommand
from django.utils import timezone
from courses.services import NotificationService
from accounts.models import User
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test real-time reminder system with different types of reminders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            required=True,
            help='User ID to test reminders with',
        )
        parser.add_argument(
            '--reminder-type',
            type=str,
            choices=['inactivity', 'streak_break', 'goal', 'motivational', 'immediate', 'all'],
            default='all',
            help='Type of reminder to test',
        )
        parser.add_argument(
            '--days-inactive',
            type=int,
            default=3,
            help='Number of days inactive for inactivity reminder',
        )
        parser.add_argument(
            '--streak-days',
            type=int,
            default=5,
            help='Number of streak days for streak break reminder',
        )
        parser.add_argument(
            '--goal-type',
            type=str,
            choices=['daily', 'weekly', 'monthly'],
            default='daily',
            help='Type of goal reminder',
        )
        parser.add_argument(
            '--motivation-type',
            type=str,
            choices=['first_lesson', 'streak_milestone', 'level_up', 'general'],
            default='general',
            help='Type of motivational reminder',
        )
        parser.add_argument(
            '--custom-message',
            type=str,
            help='Custom message for immediate reminder',
        )

    def handle(self, *args, **options):
        try:
            user = User.objects.get(id=options['user_id'])
            self.stdout.write(f"Testing real-time reminders for user: {user.username} ({user.email})")
            
            reminder_type = options['reminder_type']
            
            if reminder_type == 'all' or reminder_type == 'inactivity':
                self.stdout.write("Testing inactivity reminder...")
                success = NotificationService.send_inactivity_reminder(user)
                if success:
                    self.stdout.write(self.style.SUCCESS("Inactivity reminder sent successfully!"))
                else:
                    self.stdout.write(self.style.ERROR("Failed to send inactivity reminder"))
            
            if reminder_type == 'all' or reminder_type == 'streak_break':
                self.stdout.write("Testing streak break reminder...")
                success = NotificationService.send_streak_break_reminder(user, options['streak_days'])
                if success:
                    self.stdout.write(self.style.SUCCESS("Streak break reminder sent successfully!"))
                else:
                    self.stdout.write(self.style.ERROR("Failed to send streak break reminder"))
            
            if reminder_type == 'all' or reminder_type == 'goal':
                self.stdout.write("Testing goal reminder...")
                self.stdout.write(self.style.WARNING("Goal reminder method not implemented yet"))
            
            if reminder_type == 'all' or reminder_type == 'motivational':
                self.stdout.write("Testing motivational reminder...")
                self.stdout.write(self.style.WARNING("Motivational reminder method not implemented yet"))
            
            if reminder_type == 'all' or reminder_type == 'immediate':
                self.stdout.write("Testing immediate reminder...")
                self.stdout.write(self.style.WARNING("Immediate reminder method not implemented yet"))
            
            # Test the comprehensive real-time reminder checker
            if reminder_type == 'all':
                self.stdout.write("Testing comprehensive real-time reminder checker...")
                success = NotificationService.check_and_send_real_time_reminders(user)
                if success:
                    self.stdout.write(self.style.SUCCESS("Real-time reminder checker completed successfully!"))
                else:
                    self.stdout.write(self.style.ERROR("Real-time reminder checker failed"))
            
            self.stdout.write(self.style.SUCCESS("Real-time reminder testing completed!"))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User with ID {options['user_id']} not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error testing real-time reminders: {str(e)}"))
            logger.error(f"Error testing real-time reminders: {str(e)}") 