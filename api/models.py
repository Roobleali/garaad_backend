from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

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

    def __str__(self):
        return f"{self.user.username}'s Streak"

    def update_energy(self):
        """Update energy based on time passed"""
        now = timezone.now()
        hours_passed = (now - self.last_energy_update).total_seconds() / 3600
        energy_to_add = int(hours_passed / 4)  # Gain 1 energy every 4 hours
        
        if energy_to_add > 0:
            self.current_energy = min(self.current_energy + energy_to_add, self.max_energy)
            self.last_energy_update = now
            self.save(update_fields=['current_energy', 'last_energy_update'])

    def use_energy(self):
        """Use one energy point if available"""
        self.update_energy()  # First update energy based on time passed
        if self.current_energy > 0:
            self.current_energy -= 1
            self.save(update_fields=['current_energy'])
            return True
        return False

    def update_streak(self, problems_solved, lesson_ids):
        today = timezone.now().date()
        
        # Check if user has energy to perform this action
        if not self.use_energy():
            raise ValueError("Not enough energy to perform this action")
        
        if not self.last_activity_date:
            self.current_streak = 1
        elif (today - self.last_activity_date).days == 1:
            self.current_streak += 1
        elif (today - self.last_activity_date).days > 1:
            self.current_streak = 1
        
        # Update streak-related fields
        self.max_streak = max(self.max_streak, self.current_streak)
        self.lessons_completed += len(lesson_ids)
        self.last_activity_date = today
        
        # Update problems_to_next_streak
        if problems_solved >= 3:
            self.problems_to_next_streak = max(1, self.problems_to_next_streak - 1)
        
        self.save()

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