from django.contrib import admin
from .models import (
    Category, Course, Lesson, LessonContentBlock,
    Problem, Hint, SolutionStep,
    UserProgress, CourseEnrollment, UserReward, LeaderboardEntry
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
    raw_id_fields = ['problem']
    
    def has_problem(self, obj):
        return bool(obj.problem)
    has_problem.boolean = True
    has_problem.short_description = 'Has Problem'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # Only for new objects
            form.base_fields['content'].initial = {}
        return form
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only for new objects
            obj.content = obj.default_content.get(obj.block_type, {})
        super().save_model(request, obj, form, change)


class HintInline(admin.TabularInline):
    model = Hint
    extra = 1
    fields = ['content', 'order']


class SolutionStepInline(admin.TabularInline):
    model = SolutionStep
    extra = 1
    fields = ['explanation', 'order']


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
                   'difficulty', 'order', 'created_at']
    list_filter = ['question_type', 'difficulty', 'lesson__course']
    search_fields = ['question_text', 'explanation']
    inlines = [HintInline, SolutionStepInline]
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # Only for new objects
            form.base_fields['content'].initial = {}
        return form
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only for new objects
            obj.content = {}
        super().save_model(request, obj, form, change)

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


class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'progress_percent', 'enrolled_at']
    list_filter = ['course', 'enrolled_at']
    search_fields = ['user__username', 'course__title']
    date_hierarchy = 'enrolled_at'


class UserRewardAdmin(admin.ModelAdmin):
    list_display = ['user', 'reward_type',
                    'reward_name', 'value', 'awarded_at']
    list_filter = ['reward_type', 'awarded_at']
    search_fields = ['user__username', 'reward_name']
    date_hierarchy = 'awarded_at'


class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'time_period', 'points', 'last_updated']
    list_filter = ['time_period']
    search_fields = ['user__username']
    ordering = ['-points']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(LessonContentBlock, LessonContentBlockAdmin)
admin.site.register(Problem, ProblemAdmin)

# Register new models
admin.site.register(UserProgress, UserProgressAdmin)
admin.site.register(CourseEnrollment, CourseEnrollmentAdmin)
admin.site.register(UserReward, UserRewardAdmin)
admin.site.register(LeaderboardEntry, LeaderboardEntryAdmin)
