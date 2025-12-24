from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, PostImage, Reply, Reaction
from courses.models import Category

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for community features"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture', 'first_name', 'last_name']


class ReplySerializer(serializers.ModelSerializer):
    """Reply serializer - shallow, no nesting"""
    author = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Reply
        fields = [
            'id',
            'author',
            'content',
            'created_at',
            'updated_at',
            'is_edited'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_edited']


class PostImageSerializer(serializers.ModelSerializer):
    """Post image serializer"""
    
    class Meta:
        model = PostImage
        fields = ['id', 'image', 'uploaded_at']
        read_only_fields = ['uploaded_at']


class PostSerializer(serializers.ModelSerializer):
    """Post serializer with replies and reaction counts"""
    author = UserBasicSerializer(read_only=True)
    replies = ReplySerializer(many=True, read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    reactions_count = serializers.SerializerMethodField()
    user_reactions = serializers.SerializerMethodField()
    replies_count = serializers.IntegerField(source='replies.count', read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id',
            'category',
            'author',
            'content',
            'created_at',
            'updated_at',
            'is_edited',
            'images',
            'replies',
            'replies_count',
            'reactions_count',
            'user_reactions'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_edited', 'author']
    
    def get_reactions_count(self, obj):
        """Get count of each reaction type"""
        from django.db.models import Count
        reactions = obj.reactions.values('type').annotate(count=Count('type'))
        return {r['type']: r['count'] for r in reactions}
    
    def get_user_reactions(self, obj):
        """Get current user's reactions to this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return list(obj.reactions.filter(user=request.user).values_list('type', flat=True))
        return []


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts"""
    
    class Meta:
        model = Post
        fields = ['category', 'content']
    
    def validate_category(self, value):
        """Ensure category has community enabled"""
        if not value.is_community_enabled:
            raise serializers.ValidationError(
                "This category does not have community features enabled."
            )
        return value
    
    def create(self, validated_data):
        """Set author from request user"""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ReplyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating replies"""
    
    class Meta:
        model = Reply
        fields = ['content']
    
    def create(self, validated_data):
        """Set author and post from context"""
        validated_data['author'] = self.context['request'].user
        validated_data['post'] = self.context['post']
        return super().create(validated_data)


class ReactionSerializer(serializers.Serializer):
    """Serializer for toggling reactions"""
    type = serializers.ChoiceField(choices=Reaction.REACTION_CHOICES)
    
    def create(self, validated_data):
        """Toggle reaction (create or delete)"""
        user = self.context['request'].user
        post = self.context['post']
        reaction_type = validated_data['type']
        
        reaction, created = Reaction.objects.get_or_create(
            post=post,
            user=user,
            type=reaction_type
        )
        
        if not created:
            # Remove reaction if it already exists
            reaction.delete()
            return {'action': 'removed', 'type': reaction_type}
        
        return {'action': 'added', 'type': reaction_type}