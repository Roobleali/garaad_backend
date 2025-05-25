from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import F
from django.utils import timezone
from datetime import timedelta
from .models import League, UserLeague
from api.models import Streak
from .serializers import (
    LeagueSerializer, UserLeagueSerializer, 
    LeagueStatusSerializer
)

# Create your views here.

class LeagueViewSet(viewsets.ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get current user's league status."""
        try:
            user_league = UserLeague.objects.get_or_create(
                user=request.user,
                defaults={'current_league': League.objects.order_by('min_xp_required').first()}
            )[0]
            
            # Get weekly rank
            week_start = timezone.now() - timedelta(days=7)
            weekly_rank = UserLeague.objects.filter(
                current_week_points__gt=user_league.current_week_points
            ).count() + 1
            
            # Get streak
            streak = Streak.objects.get(user=request.user)
            
            # Get next league
            next_league = League.objects.filter(
                min_xp_required__gt=user_league.league.min_xp_required
            ).order_by('min_xp_required').first()
            
            data = {
                'current_league': {
                    'id': user_league.league.id,
                    'name': user_league.league.get_level_display(),
                    'min_xp': user_league.league.min_xp_required
                },
                'current_points': user_league.current_week_points,
                'weekly_rank': weekly_rank,
                'streak': {
                    'current_streak': streak.current_streak,
                    'max_streak': streak.max_streak,
                    'streak_charges': streak.current_energy,
                    'last_activity_date': streak.last_activity_date
                },
                'next_league': {
                    'id': next_league.id,
                    'name': next_league.get_level_display(),
                    'min_xp': next_league.min_xp_required,
                    'points_needed': next_league.min_xp_required - user_league.current_week_points
                } if next_league else None
            }
            
            return Response(data)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get leaderboard standings."""
        try:
            time_period = request.query_params.get('time_period', 'weekly')
            league_id = request.query_params.get('league')
            
            queryset = UserLeague.objects.all()
            
            if league_id:
                queryset = queryset.filter(league_id=league_id)
            
            if time_period == 'weekly':
                queryset = queryset.order_by('-current_week_points')
            elif time_period == 'monthly':
                queryset = queryset.order_by('-last_week_points')
            else:  # all_time
                queryset = queryset.order_by('-current_week_points')
            
            # Get top 100 users
            top_users = queryset[:100]
            
            # Get user's own standing
            user_league = UserLeague.objects.get(user=request.user)
            user_rank = queryset.filter(
                current_week_points__gt=user_league.current_week_points
            ).count() + 1
            
            return Response({
                'time_period': time_period,
                'league': league_id,
                'standings': [{
                    'rank': idx + 1,
                    'user': {
                        'id': user_league.user.id,
                        'name': user_league.user.username,
                    },
                    'points': user_league.current_week_points,
                    'streak': Streak.objects.get(user=user_league.user).current_streak
                } for idx, user_league in enumerate(top_users)],
                'my_standing': {
                    'rank': user_rank,
                    'points': user_league.current_week_points,
                    'streak': Streak.objects.get(user=request.user).current_streak
                }
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def use_streak_charge(self, request):
        """Use a streak charge to maintain streak."""
        try:
            streak = Streak.objects.get(user=request.user)
            if streak.use_streak_charge():
                return Response({
                    'success': True,
                    'streak_maintained': True,
                    'remaining_charges': streak.current_energy,
                    'message': 'Waad ku mahadsantahay ilaalinta xariggaaga'
                })
            return Response({
                'success': False,
                'message': 'Ma haysato kayd maalmeed'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Streak.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Ma jiraan streak-kaaga'
            }, status=status.HTTP_404_NOT_FOUND)
