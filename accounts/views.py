from rest_framework.decorators import api_view, permission_classes, parser_classes
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
from .email_verification import generate_verification_token, send_verification_email, store_verification_token
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
import json
import logging

logger = logging.getLogger(__name__)

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

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([JSONParser])
def signup_view(request):
    try:
        # Parse JSON data manually if needed
        if isinstance(request.body, bytes):
            try:
                data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                return Response({
                    'error': 'Invalid JSON data'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = request.data

        logger.info("Raw request body: %s", request.body.decode('utf-8'))
        logger.info("Request content type: %s", request.content_type)
        logger.info("Request headers: %s", request.headers)
        logger.info("Request data: %s", data)
        
        # Check for required fields
        required_fields = ['username', 'email', 'password', 'age']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            error_msg = f'Missing required fields: {", ".join(missing_fields)}'
            logger.error("Validation error: %s", error_msg)
            return Response({
                'error': error_msg
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if username or email already exists
        if User.objects.filter(username=data['username']).exists():
            error_msg = 'Username already exists'
            logger.error("Validation error: %s", error_msg)
            return Response({
                'username': [error_msg]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=data['email']).exists():
            error_msg = 'Email already exists'
            logger.error("Validation error: %s", error_msg)
            return Response({
                'email': [error_msg]
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = SignupSerializer(data=data)
        if serializer.is_valid():
            with transaction.atomic():
                # Create the user with is_active=False initially
                user = serializer.save(is_active=False)
                
                # Generate verification token and send email
                token = generate_verification_token()
                email_sent = send_verification_email(user.email, token)
                
                if not email_sent:
                    user.delete()  # Rollback user creation if email fails
                    error_msg = 'Failed to send verification email'
                    logger.error("Email error: %s", error_msg)
                    return Response({
                        'error': error_msg
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # Store verification token
                store_verification_token(user.email, token)
                
                # Create onboarding record if onboarding data is provided
                onboarding_data = data.get('onboarding_data')
                if onboarding_data:
                    onboarding_serializer = UserOnboardingSerializer(data=onboarding_data)
                    if onboarding_serializer.is_valid():
                        onboarding = onboarding_serializer.save(user=user, has_completed_onboarding=True)
                    else:
                        error_msg = onboarding_serializer.errors
                        logger.error("Onboarding error: %s", error_msg)
                        return Response({
                            'onboarding_data': error_msg
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                logger.info("User registered successfully: %s", user.email)
                return Response({
                    'message': 'Registration successful. Please check your email to verify your account.',
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
        
        logger.error("Serializer errors: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error("Exception in signup_view: %s", str(e), exc_info=True)
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, token):
    """Verify user's email using the token"""
    from .email_verification import verify_email_token
    
    success, message = verify_email_token(token)
    if success:
        return Response({
            'message': message
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': message
        }, status=status.HTTP_400_BAD_REQUEST)

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
