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
            user_league, _ = UserLeague.objects.get_or_create(
                user=request.user,
                defaults={'current_league': League.objects.order_by('min_xp').first()}
            )
            
            # Get weekly rank
            week_start = timezone.now() - timedelta(days=7)
            weekly_rank = UserLeague.objects.filter(
                weekly_xp__gt=user_league.weekly_xp
            ).count() + 1
            
            # Get streak
            streak, _ = Streak.objects.get_or_create(user=request.user)
            
            # Get next league
            next_league = League.objects.filter(
                min_xp__gt=user_league.current_league.min_xp
            ).order_by('min_xp').first()
            
            data = {
                'current_league': {
                    'id': user_league.current_league.id,
                    'name': str(user_league.current_league),
                    'min_xp': user_league.current_league.min_xp
                },
                'current_points': user_league.weekly_xp,
                'weekly_rank': weekly_rank,
                'streak': {
                    'current_streak': streak.current_streak,
                    'max_streak': streak.max_streak,
                    'streak_charges': streak.current_energy,
                    'last_activity_date': streak.last_activity_date
                },
                'next_league': {
                    'id': next_league.id,
                    'name': str(next_league),
                    'min_xp': next_league.min_xp,
                    'points_needed': next_league.min_xp - user_league.weekly_xp
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
                queryset = queryset.filter(current_league_id=league_id)
            
            if time_period == 'weekly':
                queryset = queryset.order_by('-weekly_xp')
            elif time_period == 'monthly':
                queryset = queryset.order_by('-monthly_xp')
            else:  # all_time
                queryset = queryset.order_by('-weekly_xp')
            
            # Get top 100 users
            top_users = queryset[:100]
            
            # Get user's own standing
            user_league, _ = UserLeague.objects.get_or_create(user=request.user)
            user_rank = queryset.filter(
                weekly_xp__gt=user_league.weekly_xp
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
                    'points': user_league.weekly_xp,
                    'streak': Streak.objects.get(user=user_league.user).current_streak
                } for idx, user_league in enumerate(top_users)],
                'my_standing': {
                    'rank': user_rank,
                    'points': user_league.weekly_xp,
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
            streak, _ = Streak.objects.get_or_create(user=request.user)
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
