from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from api.models import Streak, DailyActivity
from datetime import timedelta
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test the new activity tracking system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Test activity tracking for a specific user ID',
        )
        parser.add_argument(
            '--simulate-days',
            type=int,
            default=7,
            help='Number of days to simulate activity for',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        simulate_days = options.get('simulate_days')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                self.test_user_activity(user, simulate_days)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User with ID {user_id} not found"))
        else:
            # Test with a sample user
            users = User.objects.filter(is_active=True)[:5]
            for user in users:
                self.stdout.write(f"Testing activity tracking for user: {user.username}")
                self.test_user_activity(user, simulate_days)
                self.stdout.write("")

    def test_user_activity(self, user, simulate_days):
        """Test activity tracking for a specific user"""
        self.stdout.write(f"User: {user.username} ({user.email})")
        
        # Get current streak info
        try:
            streak = Streak.objects.get(user=user)
            self.stdout.write(f"  Current streak: {streak.current_streak}")
            self.stdout.write(f"  Max streak: {streak.max_streak}")
            self.stdout.write(f"  Last activity: {streak.last_activity_date}")
        except Streak.DoesNotExist:
            self.stdout.write("  No streak record found")
            streak = None
        
        # Get recent daily activities
        recent_activities = DailyActivity.objects.filter(
            user=user
        ).order_by('-date')[:simulate_days]
        
        self.stdout.write(f"  Recent activities ({recent_activities.count()} records):")
        for activity in recent_activities:
            self.stdout.write(f"    {activity.date}: {activity.status} ({activity.problems_solved} problems)")
        
        # Simulate activity for the last N days
        self.simulate_activity(user, simulate_days)
        
        # Show updated info
        try:
            streak = Streak.objects.get(user=user)
            self.stdout.write(f"  Updated streak: {streak.current_streak}")
            self.stdout.write(f"  Updated last activity: {streak.last_activity_date}")
        except Streak.DoesNotExist:
            self.stdout.write("  Still no streak record")

    def simulate_activity(self, user, days):
        """Simulate user activity for the past N days"""
        today = timezone.now().date()
        
        for i in range(days):
            activity_date = today - timedelta(days=i)
            
            # Create or update daily activity
            activity, created = DailyActivity.objects.get_or_create(
                user=user,
                date=activity_date,
                defaults={
                    'status': 'partial',
                    'problems_solved': 0,
                    'lesson_ids': []
                }
            )
            
            if created:
                self.stdout.write(f"    Created activity for {activity_date}")
            else:
                self.stdout.write(f"    Activity exists for {activity_date}")
        
        # Update streak based on consecutive days
        streak, created = Streak.objects.get_or_create(
            user=user,
            defaults={
                'current_streak': 1,
                'max_streak': 1,
                'last_activity_date': today
            }
        )
        
        if not created:
            # Calculate consecutive days
            consecutive_days = 0
            current_date = today
            
            while consecutive_days < days:
                if DailyActivity.objects.filter(user=user, date=current_date).exists():
                    consecutive_days += 1
                    current_date -= timedelta(days=1)
                else:
                    break
            
            streak.current_streak = consecutive_days
            streak.max_streak = max(streak.max_streak, consecutive_days)
            streak.last_activity_date = today
            streak.save()
            
            self.stdout.write(f"    Updated streak to {consecutive_days} days")

    def test_middleware_integration(self):
        """Test that middleware properly updates activity"""
        from core.middleware import UserActivityMiddleware
        
        # Create a mock request
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        # Test with a real user
        user = User.objects.filter(is_active=True).first()
        if user:
            request = MockRequest(user)
            middleware = UserActivityMiddleware(lambda req: None)
            
            try:
                middleware._update_user_activity(user)
                self.stdout.write(self.style.SUCCESS("Middleware activity update successful"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Middleware activity update failed: {e}")) 