from rest_framework import permissions

class AllowAnyForAuth(permissions.BasePermission):
    """
    Custom permission to allow any access to auth endpoints
    """
    def has_permission(self, request, view):
        return True

class IsProgrammaticRequest(permissions.BasePermission):
    """
    Custom permission to only allow programmatic requests (no browser access)
    """
    def has_permission(self, request, view):
        # Check if the request is from a browser
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        is_browser = any(agent in user_agent.lower() for agent in ['mozilla', 'chrome', 'safari', 'edge', 'opera'])
        
        # Allow the request if it's not from a browser
        return not is_browser

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow authenticated users to access resources
    """
    def has_permission(self, request, view):
        # Allow read-only access for unauthenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow full access for authenticated users
        return request.user and request.user.is_authenticated

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object
        return obj.user == request.user 