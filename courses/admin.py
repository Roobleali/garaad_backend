from django.contrib import admin
from .models import (
    Category, Course, Module, Lesson, LessonContentBlock,
    Problem, Hint, SolutionStep, PracticeSet, PracticeSetProblem,
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


class ModuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'course', 'created_at']
    list_filter = ['course']
    search_fields = ['title', 'description']


class LessonContentBlockInline(admin.TabularInline):
    model = LessonContentBlock
    extra = 1
    fields = ['block_type', 'content', 'order']


class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'lesson_number',
                    'estimated_time', 'is_published', 'created_at']
    list_filter = ['module', 'is_published']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonContentBlockInline]


class LessonContentBlockAdmin(admin.ModelAdmin):
    list_display = ['id', 'lesson', 'block_type', 'order', 'created_at']
    list_filter = ['block_type', 'lesson__module']
    search_fields = ['lesson__title', 'content']


class HintInline(admin.TabularInline):
    model = Hint
    extra = 1
    fields = ['content', 'order']


class SolutionStepInline(admin.TabularInline):
    model = SolutionStep
    extra = 1
    fields = ['explanation', 'order']


class ProblemAdmin(admin.ModelAdmin):
    list_display = ['id', 'question_text_short',
                    'question_type', 'difficulty', 'created_at']
    list_filter = ['question_type', 'difficulty']
    search_fields = ['question_text', 'explanation']
    inlines = [HintInline, SolutionStepInline]

    def question_text_short(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = "Question"


class PracticeSetProblemInline(admin.TabularInline):
    model = PracticeSetProblem
    extra = 1
    fields = ['problem', 'order']


class PracticeSetAdmin(admin.ModelAdmin):
    list_display = ['title', 'practice_type', 'related_to',
                    'difficulty_level', 'is_published', 'created_at']
    list_filter = ['practice_type', 'difficulty_level', 'is_published']
    search_fields = ['title']
    inlines = [PracticeSetProblemInline]

    def related_to(self, obj):
        return obj.lesson.title if obj.lesson else obj.module.title
    related_to.short_description = "Related To"


class PracticeSetProblemAdmin(admin.ModelAdmin):
    list_display = ['id', 'practice_set', 'problem', 'order']
    list_filter = ['practice_set']
    search_fields = ['practice_set__title', 'problem__question_text']


# New admin classes for progress and rewards models

class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'status',
                    'score', 'last_visited_at', 'completed_at']
    list_filter = ['status', 'lesson__module', 'completed_at']
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
admin.site.register(Module, ModuleAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(LessonContentBlock, LessonContentBlockAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(PracticeSet, PracticeSetAdmin)
admin.site.register(PracticeSetProblem, PracticeSetProblemAdmin)

# Register new models
admin.site.register(UserProgress, UserProgressAdmin)
admin.site.register(CourseEnrollment, CourseEnrollmentAdmin)
admin.site.register(UserReward, UserRewardAdmin)
admin.site.register(LeaderboardEntry, LeaderboardEntryAdmin)
