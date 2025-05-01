from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import (
    Category, Course, Lesson, LessonContentBlock, Problem,
    UserProgress, UserReward
)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description']
    search_fields = ['title', 'description']


class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'created_at']
    list_filter = ['category', 'is_published']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}


class LessonContentBlockInline(admin.TabularInline):
    model = LessonContentBlock
    extra = 1
    fields = ['block_type', 'content', 'problem', 'order']
    raw_id_fields = ['problem']
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['content'].initial = {}
        return formset


class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'lesson_number', 'is_published']
    list_filter = ['course', 'is_published']
    search_fields = ['title', 'course__title']
    inlines = [LessonContentBlockInline]
    
    def get_inline_instances(self, request, obj=None):
        if not obj:  # Don't show inlines on create view
            return []
        return super().get_inline_instances(request, obj)


class LessonContentBlockAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'block_type', 'order', 'has_problem']
    list_filter = ['block_type', 'lesson__course']
    search_fields = ['lesson__title', 'content']
    raw_id_fields = ['problem', 'lesson']
    
    def has_problem(self, obj):
        return bool(obj.problem)
    has_problem.boolean = True
    has_problem.short_description = 'Has Problem'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # Only for new objects
            form.base_fields['content'].initial = {}
            
        # Make problem field required for problem block type
        if obj and obj.block_type == 'problem':
            form.base_fields['problem'].required = True
            
        return form
    
    def save_model(self, request, obj, form, change):
        """
        Custom save method to handle content initialization
        """
        if not change:  # Only for new objects
            if obj.block_type == 'problem':
                # Initialize problem block content
                obj.content = {
                    "introduction": obj.content.get('introduction', ''),
                    "attempts_allowed": obj.content.get('attempts_allowed', 3),
                    "points": obj.content.get('points', 10)
                }
            else:
                # For other block types
                obj.content = obj.content or {}
        
        try:
            super().save_model(request, obj, form, change)
        except Exception as e:
            # Add more context to the error
            if 'content' in str(e):
                raise ValidationError(f"Content validation error: {str(e)}")
            raise


class ProblemInline(admin.TabularInline):
    model = Problem
    extra = 1
    fields = ['question_text', 'question_type', 'order']
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['content'].initial = {}
        return formset


class ProblemAdmin(admin.ModelAdmin):
    list_display = ['id', 'question_text_short', 'lesson', 'question_type', 
                   'order', 'created_at']
    list_filter = ['question_type', 'lesson__course']
    search_fields = ['question_text', 'explanation']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # Only for new objects
            form.base_fields['content'].initial = {}
            form.base_fields['options'].initial = []
            form.base_fields['correct_answer'].initial = []
        return form
    
    def save_model(self, request, obj, form, change):
        try:
            # Initialize content if empty
            if not obj.content or obj.content == []:
                obj.content = {}
            
            # Initialize options and correct_answer for multiple choice questions
            if obj.question_type in ['multiple_choice', 'single_choice']:
                if not obj.options:
                    obj.options = []
                if not obj.correct_answer:
                    obj.correct_answer = []
            
            # Run validation
            obj.clean()
            
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            from django.contrib import messages
            messages.error(request, str(e))
            raise
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f"An error occurred: {str(e)}")
            raise

    def question_text_short(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = "Question"


# New admin classes for progress and rewards models

class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'status',
                    'score', 'last_visited_at', 'completed_at']
    list_filter = ['status', 'lesson__course', 'completed_at']
    search_fields = ['user__username', 'lesson__title']
    date_hierarchy = 'last_visited_at'


class UserRewardAdmin(admin.ModelAdmin):
    list_display = ['user', 'reward_type',
                    'reward_name', 'value', 'awarded_at']
    list_filter = ['reward_type', 'awarded_at']
    search_fields = ['user__username', 'reward_name']
    date_hierarchy = 'awarded_at'


# Register your models here
admin.site.register(Category)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(LessonContentBlock, LessonContentBlockAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(UserProgress, UserProgressAdmin)
admin.site.register(UserReward, UserRewardAdmin)
