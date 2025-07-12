from rest_framework import permissions
from django.contrib.auth import get_user_model
from .models import CampusMembership, Post, Comment

User = get_user_model()


class IsCampusMember(permissions.BasePermission):
    """
    Permission to check if user is a member of the campus
    """
    message = "Waa inaad ka mid tahay campus-ka si aad u geli karto."  # You must be a member of the campus to access

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # For list views, check if user has access to any campus
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
            
        # Get the campus from the object
        campus = None
        if hasattr(obj, 'campus'):
            campus = obj.campus
        elif hasattr(obj, 'room') and hasattr(obj.room, 'campus'):
            campus = obj.room.campus
        elif hasattr(obj, 'post') and hasattr(obj.post, 'room'):
            campus = obj.post.room.campus
            
        if not campus:
            return False
            
        # Check if user is a member of the campus
        return CampusMembership.objects.filter(
            user=request.user,
            campus=campus,
            is_active=True
        ).exists()


class IsCampusModeratorOrOwner(permissions.BasePermission):
    """
    Permission to check if user is campus moderator or object owner
    """
    message = "Waa inaad tahay maamulaha campus-ka ama milkiilaha walaxan."  # You must be campus moderator or owner

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
            
        # Get the campus and check if user is moderator
        campus = None
        if hasattr(obj, 'campus'):
            campus = obj.campus
        elif hasattr(obj, 'room') and hasattr(obj.room, 'campus'):
            campus = obj.room.campus
        elif hasattr(obj, 'post') and hasattr(obj.post, 'room'):
            campus = obj.post.room.campus
            
        if campus:
            # Check if user is campus moderator
            try:
                membership = CampusMembership.objects.get(
                    user=request.user,
                    campus=campus,
                    is_active=True
                )
                if membership.is_moderator:
                    return True
            except CampusMembership.DoesNotExist:
                pass
        
        # Check if user is the owner of the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
            
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to allow owners to edit their own content, others can only read
    """
    message = "Waa inaad tahay milkiilaha walaxan si aad u wax ka beddesho."  # You must be the owner to modify

    def has_object_permission(self, request, view, obj):
        # Read permissions for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
            
        if not request.user.is_authenticated:
            return False
            
        # Write permissions only for owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
            
        return False


class CanCreateInCampus(permissions.BasePermission):
    """
    Permission to check if user can create content in a campus
    """
    message = "Waa inaad ka mid tahay campus-ka si aad u sameyso waxyaabo cusub."  # You must be a member to create

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # For POST requests, check if user can create in the specified campus
        if request.method == 'POST':
            # Get campus from request data
            campus_id = None
            room_id = request.data.get('room_id')
            
            if room_id:
                try:
                    from .models import Room
                    room = Room.objects.get(id=room_id, is_active=True)
                    campus_id = room.campus.id
                except Room.DoesNotExist:
                    return False
            
            campus_id = campus_id or request.data.get('campus_id')
            
            if campus_id:
                return CampusMembership.objects.filter(
                    user=request.user,
                    campus_id=campus_id,
                    is_active=True
                ).exists()
                
        return True


class CanCreatePost(permissions.BasePermission):
    """
    Permission to allow any authenticated user to create posts
    """
    message = "Waa inaad ku saabsan tahay si aad u sameyso qoraal."  # You must be authenticated to create a post

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Any authenticated user can create posts
        return True


class CanCreateContent(permissions.BasePermission):
    """
    Permission to allow any authenticated user to create content (posts, comments, likes)
    """
    message = "Waa inaad ku saabsan tahay si aad u sameyso waxyaabo."  # You must be authenticated to create content

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Any authenticated user can create content
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
            
        # Users can edit their own content
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
            
        return False


class CanModerateContent(permissions.BasePermission):
    """
    Permission for content moderation (approve/disapprove posts and comments)
    """
    message = "Waa inaad tahay maamule si aad u maamulto waxyaabaha."  # You must be a moderator to moderate content

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Check if user is staff or superuser
        if request.user.is_staff or request.user.is_superuser:
            return True
            
        # Check if user is moderator in any campus
        return CampusMembership.objects.filter(
            user=request.user,
            is_moderator=True,
            is_active=True
        ).exists()

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
            
        # Staff and superuser can moderate everything
        if request.user.is_staff or request.user.is_superuser:
            return True
            
        # Get the campus for the object
        campus = None
        if hasattr(obj, 'campus'):
            campus = obj.campus
        elif hasattr(obj, 'room') and hasattr(obj.room, 'campus'):
            campus = obj.room.campus
        elif hasattr(obj, 'post') and hasattr(obj.post, 'room'):
            campus = obj.post.room.campus
            
        if campus:
            # Check if user is moderator of this specific campus
            return CampusMembership.objects.filter(
                user=request.user,
                campus=campus,
                is_moderator=True,
                is_active=True
            ).exists()
            
        return False


class IsApprovedContent(permissions.BasePermission):
    """
    Permission to ensure only approved content is visible to regular users
    """
    message = "Waxa kaliya ee la arki karo waa kuwa la ansixiyay."  # Only approved content can be viewed

    def has_object_permission(self, request, view, obj):
        # Staff and superusers can see all content
        if request.user.is_staff or request.user.is_superuser:
            return True
            
        # Content owners can see their own content even if not approved
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
            
        # Campus moderators can see all content in their campus
        campus = None
        if hasattr(obj, 'campus'):
            campus = obj.campus
        elif hasattr(obj, 'room') and hasattr(obj.room, 'campus'):
            campus = obj.room.campus
        elif hasattr(obj, 'post') and hasattr(obj.post, 'room'):
            campus = obj.post.room.campus
            
        if campus and request.user.is_authenticated:
            try:
                membership = CampusMembership.objects.get(
                    user=request.user,
                    campus=campus,
                    is_active=True
                )
                if membership.is_moderator:
                    return True
            except CampusMembership.DoesNotExist:
                pass
        
        # For regular users, content must be approved
        return getattr(obj, 'is_approved', True)


class CanJoinCampus(permissions.BasePermission):
    """
    Permission to check if user can join a campus
    """
    message = "Ma kuu ogola inaad ku biirto campus-kan."  # You are not allowed to join this campus

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
            
        # Check if campus is active
        if not obj.is_active:
            return False
            
        # Check if user is already a member
        if CampusMembership.objects.filter(
            user=request.user,
            campus=obj,
            is_active=True
        ).exists():
            return False
            
        # If campus requires approval, only staff can approve
        if obj.requires_approval and not request.user.is_staff:
            return False
            
        return True


class CanLikeContent(permissions.BasePermission):
    """
    Permission to check if user can like content
    """
    message = "Ma kuu ogola inaad jeclaato waxyaalahan."  # You are not allowed to like this content

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Users can like content they have access to
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
            
        # Users cannot like their own content
        if hasattr(obj, 'user') and obj.user == request.user:
            self.message = "Ma kuu ogola inaad jeclaato waxyaahaaga."  # You cannot like your own content
            return False
            
        # Check if user is member of the campus
        campus = None
        if hasattr(obj, 'room') and hasattr(obj.room, 'campus'):
            campus = obj.room.campus
        elif hasattr(obj, 'post') and hasattr(obj.post, 'room'):
            campus = obj.post.room.campus
            
        if campus:
            return CampusMembership.objects.filter(
                user=request.user,
                campus=campus,
                is_active=True
            ).exists()
            
        return True


class IsCampusActive(permissions.BasePermission):
    """
    Permission to ensure campus is active
    """
    message = "Campus-kan ma shaqeeyo hadda."  # This campus is not active

    def has_object_permission(self, request, view, obj):
        # Get the campus
        campus = None
        if hasattr(obj, 'campus'):
            campus = obj.campus
        elif hasattr(obj, 'room') and hasattr(obj.room, 'campus'):
            campus = obj.room.campus
        elif hasattr(obj, 'post') and hasattr(obj.post, 'room'):
            campus = obj.post.room.campus
        elif hasattr(obj, 'is_active'):  # For Campus objects
            return obj.is_active
            
        return campus.is_active if campus else True


class CommunityPermission(permissions.BasePermission):
    """
    Combined permission class for community features
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Different permissions based on action
        action = getattr(view, 'action', None)
        
        if action in ['list', 'retrieve']:
            return True
        elif action in ['create']:
            return CanCreatePost().has_permission(request, view)
        elif action in ['update', 'partial_update', 'destroy']:
            return True  # Will be checked at object level
        elif action in ['like', 'unlike']:
            return CanLikeContent().has_permission(request, view)
        elif action in ['join', 'leave']:
            return True  # Will be checked at object level
        elif action in ['approve', 'disapprove']:
            return CanModerateContent().has_permission(request, view)
            
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
            
        action = getattr(view, 'action', None)
        
        # Check if campus is active
        if not IsCampusActive().has_object_permission(request, view, obj):
            return False
            
        # Check campus membership
        if not IsCampusMember().has_object_permission(request, view, obj):
            return False
            
        # Check content approval status
        if action in ['retrieve'] and not IsApprovedContent().has_object_permission(request, view, obj):
            return False
            
        if action in ['update', 'partial_update', 'destroy']:
            return (IsOwnerOrReadOnly().has_object_permission(request, view, obj) or 
                   IsCampusModeratorOrOwner().has_object_permission(request, view, obj))
        elif action in ['like', 'unlike']:
            return CanLikeContent().has_object_permission(request, view, obj)
        elif action in ['join']:
            return CanJoinCampus().has_object_permission(request, view, obj)
        elif action in ['approve', 'disapprove']:
            return CanModerateContent().has_object_permission(request, view, obj)
            
        return True 