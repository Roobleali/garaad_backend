from rest_framework import serializers
from .models import (
    Category, Course, Lesson, LessonContentBlock,
    Problem, UserProgress, UserReward
)
from django.db import models

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'description', 'image']

class LessonContentBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonContentBlock
        fields = ['id', 'lesson', 'block_type', 'content', 'order', 'problem']

    def to_internal_value(self, data):
        """
        Handle the case where content is empty or not provided
        """
        if 'content' not in data:
            data['content'] = None
        return super().to_internal_value(data)

    def validate(self, data):
        """
        Validate the complete object
        """
        block_type = data.get('block_type')
        content = data.get('content')
        problem = data.get('problem')

        # Handle problem block type
        if block_type == 'problem':
            if not problem:
                raise serializers.ValidationError({
                    'problem': 'Problem reference is required for problem blocks'
                })
            
            # Ensure minimum content structure for problem blocks
            default_content = {
                "introduction": "",
                "attempts_allowed": 3,
                "points": 10
            }
            
            # Update content with defaults for missing fields
            if content is None:
                content = default_content
            else:
                for key, value in default_content.items():
                    if key not in content:
                        content[key] = value
            
            data['content'] = content
            return data

        # Validate other block types
        content_schemas = {
            'text': {
                'text': serializers.CharField(),
                'format': serializers.ChoiceField(choices=['markdown', 'html'])
            },
            'example': {
                'title': serializers.CharField(),
                'description': serializers.CharField(),
                'problem': serializers.CharField(),
                'explanation': serializers.CharField()
            },
            'code': {
                'language': serializers.CharField(),
                'code': serializers.CharField(),
                'explanation': serializers.CharField(required=False),
                'show_line_numbers': serializers.BooleanField(default=True)
            },
            'image': {
                'url': serializers.URLField(),
                'caption': serializers.CharField(required=False),
                'alt': serializers.CharField(),
                'width': serializers.IntegerField(required=False, allow_null=True),
                'height': serializers.IntegerField(required=False, allow_null=True)
            },
            'video': {
                'url': serializers.URLField(),
                'title': serializers.CharField(),
                'description': serializers.CharField(required=False),
                'thumbnail': serializers.URLField(required=False),
                'duration': serializers.IntegerField(required=False, allow_null=True)
            },
            'quiz': {
                'title': serializers.CharField(),
                'questions': serializers.ListField(
                    child=serializers.DictField()
                )
            }
        }

        if block_type in content_schemas:
            schema = content_schemas[block_type]
            default_content = {}
            for field, field_type in schema.items():
                if content is None:
                    default_content[field] = field_type.default if hasattr(field_type, 'default') else None
                elif field not in content:
                    default_content[field] = field_type.default if hasattr(field_type, 'default') else None
            data['content'] = {**default_content, **content} if content is not None else default_content

        return data

    def create(self, validated_data):
        """
        Create a new LessonContentBlock instance
        """
        instance = super().create(validated_data)
        instance.validate_content()  # Run model validation
        return instance

    def update(self, instance, validated_data):
        """
        Update a LessonContentBlock instance
        """
        instance = super().update(instance, validated_data)
        instance.validate_content()  # Run model validation
        return instance

class LessonSerializer(serializers.ModelSerializer):
    content_blocks = LessonContentBlockSerializer(many=True, read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'slug', 'course', 'lesson_number',
            'estimated_time', 'is_published', 'content_blocks',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'is_new', 'progress', 'lessons',
            'category', 'author_id', 'is_published',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = [
            'id', 'introduction_text', 'question_text', 'question_type', 'options',
            'correct_answer', 'explanation', 'content', 'diagram_config', 'img',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def to_internal_value(self, data):
        """
        Handle the case where content is empty or not provided
        """
        if 'content' not in data or data['content'] == []:
            data['content'] = {}
        return super().to_internal_value(data)

    def validate(self, data):
        """
        Validate the complete object
        """
        # Ensure content is a dictionary
        if data.get('content') == []:
            data['content'] = {}
            
        # Validate options for multiple choice questions
        if data.get('question_type') in ['multiple_choice', 'single_choice']:
            options = data.get('options', [])
            if not options:
                raise serializers.ValidationError({
                    'options': 'Options are required for multiple choice questions'
                })
            
            # Validate each option has required fields
            for option in options:
                if not isinstance(option, dict):
                    raise serializers.ValidationError({
                        'options': 'Each option must be a dictionary'
                    })
                if 'id' not in option or 'text' not in option:
                    raise serializers.ValidationError({
                        'options': 'Each option must have an id and text field'
                    })
            
            # Validate correct_answer
            correct_answer = data.get('correct_answer', [])
            if not correct_answer:
                raise serializers.ValidationError({
                    'correct_answer': 'Correct answer is required for multiple choice questions'
                })
            
            # For single choice, ensure only one correct answer
            if data.get('question_type') == 'single_choice' and len(correct_answer) > 1:
                raise serializers.ValidationError({
                    'correct_answer': 'Single choice questions can only have one correct answer'
                })
            
            # Validate correct_answer IDs exist in options
            option_ids = {opt['id'] for opt in options}
            for answer in correct_answer:
                if answer['id'] not in option_ids:
                    raise serializers.ValidationError({
                        'correct_answer': f"Answer ID '{answer['id']}' not found in options"
                    })
        
        return data

class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = ['id', 'user', 'lesson', 'completed', 'last_visited_at']

class UserRewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReward
        fields = ['id', 'user', 'reward_type', 'points', 'awarded_at'] 