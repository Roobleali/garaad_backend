from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta

User = get_user_model()

class Streak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)
    lessons_completed = models.IntegerField(default=0)
    problems_to_next_streak = models.IntegerField(default=3, validators=[MinValueValidator(1)])
    current_energy = models.IntegerField(default=3, validators=[MinValueValidator(0), MaxValueValidator(3)])
    max_energy = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    last_activity_date = models.DateField(null=True, blank=True)
    last_energy_update = models.DateTimeField(default=timezone.now)
    
    # XP tracking
    xp = models.IntegerField(default=0)  # Total XP earned
    daily_xp = models.IntegerField(default=0)  # XP earned today
    weekly_xp = models.IntegerField(default=0)  # XP earned this week
    monthly_xp = models.IntegerField(default=0)  # XP earned this month
    last_xp_reset = models.DateField(null=True, blank=True)  # Track when daily XP was last reset
    last_weekly_reset = models.DateField(null=True, blank=True)  # Track when weekly XP was last reset
    last_monthly_reset = models.DateField(null=True, blank=True)  # Track when monthly XP was last reset

    def __str__(self):
        return f"{self.user.username}'s Streak"

    def update_energy(self):
        """Update energy based on time passed"""
        now = timezone.now()
        hours_passed = (now - self.last_energy_update).total_seconds() / 3600
        energy_to_add = int(hours_passed / 4)  # Gain 1 energy every 4 hours
        
        if energy_to_add > 0:
            self.current_energy = min(self.current_energy + energy_to_add, self.max_energy)
            self.last_energy_update = now - timedelta(hours=hours_passed % 4)
            self.save(update_fields=['current_energy', 'last_energy_update'])
            return True
        return False

    def use_energy(self):
        """Use one energy point if available"""
        if self.current_energy > 0:
            self.current_energy -= 1
            self.last_energy_update = timezone.now()
            self.save(update_fields=['current_energy', 'last_energy_update'])
            # Create notification for energy usage
            Notification.objects.create(
                user=self.user,
                type='energy',
                title='Energy Used',
                message=f'Tamar ayaa la isticmaalay. Waxaad haysataa {self.current_energy} tamar ah.',
                data={'remaining_energy': self.current_energy}
            )
            return True
        return False

    def reset_xp_counters(self):
        """Reset daily, weekly, and monthly XP if needed"""
        today = timezone.now().date()
        
        # Reset daily XP
        if self.last_xp_reset != today:
            self.daily_xp = 0
            self.last_xp_reset = today
        
        # Reset weekly XP (on Mondays)
        if not self.last_weekly_reset or (today - self.last_weekly_reset).days >= 7:
            self.weekly_xp = 0
            self.last_weekly_reset = today
        
        # Reset monthly XP (on 1st of month)
        if not self.last_monthly_reset or (today - self.last_monthly_reset).days >= 30:
            self.monthly_xp = 0
            self.last_monthly_reset = today
        
        self.save(update_fields=['daily_xp', 'weekly_xp', 'monthly_xp', 
                                'last_xp_reset', 'last_weekly_reset', 'last_monthly_reset'])

    def award_xp(self, amount, xp_type='problem'):
        """Award XP to the user with different types of rewards"""
        self.reset_xp_counters()
        
        # Base XP for daily streak
        if xp_type == 'streak':
            self.xp += amount
            self.daily_xp += amount
            self.weekly_xp += amount
            self.monthly_xp += amount
        # XP for completing problems
        elif xp_type == 'problem':
            self.xp += amount
            self.daily_xp += amount
            self.weekly_xp += amount
            self.monthly_xp += amount
        # Bonus XP for milestones
        elif xp_type == 'milestone':
            self.xp += amount
            self.daily_xp += amount
            self.weekly_xp += amount
            self.monthly_xp += amount
        
        self.save(update_fields=['xp', 'daily_xp', 'weekly_xp', 'monthly_xp'])
        
        # Check for league promotion
        from leagues.models import UserLeague, League
        default_league = League.objects.order_by('min_xp').first()
        if not default_league:
            raise Exception("No default league found in the system")
            
        user_league, _ = UserLeague.objects.get_or_create(
            user=self.user,
            defaults={
                'current_league': default_league,
                'total_xp': 0,
                'weekly_xp': 0,
                'monthly_xp': 0
            }
        )
        
        # Update UserLeague points
        user_league.update_weekly_points(amount)
        
        next_league = League.objects.filter(min_xp__gt=user_league.current_league.min_xp).order_by('min_xp').first()
        if next_league and self.xp >= next_league.min_xp:
            old_league = user_league.current_league
            user_league.current_league = next_league
            user_league.save()
            
            # Create league promotion notification
            Notification.objects.create(
                user=self.user,
                type='league',
                title='League Promotion!',
                message=f'Waad ku mahadsantahay kor u kacista {next_league.somali_name}!',
                data={
                    'old_league': old_league.name,
                    'new_league': next_league.name,
                    'xp_earned': amount
                }
            )
            
            # Create competition notification for league ranking
            Notification.create_competition_notification(
                self.user,
                'league_rank',
                {
                    'rank': user_league.rank,
                    'league': next_league.somali_name
                }
            )

    def update_streak(self, problems_solved, lesson_ids):
        today = timezone.now().date()
        
        # Check if user has energy to perform this action
        if not self.use_energy():
            raise ValueError("Not enough energy to perform this action")
        
        # Reset XP counters
        self.reset_xp_counters()
        
        # Update streak
        if not self.last_activity_date:
            self.current_streak = 1
            self.award_xp(20, 'streak')
            # Create first streak notification
            Notification.objects.create(
                user=self.user,
                type='streak',
                title='First Streak!',
                message='Waad ku mahadsantahay bilowga xariggaaga!',
                data={'streak_days': 1, 'xp_earned': 20}
            )
            # Create first problem achievement
            Notification.create_achievement_notification(
                self.user,
                'first_problem',
                {'problems_solved': problems_solved}
            )
        elif (today - self.last_activity_date).days == 1:
            self.current_streak += 1
            self.award_xp(20, 'streak')
            
            # Create reminder for next day
            Notification.create_reminder_notification(self.user, self.current_streak)
            
            # Award milestone XP and create notifications
            if self.current_streak in [7, 30, 100]:
                self.award_xp(50, 'milestone')
                Notification.objects.create(
                    user=self.user,
                    type='milestone',
                    title=f'{self.current_streak} Day Streak!',
                    message=f'Waad ku mahadsantahay {self.current_streak} maalmood oo xarig ah!',
                    data={'streak_days': self.current_streak, 'xp_earned': 50}
                )
                
                # Create weekly/monthly achievement notifications
                if self.current_streak == 7:
                    Notification.create_achievement_notification(
                        self.user,
                        'first_week',
                        {'streak_days': 7}
                    )
                elif self.current_streak == 30:
                    Notification.create_achievement_notification(
                        self.user,
                        'first_month',
                        {'streak_days': 30}
                    )
        elif (today - self.last_activity_date).days > 1:
            self.current_streak = 1
            self.award_xp(20, 'streak')
            # Create streak reset notification with encouragement
            Notification.objects.create(
                user=self.user,
                type='streak',
                title='Streak Reset',
                message='Xariggaaga waa la cusboonaysiiyay. Aan kuu sameyno mid cusub!',
                data={'streak_days': 1, 'xp_earned': 20}
            )
            # Create reminder to come back
            Notification.create_reminder_notification(self.user, 0)
        
        # Update streak-related fields
        self.max_streak = max(self.max_streak, self.current_streak)
        self.lessons_completed += len(lesson_ids)
        self.last_activity_date = today
        
        # Award XP for problems solved
        problem_xp = min(problems_solved * 5, 20)
        self.award_xp(problem_xp, 'problem')
        
        # Update problems_to_next_streak
        if problems_solved >= 3:
            self.problems_to_next_streak = max(1, self.problems_to_next_streak - 1)
        
        self.save()
        
        # Create or update DailyActivity
        activity, created = DailyActivity.objects.get_or_create(user=self.user, date=today)
        activity.problems_solved = problems_solved
        activity.lesson_ids = lesson_ids
        if problems_solved == 0:
            activity.status = 'none'
        elif problems_solved < 3:
            activity.status = 'partial'
        else:
            activity.status = 'complete'
            # Create first lesson achievement if this is the first complete day
            if not DailyActivity.objects.filter(user=self.user, status='complete').exclude(id=activity.id).exists():
                Notification.create_achievement_notification(
                    self.user,
                    'first_lesson',
                    {'problems_solved': problems_solved}
                )
        activity.save()

class DailyActivity(models.Model):
    ACTIVITY_STATUS = (
        ('none', 'None'),
        ('partial', 'Partial'),
        ('complete', 'Complete'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_activities')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=ACTIVITY_STATUS, default='none')
    problems_solved = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    lesson_ids = models.JSONField(default=list)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']  # Order by date descending
        indexes = [
            models.Index(fields=['user', 'date']),  # Add index for faster queries
        ]

    def __str__(self):
        return f"{self.user.username}'s activity on {self.date}"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('streak', 'Streak Update'),
        ('league', 'League Promotion'),
        ('milestone', 'Milestone Achieved'),
        ('energy', 'Energy Update'),
        ('welcome', 'Welcome Message'),
        ('reminder', 'Reminder'),
        ('achievement', 'Achievement'),
        ('competition', 'Competition'),
        ('social', 'Social Interaction'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gamification_notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=255)
    data = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'type', 'is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.created_at}"

    @classmethod
    def create_welcome_notification(cls, user):
        """Create welcome notification for new users"""
        return cls.objects.create(
            user=user,
            type='welcome',
            title='Welcome to Garaad!',
            message='Ku soo dhaweeyay Garaad! Aan kuu sameyno maalintaa aad u baahan tahay.',
            data={'action': 'start_learning'}
        )

    @classmethod
    def create_reminder_notification(cls, user, streak_days):
        """Create reminder notification based on streak status"""
        if streak_days == 0:
            return cls.objects.create(
                user=user,
                type='reminder',
                title='Come Back!',
                message='Maanta waa maalin wanaagsan oo aad ku baran karto!',
                data={'action': 'continue_learning'}
            )
        elif streak_days == 2:
            return cls.objects.create(
                user=user,
                type='reminder',
                title='Keep Going!',
                message='Waxaad horey u qaadatay 2 maalmood! Aan kuu sameyno 3aad!',
                data={'action': 'maintain_streak'}
            )
        elif streak_days == 6:
            return cls.objects.create(
                user=user,
                type='reminder',
                title='Weekly Goal!',
                message='Waxaad horey u qaadatay 6 maalmood! Aan kuu sameyno 7aad!',
                data={'action': 'weekly_goal'}
            )

    @classmethod
    def create_achievement_notification(cls, user, achievement_type, data):
        """Create achievement notification"""
        achievements = {
            'first_problem': {
                'title': 'First Problem Solved!',
                'message': 'Waad ku mahadsantahay xallinta su\'aasha ugu horeysa!'
            },
            'first_lesson': {
                'title': 'First Lesson Completed!',
                'message': 'Waad ku mahadsantahay dhammaystirka casharka ugu horeysa!'
            },
            'first_week': {
                'title': 'First Week Complete!',
                'message': 'Waad ku mahadsantahay dhammaystirka toddobaadka ugu horeysa!'
            },
            'first_month': {
                'title': 'First Month Complete!',
                'message': 'Waad ku mahadsantahay dhammaystirka bilka ugu horeysa!'
            }
        }
        
        if achievement_type in achievements:
            return cls.objects.create(
                user=user,
                type='achievement',
                title=achievements[achievement_type]['title'],
                message=achievements[achievement_type]['message'],
                data=data
            )

    @classmethod
    def create_competition_notification(cls, user, competition_type, data):
        """Create competition notification"""
        competitions = {
            'league_rank': {
                'title': 'League Ranking Update!',
                'message': 'Waxaad ku jirtaa {rank}kaa {league}ka!'
            },
            'weekly_challenge': {
                'title': 'Weekly Challenge!',
                'message': 'Maanta waa cusub! Aan kuu sameyno cabsiyada usbuuca!'
            },
            'top_performer': {
                'title': 'Top Performer!',
                'message': 'Waxaad ka mid tahay kuwa ugu fiican {league}ka!'
            }
        }
        
        if competition_type in competitions:
            return cls.objects.create(
                user=user,
                type='competition',
                title=competitions[competition_type]['title'],
                message=competitions[competition_type]['message'].format(**data),
                data=data
            ) 