from rest_framework import serializers
from .models import (
    Category, Course, Lesson, LessonContentBlock,
    Problem, Hint, SolutionStep,
    UserProgress, CourseEnrollment, UserReward, LeaderboardEntry,
    DailyChallenge, UserChallengeProgress, UserLevel,
    Achievement, UserAchievement, CulturalEvent,
    UserCulturalProgress, CommunityContribution, UserLeague, League
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
    class Meta:
        model = Problem
        fields = [
            'id', 'which', 'question_text', 'question_type', 'options',
            'correct_answer', 'explanation', 'content',
            'diagram_config', 'img', 'xp', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        """
        Add XP information to the response and handle diagram_config visibility
        """
        data = super().to_representation(instance)
        
        # Handle XP value - check if content is dict or list
        if isinstance(instance.content, dict):
            data['xp_value'] = instance.content.get('points', instance.xp)
        else:
            data['xp_value'] = instance.xp
        
        # Only include diagram_config for diagram type problems
        if instance.question_type != 'diagram':
            data.pop('diagram_config', None)
            
        return data

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
                "show_hints": True,
                "show_solution": False,
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


class CourseListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing courses without including all related lessons.
    """
    category = serializers.StringRelatedField()
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'is_new', 'progress', 'category', 'author_id',
            'is_published', 'lesson_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_lesson_count(self, obj):
        return obj.lessons.count()


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
    lesson_title = serializers.StringRelatedField(source='lesson.title', read_only=True)
    course_title = serializers.StringRelatedField(source='course.title', read_only=True)

    class Meta:
        model = UserReward
        fields = [
            'id', 'user', 'reward_type', 'reward_name',
            'value', 'awarded_at', 'lesson', 'lesson_title',
            'course', 'course_title'
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


class DailyChallengeSerializer(serializers.ModelSerializer):
    """Serializer for daily challenges"""
    class Meta:
        model = DailyChallenge
        fields = [
            'id', 'title', 'description', 'challenge_date',
            'points_reward', 'problem', 'course', 'lesson'
        ]


class UserChallengeProgressSerializer(serializers.ModelSerializer):
    """Serializer for user challenge progress"""
    challenge = DailyChallengeSerializer(read_only=True)
    
    class Meta:
        model = UserChallengeProgress
        fields = [
            'id', 'challenge', 'completed', 'completed_at',
            'score', 'attempts'
        ]
        read_only_fields = ['completed', 'completed_at', 'score']


class UserLevelSerializer(serializers.ModelSerializer):
    """Serializer for user levels"""
    username = serializers.CharField(source='user.username', read_only=True)
    progress_to_next_level = serializers.SerializerMethodField()
    
    class Meta:
        model = UserLevel
        fields = [
            'id', 'username', 'level', 'experience_points',
            'experience_to_next_level', 'progress_to_next_level',
            'last_level_up'
        ]
    
    def get_progress_to_next_level(self, obj):
        """Calculate progress percentage to next level"""
        if obj.experience_to_next_level == 0:
            return 0
        return (obj.experience_points / obj.experience_to_next_level) * 100


class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for achievements"""
    class Meta:
        model = Achievement
        fields = [
            'id', 'name', 'description', 'icon',
            'points_reward', 'level_required', 'achievement_type'
        ]


class UserAchievementSerializer(serializers.ModelSerializer):
    """Serializer for user achievements"""
    achievement = AchievementSerializer(read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = ['id', 'achievement', 'earned_at']


class CulturalEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CulturalEvent
        fields = ['id', 'name', 'description', 'event_date', 'event_type', 
                 'points_reward', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserCulturalProgressSerializer(serializers.ModelSerializer):
    event = CulturalEventSerializer(read_only=True)
    
    class Meta:
        model = UserCulturalProgress
        fields = ['id', 'user', 'event', 'completed', 'completed_at', 
                 'points_earned', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CommunityContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityContribution
        fields = ['id', 'user', 'contribution_type', 'description', 
                 'points_awarded', 'verified', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = ['id', 'level', 'promotion_threshold', 'stay_threshold', 
                 'demotion_threshold', 'min_xp_required']


class UserLeagueSerializer(serializers.ModelSerializer):
    league = LeagueSerializer()
    next_league = serializers.SerializerMethodField()
    previous_league = serializers.SerializerMethodField()
    
    class Meta:
        model = UserLeague
        fields = ['id', 'league', 'current_week_points', 'last_week_rank',
                 'current_streak', 'max_streak', 'streak_charges',
                 'last_activity_date', 'next_league', 'previous_league']
    
    def get_next_league(self, obj):
        next_league = League.get_next_league(obj.league)
        if next_league:
            return LeagueSerializer(next_league).data
        return None
    
    def get_previous_league(self, obj):
        prev_league = League.get_previous_league(obj.league)
        if prev_league:
            return LeagueSerializer(prev_league).data
        return None
