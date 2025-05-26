from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
import logging
import traceback
from .serializers import (
    SignupWithOnboardingSerializer,
    SigninSerializer,
    UserSerializer,
    StreakSerializer,
    StreakUpdateSerializer,
    NotificationSerializer
)
from django.utils import timezone
from .models import Streak, DailyActivity, Notification
from rest_framework import viewsets
from rest_framework.decorators import action
from django.db.models import F
from datetime import timedelta
from leagues.models import League, UserLeague
from leagues.serializers import LeagueSerializer

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
            'auth': {
                'signup': '/api/auth/signup/',
                'signin': '/api/auth/signin/',
                'refresh': '/api/auth/refresh/',
                'profile': '/api/auth/profile/',
                'student/register': '/api/auth/student/register/'
            },
            'hello': '/hello-world/',
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
                onboarding = result['onboarding']
                refresh = RefreshToken.for_user(user)

                # Import UserOnboardingSerializer here to avoid circular imports
                from accounts.serializers import UserOnboardingSerializer

                # Return user data, onboarding data, and tokens
                return Response({
                    'message': 'User registered successfully',
                    'user': UserSerializer(user).data,
                    'onboarding': UserOnboardingSerializer(onboarding).data,
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

            # Import UserOnboardingSerializer here to avoid circular imports
            from accounts.serializers import UserOnboardingSerializer

            # Get user's onboarding data if it exists
            try:
                from accounts.models import UserOnboarding
                onboarding = UserOnboarding.objects.get(user=user)
                onboarding_data = UserOnboardingSerializer(onboarding).data
            except:
                onboarding_data = None

            return Response({
                'user': UserSerializer(user).data,
                'onboarding': onboarding_data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def streak_view(request):
    if request.method == 'GET':
        streak, created = Streak.objects.get_or_create(user=request.user)
        
        # Update energy before returning response
        streak.update_energy()
        
        # Get the last 7 days of activity
        today = timezone.now().date()
        dates = [today - timezone.timedelta(days=i) for i in range(6, -1, -1)]
        
        # Get or create daily activities for the last 7 days
        for date in dates:
            DailyActivity.objects.get_or_create(
                user=request.user,
                date=date,
                defaults={'status': 'none', 'problems_solved': 0, 'lesson_ids': []}
            )
        
        serializer = StreakSerializer(streak)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = StreakUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                problems_solved = serializer.validated_data['problems_solved']
                lesson_ids = serializer.validated_data['lesson_ids']
                
                streak, created = Streak.objects.get_or_create(user=request.user)
                
                try:
                    streak.update_streak(problems_solved, lesson_ids)
                except ValueError as e:
                    return Response({
                        'error': str(e),
                        'energy': {
                            'current': streak.current_energy,
                            'max': streak.max_energy,
                            'next_update': streak.last_energy_update + timezone.timedelta(hours=4)
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Update or create today's activity
                today = timezone.now().date()
                activity, _ = DailyActivity.objects.get_or_create(
                    user=request.user,
                    date=today,
                    defaults={'status': 'none', 'problems_solved': 0, 'lesson_ids': []}
                )
                
                # Update activity status based on problems solved
                activity.problems_solved = problems_solved
                activity.lesson_ids = lesson_ids
                if problems_solved >= 3:
                    activity.status = 'complete'
                elif problems_solved > 0:
                    activity.status = 'partial'
                activity.save()
                
                response_data = {
                    'message': 'Streak updated',
                    'currentStreak': streak.current_streak,
                    'energy': {
                        'current': streak.current_energy,
                        'max': streak.max_energy,
                        'next_update': streak.last_energy_update + timezone.timedelta(hours=4)
                    },
                    'dailyActivity': [{
                        'date': today.isoformat(),
                        'day': today.strftime('%a'),
                        'status': activity.status,
                        'problemsSolved': activity.problems_solved,
                        'lessonIds': activity.lesson_ids,
                        'isToday': True
                    }]
                }
                return Response(response_data)
            except Exception as e:
                logger.error(f"Error updating streak: {str(e)}")
                logger.error(traceback.format_exc())
                return Response({
                    'error': 'An error occurred while updating streak',
                    'detail': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GamificationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get user's complete gamification status"""
        streak, _ = Streak.objects.get_or_create(user=request.user)
        user_league, _ = UserLeague.objects.get_or_create(user=request.user, defaults={'current_league': League.objects.first()})
        
        # Get next league
        next_league = League.objects.filter(
            min_xp__gt=user_league.current_league.min_xp
        ).order_by('min_xp').first()
        
        # Get weekly rank
        weekly_rank = Streak.objects.filter(
            weekly_xp__gt=streak.weekly_xp
        ).count() + 1
        
        return Response({
            'xp': {
                'total': streak.xp,
                'daily': streak.daily_xp,
                'weekly': streak.weekly_xp,
                'monthly': streak.monthly_xp
            },
            'streak': {
                'current': streak.current_streak,
                'max': streak.max_streak,
                'energy': streak.current_energy,
                'problems_to_next': streak.problems_to_next_streak
            },
            'league': {
                'current': LeagueSerializer(user_league.current_league).data,
                'next': {
                    'id': next_league.id,
                    'name': next_league.name,
                    'somali_name': next_league.somali_name,
                    'min_xp': next_league.min_xp,
                    'points_needed': next_league.min_xp - streak.xp
                } if next_league else None
            },
            'rank': {
                'weekly': weekly_rank
            }
        })

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get leaderboard with filtering options"""
        time_period = request.query_params.get('time_period', 'weekly')
        league_id = request.query_params.get('league')
        
        queryset = Streak.objects.all()
        if league_id:
            queryset = queryset.filter(user__userleague__current_league_id=league_id)
        
        if time_period == 'weekly':
            queryset = queryset.order_by('-weekly_xp')
        elif time_period == 'monthly':
            queryset = queryset.order_by('-monthly_xp')
        else:  # all_time
            queryset = queryset.order_by('-xp')
        
        # Get top 100 users
        top_users = queryset[:100]
        
        # Get user's own standing
        user_streak = Streak.objects.get(user=request.user)
        user_rank = queryset.filter(
            xp__gt=user_streak.xp
        ).count() + 1
        
        return Response({
            'time_period': time_period,
            'league': league_id,
            'standings': [{
                'rank': idx + 1,
                'user': {
                    'id': streak.user.id,
                    'name': streak.user.username,
                },
                'points': streak.xp,
                'streak': streak.current_streak,
                'league': LeagueSerializer(streak.user.userleague.current_league).data
            } for idx, streak in enumerate(top_users)],
            'my_standing': {
                'rank': user_rank,
                'points': user_streak.xp,
                'streak': user_streak.current_streak,
                'league': LeagueSerializer(request.user.userleague.current_league).data
            }
        })

    @action(detail=False, methods=['post'])
    def use_energy(self, request):
        """Use energy to maintain streak"""
        streak = Streak.objects.get(user=request.user)
        if streak.use_energy():
            return Response({
                'success': True,
                'remaining_energy': streak.current_energy,
                'message': 'Waad ku mahadsantahay ilaalinta xariggaaga'
            })
        return Response({
            'success': False,
            'message': 'Ma haysato tamar'
        }, status=status.HTTP_400_BAD_REQUEST)


class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'message': 'All notifications marked as read'})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})
