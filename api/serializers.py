from rest_framework import serializers
from accounts.models import User, UserOnboarding
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction


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

    def validate_email(self, value):
        """
        Check if the email already exists
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "User with this email already exists.")
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
        # Extract user data
        name = validated_data.pop('name')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        # Create user (using username as name since name isn't a field in the User model)
        user = User.objects.create_user(
            username=name,
            email=email,
            password=password,
            first_name=name.split()[0] if ' ' in name else name,
            last_name=' '.join(name.split()[1:]) if ' ' in name else '',
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
