from django.contrib import admin
from .models import Course, Module, Lesson, Exercise


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'level',
                    'author_id', 'is_published', 'created_at')
    list_filter = ('is_published', 'level', 'category')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course',)
    search_fields = ('title', 'description')
    inlines = [LessonInline]


class ExerciseInline(admin.TabularInline):
    model = Exercise
    extra = 1


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'type', 'order', 'created_at')
    list_filter = ('module', 'type')
    search_fields = ('title', 'content')
    inlines = [ExerciseInline]


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('question', 'lesson', 'type', 'created_at')
    list_filter = ('type', 'lesson')
    search_fields = ('question', 'explanation')
