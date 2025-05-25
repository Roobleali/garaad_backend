from rest_framework import serializers
from accounts.models import User, UserOnboarding
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
import logging
from .models import Streak, DailyActivity, Notification
from django.utils import timezone

logger = logging.getLogger(__name__)


class UserOnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOnboarding
        fields = ['goal', 'learning_approach',
                  'topic', 'math_level', 'minutes_per_day']


class SignupWithOnboardingSerializer(serializers.Serializer):
    # User credentials
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True, style={'input_type': 'password'}, write_only=True)

    # Onboarding fields
    goal = serializers.CharField(
        required=False, default="Horumarinta xirfadaha")
    learning_approach = serializers.CharField(
        required=False, default="Waxbarasho shaqsiyeed")
    topic = serializers.CharField(required=False, default="Xisaab")
    math_level = serializers.CharField(required=False, default="Bilowga")
    minutes_per_day = serializers.IntegerField(required=False, default=30)

    def validate_name(self, value):
        """
        Validate that name is not empty and doesn't contain invalid characters
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        if len(value) > 150:  # Django's default max_length for username
            raise serializers.ValidationError("Name is too long")
        return value.strip()

    def validate_email(self, value):
        """
        Check if the email already exists
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "User with this email already exists.")
        return value.lower()  # Normalize email to lowercase

    def validate_password(self, value):
        """
        Validate password strength
        """
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long")
        return value

    def validate_minutes_per_day(self, value):
        """
        Validate that minutes_per_day is a positive integer
        """
        if value <= 0:
            raise serializers.ValidationError(
                "Minutes per day must be a positive number.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        """
        Create user and onboarding profile in a transaction
        """
        try:
            # Extract user data
            name = validated_data.pop('name')
            email = validated_data.pop('email')
            password = validated_data.pop('password')

            # Create a sanitized username (required by Django)
            # Use email as username to ensure uniqueness if name is not suitable
            username = name

            # If name contains spaces, use the email prefix as username
            if ' ' in name or len(name) > 150:
                username = email.split('@')[0]

            # Check for username conflicts and append number if needed
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            # Get first and last name safely
            name_parts = name.split(' ', 1)
            first_name = name_parts[0] if name_parts else name
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            # Create user
            user = User.objects.create_user(
                username=username[:150],  # Ensure within field limit
                email=email,
                password=password,
                first_name=first_name[:30],  # Respect Django field limits
                last_name=last_name[:150]
            )

            # Create onboarding profile
            onboarding = UserOnboarding.objects.create(
                user=user,
                **validated_data,
                has_completed_onboarding=True
            )

            return {
                'user': user,
                'onboarding': onboarding,
            }
        except Exception as e:
            # Log any errors during user creation
            logger.error(f"Error creating user: {str(e)}")
            raise serializers.ValidationError(
                f"Failed to create user: {str(e)}")


class SigninSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True, style={'input_type': 'password'}, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get(
                'request'), username=email, password=password)

            if not user:
                raise serializers.ValidationError(
                    "Invalid credentials. Please try again.")

            if not user.is_active:
                raise serializers.ValidationError("This account is inactive.")

            data['user'] = user
            return data

        raise serializers.ValidationError("Must provide email and password.")


class UserSerializer(serializers.ModelSerializer):
    has_completed_onboarding = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name', 'is_premium', 'has_completed_onboarding']

    def get_has_completed_onboarding(self, obj):
        try:
            return obj.useronboarding.has_completed_onboarding
        except UserOnboarding.DoesNotExist:
            return False


class DailyActivitySerializer(serializers.ModelSerializer):
    day = serializers.SerializerMethodField()
    isToday = serializers.SerializerMethodField()

    class Meta:
        model = DailyActivity
        fields = ['date', 'day', 'status', 'problems_solved', 'lesson_ids', 'isToday']

    def get_day(self, obj):
        return obj.date.strftime('%a')

    def get_isToday(self, obj):
        return obj.date == timezone.now().date()


class StreakSerializer(serializers.ModelSerializer):
    energy = serializers.SerializerMethodField()
    dailyActivity = DailyActivitySerializer(source='user.daily_activities', many=True)
    username = serializers.CharField(source='user.username', read_only=True)
    userId = serializers.CharField(source='user.id', read_only=True)
    xp = serializers.IntegerField(read_only=True)
    daily_xp = serializers.IntegerField(read_only=True)

    class Meta:
        model = Streak
        fields = ['userId', 'username', 'current_streak', 'max_streak', 'lessons_completed',
                 'problems_to_next_streak', 'energy', 'dailyActivity', 'xp', 'daily_xp']

    def get_energy(self, obj):
        return {
            'current': obj.current_energy,
            'max': obj.max_energy,
            'next_update': obj.last_energy_update + timezone.timedelta(hours=4)
        }


class StreakUpdateSerializer(serializers.Serializer):
    problems_solved = serializers.IntegerField(min_value=0)
    lesson_ids = serializers.ListField(child=serializers.CharField(), required=False, default=list)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'type', 'title', 'message', 'data', 'is_read', 'created_at']
        read_only_fields = ['id', 'type', 'title', 'message', 'data', 'created_at']
