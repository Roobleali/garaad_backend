from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from leagues.models import UserLeague, League
from courses.models import UserReward
from api.models import Streak

class Command(BaseCommand):
    help = 'Fix league points calculation by updating UserLeague records with correct points from UserReward'

    def handle(self, *args, **options):
        self.stdout.write("Starting league points fix...")
        
        # Get all users with UserLeague records
        user_leagues = UserLeague.objects.all()
        self.stdout.write(f"Found {user_leagues.count()} UserLeague records")
        
        # Calculate time periods
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        updated_count = 0
        
        for user_league in user_leagues:
            user = user_league.user
            
            # Calculate points from UserReward records
            # All time points
            all_time_points = UserReward.objects.filter(
                user=user,
                reward_type='points'
            ).aggregate(total=Sum('value'))['total'] or 0
            
            # Weekly points
            weekly_points = UserReward.objects.filter(
                user=user,
                reward_type='points',
                awarded_at__gte=week_ago
            ).aggregate(total=Sum('value'))['total'] or 0
            
            # Monthly points
            monthly_points = UserReward.objects.filter(
                user=user,
                reward_type='points',
                awarded_at__gte=month_ago
            ).aggregate(total=Sum('value'))['total'] or 0
            
            # Update UserLeague record
            user_league.total_xp = all_time_points
            user_league.weekly_xp = weekly_points
            user_league.monthly_xp = monthly_points
            
            # Check for league promotion based on total XP
            next_league = League.objects.filter(min_xp__gt=user_league.current_league.min_xp).order_by('min_xp').first()
            if next_league and all_time_points >= next_league.min_xp:
                user_league.current_league = next_league
                self.stdout.write(f"Promoting {user.username} to {next_league.name}")
            
            user_league.save()
            updated_count += 1
            
            self.stdout.write(f"Updated {user.username}: total={all_time_points}, weekly={weekly_points}, monthly={monthly_points}")
        
        self.stdout.write(f"Successfully updated {updated_count} UserLeague records")
        
        # Also update Streak records to ensure consistency
        streaks = Streak.objects.all()
        self.stdout.write(f"Updating {streaks.count()} Streak records...")
        
        for streak in streaks:
            user = streak.user
            
            # Calculate total XP from UserReward
            total_xp = UserReward.objects.filter(
                user=user,
                reward_type='points'
            ).aggregate(total=Sum('value'))['total'] or 0
            
            # Update Streak XP
            streak.xp = total_xp
            streak.save()
            
            self.stdout.write(f"Updated {user.username} Streak XP to {total_xp}")
        
        self.stdout.write(
            self.style.SUCCESS('League points fix completed!')
        ) 