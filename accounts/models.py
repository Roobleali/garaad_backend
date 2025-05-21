# auth/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
import random
import string

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    
    # Additional fields
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    # Fix the related_name for groups and user_permissions
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="user_set_custom",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="user_set_custom",
        related_query_name="user",
    )
    
    def __str__(self):
        return self.username
    
    class Meta:
        ordering = ['-date_joined']
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class StudentProfile(models.Model):
    STUDY_TIME_CHOICES = [
        ('morning', 'Aroorti Subaxda inta aan quraacaynayo'),
        ('afternoon', 'Waqtiga Nasashasha intaan Khadaynayo'),
        ('evening', 'Habeenki ah ka dib cashada ama Kahor intan seexanin'),
        ('flexible', 'Waqti kale oo maalintayda ah')
    ]

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    preferred_study_time = models.CharField(
        max_length=20,
        choices=STUDY_TIME_CHOICES,
        default='flexible'
    )
    daily_goal_minutes = models.IntegerField(default=15)
    streak_charges = models.IntegerField(default=2)
    notification_preferences = models.JSONField(
        default=dict,
        help_text="User's notification preferences"
    )
    subjects = models.TextField(default='[]', blank=True)
    proficiency_level = models.CharField(
        max_length=20,
        choices=[
            ('Beginner', 'Beginner'),
            ('Intermediate', 'Intermediate'),
            ('Advanced', 'Advanced')
        ]
    )
    study_frequency = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_studentprofile'
        
    def __str__(self):
        return f"{self.user.email}'s Profile"

    def get_reminder_time(self):
        """Get the optimal reminder time based on preferred study time"""
        reminder_times = {
            'morning': 7,  # 7 AM for morning study
            'afternoon': 11,  # 11 AM for afternoon study
            'evening': 19,  # 7 PM for evening study
            'flexible': 12,  # Noon for flexible schedule
        }
        return reminder_times.get(self.preferred_study_time, 12)

    def get_study_time_badge(self):
        """Get the motivational badge for study time"""
        badges = {
            'morning': "قُلْ هَلْ يَسْتَوِي الَّذِينَ يَعْلَمُونَ وَالَّذِينَ لَا يَعْلَمُونَ",
            'afternoon': "وَقُل رَّبِّ زِدْنِي عِلْمًا",
            'evening': "يَرْفَعِ اللَّهُ الَّذِينَ آمَنُوا مِنْكُمْ وَالَّذِينَ أُوتُوا الْعِلْمَ دَرَجَاتٍ",
            'flexible': "فَاسْأَلُوا أَهْلَ الذِّكْرِ إِن كُنْتُمْ لَا تَعْلَمُونَ"
        }
        return badges.get(self.preferred_study_time, '')

    def get_goal_badge(self):
        """Get the motivational badge based on daily goal"""
        if self.daily_goal_minutes <= 5:
            return "Talaabo yar, guul weyn"
        elif self.daily_goal_minutes <= 10:
            return "Waqtigaaga si fiican u isticmaal"
        elif self.daily_goal_minutes <= 15:
            return "Adkaysi iyo dadaal"
        else:
            return "Waxbarasho joogto ah"

    def get_subjects(self):
        import json
        return json.loads(self.subjects)

    def set_subjects(self, subjects):
        import json
        self.subjects = json.dumps(subjects)

    def get_notification_preferences(self):
        """Get user's notification preferences with defaults"""
        defaults = {
            'email_notifications': True,
            'streak_reminders': True,
            'achievement_notifications': True,
            'daily_goal_reminders': True,
            'league_updates': True,
        }
        return {**defaults, **self.notification_preferences}

    def set_notification_preferences(self, preferences):
        """Update user's notification preferences"""
        current = self.get_notification_preferences()
        self.notification_preferences = {**current, **preferences}
        self.save()

    def use_streak_charge(self):
        """Use a streak charge to maintain streak"""
        if self.streak_charges > 0:
            self.streak_charges -= 1
            self.save()
            return True
        return False

    def add_streak_charge(self, amount=1):
        """Add streak charges to user's account"""
        self.streak_charges += amount
        self.save()

class UserOnboarding(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    goal = models.CharField(max_length=255, default="Horumarinta xirfadaha")
    learning_approach = models.CharField(max_length=255, default="Waxbarasho shaqsiyeed")
    topic = models.CharField(max_length=255, default="Xisaab")
    math_level = models.CharField(max_length=255, default="Bilowga")
    minutes_per_day = models.IntegerField(default=30)
    has_completed_onboarding = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s onboarding status: {'Completed' if self.has_completed_onboarding else 'Pending'}"

    class Meta:
        db_table = 'user_onboarding'

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='user_profile'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_userprofile'
        
    def __str__(self):
        return f"{self.user.username}'s Profile"

class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    @classmethod
    def generate_code(cls):
        """Generate a random 6-digit code"""
        return ''.join(random.choices(string.digits, k=6))

    def __str__(self):
        return f"Verification code for {self.user.email}"