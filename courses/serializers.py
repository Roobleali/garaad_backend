from rest_framework import serializers
from .models import (
    Category, Course, Module, Lesson, LessonContentBlock,
    Problem, Hint, SolutionStep, PracticeSet, PracticeSetProblem
)


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
