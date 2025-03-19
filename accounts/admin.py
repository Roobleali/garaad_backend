# auth/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import StudentProfile

User = get_user_model()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_premium', 'created_at')
    search_fields = ('username', 'email')
    list_filter = ('is_premium', 'created_at')

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'proficiency_level', 'study_frequency')
    search_fields = ('user__username', 'user__email')
    list_filter = ('proficiency_level', 'created_at')