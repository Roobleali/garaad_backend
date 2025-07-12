from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, F, Count, Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction

from .models import (
    Campus, Room, CampusMembership, Post, Comment, Like,
    UserCommunityProfile, CommunityNotification
)
from .serializers import (
    CampusListSerializer, CampusDetailSerializer, RoomSerializer,
    CampusMembershipSerializer, PostCreateSerializer, PostListSerializer,
    PostDetailSerializer, CommentCreateSerializer, CommentSerializer,
    CommentWithRepliesSerializer, LikeSerializer, LikeCreateSerializer,
    UserCommunityProfileSerializer, CommunityNotificationSerializer,
    JoinCampusSerializer
)
from .permissions import (
    CommunityPermission, IsCampusMember, CanCreateInCampus,
    IsCampusModeratorOrOwner, CanModerateContent, CanCreateContent
)


class CampusViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Campus model - subject-based communities
    """
    queryset = Campus.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CampusDetailSerializer
        return CampusListSerializer
    
    def get_queryset(self):
        queryset = Campus.objects.filter(is_active=True)
        
        # Filter by subject tag if provided
        subject_tag = self.request.query_params.get('subject_tag')
        if subject_tag:
            queryset = queryset.filter(subject_tag=subject_tag)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(name_somali__icontains=search) |
                Q(description__icontains=search) |
                Q(description_somali__icontains=search)
            )
        
        return queryset.annotate(
            actual_member_count=Count('memberships', filter=Q(memberships__is_active=True)),
            actual_post_count=Count('rooms__posts', filter=Q(rooms__posts__is_approved=True))
        ).order_by('-actual_member_count', 'name_somali')

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, slug=None):
        """Join a campus"""
        campus = self.get_object()
        
        # Check if already a member
        membership, created = CampusMembership.objects.get_or_create(
            user=request.user,
            campus=campus,
            defaults={'is_active': True}
        )
        
        if not created:
            if membership.is_active:
                return Response({
                    'error': 'Waad ka mid tahay campus-kan horay.'  # Already a member
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                membership.is_active = True
                membership.save()
        
        # Update campus member count
        campus.member_count = campus.memberships.filter(is_active=True).count()
        campus.save(update_fields=['member_count'])
        
        # Create notification for campus moderators
        moderators = CampusMembership.objects.filter(
            campus=campus,
            is_moderator=True,
            is_active=True
        ).select_related('user')
        
        for mod_membership in moderators:
            CommunityNotification.objects.create(
                recipient=mod_membership.user,
                sender=request.user,
                notification_type='new_campus_member',
                campus=campus,
                title=f'Xubin cusub ayaa ku biiray {campus.name_somali}',  # New member joined
                message=f'{request.user.username} ayaa ku biiray campus-ka {campus.name_somali}.'
            )
        
        return Response({
            'message': f'Si guul leh ayaad ugu biirtay {campus.name_somali}!'  # Successfully joined
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsCampusMember])
    def leave(self, request, slug=None):
        """Leave a campus"""
        campus = self.get_object()
        
        try:
            membership = CampusMembership.objects.get(
                user=request.user,
                campus=campus,
                is_active=True
            )
            membership.is_active = False
            membership.save()
            
            # Update campus member count
            campus.member_count = campus.memberships.filter(is_active=True).count()
            campus.save(update_fields=['member_count'])
            
            return Response({
                'message': f'Si guul leh ayaad uga baxday {campus.name_somali}.'  # Successfully left
            })
        
        except CampusMembership.DoesNotExist:
            return Response({
                'error': 'Ma ahayn xubin campus-kan.'  # You were not a member
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsCampusMember])
    def rooms(self, request, slug=None):
        """Get rooms in a campus"""
        campus = self.get_object()
        rooms = Room.objects.filter(
            campus=campus,
            is_active=True
        ).order_by('name_somali')
        
        serializer = RoomSerializer(rooms, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsCampusMember])
    def members(self, request, slug=None):
        """Get campus members"""
        campus = self.get_object()
        memberships = CampusMembership.objects.filter(
            campus=campus,
            is_active=True
        ).select_related('user').order_by('-is_moderator', '-joined_at')
        
        serializer = CampusMembershipSerializer(memberships, many=True, context={'request': request})
        return Response(serializer.data)


class RoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Room model - specific discussion areas within campuses
    """
    queryset = Room.objects.filter(is_active=True)
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated, IsCampusMember]
    
    def get_queryset(self):
        queryset = Room.objects.filter(is_active=True)
        
        # Filter by campus
        campus_slug = self.request.query_params.get('campus')
        if campus_slug:
            queryset = queryset.filter(campus__slug=campus_slug)
        
        # Filter by room type
        room_type = self.request.query_params.get('room_type')
        if room_type:
            queryset = queryset.filter(room_type=room_type)
        
        return queryset.select_related('campus', 'created_by').order_by('campus__name', 'name_somali')

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get posts in a room"""
        room = self.get_object()
        posts = Post.objects.filter(
            room=room,
            is_approved=True
        ).select_related('user', 'room__campus').prefetch_related(
            'likes',
            Prefetch('comments', queryset=Comment.objects.filter(is_approved=True))
        ).order_by('-is_pinned', '-last_activity')
        
        # Pagination
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Post model - user posts in rooms
    """
    queryset = Post.objects.filter(is_approved=True)
    permission_classes = [IsAuthenticated, CanCreateContent]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        elif self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer
    
    def get_queryset(self):
        queryset = Post.objects.filter(is_approved=True)
        
        # Filter by room
        room_id = self.request.query_params.get('room')
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        
        # Filter by campus
        campus_slug = self.request.query_params.get('campus')
        if campus_slug:
            queryset = queryset.filter(room__campus__slug=campus_slug)
        
        # Filter by post type
        post_type = self.request.query_params.get('post_type')
        if post_type:
            queryset = queryset.filter(post_type=post_type)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search)
            )
        
        return queryset.select_related('user', 'room__campus').order_by('-is_pinned', '-last_activity')

    def perform_create(self, serializer):
        """Create a new post and award points"""
        with transaction.atomic():
            post = serializer.save(user=self.request.user)
            
            # Award points for creating a post
            profile, created = UserCommunityProfile.objects.get_or_create(
                user=self.request.user
            )
            profile.add_points(10)  # +10 points for post
            profile.total_posts += 1
            profile.save()
            
            # Update campus membership stats
            try:
                membership = CampusMembership.objects.get(
                    user=self.request.user,
                    campus=post.room.campus,
                    is_active=True
                )
                membership.posts_count += 1
                membership.save()
            except CampusMembership.DoesNotExist:
                pass
            
            # Update room post count
            post.room.post_count = post.room.posts.filter(is_approved=True).count()
            post.room.save(update_fields=['post_count'])

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a post and increment view count"""
        instance = self.get_object()
        
        # Increment view count
        Post.objects.filter(id=instance.id).update(views_count=F('views_count') + 1)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like or unlike a post"""
        post = self.get_object()
        
        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post,
            defaults={'content_type': 'post'}
        )
        
        if not created:
            # Unlike if already liked
            like.delete()
            message = 'Qoraalka waa laga qaaday jecelka.'  # Post unliked
            liked = False
        else:
            message = 'Qoraalka waa la jeclaystay.'  # Post liked
            liked = True
            
            # Award points to post owner for receiving a like
            if post.user != request.user:
                profile, created = UserCommunityProfile.objects.get_or_create(
                    user=post.user
                )
                profile.add_points(1)  # +1 point for receiving like
                profile.total_likes_received += 1
                profile.save()
                
                # Create notification
                CommunityNotification.objects.create(
                    recipient=post.user,
                    sender=request.user,
                    notification_type='post_like',
                    post=post,
                    title='Qof ayaa jeclaystay qoraalkaaga',  # Someone liked your post
                    message=f'{request.user.username} ayaa jeclaystay qoraalkaaga "{post.title}"'
                )
        
        # Update post like count
        post.likes_count = post.likes.count()
        post.save(update_fields=['likes_count'])
        
        return Response({
            'message': message,
            'liked': liked,
            'likes_count': post.likes_count
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanModerateContent])
    def approve(self, request, pk=None):
        """Approve a post (moderators only)"""
        post = self.get_object()
        post.is_approved = True
        post.save(update_fields=['is_approved'])
        
        return Response({'message': 'Qoraalka waa la ansixiyay.'})  # Post approved

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanModerateContent])
    def disapprove(self, request, pk=None):
        """Disapprove a post (moderators only)"""
        post = self.get_object()
        post.is_approved = False
        post.save(update_fields=['is_approved'])
        
        return Response({'message': 'Qoraalka waa la diiday.'})  # Post disapproved


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Comment model - comments on posts
    """
    queryset = Comment.objects.filter(is_approved=True)
    permission_classes = [IsAuthenticated, CanCreateContent]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer
    
    def get_queryset(self):
        queryset = Comment.objects.filter(is_approved=True)
        
        # Filter by post
        post_id = self.request.query_params.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        return queryset.select_related('user', 'post').order_by('created_at')

    def perform_create(self, serializer):
        """Create a comment and award points"""
        with transaction.atomic():
            comment = serializer.save(user=self.request.user)
            
            # Award points for creating a comment
            profile, created = UserCommunityProfile.objects.get_or_create(
                user=self.request.user
            )
            profile.add_points(5)  # +5 points for comment
            profile.total_comments += 1
            profile.save()
            
            # Update campus membership stats
            try:
                membership = CampusMembership.objects.get(
                    user=self.request.user,
                    campus=comment.post.room.campus,
                    is_active=True
                )
                membership.comments_count += 1
                membership.save()
            except CampusMembership.DoesNotExist:
                pass
            
            # Create notification for post owner
            if comment.post.user != self.request.user:
                notification_type = 'comment_reply' if comment.parent_comment else 'post_comment'
                title = 'Qof ayaa ka faalleeyay qoraalkaaga' if not comment.parent_comment else 'Qof ayaa kaa jawaabay faalladaada'
                
                CommunityNotification.objects.create(
                    recipient=comment.post.user,
                    sender=self.request.user,
                    notification_type=notification_type,
                    post=comment.post,
                    comment=comment,
                    title=title,
                    message=f'{self.request.user.username} ayaa qoray: "{comment.content[:50]}..."'
                )

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like or unlike a comment"""
        comment = self.get_object()
        
        like, created = Like.objects.get_or_create(
            user=request.user,
            comment=comment,
            defaults={'content_type': 'comment'}
        )
        
        if not created:
            like.delete()
            message = 'Faallada waa laga qaaday jecelka.'  # Comment unliked
            liked = False
        else:
            message = 'Faallada waa la jeclaystay.'  # Comment liked
            liked = True
            
            # Award points to comment owner
            if comment.user != request.user:
                profile, created = UserCommunityProfile.objects.get_or_create(
                    user=comment.user
                )
                profile.add_points(1)  # +1 point for receiving like
                profile.total_likes_received += 1
                profile.save()
                
                # Create notification
                CommunityNotification.objects.create(
                    recipient=comment.user,
                    sender=request.user,
                    notification_type='comment_like',
                    post=comment.post,
                    comment=comment,
                    title='Qof ayaa jeclaystay faalladaada',  # Someone liked your comment
                    message=f'{request.user.username} ayaa jeclaystay faalladaada'
                )
        
        # Update comment like count
        comment.likes_count = comment.likes.count()
        comment.save(update_fields=['likes_count'])
        
        return Response({
            'message': message,
            'liked': liked,
            'likes_count': comment.likes_count
        })


class UserCommunityProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user community profiles
    """
    queryset = UserCommunityProfile.objects.all()
    serializer_class = UserCommunityProfileSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's community profile"""
        profile, created = UserCommunityProfile.objects.get_or_create(
            user=request.user
        )
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get community leaderboard"""
        campus_slug = request.query_params.get('campus')
        
        queryset = UserCommunityProfile.objects.select_related('user')
        
        if campus_slug:
            # Campus-specific leaderboard
            queryset = queryset.filter(
                user__campusmembership__campus__slug=campus_slug,
                user__campusmembership__is_active=True
            )
        
        # Top 50 users by community points
        profiles = queryset.order_by('-community_points')[:50]
        serializer = self.get_serializer(profiles, many=True)
        return Response(serializer.data)


class CommunityNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for community notifications
    """
    serializer_class = CommunityNotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CommunityNotification.objects.filter(
            recipient=self.request.user
        ).select_related('sender', 'post', 'campus').order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        
        return Response({'message': 'Ogeysiisku waa la akhriday.'})  # Notification marked as read

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        updated = CommunityNotification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
        
        return Response({
            'message': f'{updated} ogeysiis oo dhan ayaa loo calaamadeeyay inay akhristaan.'  # All notifications marked as read
        }) 