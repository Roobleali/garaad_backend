from rest_framework import serializers
from .models import (
    Category, Course, Module, Lesson, LessonContentBlock,
    Problem, Hint, SolutionStep, PracticeSet, PracticeSetProblem,
    UserProgress, CourseEnrollment, UserReward, LeaderboardEntry
)
from django.db import models


class HintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hint
        fields = ['id', 'content', 'order']


class SolutionStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolutionStep
        fields = ['id', 'explanation', 'order']


class ProblemSerializer(serializers.ModelSerializer):
    hints = HintSerializer(many=True, read_only=True)
    solution_steps = SolutionStepSerializer(many=True, read_only=True)

    class Meta:
        model = Problem
        fields = [
            'id', 'question_text', 'question_type', 'options',
            'correct_answer', 'explanation', 'difficulty',
            'hints', 'solution_steps', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class LessonContentBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonContentBlock
        fields = ['id', 'lesson', 'block_type',
                  'content', 'order', 'created_at']
        read_only_fields = ['created_at']


class LessonSerializer(serializers.ModelSerializer):
    content_blocks = LessonContentBlockSerializer(many=True, read_only=True)
    module = serializers.PrimaryKeyRelatedField(queryset=Module.objects.all())

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'slug', 'module', 'lesson_number',
            'estimated_time', 'is_published', 'content_blocks',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PracticeSetProblemSerializer(serializers.ModelSerializer):
    problem_details = ProblemSerializer(source='problem', read_only=True)

    class Meta:
        model = PracticeSetProblem
        fields = ['id', 'practice_set', 'problem', 'problem_details', 'order']


class PracticeSetSerializer(serializers.ModelSerializer):
    practice_set_problems = PracticeSetProblemSerializer(
        many=True, read_only=True)

    class Meta:
        model = PracticeSet
        fields = [
            'id', 'title', 'lesson', 'module', 'practice_type',
            'difficulty_level', 'is_randomized', 'is_published',
            'practice_set_problems', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    practice_sets = PracticeSetSerializer(many=True, read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Module
        fields = [
            'id', 'title', 'description', 'lesson_ids',
            'lessons', 'practice_sets', 'course', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all())

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'is_new', 'progress', 'module_ids', 'modules',
            'author_id', 'is_published', 'category', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']


class CourseListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing courses without including all related modules.
    """
    module_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'is_new', 'progress', 'category', 'author_id',
            'is_published', 'module_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_module_count(self, obj):
        return obj.modules.count()


class CategorySerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'title', 'description', 'image',
            'in_progress', 'course_ids', 'courses'
        ]


# New serializers for progress and rewards

class UserProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.StringRelatedField(
        source='lesson.title', read_only=True)
    module_title = serializers.StringRelatedField(
        source='lesson.module.title', read_only=True)

    class Meta:
        model = UserProgress
        fields = [
            'id', 'user', 'lesson', 'lesson_title', 'module_title',
            'status', 'score', 'last_visited_at', 'completed_at'
        ]
        read_only_fields = ['last_visited_at', 'completed_at']


class UserProgressUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user progress (used for marking lessons as in progress or completed).
    """
    class Meta:
        model = UserProgress
        fields = ['status', 'score']


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.StringRelatedField(
        source='course.title', read_only=True)

    class Meta:
        model = CourseEnrollment
        fields = [
            'id', 'user', 'course', 'course_title',
            'progress_percent', 'enrolled_at'
        ]
        read_only_fields = ['progress_percent', 'enrolled_at']


class UserRewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReward
        fields = [
            'id', 'user', 'reward_type', 'reward_name',
            'value', 'awarded_at'
        ]
        read_only_fields = ['awarded_at']


class LeaderboardEntrySerializer(serializers.ModelSerializer):
    username = serializers.StringRelatedField(
        source='user.username', read_only=True)
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = LeaderboardEntry
        fields = [
            'id', 'user', 'username', 'points',
            'time_period', 'last_updated', 'user_info'
        ]
        read_only_fields = ['points', 'last_updated']

    def get_user_info(self, obj):
        """
        Get additional user information including profile, badges, 
        total rewards, and stats.
        """
        user = obj.user

        # Get user's badges
        badges = UserReward.objects.filter(
            user=user,
            reward_type='badge'
        ).values('id', 'reward_name', 'value', 'awarded_at')

        # Get user's streak information
        streak = UserReward.objects.filter(
            user=user,
            reward_type='streak'
        ).order_by('-awarded_at').first()

        # Get total points
        total_points = UserReward.objects.filter(
            user=user,
            reward_type='points'
        ).aggregate(total=models.Sum('value'))['total'] or 0

        # Get progress data
        completed_lessons = UserProgress.objects.filter(
            user=user,
            status='completed'
        ).count()

        enrolled_courses = CourseEnrollment.objects.filter(
            user=user
        ).count()

        # Return compiled user information
        return {
            # Basic user info
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,

            # User stats
            'stats': {
                'total_points': total_points,
                'completed_lessons': completed_lessons,
                'enrolled_courses': enrolled_courses,
                'current_streak': streak.value if streak else 0,
                'badges_count': len(badges)
            },

            # Badges collection
            'badges': list(badges)
        }


class LessonWithNextSerializer(LessonSerializer):
    """
    Extended Lesson serializer that includes information about the next lesson.
    """
    next_lesson = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()

    class Meta(LessonSerializer.Meta):
        fields = LessonSerializer.Meta.fields + \
            ['next_lesson', 'user_progress']

    def get_next_lesson(self, obj):
        next_lesson = obj.get_next_lesson()
        if next_lesson:
            return {
                'id': next_lesson.id,
                'title': next_lesson.title,
                'slug': next_lesson.slug
            }
        return None

    def get_user_progress(self, obj):
        # Get user from context if provided
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None

        user = request.user
        try:
            progress = UserProgress.objects.get(user=user, lesson=obj)
            return {
                'status': progress.status,
                'score': progress.score,
                'completed_at': progress.completed_at
            }
        except UserProgress.DoesNotExist:
            return {
                'status': 'not_started',
                'score': None,
                'completed_at': None
            }


class CourseWithProgressSerializer(CourseSerializer):
    """
    Extended Course serializer that includes user's progress in the course.
    """
    user_progress = serializers.SerializerMethodField()

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['user_progress']

    def get_user_progress(self, obj):
        # Get user from context if provided
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None

        user = request.user
        try:
            enrollment = CourseEnrollment.objects.get(user=user, course=obj)
            return {
                'enrolled_at': enrollment.enrolled_at,
                'progress_percent': enrollment.progress_percent
            }
        except CourseEnrollment.DoesNotExist:
            return None
