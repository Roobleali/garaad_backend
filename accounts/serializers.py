from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import User as CustomUser, StudentProfile, UserOnboarding, UserProfile
import json

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['id'] = user.id

        return token
    
class StudentProfileSerializer(serializers.ModelSerializer):
    preferred_study_time = serializers.ListField(child=serializers.CharField(), required=False)
    subjects = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = StudentProfile
        exclude = ('user', 'created_at', 'updated_at')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['preferred_study_time'] = instance.get_preferred_study_time()
        ret['subjects'] = instance.get_subjects()
        return ret

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        if 'preferred_study_time' in internal_value:
            internal_value['preferred_study_time'] = json.dumps(internal_value['preferred_study_time'])
        if 'subjects' in internal_value:
            internal_value['subjects'] = json.dumps(internal_value['subjects'])
        return internal_value

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    has_completed_onboarding = serializers.SerializerMethodField()
    profile = UserProfileSerializer(source='user_profile', required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name', 'is_premium', 'has_completed_onboarding', 'profile', 'age']

    def get_has_completed_onboarding(self, obj):
        try:
            return obj.useronboarding.has_completed_onboarding
        except UserOnboarding.DoesNotExist:
            return False

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    age = serializers.IntegerField(required=True, min_value=1, max_value=120)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'age')
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            age=validated_data['age']
        )
        return user

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['name'] = user.get_full_name()
        token['is_premium'] = user.is_premium

        return token

    def validate(self, attrs):
        # The default username_field is 'username', we need to replace it with 'email'
        attrs[self.username_field] = attrs.pop('email')
        return super().validate(attrs)

class UserOnboardingSerializer(serializers.ModelSerializer):
    preferred_study_time = serializers.ChoiceField(choices=[
        ('morning', 'Aroorti Subaxda inta aan quraacaynayo'),
        ('afternoon', 'Waqtiga Nasashasha intaan Khadaynayo'),
        ('evening', 'Habeenki ah ka dib cashada ama Kahor intan seexanin'),
        ('flexible', 'Waqti kale oo maalintayda ah')
    ], default='flexible')

    class Meta:
        model = UserOnboarding
        fields = ('goal', 'learning_approach', 'topic', 'math_level', 'minutes_per_day', 'preferred_study_time', 'has_completed_onboarding')
        read_only_fields = ('has_completed_onboarding',)