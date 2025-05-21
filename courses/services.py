from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from .models import UserNotification
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_notification_email(notification):
        """Send notification email to user"""
        try:
            # Get user's profile for personalization
            user_profile = notification.user.student_profile
            
            # Email templates based on notification type
            templates = {
                'streak_reminder': {
                    'subject': 'Ilaaligaaga Waxbarashada! 🔥',
                    'template': 'emails/streak_reminder.html',
                },
                'achievement_earned': {
                    'subject': 'Hambalyo! Guul Cusub! 🏆',
                    'template': 'emails/achievement_earned.html',
                },
                'league_update': {
                    'subject': 'Warbixin Tartanka! 🏅',
                    'template': 'emails/league_update.html',
                },
                'daily_goal': {
                    'subject': f'Waqtiga Waxbarashada! ({user_profile.daily_goal_minutes} Daqiiqo) 🎯',
                    'template': 'emails/daily_goal.html',
                },
            }

            template_info = templates.get(notification.notification_type)
            if not template_info:
                return False

            # Add personalized context
            context = {
                'user': notification.user,
                'notification': notification,
                'site_url': settings.SITE_URL,
                'study_badge': user_profile.get_study_time_badge(),
                'goal_badge': user_profile.get_goal_badge(),
                'daily_goal_minutes': user_profile.daily_goal_minutes,
                'preferred_study_time': user_profile.get_preferred_study_time_display()
            }

            # Send email
            send_mail(
                subject=template_info['subject'],
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                html_message=render_to_string(template_info['template'], context),
                fail_silently=False,
            )

            # Mark notification as sent
            notification.is_sent = True
            notification.save()

            return True

        except Exception as e:
            logger.error(f"Failed to send notification email: {str(e)}")
            return False

    @staticmethod
    def schedule_daily_reminder(user):
        """Schedule daily reminder based on user's preferred study time"""
        profile = user.student_profile
        reminder_hour = profile.get_reminder_time()
        
        # Calculate next reminder time
        now = timezone.now()
        reminder_time = now.replace(
            hour=reminder_hour,
            minute=0,
            second=0,
            microsecond=0
        )
        
        # If reminder time has passed for today, schedule for tomorrow
        if now >= reminder_time:
            reminder_time = reminder_time + timezone.timedelta(days=1)

        # Create reminder notification
        return UserNotification.objects.create(
            user=user,
            notification_type='daily_goal',
            title=f'Waqtiga Waxbarashada! ({profile.daily_goal_minutes} Daqiiqo)',
            message=(
                f'Waa waqtigii waxbarasho ee {profile.get_preferred_study_time_display()}!\n'
                f'Hadafkaaga maanta: {profile.daily_goal_minutes} daqiiqo\n'
                f'"{profile.get_goal_badge()}"\n'
                f'{profile.get_study_time_badge()}'
            ),
            scheduled_for=reminder_time
        )

    @staticmethod
    def process_scheduled_notifications():
        """Process all scheduled notifications that are due"""
        now = timezone.now()
        
        # Get all unsent scheduled notifications that are due
        due_notifications = UserNotification.objects.filter(
            is_sent=False,
            scheduled_for__lte=now
        )

        for notification in due_notifications:
            NotificationService.send_notification_email(notification)
            
            # Schedule next daily reminder if this was a daily goal notification
            if notification.notification_type == 'daily_goal':
                NotificationService.schedule_daily_reminder(notification.user)

    @staticmethod
    def send_streak_reminder(user, streak_count, streak_charge=None):
        """Send streak reminder notification"""
        profile = user.student_profile
        
        message = (
            f'Waxaa kuu hadhay {streak_count} maalmood oo aad ilaalisid.\n'
            f'Hadafkaaga maanta: {profile.daily_goal_minutes} daqiiqo\n'
            f'"{profile.get_goal_badge()}"'
        )
        
        if streak_charge is not None:
            message += f"\nWaxaad haysataa {streak_charge} streak charges."
            
        notification = UserNotification.objects.create(
            user=user,
            notification_type='streak_reminder',
            title='Ilaaligaaga Waxbarashada! 🔥',
            message=message
        )
        
        return NotificationService.send_notification_email(notification)

    @staticmethod
    def send_achievement_notification(user, achievement):
        """Send achievement earned notification"""
        profile = user.student_profile
        notification = UserNotification.objects.create(
            user=user,
            notification_type='achievement_earned',
            title='Hambalyo! Guul Cusub! 🏆',
            message=f'Waad dhamaysatay "{achievement["name"]}"!\n{achievement["description"]}\n\n{profile.get_study_time_badge()}'
        )
        return NotificationService.send_notification_email(notification)

    @staticmethod
    def send_league_update(user, league_position, league_name):
        """Send league update notification"""
        notification = UserNotification.objects.create(
            user=user,
            notification_type='league_update',
            title='Warbixin Tartanka! 🏅',
            message=f'Waxaad ku jirtaa kaalinta {league_position} ee {league_name}!'
        )
        return NotificationService.send_notification_email(notification) 