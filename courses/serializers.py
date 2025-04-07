from rest_framework import serializers
from .models import Category, Course, Module, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'slug', 'description', 'progress', 
            'type', 'problem', 'language_options', 'narration',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = [
            'id', 'title', 'description', 'lesson_ids',
            'lessons', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'is_new', 'progress', 'module_ids', 'modules',
            'author_id', 'is_published', 'created_at', 'updated_at'
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
