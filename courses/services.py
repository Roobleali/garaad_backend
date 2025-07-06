from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from .models import (
    UserNotification, UserReward, UserLevel, UserProgress, 
    LeaderboardEntry, Achievement, UserAchievement,
    CulturalEvent, UserCulturalProgress, CommunityContribution
)
from django.db import transaction
from django.db.models import F, Sum, OuterRef, Subquery
from django.core.cache import cache
import logging
from leagues.models import UserLeague, League  # Import from leagues app
from accounts.utils import send_resend_email, TEST_MODE
from courses.models import CourseEnrollment, Lesson, UserProgress
from api.models import Streak

logger = logging.getLogger(__name__)

def get_user_learning_context(user):
    """
    Gathers the user's current learning context for personalized emails.
    """
    enrollment = CourseEnrollment.objects.filter(user=user).order_by('-enrolled_at').first()
    if not enrollment:
        return None

    course = enrollment.course
    progress_percent = enrollment.progress_percent

    # Find the last completed lesson to determine the next one
    last_progress = UserProgress.objects.filter(
        user=user, 
        lesson__course=course, 
        status='completed'
    ).order_by('-lesson__lesson_number').first()

    if last_progress:
        # The next lesson is the one after the last completed lesson
        next_lesson = Lesson.objects.filter(
            course=course,
            lesson_number__gt=last_progress.lesson.lesson_number
        ).order_by('lesson_number').first()
    else:
        # If no lesson is completed, the first lesson is the next one
        next_lesson = Lesson.objects.filter(course=course).order_by('lesson_number').first()

    return {
        "course_name": course.title,
        "progress_percent": progress_percent,
        "next_lesson_title": next_lesson.title if next_lesson else "No more lessons",
        "next_lesson_url": f"/courses/{course.slug}/{next_lesson.slug}/" if next_lesson else f"/courses/{course.slug}/",
        "course_thumbnail": course.thumbnail if course.thumbnail else None
    }

class NotificationService:
    @staticmethod
    def check_and_send_real_time_reminders(user):
        """
        Checks for various real-time events and sends the highest priority notification.
        Uses last_active field for more accurate activity tracking.
        """
        # --- 1. Check for Streak Break ---
        streak_broken, streak_count = NotificationService.is_streak_broken(user)
        if streak_broken:
            print(f"Condition met: Streak broken for user {user.id}.")
            NotificationService.send_streak_break_reminder(user, streak_count)
            return  # Stop after sending the highest priority email

        # --- 2. Check for Inactivity ---
        inactive_days = NotificationService.get_inactivity_days(user)
        if inactive_days and inactive_days >= 1:
            print(f"Condition met: User {user.id} inactive for {inactive_days} days.")
            NotificationService.send_inactivity_reminder(user)
            return

        # --- 3. Check for Daily Reminder ---
        # Check if user hasn't been active today
        if not NotificationService.is_user_active_today(user):
            print(f"Condition met: User {user.id} not active today.")
            NotificationService.send_daily_reminder_notification(user)
            return

        # --- 4. Send a general motivational reminder if no other conditions are met ---
        # (Implementation for this check would go here)
    
    @staticmethod
    def process_scheduled_notifications():
        """
        Process all scheduled notifications that are due to be sent.
        """
        from courses.models import UserNotification
        from django.utils import timezone
        
        now = timezone.now()
        
        # Get all due notifications
        due_notifications = UserNotification.objects.filter(
            is_sent=False,
            scheduled_for__lte=now
        )
        
        processed_count = 0
        for notification in due_notifications:
            try:
                # Send the notification email
                success = NotificationService.send_notification_email(notification)
                if success:
                    notification.is_sent = True
                    notification.save()
                    processed_count += 1
                    print(f"Successfully processed notification {notification.id} for user {notification.user.username}")
                else:
                    print(f"Failed to process notification {notification.id} for user {notification.user.username}")
            except Exception as e:
                print(f"Error processing notification {notification.id}: {e}")
        
        print(f"Processed {processed_count} scheduled notifications")
        return processed_count
    
    @staticmethod
    def send_notification_email(notification):
        """
        Send an email for a specific notification.
        """
        try:
            context = get_user_learning_context(notification.user)
            if not context:
                context = {
                    'user': notification.user,
                    'notification': notification,
                    'site_url': 'https://garaad.org'
                }
            
            # Add notification-specific context
            context['notification'] = notification
            context['notification_type'] = notification.notification_type
            
            # Choose template based on notification type
            template_map = {
                'streak_reminder': 'emails/streak_reminder.html',
                'daily_goal': 'emails/daily_goal.html',
                'achievement_earned': 'emails/achievement_earned.html',
                'league_update': 'emails/league_update.html',
                'challenge_available': 'emails/challenge_available.html'
            }
            
            template_name = template_map.get(notification.notification_type, 'emails/general_notification.html')
            
            html = render_to_string(template_name, context)
            success = send_resend_email(
                to_email=notification.user.email,
                subject=notification.title,
                html=html
            )
            
            if success:
                print(f"Successfully sent {notification.notification_type} email to {notification.user.email}")
                return True
            else:
                print(f"Failed to send {notification.notification_type} email to {notification.user.email}")
                return False
                
        except Exception as e:
            print(f"Error sending notification email: {e}")
            return False
        
    @staticmethod
    def is_user_active_today(user):
        """
        Check if user has been active today using last_active field
        """
        if not user.last_active:
            return False
        
        today = timezone.now().date()
        last_active_date = user.last_active.date()
        
        return last_active_date == today

    @staticmethod
    def is_streak_broken(user):
        """
        Checks if a user's streak is broken using last_active field.
        More accurate than using streak.last_activity_date alone.
        """
        try:
            streak = Streak.objects.get(user=user)
            
            # Use last_active if available, otherwise fall back to streak.last_activity_date
            if user.last_active:
                last_activity_date = user.last_active.date()
            elif streak.last_activity_date:
                last_activity_date = streak.last_activity_date
            else:
                return False, 0
            
            days_since_last_activity = (timezone.now().date() - last_activity_date).days
            if days_since_last_activity > 1 and streak.current_streak > 0:
                return True, streak.current_streak
        except Streak.DoesNotExist:
            return False, 0
        return False, 0

    @staticmethod
    def get_inactivity_days(user):
        """
        Calculates the number of days a user has been inactive using last_active field.
        """
        if user.last_active:
            return (timezone.now().date() - user.last_active.date()).days
        
        # Fallback to streak.last_activity_date if last_active is not available
        try:
            streak = Streak.objects.get(user=user)
            if streak.last_activity_date:
                return (timezone.now().date() - streak.last_activity_date).days
        except Streak.DoesNotExist:
            return None  # Can't determine inactivity if there's no activity record
        return None

    @staticmethod
    def send_inactivity_reminder(user):
        """
        Sends a motivational reminder to an inactive user.
        """
        context = get_user_learning_context(user)
        if not context:
            print(f"Could not send inactivity reminder to user {user.id}: No learning context found.")
            return

        try:
            html = render_to_string('emails/streak_reminder.html', context)
            success = send_resend_email(
                to_email=user.email,
                subject='Waxbarashada waa ku sugayaa! Sii wad casharkaaga.',
                html=html
            )
            if success:
                print(f"Successfully sent inactivity reminder to user {user.id}.")
            else:
                print(f"Failed to send inactivity reminder to user {user.id}.")
        except Exception as e:
            print(f"Failed to send inactivity reminder to user {user.id}: {e}")

    @staticmethod
    def send_streak_break_reminder(user, streak_count):
        """
        Sends an email to a user who has just broken their streak.
        """
        context = get_user_learning_context(user)
        if not context:
            print(f"Could not send streak break reminder to user {user.id}: No learning context found.")
            return
            
        # Add streak-specific info to the context
        context['streak_count'] = streak_count
        context['broke_streak'] = True

        try:
            html = render_to_string('emails/streak_reminder.html', context)
            success = send_resend_email(
                to_email=user.email,
                subject='Ha lumin dadaalkaaga! Xariggaaga halis ayuu ku jiraa.',
                html=html
            )
            if success:
                print(f"Successfully sent streak break reminder to user {user.id}.")
            else:
                print(f"Failed to send streak break reminder to user {user.id}.")
        except Exception as e:
            print(f"Failed to send streak break reminder to user {user.id}: {e}")

    @staticmethod
    def send_lesson_completion_notification(user, lesson):
        """
        Send a notification when a user completes a lesson.
        """
        try:
            # Check if user should receive a notification
            streak = Streak.objects.get(user=user)
            
            # If this is the first lesson of the day, send a motivational notification
            if streak.last_activity_date != timezone.now().date():
                context = get_user_learning_context(user)
                if context:
                    context['lesson_title'] = lesson.title
                    context['course_name'] = lesson.course.title
                    
                    html = render_to_string('emails/lesson_completion.html', context)
                    success = send_resend_email(
                        to_email=user.email,
                        subject='Hambalyo! Waad dhammaystirtay casharkaaga!',
                        html=html
                    )
                    if success:
                        print(f"Sent lesson completion notification to user {user.id}")
                        
        except Streak.DoesNotExist:
            pass  # User doesn't have a streak record yet
        except Exception as e:
            print(f"Error sending lesson completion notification: {e}")

    @staticmethod
    def send_problem_completion_notification(user, problem):
        """
        Send a notification when a user completes a problem.
        """
        try:
            # Check if user should receive a notification
            streak = Streak.objects.get(user=user)
            
            # If user solved multiple problems in a row, send encouragement
            recent_problems = UserProgress.objects.filter(
                user=user,
                status='completed',
                completed_at__gte=timezone.now() - timedelta(hours=1)
            ).count()
            
            if recent_problems >= 3:
                context = get_user_learning_context(user)
                if context:
                    context['problems_solved'] = recent_problems
                    context['problem_title'] = problem.question_text[:50] + "..." if len(problem.question_text) > 50 else problem.question_text
                    
                    html = render_to_string('emails/problem_completion.html', context)
                    success = send_resend_email(
                        to_email=user.email,
                        subject='Waxaad ku mahadsantahay dadaalkaaga!',
                        html=html
                    )
                    if success:
                        print(f"Sent problem completion notification to user {user.id}")
                        
        except Streak.DoesNotExist:
            pass  # User doesn't have a streak record yet
        except Exception as e:
            print(f"Error sending problem completion notification: {e}")

    @staticmethod
    def send_daily_reminder_notification(user):
        """
        Send a daily reminder notification to encourage learning.
        """
        try:
            context = get_user_learning_context(user)
            if not context:
                context = {
                    'user': user,
                    'site_url': 'https://garaad.org'
                }
            
            # Add daily motivation context
            context['daily_motivation'] = True
            context['streak_days'] = 0
            
            # Get user's current streak
            try:
                streak = Streak.objects.get(user=user)
                context['streak_days'] = streak.current_streak
            except Streak.DoesNotExist:
                pass
            
            html = render_to_string('emails/daily_reminder.html', context)
            success = send_resend_email(
                to_email=user.email,
                subject='Maanta waa maalin wanaagsan oo aad ku baran karto!',
                html=html
            )
            if success:
                print(f"Sent daily reminder to user {user.id}")
                return True
            else:
                print(f"Failed to send daily reminder to user {user.id}")
                return False
                
        except Exception as e:
            print(f"Error sending daily reminder: {e}")
            return False


class LearningProgressService:
    """
    Placeholder for LearningProgressService to resolve import errors.
    The original logic has been moved or is no longer needed for the core notification system.
    """
    pass


class LeagueService:
    """
    Placeholder for LeagueService to resolve import errors.
    The original logic has been moved or is no longer needed for the core notification system.
    """
    pass