from django.contrib import admin
from .models import Course, Lesson

class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']  # Changed 'name' to 'title'
    list_filter = ['category']

class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']  # Changed 'duration' to 'description'

admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
