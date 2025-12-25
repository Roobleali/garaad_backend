import logging
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)

class UserActivityMiddleware(MiddlewareMixin):
    """
    Passive middleware to track user presence.
    Ensures last_active is updated for presence tracking.
    DO NOT MUTATE GAMIFICATION STATE HERE.
    """
    
    def process_request(self, request):
        if request.user.is_authenticated and self._should_track_request(request):
            try:
                self._update_presence(request.user)
            except Exception as e:
                logger.error(f"Error updating presence: {e}")
        return None
    
    def _should_track_request(self, request):
        excluded_paths = ['/static/', '/media/', '/admin/', '/api/health/']
        path = request.path
        return not any(path.startswith(excluded) for excluded in excluded_paths)
    
    def _update_presence(self, user):
        """Debounced update of last_active timestamp"""
        now = timezone.now()
        should_update = (
            not user.last_active or 
            (now - user.last_active).total_seconds() > 300  # 5 minutes
        )
        if should_update:
            user.last_active = now
            user.save(update_fields=['last_active'])

class SessionActivityMiddleware(MiddlewareMixin):
    """
    Simplified session tracking.
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            now = timezone.now()
            user = request.user
            if not user.last_login or (now - user.last_login).total_seconds() > 3600:
                user.last_login = now
                user.save(update_fields=['last_login'])
        return None

# LearningActivityMiddleware is deprecated in v2 as activity is now central.
# Keeping a dummy class if needed for settings.py stability, but preferably remove it from settings.
class LearningActivityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        return None