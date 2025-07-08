from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import StudentProfile, UserOnboarding, UserProfile, EmailVerification
from .serializers import (
    StudentProfileSerializer, 
    UserSerializer, 
    SignupSerializer, 
    EmailTokenObtainPairSerializer, 
    UserOnboardingSerializer,
    UserProfileSerializer,
    ReferralSerializer,
    ReferredUserSerializer,
    ProfilePictureSerializer
)
from django.db import transaction
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .utils import send_verification_email
from datetime import timedelta
from django.utils import timezone
from api.models import Streak, Notification
from leagues.models import UserLeague, League
from courses.models import UserReward

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
                'is_email_verified': user.is_email_verified,
                'has_completed_onboarding': user.useronboarding.has_completed_onboarding if hasattr(user, 'useronboarding') else False
            }
        })
    else:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """
    Verify user's email using the verification code
    """
    email = request.data.get('email')
    code = request.data.get('code')

    if not email or not code:
        return Response({
            'error': 'Please provide both email and verification code'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Check if email is already verified
    if user.is_email_verified:
        return Response({
            'error': 'Email is already verified'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get the most recent verification code
    try:
        verification = EmailVerification.objects.filter(
            user=user,
            is_used=False,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).latest('created_at')
    except EmailVerification.DoesNotExist:
        return Response({
            'error': 'Invalid or expired verification code'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Verify the code
    if verification.code != code:
        return Response({
            'error': 'Invalid verification code'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Mark the code as used and verify the email
    verification.is_used = True
    verification.save()
    user.is_email_verified = True
    user.save()

    return Response({
        'message': 'Email verified successfully'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_email(request):
    """
    Resend verification email to user
    """
    email = request.data.get('email')

    if not email:
        return Response({
            'error': 'Please provide email'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Check if email is already verified
    if user.is_email_verified:
        return Response({
            'error': 'Email is already verified'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        send_verification_email(user)
        return Response({
            'message': 'Verification email sent successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': f'Failed to send verification email: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            # Create the user (referral handling is done in serializer)
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
            
            # Send verification email
            try:
                send_verification_email(user)
            except Exception as e:
                return Response({
                    'error': f'Failed to send verification email: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                },
                'message': 'User registered successfully. Please check your email for verification.'
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
        referral_code = request.data.get('referral_code')

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

        # Validate referral code if provided
        referrer = None
        if referral_code:
            try:
                referrer = User.objects.get(referral_code=referral_code)
            except User.DoesNotExist:
                return Response({
                    'error': 'Invalid referral code'
                }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                age=age
            )

            # Handle referral if provided
            if referrer:
                user.referred_by = referrer
                user.save()
                
                # Award points to referrer
                referrer.award_referral_points(10)

            # Send verification email
            try:
                send_verification_email(user)
            except Exception as e:
                return Response({
                    'error': f'Failed to send verification email: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token),
                'user': UserSerializer(user).data,
                'message': 'User registered successfully. Please check your email for verification.'
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

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """Update user profile data including profile picture"""
    try:
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_picture(request):
    """Upload or update user profile picture"""
    try:
        if 'profile_picture' not in request.FILES:
            return Response({
                'error': 'Sawirka profile-ka ayaa loo baahan yahay'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ProfilePictureSerializer(
            request.user, 
            data={'profile_picture': request.FILES['profile_picture']},
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # Return updated user data
            user_serializer = UserSerializer(request.user)
            return Response({
                'message': 'Sawirka profile-ka ayaa si guul leh loo cusbooneysiyey',
                'user': user_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_profile_picture(request):
    """Delete user profile picture"""
    try:
        user = request.user
        if user.profile_picture:
            # Delete the file from storage
            user.profile_picture.delete()
            user.profile_picture = None
            user.save()
            
            return Response({
                'message': 'Sawirka profile-ka ayaa la tirtiray'
            })
        else:
            return Response({
                'error': 'Ma jiro sawir profile ah'
            }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get or update user profile including qabiil and laan, plus gamification info"""
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        if request.method == 'GET':
            serializer = UserProfileSerializer(profile)
            # --- Gamification info ---
            # XP, streak, league, badges, notification preferences
            xp = 0
            streak = None
            league = None
            badges = []
            notification_prefs = {}
            try:
                streak = Streak.objects.get(user=request.user)
                xp = streak.xp
            except Exception:
                pass
            try:
                user_league = UserLeague.objects.get(user=request.user)
                league = {
                    'id': user_league.current_league.id,
                    'name': str(user_league.current_league),
                    'min_xp': user_league.current_league.min_xp
                }
            except Exception:
                pass
            try:
                badges = list(UserReward.objects.filter(user=request.user, reward_type='badge').values('reward_name', 'awarded_at'))
            except Exception:
                pass
            try:
                notification_prefs = getattr(request.user.student_profile, 'notification_preferences', {})
            except Exception:
                pass
            data = serializer.data
            data['xp'] = xp
            data['streak'] = {
                'current': getattr(streak, 'current_streak', 0),
                'max': getattr(streak, 'max_streak', 0),
                'energy': getattr(streak, 'current_energy', 0)
            }
            data['league'] = league
            data['badges'] = badges
            data['notification_preferences'] = notification_prefs
            return Response(data)
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_premium_status(request):
    """Update a user's premium status and subscription details"""
    try:
        user = request.user
        is_premium = request.data.get('is_premium')
        subscription_type = request.data.get('subscription_type')
        subscription_start_date = request.data.get('subscription_start_date')
        subscription_end_date = request.data.get('subscription_end_date')
        
        # Payment-related fields
        payment_method = request.data.get('payment_method', 'admin')
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'USD')
        waafi_transaction_id = request.data.get('waafi_transaction_id')
        waafi_reference_id = request.data.get('waafi_reference_id')
        
        if is_premium is None:
            return Response({
                'error': 'is_premium field is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if is_premium and not subscription_type:
            return Response({
                'error': 'subscription_type is required when setting premium status'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Import Order models here to avoid circular imports
        from payment.models import Order, OrderItem
        
        order = None
        
        # Create order record if activating premium
        if is_premium:
            # Define subscription prices and names
            subscription_prices = {
                'monthly': {'USD': 9.99, 'EUR': 8.99, 'SOS': 500},
                'yearly': {'USD': 99.99, 'EUR': 89.99, 'SOS': 5000},
                'lifetime': {'USD': 299.99, 'EUR': 269.99, 'SOS': 15000}
            }
            
            subscription_names = {
                'monthly': 'Ishtiraak Bishii',
                'yearly': 'Ishtiraak Sannadkii',
                'lifetime': 'Ishtiraak Daa\'im'
            }
            
            # Use provided amount or default price
            if not amount:
                amount = subscription_prices.get(subscription_type, {}).get(currency, 0)
            
            # Create order
            order = Order.objects.create(
                user=user,
                total_amount=amount,
                currency=currency,
                payment_method=payment_method,
                status='completed',  # Mark as completed since we're activating premium
                description=f'Garaad {subscription_type.title()} Subscription',
                paid_at=timezone.now(),
                waafi_transaction_id=waafi_transaction_id,
                waafi_reference_id=waafi_reference_id,
                metadata={
                    'activated_via': 'admin_update',
                    'processed_at': timezone.now().isoformat()
                }
            )
            
            # Set subscription dates
            start_date = timezone.now() if not subscription_start_date else timezone.datetime.fromisoformat(subscription_start_date.replace('Z', '+00:00'))
            end_date = None
            
            if subscription_type == 'monthly':
                end_date = start_date + timedelta(days=30) if not subscription_end_date else timezone.datetime.fromisoformat(subscription_end_date.replace('Z', '+00:00'))
            elif subscription_type == 'yearly':
                end_date = start_date + timedelta(days=365) if not subscription_end_date else timezone.datetime.fromisoformat(subscription_end_date.replace('Z', '+00:00'))
            # lifetime has no end date
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                item_type='subscription',
                name=subscription_names[subscription_type],
                description=f'Ishtiraak Garaad {subscription_type}',
                unit_price=amount,
                quantity=1,
                total_price=amount,
                subscription_type=subscription_type,
                subscription_start_date=start_date,
                subscription_end_date=end_date
            )
            
        # Update subscription details
        user.is_premium = is_premium
        if is_premium:
            user.subscription_type = subscription_type
            user.subscription_start_date = timezone.now() if not subscription_start_date else timezone.datetime.fromisoformat(subscription_start_date.replace('Z', '+00:00'))
            
            if subscription_type == 'lifetime':
                user.subscription_end_date = None
            elif subscription_type == 'monthly':
                user.subscription_end_date = timezone.now() + timedelta(days=30) if not subscription_end_date else timezone.datetime.fromisoformat(subscription_end_date.replace('Z', '+00:00'))
            elif subscription_type == 'yearly':
                user.subscription_end_date = timezone.now() + timedelta(days=365) if not subscription_end_date else timezone.datetime.fromisoformat(subscription_end_date.replace('Z', '+00:00'))
        else:
            # Reset subscription details when removing premium status
            user.subscription_type = None
            user.subscription_start_date = None
            user.subscription_end_date = None
            
        user.save()
        
        # Create notification for premium status change
        notification_type = 'achievement' if is_premium else 'reminder'
        title = 'Hambalyo! Waad noqotay Premium' if is_premium else 'Xasuuso Premium-kaaga'
        message = 'Waad ku mahadsantahay inaad noqoto Premium! Waxaad hadda heli doontaa dhammaan awoodaha.' if is_premium else 'Premium-kaaga wuu dhacay. Dib u noqo si aad u hesho dhammaan awoodaha.'
        
        Notification.objects.create(
            user=user,
            type=notification_type,
            title=title,
            message=message,
            data={
                'premium_status': is_premium,
                'subscription_type': subscription_type,
                'subscription_end_date': user.subscription_end_date.isoformat() if user.subscription_end_date else None,
                'order_id': str(order.id) if order else None
            }
        )
        
        response_data = {
            'message': 'Premium status updated successfully',
            'is_premium': user.is_premium,
            'subscription_type': user.subscription_type,
            'subscription_start_date': user.subscription_start_date.isoformat() if user.subscription_start_date else None,
            'subscription_end_date': user.subscription_end_date.isoformat() if user.subscription_end_date else None
        }
        
        # Add order information if created
        if order:
            response_data['order'] = {
                'id': str(order.id),
                'order_number': order.order_number,
                'total_amount': str(order.total_amount),
                'currency': order.currency,
                'payment_method': order.payment_method,
                'status': order.status
            }
        
        return Response(response_data)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def referrals_view(request):
    """
    API endpoint to fetch referral data for the currently logged-in user.
    Returns:
    - User's referral code
    - Total referral points earned
    - Count of referred users
    - List of referred users with their details
    """
    user = request.user
    referred_users = user.get_referral_list()
    
    # Serialize referred users
    referred_users_data = ReferredUserSerializer(referred_users, many=True).data
    
    referral_data = {
        'referral_code': user.referral_code,
        'referral_points': user.referral_points,
        'referral_count': user.get_referral_count(),
        'referred_users': referred_users_data
    }
    
    return Response(referral_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def referral_stats_view(request):
    """
    API endpoint to fetch referral statistics for the currently logged-in user.
    Returns summary statistics without detailed user information.
    """
    user = request.user
    
    stats = {
        'referral_code': user.referral_code,
        'referral_points': user.referral_points,
        'referral_count': user.get_referral_count(),
        'referred_by': user.referred_by.username if user.referred_by else None,
        'is_referred_user': user.referred_by is not None
    }
    
    return Response(stats, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_referral_code_view(request):
    """
    API endpoint to generate a referral code for the currently logged-in user.
    This is useful for users who don't have a referral code yet.
    """
    user = request.user
    
    # Check if user already has a referral code
    if user.referral_code:
        return Response({
            'error': 'User already has a referral code',
            'referral_code': user.referral_code
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Generate a new referral code
        user.referral_code = User.generate_referral_code()
        user.save()
        
        return Response({
            'message': 'Referral code generated successfully',
            'referral_code': user.referral_code
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to generate referral code: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
