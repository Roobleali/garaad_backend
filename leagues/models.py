from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from api.models import Streak

class League(models.Model):
    """Model representing a league level in the system."""
    name = models.CharField(max_length=100)
    somali_name = models.CharField(max_length=100)
    description = models.TextField()
    min_xp = models.IntegerField(default=0)
    order = models.IntegerField(unique=True)
    icon = models.ImageField(upload_to='league_icons/', null=True, blank=True)
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return self.somali_name  # Display only Somali name

class UserLeague(models.Model):
    """Model tracking user's league progress and XP."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    current_league = models.ForeignKey(League, on_delete=models.PROTECT)
    total_xp = models.IntegerField(default=0)
    weekly_xp = models.IntegerField(default=0)
    monthly_xp = models.IntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.current_league.name}"
    
    def add_xp(self, amount):
        """Add XP and update league if necessary."""
        self.total_xp += amount
        self.weekly_xp += amount
        self.monthly_xp += amount
        
        # Check for league promotion
        next_league = League.objects.filter(min_xp__gt=self.current_league.min_xp).order_by('min_xp').first()
        if next_league and self.total_xp >= next_league.min_xp:
            self.current_league = next_league
        
        self.save()
    
    def update_weekly_points(self, amount):
        """Update weekly points for the user."""
        self.weekly_xp += amount
        self.total_xp += amount
        self.monthly_xp += amount
        self.save()
    
    def update_monthly_points(self, amount):
        """Update monthly points for the user."""
        self.monthly_xp += amount
        self.total_xp += amount
        self.save()
    
    def reset_weekly_points(self):
        """Reset weekly points to 0."""
        self.weekly_xp = 0
        self.save()
    
    def reset_monthly_points(self):
        """Reset monthly points to 0."""
        self.monthly_xp = 0
        self.save()
