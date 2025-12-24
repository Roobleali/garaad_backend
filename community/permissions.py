from rest_framework import permissions


class IsAuthorOrStaffOrReadOnly(permissions.BasePermission):
    """
    Allow authors to edit/delete their own content.
    Allow staff to moderate (delete any content).
    Everyone else can only read.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Staff can do anything
        if request.user.is_staff:
            return True
        
        # Authors can edit/delete their own content
        return obj.author == request.user


class IsCommunityEnabled(permissions.BasePermission):
    """
    Check if category has community features enabled.
    """
    
    def has_permission(self, request, view):
        # For list/create views, check category from request
        category_id = request.data.get('category') or view.kwargs.get('category_id')
        
        if not category_id:
            return False
        
        from courses.models import Category
        try:
            category = Category.objects.get(id=category_id)
            return category.is_community_enabled
        except Category.DoesNotExist:
            return False