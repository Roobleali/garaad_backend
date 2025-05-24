from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from .models import (
    UserNotification, UserReward, UserLevel, UserProgress, 
    LeaderboardEntry, Achievement, UserAchievement, UserLeague, League
)
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

class LearningProgressService:
    """
    Central service for handling all learning progress, rewards, and notifications.
    """
    
    # Reward constants
    REWARDS = {
        'lesson_completion': {
            'xp': 10,
            'streak': 5
        },
        'perfect_score': {
            'xp_bonus': 5
        },
        'streak_multipliers': {
            1: 1,    # 1 day = 1x
            3: 1.5,  # 3 days = 1.5x
            7: 2,    # 7 days = 2x
            14: 2.5, # 14 days = 2.5x
            30: 3    # 30 days = 3x
        }
    }
    
    @classmethod
    def process_lesson_completion(cls, user, lesson, score=None):
        """
        Process lesson completion and handle all related rewards and notifications.
        """
        try:
            # 1. Update lesson progress
            progress = cls._update_lesson_progress(user, lesson, score)
            
            # 2. Calculate and award rewards
            rewards = cls._calculate_rewards(user, lesson, score)
            
            # 3. Update user level with XP
            cls._update_user_level(user, rewards['xp'])
            
            # 4. Award streak points
            cls._award_streak_points(user, lesson, rewards['streak'])
            
            # 5. Check and award achievements
            achievements = cls._check_achievements(user, lesson, score)
            
            # 6. Update leaderboard
            cls._update_leaderboard(user)
            
            # 7. Send notifications
            cls._send_notifications(user, rewards, achievements)
            
            return {
                'progress': progress,
                'rewards': rewards,
                'achievements': achievements
            }
            
        except Exception as e:
            logger.error(f"Error processing lesson completion: {str(e)}")
            raise
    
    @classmethod
    def _update_lesson_progress(cls, user, lesson, score):
        """Update user's lesson progress"""
        progress, created = UserProgress.objects.get_or_create(
            user=user,
            lesson=lesson,
            defaults={'status': 'in_progress'}
        )
        
        progress.mark_as_completed(score=score)
        return progress
    
    @classmethod
    def _calculate_rewards(cls, user, lesson, score):
        """Calculate XP and streak rewards"""
        # Base rewards
        xp = cls.REWARDS['lesson_completion']['xp']
        streak = cls.REWARDS['lesson_completion']['streak']
        
        # Perfect score bonus
        if score == 100:
            xp += cls.REWARDS['perfect_score']['xp_bonus']
        
        # Calculate streak multiplier
        current_streak = cls._get_current_streak(user)
        streak_multiplier = cls._get_streak_multiplier(current_streak)
        
        return {
            'xp': xp,
            'streak': int(streak * streak_multiplier),
            'streak_days': current_streak
        }
    
    @classmethod
    def _update_user_level(cls, user, xp):
        """Update user's level with earned XP"""
        user_level = UserLevel.objects.get_or_create(user=user)[0]
        user_level.add_experience(xp)
        return user_level
    
    @classmethod
    def _award_streak_points(cls, user, lesson, streak_points):
        """Award streak points to user"""
        return UserReward.objects.create(
            user=user,
            reward_type='streak',
            reward_name='Lesson Completion',
            value=streak_points,
            lesson=lesson
        )
    
    @classmethod
    def _get_current_streak(cls, user):
        """Get user's current streak in days"""
        recent_completions = UserProgress.objects.filter(
            user=user,
            status='completed',
            completed_at__isnull=False
        ).order_by('-completed_at')
        
        if not recent_completions.exists():
            return 0
        
        streak_days = 1
        last_completion = recent_completions.first().completed_at.date()
        today = timezone.now().date()
        
        if last_completion == today - timedelta(days=1):
            for completion in recent_completions[1:]:
                completion_date = completion.completed_at.date()
                expected_date = last_completion - timedelta(days=1)
                
                if completion_date == expected_date:
                    streak_days += 1
                    last_completion = completion_date
                else:
                    break
        
        return streak_days
    
    @classmethod
    def _get_streak_multiplier(cls, streak_days):
        """Get streak multiplier based on streak days"""
        multipliers = cls.REWARDS['streak_multipliers']
        applicable_multipliers = [
            multiplier for days, multiplier in multipliers.items()
            if streak_days >= days
        ]
        return max(applicable_multipliers) if applicable_multipliers else 1
    
    @classmethod
    def _check_achievements(cls, user, lesson, score):
        """Check and award achievements"""
        achievements = []
        
        # Check streak achievements
        streak_days = cls._get_current_streak(user)
        for milestone in cls.REWARDS['streak_multipliers'].keys():
            if streak_days >= milestone:
                achievement = Achievement.objects.filter(
                    achievement_type='streak_milestone',
                    level_required__lte=user.level.level
                ).first()
                
                if achievement:
                    user_achievement, created = UserAchievement.objects.get_or_create(
                        user=user,
                        achievement=achievement
                    )
                    if created:
                        achievements.append(achievement)
        
        # Check perfect score achievement
        if score == 100:
            achievement = Achievement.objects.filter(
                achievement_type='perfect_score',
                level_required__lte=user.level.level
            ).first()
            
            if achievement:
                user_achievement, created = UserAchievement.objects.get_or_create(
                    user=user,
                    achievement=achievement
                )
                if created:
                    achievements.append(achievement)
        
        return achievements
    
    @classmethod
    def _update_leaderboard(cls, user):
        """Update leaderboard entries"""
        LeaderboardEntry.update_points(user)
    
    @classmethod
    def _send_notifications(cls, user, rewards, achievements):
        """Send relevant notifications"""
        # Send streak notification
        if rewards['streak_days'] > 0:
            NotificationService.send_streak_reminder(
                user=user,
                streak_count=rewards['streak_days']
            )
        
        # Send achievement notifications
        for achievement in achievements:
            NotificationService.send_achievement_notification(
                user=user,
                achievement=achievement
            )
        
        # Send leaderboard update if position changed
        leaderboard_entry = LeaderboardEntry.objects.filter(
            user=user,
            time_period='weekly'
        ).first()
        
        if leaderboard_entry:
            NotificationService.send_league_update(
                user=user,
                league_position=leaderboard_entry.get_rank(),
                league_name='Weekly Leaderboard'
            )

class LeagueService:
    """
    Service for managing leagues and streaks.
    """
    
    # XP rewards
    XP_REWARDS = {
        'problem_correct': 15,  # Base XP for correct problem
        'hard_problem': 40,     # XP for hard problem
        'first_lesson': 30,     # XP for first lesson completion
        'lesson_completion': 10  # XP for any lesson completion
    }
    
    @classmethod
    def process_lesson_completion(cls, user, lesson, score=None):
        """
        Process lesson completion and handle league/streak updates.
        """
        # Get or create user league
        user_league = cls._get_or_create_user_league(user)
        
        # Calculate XP earned
        xp_earned = cls._calculate_xp_earned(user, lesson, score)
        
        # Update user's XP and league points
        user_league.update_weekly_points(xp_earned)
        
        # Update streak
        streak_updated = cls._update_streak(user_league)
        
        # Check for league promotion/demotion
        league_changed = cls._check_league_change(user_league)
        
        return {
            'xp_earned': xp_earned,
            'streak_updated': streak_updated,
            'league_changed': league_changed,
            'current_league': user_league.league.get_level_display(),
            'current_points': user_league.current_week_points
        }
    
    @classmethod
    def _get_or_create_user_league(cls, user):
        """Get or create user's league based on XP"""
        try:
            return UserLeague.objects.get(user=user)
        except UserLeague.DoesNotExist:
            # Get user's total XP
            total_xp = UserReward.objects.filter(
                user=user,
                reward_type='points'
            ).aggregate(total=models.Sum('value'))['total'] or 0
            
            # Get appropriate league
            league = League.get_league_for_xp(total_xp)
            if not league:
                league = League.objects.first()  # Start with lowest league
            
            return UserLeague.objects.create(
                user=user,
                league=league
            )
    
    @classmethod
    def _calculate_xp_earned(cls, user, lesson, score):
        """Calculate XP earned from lesson completion"""
        xp = 0
        
        # First lesson bonus
        if not UserProgress.objects.filter(user=user).exists():
            xp += cls.XP_REWARDS['first_lesson']
        
        # Lesson completion XP
        xp += cls.XP_REWARDS['lesson_completion']
        
        # Perfect score bonus
        if score == 100:
            xp += cls.XP_REWARDS['problem_correct']
        
        return xp
    
    @classmethod
    def _update_streak(cls, user_league):
        """Update user's streak"""
        today = timezone.now().date()
        
        # Check if user has streak charges
        if user_league.last_activity_date and (today - user_league.last_activity_date).days > 1:
            if user_league.use_streak_charge():
                # Streak maintained using charge
                user_league.last_activity_date = today
                user_league.save(update_fields=['last_activity_date'])
                return True
            else:
                # Streak broken
                user_league.last_activity_date = today
                user_league.save(update_fields=['last_activity_date'])
                return False
        
        # Normal streak update
        if not user_league.last_activity_date or (today - user_league.last_activity_date).days == 1:
            user_league.last_activity_date = today
            user_league.save(update_fields=['last_activity_date'])
            
            # Award streak charge if earned
            if user_league.last_activity_date and (today - user_league.last_activity_date).days == 1:
                user_league.add_streak_charge()
            
            return True
        
        return False
    
    @classmethod
    def _check_league_change(cls, user_league):
        """Check if user should change leagues"""
        # Get current rank in league
        rank = UserLeague.objects.filter(
            league=user_league.league,
            current_week_points__gt=user_league.current_week_points
        ).count() + 1
        
        # Check promotion
        if rank <= user_league.league.promotion_threshold:
            next_league = League.get_next_league(user_league.league)
            if next_league:
                user_league.league = next_league
                user_league.save(update_fields=['league'])
                return True
        
        # Check demotion
        elif rank > (user_league.league.promotion_threshold + user_league.league.stay_threshold):
            prev_league = League.get_previous_league(user_league.league)
            if prev_league:
                user_league.league = prev_league
                user_league.save(update_fields=['league'])
                return True
        
        return False
    
    @classmethod
    def reset_weekly_standings(cls):
        """Reset weekly standings and handle promotions/demotions"""
        # Get all leagues
        leagues = League.objects.all()
        
        for league in leagues:
            # Get all users in this league
            user_leagues = UserLeague.objects.filter(league=league).order_by('-current_week_points')
            
            # Process promotions
            for i, user_league in enumerate(user_leagues[:league.promotion_threshold]):
                next_league = League.get_next_league(league)
                if next_league:
                    user_league.league = next_league
                    user_league.last_week_rank = i + 1
                    user_league.reset_weekly_points()
                    user_league.save()
            
            # Process demotions
            for i, user_league in enumerate(user_leagues[-(league.demotion_threshold):]):
                prev_league = League.get_previous_league(league)
                if prev_league:
                    user_league.league = prev_league
                    user_league.last_week_rank = len(user_leagues) - i
                    user_league.reset_weekly_points()
                    user_league.save()
            
            # Reset points for users staying in league
            middle_users = user_leagues[league.promotion_threshold:-(league.demotion_threshold)]
            for i, user_league in enumerate(middle_users):
                user_league.last_week_rank = league.promotion_threshold + i + 1
                user_league.reset_weekly_points()
                user_league.save() 