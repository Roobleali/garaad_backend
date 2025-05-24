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
    last_energy_update = models.DateTimeField(auto_now=True)
    xp = models.IntegerField(default=0)  # Total XP earned
    daily_xp = models.IntegerField(default=0)  # XP earned today
    last_xp_reset = models.DateField(null=True, blank=True)  # Track when daily XP was last reset

    def __str__(self):
        return f"{self.user.username}'s Streak"

    def update_energy(self):
        """Update energy based on time passed"""
        now = timezone.now()
        hours_passed = (now - self.last_energy_update).total_seconds() / 3600
        energy_to_add = int(hours_passed / 4)  # Gain 1 energy every 4 hours
        
        if energy_to_add > 0:
            self.current_energy = min(self.current_energy + energy_to_add, self.max_energy)
            # Update last_energy_update to reflect the time used for energy regeneration
            self.last_energy_update = now - timedelta(hours=hours_passed % 4)
            self.save(update_fields=['current_energy', 'last_energy_update'])
            return True
        return False

    def use_energy(self):
        """Use one energy point if available"""
        if self.current_energy > 0:
            self.current_energy -= 1
            self.save(update_fields=['current_energy'])
            return True
        return False

    def reset_daily_xp(self):
        """Reset daily XP if it's a new day"""
        today = timezone.now().date()
        if self.last_xp_reset != today:
            self.daily_xp = 0
            self.last_xp_reset = today
            self.save(update_fields=['daily_xp', 'last_xp_reset'])

    def award_xp(self, amount, xp_type='problem'):
        """Award XP to the user with different types of rewards"""
        self.reset_daily_xp()
        
        # Base XP for daily streak
        if xp_type == 'streak':
            self.xp += amount
            self.daily_xp += amount
        # XP for completing problems
        elif xp_type == 'problem':
            self.xp += amount
            self.daily_xp += amount
        # Bonus XP for milestones
        elif xp_type == 'milestone':
            self.xp += amount
            self.daily_xp += amount
        
        self.save(update_fields=['xp', 'daily_xp'])

    def update_streak(self, problems_solved, lesson_ids):
        today = timezone.now().date()
        
        # Check if user has energy to perform this action
        if not self.use_energy():
            raise ValueError("Not enough energy to perform this action")
        
        # Reset daily XP if it's a new day
        self.reset_daily_xp()
        
        # Update streak
        if not self.last_activity_date:
            self.current_streak = 1
            self.award_xp(20, 'streak')  # Base XP for first streak
        elif (today - self.last_activity_date).days == 1:
            self.current_streak += 1
            self.award_xp(20, 'streak')  # Base XP for maintaining streak
            
            # Award milestone XP
            if self.current_streak in [7, 30, 100]:
                self.award_xp(50, 'milestone')  # Bonus XP for milestone streaks
        elif (today - self.last_activity_date).days > 1:
            self.current_streak = 1
            self.award_xp(20, 'streak')  # Base XP for new streak
        
        # Update streak-related fields
        self.max_streak = max(self.max_streak, self.current_streak)
        self.lessons_completed += len(lesson_ids)
        self.last_activity_date = today
        
        # Award XP for problems solved (cap at 20 XP per day)
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
        # Set status
        if problems_solved == 0:
            activity.status = 'none'
        elif problems_solved < 3:
            activity.status = 'partial'
        else:
            activity.status = 'complete'
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