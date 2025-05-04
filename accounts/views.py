from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import StudentProfile, UserOnboarding, UserProfile
from .serializers import (
    StudentProfileSerializer, 
    UserSerializer, 
    SignupSerializer, 
    EmailTokenObtainPairSerializer, 
    UserOnboardingSerializer,
    UserProfileSerializer
)
from django.db import transaction
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def custom_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({
            'error': 'Please provide both email and password'
        }, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request=request, email=email, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_premium': user.is_premium,
                'age': user.age,
                'has_completed_onboarding': user.useronboarding.has_completed_onboarding if hasattr(user, 'useronboarding') else False
            }
        })
    else:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    # Check for required fields
    required_fields = ['username', 'email', 'password', 'age']
    missing_fields = [field for field in required_fields if not request.data.get(field)]
    
    if missing_fields:
        return Response({
            'error': f'Missing required fields: {", ".join(missing_fields)}'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if username or email already exists
    if User.objects.filter(username=request.data['username']).exists():
        return Response({
            'username': ['Username already exists']
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=request.data['email']).exists():
        return Response({
            'email': ['Email already exists']
        }, status=status.HTTP_400_BAD_REQUEST)

    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        with transaction.atomic():
            # Create the user
            user = serializer.save()
            
            # Create onboarding record if onboarding data is provided
            onboarding_data = request.data.get('onboarding_data')
            if onboarding_data:
                onboarding_serializer = UserOnboardingSerializer(data=onboarding_data)
                if onboarding_serializer.is_valid():
                    onboarding = onboarding_serializer.save(user=user, has_completed_onboarding=True)
                else:
                    return Response({
                        'onboarding_data': onboarding_serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def student_registration(request):
    # Check if user already has a profile
    try:
        profile = request.user.student_profile
        return Response({"detail": "Profile already exists"}, status=status.HTTP_400_BAD_REQUEST)
    except:
        pass
    
    serializer = StudentProfileSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # You can add custom logic here before or after refreshing the token
        return super().post(request, *args, **kwargs)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def onboarding_status(request):
    try:
        onboarding = UserOnboarding.objects.get(user=request.user)
        return Response({
            'has_completed_onboarding': onboarding.has_completed_onboarding
        })
    except UserOnboarding.DoesNotExist:
        return Response({
            'has_completed_onboarding': False
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_onboarding(request):
    try:
        onboarding, created = UserOnboarding.objects.get_or_create(user=request.user)
        serializer = UserOnboardingSerializer(onboarding, data=request.data)
        
        if serializer.is_valid():
            onboarding = serializer.save()
            onboarding.has_completed_onboarding = True
            onboarding.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def register_user(request):
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        age = request.data.get('age')

        if not all([username, email, password, age]):
            return Response({
                'error': 'Please provide username, email, password and age'
            }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'Username already exists'
            }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'Email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            age=age
        )

        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get or update user profile including qabiil and laan"""
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
            
        elif request.method == 'PUT':
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
