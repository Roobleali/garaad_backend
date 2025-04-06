from rest_framework import serializers
from .models import Course, Module, Lesson, Exercise


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'lesson', 'question', 'type', 'choices',
                  'correct_answer', 'explanation', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class LessonSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'module', 'title', 'content', 'type',
                  'order', 'exercises', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'course', 'title', 'description',
                  'order', 'lessons', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'description', 'thumbnail', 'level', 'category',
                  'author_id', 'is_published', 'modules', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']


class CourseListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing courses without including all related modules.
    """
    module_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'description', 'thumbnail', 'level', 'category',
                  'author_id', 'is_published', 'module_count', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_module_count(self, obj):
        return obj.modules.count()


class SubmitExerciseSerializer(serializers.Serializer):
    """
    Serializer for submitting answers to exercises.
    """
    answer = serializers.CharField(required=True)

    def validate_answer(self, value):
        if not value:
            raise serializers.ValidationError("Answer cannot be empty")
        return value
