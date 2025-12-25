from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta

User = get_user_model()

class GamificationProgress(models.Model):
    """
    Phase 10: user_progress table.
    Single Source of Truth for a learner's stored value.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gamification_progress')
    xp_total = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    identity = models.CharField(
        max_length=50, 
        choices=[
            ('explorer', 'Explorer'),
            ('builder', 'Builder'),
            ('solver', 'Solver'),
            ('mentor', 'Mentor')
        ],
        default='explorer'
    )
    league = models.CharField(max_length=50, default='Bronze')
    weekly_velocity = models.FloatField(default=0.0, help_text="XP earned in the last 7 days")

    def __str__(self):
        return f"{self.user.username} - {self.identity} (Lvl {self.level})"

class MomentumState(models.Model):
    """
    Phase 10: momentum_state table.
    Tracks rhythm and consecutive engagement with soft decay.
    """
    STATE_CHOICES = [
        ('stable', 'Stable'),
        ('unstable', 'Unstable'),
        ('dormant', 'Dormant'),
        ('restored', 'Restored'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='momentum_state')
    streak_count = models.FloatField(default=0.0)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='stable')
    last_active_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.streak_count} days ({self.state})"

class EnergyWallet(models.Model):
    """
    Phase 10: energy_wallet table.
    Conserved quantity used to absorb friction.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='energy_wallet')
    energy_balance = models.IntegerField(default=3, validators=[MinValueValidator(0)])
    lifetime_earned = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Energy: {self.energy_balance}"

class ActivityLog(models.Model):
    """
    Phase 10: activity_log (append-only).
    Financial-grade audit trail of every unit of effort.
    """
    ACTION_TYPES = [
        ('problem_attempt', 'Problem Attempt'),
        ('solve', 'Solve'),
        ('return', 'Return After Absence'),
        ('help', 'Help Others'),
        ('momentum_decay', 'Momentum Decay'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    xp_delta = models.IntegerField(default=0)
    energy_delta = models.IntegerField(default=0)
    request_id = models.UUIDField(null=True, unique=True, db_index=True)
    created_at = models.DateTimeField(db_index=True, default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.action_type} - {self.xp_delta}XP"

# Legacy support / To be refactored
class Streak(models.Model):
    """
    DEPRECATED: Use MomentumState and GamificationProgress instead.
    Keeping temporarily for migration compatibility.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)
    lessons_completed = models.IntegerField(default=0)
    problems_to_next_streak = models.IntegerField(default=3)
    current_energy = models.IntegerField(default=3)
    max_energy = models.IntegerField(default=3)
    last_activity_date = models.DateField(null=True, blank=True)
    last_energy_update = models.DateTimeField(default=timezone.now)
    xp = models.IntegerField(default=0)
    daily_xp = models.IntegerField(default=0)
    weekly_xp = models.IntegerField(default=0)
    monthly_xp = models.IntegerField(default=0)
    last_xp_reset = models.DateField(null=True, blank=True)
    last_weekly_reset = models.DateField(null=True, blank=True)
    last_monthly_reset = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Legacy Streak"

class DailyActivity(models.Model):
    ACTIVITY_STATUS = (
        ('none', 'None'),
        ('partial', 'Partial'),
        ('complete', 'Complete'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_activities')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=ACTIVITY_STATUS, default='none')
    problems_solved = models.IntegerField(default=0)
    lesson_ids = models.JSONField(default=list)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

class Notification(models.Model):
    TYPE_CHOICES = [
        ('achievement', _('Achievement')),
        ('streak', _('Streak')),
        ('streak_decay_warning', _('Streak Decay Warning')),
        ('energy_full', _('Energy Full')),
        ('league', _('League Update')),
        ('system', _('System Notification')),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'type', 'is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.created_at}"
 