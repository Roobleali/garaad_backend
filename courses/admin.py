from django.contrib import admin
from .models import Category, Course, Module, Lesson


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'in_progress']
    search_fields = ['title']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_new', 'progress', 'is_published']
    list_filter = ['category', 'is_new', 'is_published']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'course']
    list_filter = ['course']
    search_fields = ['title', 'description']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'type', 'progress']
    list_filter = ['module', 'type']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
