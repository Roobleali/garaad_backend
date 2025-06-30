from django.db.models import Count, Q, Sum, Avg, F, Max
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta, date
from courses.models import (
    Course, Lesson, Problem, UserProgress, CourseEnrollment, 
    UserReward, LeaderboardEntry, Achievement, UserAchievement,
    DailyChallenge, UserChallengeProgress
)
from api.models import Streak, DailyActivity, Notification
from leagues.models import League, UserLeague
from accounts.models import UserProfile, StudentProfile
import json

User = get_user_model()

class AdminDashboardService:
    """
    Comprehensive admin dashboard service for LMS platform
    """
    
    @staticmethod
    def get_dashboard_data():
        """
        Get complete dashboard data with all important metrics
        """
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        dashboard_data = {
            'overview': AdminDashboardService.get_overview_stats(),
            'users': AdminDashboardService.get_user_stats(),
            'courses': AdminDashboardService.get_course_stats(),
            'learning': AdminDashboardService.get_learning_stats(),
            'engagement': AdminDashboardService.get_engagement_stats(),
            'revenue': AdminDashboardService.get_revenue_stats(),
            'system': AdminDashboardService.get_system_stats(),
            'recent_activity': AdminDashboardService.get_recent_activity(),
            'top_performers': AdminDashboardService.get_top_performers(),
            'alerts': AdminDashboardService.get_system_alerts()
        }
        
        return dashboard_data
    
    @staticmethod
    def get_overview_stats():
        """
        Get high-level overview statistics
        """
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        total_users = User.objects.count()
        total_courses = Course.objects.count()
        total_lessons = Lesson.objects.count()
        total_problems = Problem.objects.count()
        
        # Active users (users who have activity in last 7 days)
        active_users = User.objects.filter(
            daily_activities__date__gte=week_ago
        ).distinct().count()
        
        # New users this week
        new_users_week = User.objects.filter(
            date_joined__gte=week_ago
        ).count()
        
        # Completion rate
        total_enrollments = CourseEnrollment.objects.count()
        completed_courses = CourseEnrollment.objects.filter(
            progress_percent=100
        ).count()
        completion_rate = (completed_courses / total_enrollments * 100) if total_enrollments > 0 else 0
        
        return {
            'total_users': total_users,
            'total_courses': total_courses,
            'total_lessons': total_lessons,
            'total_problems': total_problems,
            'active_users': active_users,
            'new_users_week': new_users_week,
            'completion_rate': round(completion_rate, 2),
            'total_enrollments': total_enrollments
        }
    
    @staticmethod
    def get_user_stats():
        """
        Get detailed user statistics
        """
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Basic user counts
        total_users = User.objects.count()
        premium_users = User.objects.filter(is_premium=True).count()
        free_users = total_users - premium_users
        
        # Subscription breakdown
        monthly_subs = User.objects.filter(
            is_premium=True, 
            subscription_type='monthly'
        ).count()
        yearly_subs = User.objects.filter(
            is_premium=True, 
            subscription_type='yearly'
        ).count()
        lifetime_subs = User.objects.filter(
            is_premium=True, 
            subscription_type='lifetime'
        ).count()
        
        # Active users by time period
        active_today = User.objects.filter(
            daily_activities__date=today
        ).distinct().count()
        
        active_week = User.objects.filter(
            daily_activities__date__gte=week_ago
        ).distinct().count()
        
        active_month = User.objects.filter(
            daily_activities__date__gte=month_ago
        ).distinct().count()
        
        # User engagement levels
        high_engagement = User.objects.filter(
            streak__current_streak__gte=7
        ).count()
        
        medium_engagement = User.objects.filter(
            streak__current_streak__range=[3, 6]
        ).count()
        
        low_engagement = User.objects.filter(
            Q(streak__current_streak__range=[1, 2]) | Q(streak__isnull=True)
        ).count()
        
        # New registrations
        new_today = User.objects.filter(date_joined__date=today).count()
        new_week = User.objects.filter(date_joined__gte=week_ago).count()
        new_month = User.objects.filter(date_joined__gte=month_ago).count()
        
        # Recently active users (last 24 hours)
        recent_active = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(hours=24)
        ).values('id', 'username', 'email', 'last_login', 'is_premium').order_by('-last_login')[:10]
        
        return {
            'total_users': total_users,
            'premium_users': premium_users,
            'free_users': free_users,
            'subscription_breakdown': {
                'monthly': monthly_subs,
                'yearly': yearly_subs,
                'lifetime': lifetime_subs
            },
            'active_users': {
                'today': active_today,
                'week': active_week,
                'month': active_month
            },
            'engagement_levels': {
                'high': high_engagement,
                'medium': medium_engagement,
                'low': low_engagement
            },
            'new_registrations': {
                'today': new_today,
                'week': new_week,
                'month': new_month
            },
            'recent_active_users': list(recent_active)
        }
    
    @staticmethod
    def get_course_stats():
        """
        Get course and content statistics
        """
        # Basic course stats
        total_courses = Course.objects.count()
        published_courses = Course.objects.filter(status='published').count() if hasattr(Course, 'status') else total_courses
        total_lessons = Lesson.objects.count()
        total_problems = Problem.objects.count()
        
        # Course enrollments
        total_enrollments = CourseEnrollment.objects.count()
        unique_enrolled_users = CourseEnrollment.objects.values('user').distinct().count()
        
        # Popular courses (most enrolled)
        popular_courses = Course.objects.annotate(
            enrollment_count=Count('enrollments')
        ).order_by('-enrollment_count')[:5].values(
            'id', 'title', 'enrollment_count'
        )
        
        # Course completion stats
        completed_courses = CourseEnrollment.objects.filter(progress_percent=100).count()
        in_progress_courses = CourseEnrollment.objects.filter(
            progress_percent__gt=0, progress_percent__lt=100
        ).count()
        not_started_courses = CourseEnrollment.objects.filter(progress_percent=0).count()
        
        # Average progress
        avg_progress = CourseEnrollment.objects.aggregate(
            avg_progress=Avg('progress_percent')
        )['avg_progress'] or 0
        
        # Content engagement
        total_lessons_completed = UserProgress.objects.filter(status='completed').count()
        total_problems_solved = UserProgress.objects.aggregate(
            total_problems=Sum('problems_solved')
        )['total_problems'] or 0
        
        return {
            'total_courses': total_courses,
            'published_courses': published_courses,
            'total_lessons': total_lessons,
            'total_problems': total_problems,
            'enrollments': {
                'total': total_enrollments,
                'unique_users': unique_enrolled_users,
                'completed': completed_courses,
                'in_progress': in_progress_courses,
                'not_started': not_started_courses
            },
            'avg_progress': round(avg_progress, 2),
            'popular_courses': list(popular_courses),
            'content_engagement': {
                'lessons_completed': total_lessons_completed,
                'problems_solved': total_problems_solved
            }
        }
    
    @staticmethod
    def get_learning_stats():
        """
        Get learning and progress statistics
        """
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Daily activity stats
        today_activity = DailyActivity.objects.filter(date=today).aggregate(
            total_users=Count('user'),
            total_problems=Sum('problems_solved'),
            complete_sessions=Count('id', filter=Q(status='complete')),
            partial_sessions=Count('id', filter=Q(status='partial'))
        )
        
        # Weekly learning stats
        week_stats = DailyActivity.objects.filter(date__gte=week_ago).aggregate(
            total_problems=Sum('problems_solved'),
            active_users=Count('user', distinct=True),
            complete_days=Count('id', filter=Q(status='complete'))
        )
        
        # Problem difficulty breakdown
        problem_types = Problem.objects.values('question_type').annotate(
            count=Count('id')
        ).order_by('question_type')
        
        # XP distribution
        xp_stats = Streak.objects.aggregate(
            total_xp=Sum('xp'),
            avg_xp=Avg('xp'),
            max_xp=Max('xp')
        )
        
        # Streak statistics
        streak_stats = Streak.objects.aggregate(
            avg_streak=Avg('current_streak'),
            max_streak=Max('max_streak'),
            users_with_streaks=Count('id', filter=Q(current_streak__gt=0))
        )
        
        # Top streaks
        top_streaks = Streak.objects.select_related('user').filter(
            current_streak__gt=0
        ).order_by('-current_streak')[:10].values(
            'user__username', 'current_streak', 'max_streak', 'xp'
        )
        
        return {
            'today_activity': today_activity,
            'week_stats': week_stats,
            'problem_types': list(problem_types),
            'xp_stats': {
                'total_xp': xp_stats['total_xp'] or 0,
                'avg_xp': round(xp_stats['avg_xp'] or 0, 2),
                'max_xp': xp_stats['max_xp'] or 0
            },
            'streak_stats': {
                'avg_streak': round(streak_stats['avg_streak'] or 0, 2),
                'max_streak': streak_stats['max_streak'] or 0,
                'users_with_streaks': streak_stats['users_with_streaks']
            },
            'top_streaks': list(top_streaks)
        }
    
    @staticmethod
    def get_engagement_stats():
        """
        Get user engagement and retention statistics
        """
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Daily retention (users who were active yesterday and today)
        yesterday = today - timedelta(days=1)
        yesterday_users = set(DailyActivity.objects.filter(
            date=yesterday
        ).values_list('user_id', flat=True))
        
        today_users = set(DailyActivity.objects.filter(
            date=today
        ).values_list('user_id', flat=True))
        
        daily_retention = len(yesterday_users & today_users) / len(yesterday_users) * 100 if yesterday_users else 0
        
        # Weekly retention
        week_before_users = set(DailyActivity.objects.filter(
            date__range=[month_ago, week_ago]
        ).values_list('user_id', flat=True))
        
        current_week_users = set(DailyActivity.objects.filter(
            date__gte=week_ago
        ).values_list('user_id', flat=True))
        
        weekly_retention = len(week_before_users & current_week_users) / len(week_before_users) * 100 if week_before_users else 0
        
        # Notification engagement
        total_notifications = Notification.objects.count()
        read_notifications = Notification.objects.filter(is_read=True).count()
        notification_engagement = read_notifications / total_notifications * 100 if total_notifications > 0 else 0
        
        # League participation
        league_users = UserLeague.objects.count()
        total_users = User.objects.count()
        league_participation = league_users / total_users * 100 if total_users > 0 else 0
        
        # Achievement completion
        total_achievements = Achievement.objects.count()
        earned_achievements = UserAchievement.objects.count()
        achievement_rate = earned_achievements / (total_users * total_achievements) * 100 if total_achievements > 0 and total_users > 0 else 0
        
        return {
            'retention': {
                'daily': round(daily_retention, 2),
                'weekly': round(weekly_retention, 2)
            },
            'notification_engagement': round(notification_engagement, 2),
            'league_participation': round(league_participation, 2),
            'achievement_rate': round(achievement_rate, 2),
            'engagement_breakdown': {
                'high_engagers': Streak.objects.filter(current_streak__gte=7).count(),
                'medium_engagers': Streak.objects.filter(current_streak__range=[3, 6]).count(),
                'low_engagers': Streak.objects.filter(current_streak__range=[1, 2]).count(),
                'inactive': User.objects.filter(streak__isnull=True).count()
            }
        }
    
    @staticmethod
    def get_revenue_stats():
        """
        Get subscription and revenue statistics
        """
        today = timezone.now().date()
        month_ago = today - timedelta(days=30)
        year_ago = today - timedelta(days=365)
        
        # Premium user breakdown
        premium_users = User.objects.filter(is_premium=True)
        
        # Subscription types
        monthly_count = premium_users.filter(subscription_type='monthly').count()
        yearly_count = premium_users.filter(subscription_type='yearly').count()
        lifetime_count = premium_users.filter(subscription_type='lifetime').count()
        
        # New premium subscriptions this month
        new_premium_month = premium_users.filter(
            subscription_start_date__gte=month_ago
        ).count()
        
        # Active subscriptions (not expired)
        active_subscriptions = premium_users.filter(
            Q(subscription_type='lifetime') |
            Q(subscription_end_date__gte=today)
        ).count()
        
        # Estimate monthly recurring revenue (MRR)
        # Assuming monthly = $10, yearly = $100, lifetime = $500
        estimated_mrr = (monthly_count * 10) + (yearly_count * 100 / 12)
        estimated_arr = estimated_mrr * 12
        
        # Conversion rate
        total_users = User.objects.count()
        conversion_rate = premium_users.count() / total_users * 100 if total_users > 0 else 0
        
        return {
            'subscription_breakdown': {
                'monthly': monthly_count,
                'yearly': yearly_count,
                'lifetime': lifetime_count,
                'total_premium': premium_users.count()
            },
            'new_premium_month': new_premium_month,
            'active_subscriptions': active_subscriptions,
            'estimated_revenue': {
                'mrr': round(estimated_mrr, 2),
                'arr': round(estimated_arr, 2)
            },
            'conversion_rate': round(conversion_rate, 2),
            'churn_indicators': {
                'expired_subscriptions': premium_users.filter(
                    subscription_end_date__lt=today,
                    subscription_type__in=['monthly', 'yearly']
                ).count()
            }
        }
    
    @staticmethod
    def get_system_stats():
        """
        Get system and technical statistics
        """
        # Database counts
        db_stats = {
            'users': User.objects.count(),
            'courses': Course.objects.count(),
            'lessons': Lesson.objects.count(),
            'problems': Problem.objects.count(),
            'enrollments': CourseEnrollment.objects.count(),
            'user_progress': UserProgress.objects.count(),
            'daily_activities': DailyActivity.objects.count(),
            'notifications': Notification.objects.count(),
            'streaks': Streak.objects.count(),
            'achievements': Achievement.objects.count(),
            'user_achievements': UserAchievement.objects.count()
        }
        
        # Recent system activity
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        recent_activity = {
            'new_users_week': User.objects.filter(date_joined__gte=week_ago).count(),
            'lessons_completed_week': UserProgress.objects.filter(
                completed_at__gte=week_ago
            ).count(),
            'notifications_sent_week': Notification.objects.filter(
                created_at__gte=week_ago
            ).count()
        }
        
        return {
            'database_stats': db_stats,
            'recent_activity': recent_activity,
            'last_updated': timezone.now().isoformat()
        }
    
    @staticmethod
    def get_recent_activity():
        """
        Get recent user activities and system events
        """
        # Recent user registrations
        recent_users = User.objects.order_by('-date_joined')[:10].values(
            'id', 'username', 'email', 'date_joined', 'is_premium'
        )
        
        # Recent course completions
        recent_completions = CourseEnrollment.objects.filter(
            progress_percent=100
        ).select_related('user', 'course').order_by('-enrolled_at')[:10].values(
            'user__username', 'course__title', 'progress_percent', 'enrolled_at'
        )
        
        # Recent achievements
        recent_achievements = UserAchievement.objects.select_related(
            'user', 'achievement'
        ).order_by('-earned_at')[:10].values(
            'user__username', 'achievement__name', 'earned_at'
        )
        
        # Recent high streaks
        recent_streaks = Streak.objects.filter(
            current_streak__gte=7
        ).select_related('user').order_by('-last_activity_date')[:10].values(
            'user__username', 'current_streak', 'xp', 'last_activity_date'
        )
        
        return {
            'recent_users': list(recent_users),
            'recent_completions': list(recent_completions),
            'recent_achievements': list(recent_achievements),
            'recent_streaks': list(recent_streaks)
        }
    
    @staticmethod
    def get_top_performers():
        """
        Get top performing users and courses
        """
        # Top users by XP
        top_xp_users = Streak.objects.select_related('user').order_by('-xp')[:10].values(
            'user__username', 'user__email', 'xp', 'current_streak', 'max_streak'
        )
        
        # Top users by streak
        top_streak_users = Streak.objects.select_related('user').order_by('-current_streak')[:10].values(
            'user__username', 'user__email', 'current_streak', 'max_streak', 'xp'
        )
        
        # Most popular courses
        popular_courses = Course.objects.annotate(
            enrollment_count=Count('enrollments'),
            completion_count=Count('enrollments', filter=Q(enrollments__progress_percent=100)),
            avg_progress=Avg('enrollments__progress_percent')
        ).order_by('-enrollment_count')[:10].values(
            'id', 'title', 'enrollment_count', 'completion_count', 'avg_progress'
        )
        
        # Most completed lessons
        popular_lessons = Lesson.objects.annotate(
            completion_count=Count('user_progress', filter=Q(user_progress__status='completed'))
        ).order_by('-completion_count')[:10].values(
            'id', 'title', 'course__title', 'completion_count'
        )
        
        return {
            'top_xp_users': list(top_xp_users),
            'top_streak_users': list(top_streak_users),
            'popular_courses': list(popular_courses),
            'popular_lessons': list(popular_lessons)
        }
    
    @staticmethod
    def get_system_alerts():
        """
        Get system alerts and warnings
        """
        alerts = []
        today = timezone.now().date()
        
        # Check for users with expired subscriptions
        expired_subs = User.objects.filter(
            is_premium=True,
            subscription_end_date__lt=today,
            subscription_type__in=['monthly', 'yearly']
        ).count()
        
        if expired_subs > 0:
            alerts.append({
                'type': 'warning',
                'title': 'Expired Subscriptions',
                'message': f'{expired_subs} users have expired premium subscriptions',
                'count': expired_subs
            })
        
        # Check for inactive premium users
        week_ago = today - timedelta(days=7)
        inactive_premium = User.objects.filter(
            is_premium=True
        ).exclude(
            daily_activities__date__gte=week_ago
        ).count()
        
        if inactive_premium > 0:
            alerts.append({
                'type': 'info',
                'title': 'Inactive Premium Users',
                'message': f'{inactive_premium} premium users have been inactive for over a week',
                'count': inactive_premium
            })
        
        # Check for low course completion rates
        low_completion_courses = Course.objects.annotate(
            enrollment_count=Count('enrollments'),
            completion_count=Count('enrollments', filter=Q(enrollments__progress_percent=100)),
            completion_rate=F('completion_count') * 100.0 / F('enrollment_count')
        ).filter(
            enrollment_count__gte=10,  # Only courses with at least 10 enrollments
            completion_rate__lt=20  # Less than 20% completion rate
        ).count()
        
        if low_completion_courses > 0:
            alerts.append({
                'type': 'warning',
                'title': 'Low Completion Rates',
                'message': f'{low_completion_courses} courses have completion rates below 20%',
                'count': low_completion_courses
            })
        
        # Check for high churn (users who registered but never started)
        month_ago = today - timedelta(days=30)
        new_users_month = User.objects.filter(date_joined__gte=month_ago).count()
        active_new_users = User.objects.filter(
            date_joined__gte=month_ago,
            daily_activities__isnull=False
        ).distinct().count()
        
        churn_rate = (new_users_month - active_new_users) / new_users_month * 100 if new_users_month > 0 else 0
        
        if churn_rate > 50:
            alerts.append({
                'type': 'error',
                'title': 'High User Churn',
                'message': f'{churn_rate:.1f}% of new users this month never started learning',
                'count': new_users_month - active_new_users
            })
        
        return alerts 