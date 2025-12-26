from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
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
from .models import Streak, DailyActivity, Notification, MomentumState, GamificationProgress, EnergyWallet, ActivityLog
from .gamification_engine import GamificationEngine
from rest_framework import viewsets
from rest_framework.decorators import action
from django.db.models import F
from datetime import timedelta
from leagues.models import League, UserLeague
from leagues.serializers import LeagueSerializer
from .admin_dashboard import AdminDashboardService
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db.models import Max, Sum, Count
from django.contrib.auth import get_user_model

User = get_user_model()

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
        try:
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
                except Exception as e:
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
        except Exception as e:
            logger.error(f"Signin error: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({
                'error': 'An error occurred during sign-in',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def streak_view(request):
    """
    Deprecated in v2. Use /api/activity/update/ and /api/gamification/status/.
    Bridged for backward compatibility.
    """
    momentum, _ = MomentumState.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        serializer = StreakSerializer(momentum)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Bridge to central engine
        serializer = StreakUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                problems_solved = serializer.validated_data.get('problems_solved', 0)
                lesson_ids = serializer.validated_data.get('lesson_ids', [])
                
                engine_result = GamificationEngine.update_activity(
                    user=request.user,
                    action_type='solve',
                    problems_solved=problems_solved
                )
                
                return Response({
                    'message': 'Streak updated',
                    'current_streak': engine_result['streak_count'],
                    'gamification': engine_result
                })
            except Exception as e:
                logger.error(f"Error in streak_view bridge: {str(e)}")
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GamificationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        Get user's complete gamification status (Backend v2).
        🛡️ Phase 11: Authoritative Contract & Visibility Rules.
        """
        progress, _ = GamificationProgress.objects.get_or_create(user=request.user)
        momentum, _ = MomentumState.objects.get_or_create(user=request.user)
        wallet, _ = EnergyWallet.objects.get_or_create(user=request.user)
        user_league, _ = UserLeague.objects.get_or_create(
            user=request.user, 
            defaults={'current_league': League.objects.order_by('min_xp').first()}
        )
        
        identity = progress.identity
        
        # --- Next Smallest Action Logic ---
        next_action = {
            'title': 'Sii wad barashada',
            'action_type': 'solve',
            'priority': 'normal',
            'link': '/courses'
        }
        
        if momentum.state == 'unstable':
            next_action = {
                'title': 'Badbaadi xariggaaga!',
                'message': 'Xariggaagu wuxuu halis ugu jiraa inuu jabo. Xali hal dhibaato hadda.',
                'action_type': 'solve',
                'priority': 'high',
                'link': '/courses'
            }
        elif momentum.state == 'dormant':
             next_action = {
                'title': 'Soo celi xariggaaga',
                'message': 'Xariggaagu waa seexday. Bilow hadda si aad u soo celiso.',
                'action_type': 'solve',
                'priority': 'critical',
                'link': '/courses'
            }
        elif wallet.energy_balance == 0:
            next_action = {
                'title': 'Nasasho qaado ama caawi dadka',
                'message': 'Ma haysatid tamar. Caawi kuwa kale si aad tamar u hesho.',
                'action_type': 'help',
                'priority': 'medium',
                'link': '/community'
            }

        # --- Identity-based Visibility Rules ---
        data = {
            'identity': identity,
            'next_action': next_action,
            'streak': {
                'count': momentum.streak_count,
            }
        }

        # Explorer sees Momentum and Today's Goal
        if identity in ['explorer', 'builder', 'solver', 'mentor']:
            data['streak']['state'] = momentum.state
            data['streak']['last_active'] = momentum.last_active_at
        
        # Builder sees XP and Level
        if identity in ['builder', 'solver', 'mentor']:
            data['xp'] = {
                'total': progress.xp_total,
                'level': progress.level,
            }
        
        # Solver sees Velocity and League Rank
        if identity in ['solver', 'mentor']:
            data['xp']['weekly_velocity'] = progress.weekly_velocity
            data['league'] = {
                'current': {
                    'name': user_league.current_league.somali_name,
                    'min_xp': user_league.current_league.min_xp
                }
            }
            # Calculate weekly rank
            data['rank'] = {
                'weekly': GamificationProgress.objects.filter(
                    weekly_velocity__gt=progress.weekly_velocity
                ).count() + 1
            }

        # Mentor sees full details and energy
        if identity == 'mentor':
            data['energy'] = {
                'balance': wallet.energy_balance
            }
            next_league = League.objects.filter(
                min_xp__gt=user_league.current_league.min_xp
            ).order_by('min_xp').first()
            if next_league:
                data['league']['next'] = {
                    'name': next_league.somali_name,
                    'points_needed': next_league.min_xp - progress.xp_total
                }

        return Response(data)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get leaderboard based on total XP"""
        queryset = GamificationProgress.objects.all().select_related('user', 'user__userleague__current_league').order_by('-xp_total')
        
        # Get top 100 users
        top_entries = queryset[:100]
        
        # Get user's own standing
        user_progress, _ = GamificationProgress.objects.get_or_create(user=request.user)
        user_rank = queryset.filter(xp_total__gt=user_progress.xp_total).count() + 1
        
        return Response({
            'standings': [{
                'rank': idx + 1,
                'user': {
                    'id': entry.user.id,
                    'name': entry.user.username,
                },
                'points': entry.xp_total,
                'level': entry.level,
                'identity': entry.identity
            } for idx, entry in enumerate(top_entries)],
            'my_standing': {
                'rank': user_rank,
                'points': user_progress.xp_total,
                'level': user_progress.level
            }
        })

    @action(detail=False, methods=['post'])
    def use_energy(self, request):
        """Spend energy to absorb friction"""
        wallet, _ = EnergyWallet.objects.get_or_create(user=request.user)
        cost = int(request.data.get('cost', 1))
        
        if wallet.energy_balance >= cost:
            wallet.energy_balance -= cost
            wallet.save()
            
            # Log the spend
            ActivityLog.objects.create(
                user=request.user,
                action_type='energy_spend',
                energy_delta=-cost,
                xp_delta=0
            )
            
            return Response({
                'success': True,
                'remaining_energy': wallet.energy_balance,
                'message': 'Energy used successfully'
            })
        return Response({
            'success': False,
            'message': 'Not enough energy'
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):
    """
    Comprehensive admin dashboard with all LMS metrics
    Requires superuser or staff permissions
    """
    # Check if user is admin/staff
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'error': 'Access denied. Admin privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        dashboard_data = AdminDashboardService.get_dashboard_data()
        return Response({
            'success': True,
            'data': dashboard_data,
            'generated_at': timezone.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error generating admin dashboard: {str(e)}")
        return Response({
            'error': 'Failed to generate dashboard data',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_users_overview(request):
    """
    Detailed user overview for admin dashboard
    """
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'error': 'Access denied. Admin privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user_stats = AdminDashboardService.get_user_stats()
        return Response({
            'success': True,
            'data': user_stats
        })
    except Exception as e:
        logger.error(f"Error getting user overview: {str(e)}")
        return Response({
            'error': 'Failed to get user overview',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_course_analytics(request):
    """
    Course analytics for admin dashboard
    """
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'error': 'Access denied. Admin privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        course_stats = AdminDashboardService.get_course_stats()
        learning_stats = AdminDashboardService.get_learning_stats()
        
        return Response({
            'success': True,
            'data': {
                'courses': course_stats,
                'learning': learning_stats
            }
        })
    except Exception as e:
        logger.error(f"Error getting course analytics: {str(e)}")
        return Response({
            'error': 'Failed to get course analytics',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_revenue_report(request):
    """
    Revenue and subscription analytics
    """
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'error': 'Access denied. Admin privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        revenue_stats = AdminDashboardService.get_revenue_stats()
        return Response({
            'success': True,
            'data': revenue_stats
        })
    except Exception as e:
        logger.error(f"Error getting revenue report: {str(e)}")
        return Response({
            'error': 'Failed to get revenue report',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_user_activity(request):
    """
    Real-time user activity monitoring
    """
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({
            'error': 'Access denied. Admin privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get query parameters
        time_period = request.query_params.get('period', 'today')  # today, week, month
        limit = int(request.query_params.get('limit', 50))
        
        today = timezone.now().date()
        
        if time_period == 'today':
            start_date = today
        elif time_period == 'week':
            start_date = today - timedelta(days=7)
        elif time_period == 'month':
            start_date = today - timedelta(days=30)
        else:
            start_date = today
        
        # Get active users in the time period
        active_users = User.objects.filter(
            daily_activities__date__gte=start_date
        ).distinct().annotate(
            last_activity=Max('daily_activities__date'),
            total_problems=Sum('daily_activities__problems_solved'),
            activity_days=Count('daily_activities__date', distinct=True)
        ).order_by('-last_activity')[:limit]
        
        # Get recent activities
        recent_activities = DailyActivity.objects.filter(
            date__gte=start_date
        ).select_related('user').order_by('-date', '-problems_solved')[:100]
        
        activity_data = []
        for activity in recent_activities:
            activity_data.append({
                'user_id': activity.user.id,
                'username': activity.user.username,
                'email': activity.user.email,
                'is_premium': activity.user.is_premium,
                'date': activity.date,
                'status': activity.status,
                'problems_solved': activity.problems_solved,
                'lesson_ids': activity.lesson_ids
            })
        
        user_activity_data = []
        for user in active_users:
            user_activity_data.append({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'is_premium': user.is_premium,
                'last_activity': user.last_activity,
                'total_problems': user.total_problems or 0,
                'activity_days': user.activity_days,
                'streak': getattr(user.streak, 'current_streak', 0) if hasattr(user, 'streak') else 0
            })
        
        return Response({
            'success': True,
            'data': {
                'active_users': user_activity_data,
                'recent_activities': activity_data,
                'time_period': time_period,
                'total_active_users': len(user_activity_data)
            }
        })
    except Exception as e:
        logger.error(f"Error getting user activity: {str(e)}")
        return Response({
            'error': 'Failed to get user activity',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_activity(request):
    """
    Heartbeat of the system (Backend v2).
    🛡️ Checkpoint: Pass request_id for Idempotency.
    """
    try:
        serializer = StreakUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        action_type = serializer.validated_data.get('action_type', 'solve')
        energy_spent = serializer.validated_data.get('energy_spent', 0)
        problems_solved = serializer.validated_data.get('problems_solved', 0)
        lesson_ids = serializer.validated_data.get('lesson_ids', [])
        
        # 🛡️ Extract request_id for idempotency
        request_id = serializer.validated_data.get('request_id')
        if not request_id:
            request_id = None

        # 1. Trigger the Rule Engine
        engine_result = GamificationEngine.update_activity(
            user=request.user,
            action_type=action_type,
            problems_solved=problems_solved,
            energy_spent=energy_spent,
            request_id=request_id
        )
        
        # 🛡️ Handle idempotent response
        if 'error' in engine_result and engine_result.get('idempotent'):
             return Response({
                'success': True,
                'message': 'Duplicate request handled (Idempotent)',
                'warning': 'This action was already processed.'
            }, status=status.HTTP_200_OK)

        # 2. Update Legacy Tables for compatibility
        today = timezone.now().date()
        legacy_streak, _ = Streak.objects.get_or_create(user=request.user)
        legacy_streak.xp = engine_result['new_total_xp']
        legacy_streak.current_streak = int(engine_result['streak_count'])
        legacy_streak.save()

        # Update DailyActivity
        activity, _ = DailyActivity.objects.get_or_create(
            user=request.user,
            date=today,
            defaults={'status': 'none', 'problems_solved': 0, 'lesson_ids': []}
        )
        if action_type == 'solve' or problems_solved > 0:
            activity.problems_solved += problems_solved
            activity.lesson_ids = list(set(activity.lesson_ids + lesson_ids))
            if activity.problems_solved >= 3:
                activity.status = 'complete'
            else:
                activity.status = 'partial'
            activity.save()

        return Response({
            'success': True,
            'message': 'Engagement record updated',
            'gamification': engine_result,
            'activity': {
                'today': today.isoformat(),
                'status': activity.status
            }
        })
    except Exception as e:
        logger.error(f"Error in update_activity: {str(e)}")
        return Response({
            'error': 'Failed to update engagement activity',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
