import logging
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from api.models import Streak, DailyActivity
from datetime import timedelta
import json

User = get_user_model()
logger = logging.getLogger(__name__)

class UserActivityMiddleware(MiddlewareMixin):
    """
    Middleware to track user activity and update last_active field
    This ensures users who log in and browse the site have their activity tracked
    even if they don't perform specific learning actions.
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        
    def process_request(self, request):
        """Track user activity on each request"""
        # Only track activity for authenticated users
        if request.user.is_authenticated and self._should_track_request(request):
            try:
                self._update_user_activity(request.user)
            except Exception as e:
                logger.error(f"Error updating user activity: {e}")
        
        response = self.get_response(request)
        return response
    
    def _should_track_request(self, request):
        """Determine if this request should be tracked for activity"""
        # Don't track static files, admin, or API health checks
        excluded_paths = [
            '/static/',
            '/media/',
            '/admin/',
            '/api/health/',
            '/favicon.ico',
            '/robots.txt',
        ]
        
        path = request.path
        return not any(path.startswith(excluded) for excluded in excluded_paths)
    
    def _update_user_activity(self, user):
        """Update user's last_active and streak activity"""
        now = timezone.now()
        today = now.date()
        
        # Update last_active (debounced to avoid excessive writes)
        should_update_last_active = (
            not user.last_active or 
            (now - user.last_active).total_seconds() > 300  # 5 minutes
        )
        
        if should_update_last_active:
            user.last_active = now
            user.save(update_fields=['last_active'])
        
        # Update or create streak record
        streak, created = Streak.objects.get_or_create(
            user=user,
            defaults={
                'current_streak': 1,  # Start with 1 for first activity
                'max_streak': 1,
                'last_activity_date': today
            }
        )
        
        # Only update streak if it's a new day or if last_activity_date is None
        if not streak.last_activity_date or streak.last_activity_date != today:
            # Check if this is a consecutive day
            if streak.last_activity_date:
                days_diff = (today - streak.last_activity_date).days
                
                if days_diff == 1:
                    # Consecutive day - increment streak
                    streak.current_streak += 1
                    streak.max_streak = max(streak.max_streak, streak.current_streak)
                elif days_diff > 1:
                    # Streak broken - reset to 1
                    streak.current_streak = 1
                # If days_diff == 0, it's the same day, don't change streak
            else:
                # First activity ever - start with streak of 1
                streak.current_streak = 1
                streak.max_streak = 1
            
            streak.last_activity_date = today
            streak.save()
        
        # Create or update daily activity record
        activity, created = DailyActivity.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                'status': 'partial',  # Mark as partial for general activity
                'problems_solved': 0,
                'lesson_ids': []
            }
        )
        
        # Update activity status to at least 'partial' if user is active
        if activity.status == 'none':
            activity.status = 'partial'
            activity.save()

class SessionActivityMiddleware(MiddlewareMixin):
    """
    Middleware to track session-based activity and handle token refresh
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
    
    def process_request(self, request):
        """Track session activity and handle token refresh"""
        if request.user.is_authenticated:
            try:
                self._update_session_activity(request.user)
            except Exception as e:
                logger.error(f"Error updating session activity: {e}")
        
        response = self.get_response(request)
        return response
    
    def _update_session_activity(self, user):
        """Update user's session activity"""
        # Update Django's built-in last_login if it's been more than 1 hour
        # This is optional but useful for admin/analytics
        now = timezone.now()
        if not user.last_login or (now - user.last_login).total_seconds() > 3600:  # 1 hour
            user.last_login = now
            user.save(update_fields=['last_login'])
    
    def process_response(self, request, response):
        """Handle token refresh and activity tracking in response"""
        if request.user.is_authenticated:
            try:
                # Check if this is a token refresh request
                if request.path.endswith('/refresh/') and response.status_code == 200:
                    self._handle_token_refresh(request.user)
            except Exception as e:
                logger.error(f"Error handling token refresh: {e}")
        
        return response
    
    def _handle_token_refresh(self, user):
        """Handle activity tracking when token is refreshed"""
        now = timezone.now()
        today = now.date()
        
        # Update last_active on token refresh
        user.last_active = now
        user.save(update_fields=['last_active'])
        
        # Update streak to mark user as active today
        try:
            streak = Streak.objects.get(user=user)
            if not streak.last_activity_date or streak.last_activity_date != today:
                # This is a new day of activity
                if streak.last_activity_date:
                    days_diff = (today - streak.last_activity_date).days
                    if days_diff == 1:
                        streak.current_streak += 1
                        streak.max_streak = max(streak.max_streak, streak.current_streak)
                    elif days_diff > 1:
                        streak.current_streak = 1
                
                streak.last_activity_date = today
                streak.save()
                
                # Create or update daily activity
                activity, created = DailyActivity.objects.get_or_create(
                    user=user,
                    date=today,
                    defaults={
                        'status': 'partial',
                        'problems_solved': 0,
                        'lesson_ids': []
                    }
                )
                
                if activity.status == 'none':
                    activity.status = 'partial'
                    activity.save()
                    
        except Streak.DoesNotExist:
            # Create streak record if it doesn't exist
            Streak.objects.create(
                user=user,
                current_streak=1,
                max_streak=1,
                last_activity_date=today
            )
            
            # Create daily activity
            DailyActivity.objects.create(
                user=user,
                date=today,
                status='partial',
                problems_solved=0,
                lesson_ids=[]
            )

class LearningActivityMiddleware(MiddlewareMixin):
    """
    Middleware to track specific learning activities and update streaks accordingly
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
    
    def process_request(self, request):
        """Track learning-specific activities"""
        if request.user.is_authenticated:
            self._track_learning_activity(request)
        
        response = self.get_response(request)
        return response
    
    def _track_learning_activity(self, request):
        """Track specific learning activities"""
        path = request.path
        method = request.method
        
        # Define learning activity endpoints
        learning_endpoints = {
            '/api/streak/': 'streak_update',
            '/api/lms/lessons/': 'lesson_view',
            '/api/lms/problems/': 'problem_view',
            '/api/lms/courses/': 'course_view',
        }
        
        # Check if this is a learning activity
        for endpoint, activity_type in learning_endpoints.items():
            if path.startswith(endpoint):
                try:
                    self._update_learning_activity(request.user, activity_type)
                except Exception as e:
                    logger.error(f"Error tracking learning activity: {e}")
                break
    
    def _update_learning_activity(self, user, activity_type):
        """Update learning activity tracking"""
        today = timezone.now().date()
        
        # Get or create daily activity
        activity, created = DailyActivity.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                'status': 'partial',
                'problems_solved': 0,
                'lesson_ids': []
            }
        )
        
        # Update activity based on type
        if activity_type == 'streak_update':
            # This is a learning action - mark as partial or complete
            if activity.status == 'none':
                activity.status = 'partial'
                activity.save()
        elif activity_type in ['lesson_view', 'problem_view', 'course_view']:
            # User is actively learning - mark as partial
            if activity.status == 'none':
                activity.status = 'partial'
                activity.save() 