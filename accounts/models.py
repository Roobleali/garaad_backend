# auth/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    
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
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    preferred_study_time = models.TextField(default='[]', blank=True)
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

    def get_preferred_study_time(self):
        import json
        return json.loads(self.preferred_study_time)

    def set_preferred_study_time(self, times):
        import json
        self.preferred_study_time = json.dumps(times)

    def get_subjects(self):
        import json
        return json.loads(self.subjects)

    def set_subjects(self, subjects):
        import json
        self.subjects = json.dumps(subjects)

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