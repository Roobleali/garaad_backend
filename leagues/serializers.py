from rest_framework import serializers
from .models import League, UserLeague

class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = ['id', 'name', 'somali_name', 'description', 'min_xp', 'order', 'icon']

class UserLeagueSerializer(serializers.ModelSerializer):
    current_league = LeagueSerializer(read_only=True)
    next_league = serializers.SerializerMethodField()
    
    class Meta:
        model = UserLeague
        fields = ['current_league', 'total_xp', 'weekly_xp', 'monthly_xp', 'next_league']
    
    def get_next_league(self, obj):
        next_league = League.objects.filter(min_xp__gt=obj.current_league.min_xp).order_by('min_xp').first()
        if next_league:
            return {
                'id': next_league.id,
                'name': next_league.name,
                'somali_name': next_league.somali_name,
                'min_xp': next_league.min_xp,
                'points_needed': next_league.min_xp - obj.total_xp
            }
        return None

class LeagueStatusSerializer(serializers.Serializer):
    current_league = LeagueSerializer()
    current_points = serializers.IntegerField()
    weekly_rank = serializers.IntegerField()
    streak = serializers.DictField()
    next_league = serializers.DictField(allow_null=True) 