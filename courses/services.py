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

        # --- 3. Check for Mid-Lesson Drop-off ---
        # (Implementation for this check would go here)
        
        # --- 4. Send a general motivational reminder if no other conditions are met ---
        # (Implementation for this check would go here)
        
    @staticmethod
    def is_streak_broken(user):
        """
        Checks if a user's streak is broken (last activity > 1 day ago).
        """
        try:
            streak = Streak.objects.get(user=user)
            if streak.last_activity_date:
                days_since_last_activity = (timezone.now().date() - streak.last_activity_date).days
                if days_since_last_activity > 1 and streak.current_streak > 0:
                    return True, streak.current_streak
        except Streak.DoesNotExist:
            return False, 0
        return False, 0

    @staticmethod
    def get_inactivity_days(user):
        """
        Calculates the number of days a user has been inactive.
        """
        try:
            streak = Streak.objects.get(user=user)
            if streak.last_activity_date:
                return (timezone.now().date() - streak.last_activity_date).days
        except Streak.DoesNotExist:
            return None # Can't determine inactivity if there's no streak record
        return 0

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