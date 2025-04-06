from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
import logging
import traceback
from .serializers import (
    SignupWithOnboardingSerializer,
    SigninSerializer,
    UserSerializer
)

# Configure logger
logger = logging.getLogger(__name__)


@api_view(['GET'])
def api_root(request):
    """
    API root view that provides information about available endpoints.
    """
    return Response({
        'status': 'online',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth/',
            'hello': '/hello-world/',
            'signup': '/api/signup/',
            'signin': '/api/signin/',
            'lms': '/api/lms/',
        }
    }, status=status.HTTP_200_OK)


class SignupView(APIView):
    """
    API view for signing up with onboarding information in a single request.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = SignupWithOnboardingSerializer(data=request.data)

            if serializer.is_valid():
                # Create user and onboarding data (transaction handled in serializer)
                result = serializer.save()

                # Generate JWT tokens for the new user
                user = result['user']
                refresh = RefreshToken.for_user(user)

                # Return user data and tokens
                return Response({
                    'message': 'User registered successfully',
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the full error with traceback
            logger.error(f"Signup error: {str(e)}")
            logger.error(traceback.format_exc())

            # Return a more informative error response
            return Response({
                'error': 'An error occurred during signup',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SigninView(APIView):
    """
    API view for user authentication and token generation.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SigninSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)

            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
