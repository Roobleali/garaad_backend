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

class ReferredUserSerializer(serializers.ModelSerializer):
    """Serializer for users referred by the current user"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    has_completed_onboarding = serializers.SerializerMethodField()
    profile = UserProfileSerializer(source='user_profile', required=False)
    referral_count = serializers.SerializerMethodField()
    referred_by_username = serializers.SerializerMethodField()
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_premium', 
                  'has_completed_onboarding', 'profile', 'age', 'referral_code', 
                  'referral_points', 'referral_count', 'referred_by_username', 'is_email_verified',
                  'profile_picture', 'bio']

    def get_has_completed_onboarding(self, obj):
        try:
            return obj.useronboarding.has_completed_onboarding
        except UserOnboarding.DoesNotExist:
            return False
    
    def get_referral_count(self, obj):
        return obj.get_referral_count()
    
    def get_referred_by_username(self, obj):
        return obj.referred_by.username if obj.referred_by else None

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    age = serializers.IntegerField(required=True, min_value=1, max_value=120)
    referral_code = serializers.CharField(max_length=8, required=False, write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'age', 'referral_code')
    
    def validate_referral_code(self, value):
        """Validate that the referral code exists and is valid"""
        if value:
            try:
                User.objects.get(referral_code=value)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid referral code")
        return value
    
    def create(self, validated_data):
        referral_code = validated_data.pop('referral_code', None)
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            age=validated_data['age']
        )
        
        # Handle referral if provided
        if referral_code:
            try:
                referrer = User.objects.get(referral_code=referral_code)
                user.referred_by = referrer
                user.save()
                
                # Award points to referrer
                referrer.award_referral_points(10)
                
            except User.DoesNotExist:
                # This should not happen due to validation, but handle gracefully
                pass
        
        return user

class ReferralSerializer(serializers.Serializer):
    """Serializer for referral data"""
    referral_code = serializers.CharField(max_length=8, read_only=True)
    referral_points = serializers.IntegerField(read_only=True)
    referral_count = serializers.IntegerField(read_only=True)
    referred_users = ReferredUserSerializer(many=True, read_only=True)

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

class ProfilePictureSerializer(serializers.ModelSerializer):
    """Dedicated serializer for profile picture uploads"""
    profile_picture = serializers.ImageField()
    
    class Meta:
        model = User
        fields = ['profile_picture']
    
    def validate_profile_picture(self, value):
        """Validate profile picture upload"""
        # Check file size (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Sawirka profile-ka ma noqon karo in uu ka weyn yahay 5MB.")
        
        # Check file format
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        if not any(value.name.lower().endswith(ext) for ext in valid_extensions):
            raise serializers.ValidationError("Nooca faylka aan la aqbalin. Isticmaal JPG, PNG, GIF, ama BMP.")
        
        return value