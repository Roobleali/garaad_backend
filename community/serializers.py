from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q
from .models import (
    Campus, Room, CampusMembership, Post, Comment, Like,
    UserCommunityProfile, CommunityNotification, Message, Presence
)

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for community features"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture', 'first_name', 'last_name']


class CampusListSerializer(serializers.ModelSerializer):
    """Serializer for campus list view"""
    subject_display_somali = serializers.CharField(source='get_subject_display_somali', read_only=True)
    user_is_member = serializers.SerializerMethodField()
    
    class Meta:
        model = Campus
        fields = [
            'id', 'name', 'description',
            'subject_tag', 'subject_display_somali', 'icon', 'slug', 'color_code',
            'member_count', 'post_count', 'is_active', 'user_is_member'
        ]
    
    def get_user_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CampusMembership.objects.filter(
                user=request.user, 
                campus=obj, 
                is_active=True
            ).exists()
        return False


class CampusDetailSerializer(serializers.ModelSerializer):
    """Detailed campus serializer with additional info"""
    subject_display_somali = serializers.CharField(source='get_subject_display_somali', read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    user_membership = serializers.SerializerMethodField()
    recent_posts = serializers.SerializerMethodField()
    
    class Meta:
        model = Campus
        fields = [
            'id', 'name', 'description',
            'subject_tag', 'subject_display_somali', 'icon', 'slug', 'color_code',
            'member_count', 'post_count', 'is_active', 'requires_approval',
            'created_at', 'created_by', 'user_membership', 'recent_posts'
        ]
    
    def get_user_membership(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                membership = CampusMembership.objects.get(
                    user=request.user, 
                    campus=obj, 
                    is_active=True
                )
                return {
                    'is_member': True,
                    'is_moderator': membership.is_moderator,
                    'joined_at': membership.joined_at,
                    'posts_count': membership.posts_count,
                    'reputation_score': membership.reputation_score
                }
            except CampusMembership.DoesNotExist:
                return {'is_member': False}
        return {'is_member': False}
    
    def get_recent_posts(self, obj):
        # Get recent posts from this campus
        recent_posts = Post.objects.filter(
            room__campus=obj,
            is_approved=True
        ).select_related('user', 'room').order_by('-created_at')[:5]
        
        return [{
            'id': str(post.id),
            'title': post.title,
            'user': post.user.username,
            'room': post.room.name,
            'created_at': post.created_at,
            'likes_count': post.likes_count,
            'comments_count': post.comments_count
        } for post in recent_posts]


class RoomSerializer(serializers.ModelSerializer):
    """Room serializer"""
    campus = CampusListSerializer(read_only=True)
    campus_id = serializers.PrimaryKeyRelatedField(
        queryset=Campus.objects.filter(is_active=True),
        source='campus',
        write_only=True
    )
    created_by = UserBasicSerializer(read_only=True)
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)
    
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'slug', 'description', 'campus', 'campus_id', 
            'room_type', 'room_type_display', 'is_private', 'icon',
            'order', 'created_at', 'created_by'
        ]
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CampusMembershipSerializer(serializers.ModelSerializer):
    """Campus membership serializer"""
    user = UserBasicSerializer(read_only=True)
    campus = CampusListSerializer(read_only=True)
    
    class Meta:
        model = CampusMembership
        fields = [
            'id', 'user', 'campus', 'joined_at', 'is_moderator', 'is_active',
            'posts_count', 'comments_count', 'likes_received', 'reputation_score'
        ]


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts"""
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.filter(is_active=True),
        source='room',
        write_only=True
    )
    
    class Meta:
        model = Post
        fields = [
            'title', 'content', 'language', 'post_type', 'room_id', 'image', 'video_url'
        ]
        extra_kwargs = {
            'title': {'error_messages': {'min_length': 'Cinwaanku waa inuu yahay ugu yaraan 5 xaraf.'}},  # Title must be at least 5 characters
            'content': {'error_messages': {'min_length': 'Qoraalku waa inuu yahay ugu yaraan 10 xaraf.'}},  # Content must be at least 10 characters
        }
    
    def validate(self, data):
        # Any authenticated user can create posts
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError({
                'room_id': 'Waa inaad ku saabsan tahay si aad qoraal u qorto.'  # You must be authenticated to post
            })
        
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PostListSerializer(serializers.ModelSerializer):
    """Serializer for post list view"""
    user = UserBasicSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    post_type_display = serializers.CharField(source='get_post_type_display', read_only=True)
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    user_has_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'user', 'room', 'language', 'language_display',
            'post_type', 'post_type_display', 'image', 'video_url',
            'is_pinned', 'is_featured', 'likes_count', 'comments_count', 'views_count',
            'created_at', 'updated_at', 'user_has_liked'
        ]
    
    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(
                user=request.user,
                post=obj
            ).exists()
        return False


class PostDetailSerializer(PostListSerializer):
    """Detailed post serializer with comments"""
    comments = serializers.SerializerMethodField()
    
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ['comments']
    
    def get_comments(self, obj):
        # Get top-level comments (not replies)
        comments = Comment.objects.filter(
            post=obj,
            parent_comment__isnull=True,
            is_approved=True
        ).select_related('user').order_by('created_at')
        
        return CommentWithRepliesSerializer(comments, many=True, context=self.context).data


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments"""
    post_id = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.filter(is_approved=True),
        source='post',
        write_only=True
    )
    parent_comment_id = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.filter(is_approved=True),
        source='parent_comment',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Comment
        fields = ['content', 'language', 'post_id', 'parent_comment_id']
        extra_kwargs = {
            'content': {'error_messages': {'min_length': 'Faallaadu waa inay tahay ugu yaraan 2 xaraf.'}},  # Comment must be at least 2 characters
        }
    
    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError({
                'post_id': 'Waa inaad ku saabsan tahay si aad faallo u qorto.'  # You must be authenticated to comment
            })
        
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """Comment serializer"""
    user = UserBasicSerializer(read_only=True)
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    user_has_liked = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'user', 'language', 'language_display',
            'likes_count', 'created_at', 'updated_at', 'is_edited',
            'user_has_liked', 'replies_count'
        ]
    
    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(
                user=request.user,
                comment=obj
            ).exists()
        return False
    
    def get_replies_count(self, obj):
        return obj.replies.filter(is_approved=True).count()


class CommentWithRepliesSerializer(CommentSerializer):
    """Comment serializer with replies"""
    replies = serializers.SerializerMethodField()
    
    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + ['replies']
    
    def get_replies(self, obj):
        replies = obj.replies.filter(is_approved=True).select_related('user').order_by('created_at')
        return CommentSerializer(replies, many=True, context=self.context).data


class LikeSerializer(serializers.ModelSerializer):
    """Like serializer"""
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'content_type', 'created_at']


class LikeCreateSerializer(serializers.Serializer):
    """Serializer for creating likes"""
    content_type = serializers.ChoiceField(choices=['post', 'comment'])
    content_id = serializers.UUIDField()
    
    def validate(self, data):
        content_type = data['content_type']
        content_id = data['content_id']
        request = self.context['request']
        
        # Validate content exists and user can like it
        if content_type == 'post':
            try:
                post = Post.objects.get(id=content_id, is_approved=True)
                data['post'] = post
            except Post.DoesNotExist:
                raise serializers.ValidationError('Qoraalka lama helin.')  # Post not found
        
        elif content_type == 'comment':
            try:
                comment = Comment.objects.get(id=content_id, is_approved=True)
                data['comment'] = comment
            except Comment.DoesNotExist:
                raise serializers.ValidationError('Faallada lama helin.')  # Comment not found
        
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        content_type = validated_data['content_type']
        
        like_data = {'user': user, 'content_type': content_type}
        
        if content_type == 'post':
            like_data['post'] = validated_data['post']
        elif content_type == 'comment':
            like_data['comment'] = validated_data['comment']
        
        # Create or get existing like
        like, created = Like.objects.get_or_create(**like_data)
        
        if not created:
            # Unlike if already liked
            like.delete()
            return None
        
        return like


class UserCommunityProfileSerializer(serializers.ModelSerializer):
    """User community profile serializer"""
    user = UserBasicSerializer(read_only=True)
    badge_level_display = serializers.CharField(source='get_badge_level_display', read_only=True)
    
    class Meta:
        model = UserCommunityProfile
        fields = [
            'user', 'community_points', 'badge_level', 'badge_level_display',
            'total_posts', 'total_comments', 'total_likes_received', 'total_likes_given',
            'preferred_language', 'email_notifications', 'mention_notifications'
        ]
        read_only_fields = [
            'community_points', 'badge_level', 'total_posts', 'total_comments',
            'total_likes_received', 'total_likes_given'
        ]


class CommunityNotificationSerializer(serializers.ModelSerializer):
    """Community notification serializer"""
    sender = UserBasicSerializer(read_only=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    post_title = serializers.CharField(source='post.title', read_only=True)
    campus_name = serializers.CharField(source='campus.name', read_only=True)
    
    class Meta:
        model = CommunityNotification
        fields = [
            'id', 'sender', 'notification_type', 'notification_type_display',
            'title', 'message', 'is_read', 'created_at',
            'post_title', 'campus_name'
        ]


class JoinCampusSerializer(serializers.Serializer):
    """Serializer for joining a campus"""
    campus_id = serializers.PrimaryKeyRelatedField(
        queryset=Campus.objects.filter(is_active=True)
    )
    
    def validate_campus_id(self, value):
        request = self.context['request']
        
        # Check if user is already a member
        if CampusMembership.objects.filter(
            user=request.user,
            campus=value,
            is_active=True
        ).exists():
            raise serializers.ValidationError('Waad ka mid tahay campus-kan horay.')  # You are already a member of this campus
        
        return value
    
    def create(self, validated_data):
        campus = validated_data['campus_id']
        user = self.context['request'].user
        
        membership, created = CampusMembership.objects.get_or_create(
            user=user,
            campus=campus,
            defaults={'is_active': True}
        )
        
        if not created:
            membership.is_active = True
            membership.save()
        
        # Update campus member count
        campus.member_count = campus.memberships.filter(is_active=True).count()
        campus.save(update_fields=['member_count'])
        
        return membership 


class PresenceSerializer(serializers.ModelSerializer):
    """User presence serializer"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Presence
        fields = ['status', 'status_display', 'custom_status', 'last_seen']


class MessageSerializer(serializers.ModelSerializer):
    """Discord-style message serializer"""
    sender = UserBasicSerializer(read_only=True)
    sender_presence = serializers.SerializerMethodField()
    replies_count = serializers.IntegerField(source='replies.count', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'room', 'sender', 'sender_presence', 'content', 
            'attachment_url', 'attachment_type', 'reply_to', 
            'replies_count', 'is_edited', 'created_at', 'updated_at'
        ]
        read_only_fields = ['sender', 'is_edited', 'created_at']

    def get_sender_presence(self, obj):
        try:
            return PresenceSerializer(obj.sender.presence).data
        except:
            return {'status': 'offline'}