from rest_framework import permissions

class IsPremiumUser(permissions.BasePermission):
    """
    Custom permission to only allow premium users to access a view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_premium 