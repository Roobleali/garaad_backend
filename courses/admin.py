from django.contrib import admin
from .models import Category, Course, Module, Lesson


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'in_progress']
    search_fields = ['title']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'level', 'price', 'created_at']
    list_filter = ['category', 'level']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'course']
    list_filter = ['course']
    search_fields = ['title', 'description']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order', 'created_at']
    list_filter = ['module']
    search_fields = ['title', 'content']
