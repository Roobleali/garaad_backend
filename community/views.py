from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from courses.models import Category
from .models import Post, Reply, Reaction
from .serializers import (
    PostSerializer,
    PostCreateSerializer,
    ReplySerializer,
    ReplyCreateSerializer,
    ReactionSerializer
)
from .permissions import IsAuthorOrStaffOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for community posts.
    
    List/Create: GET/POST /api/categories/{category_id}/posts/
    Detail: GET/PATCH/DELETE /api/posts/{id}/
    React: POST /api/posts/{id}/react/
    Reply: POST /api/posts/{id}/reply/
    """
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrStaffOrReadOnly]
    
    def get_queryset(self):
        """Filter posts by category if provided"""
        queryset = Post.objects.select_related('author', 'category').prefetch_related(
            'replies',
            'replies__author',
            'reactions',
            'images'
        )
        
        # Filter by category if in URL
        category_id = self.kwargs.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """Use different serializers for create vs read"""
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new post"""
        # Validate category is community-enabled
        category_id = request.data.get('category') or kwargs.get('category_id')
        category = get_object_or_404(Category, id=category_id)
        
        if not category.is_community_enabled:
            return Response(
                {'error': 'This category does not have community features enabled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return full post data
        post = serializer.instance
        return Response(
            PostSerializer(post, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """Update a post (mark as edited)"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Mark as edited
        instance.is_edited = True
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def react(self, request, pk=None):
        """Toggle a reaction on a post"""
        post = self.get_object()
        serializer = ReactionSerializer(
            data=request.data,
            context={'request': request, 'post': post}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        
        return Response(result, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reply(self, request, pk=None):
        """Add a reply to a post"""
        post = self.get_object()
        serializer = ReplyCreateSerializer(
            data=request.data,
            context={'request': request, 'post': post}
        )
        serializer.is_valid(raise_exception=True)
        reply = serializer.save()
        
        return Response(
            ReplySerializer(reply).data,
            status=status.HTTP_201_CREATED
        )


class ReplyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing replies.
    
    Update/Delete: PATCH/DELETE /api/replies/{id}/
    """
    queryset = Reply.objects.select_related('author', 'post')
    serializer_class = ReplySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrStaffOrReadOnly]
    http_method_names = ['get', 'patch', 'delete']  # No create (use post.reply instead)
    
    def update(self, request, *args, **kwargs):
        """Update a reply (mark as edited)"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Mark as edited
        instance.is_edited = True
        self.perform_update(serializer)
        
        return Response(serializer.data)