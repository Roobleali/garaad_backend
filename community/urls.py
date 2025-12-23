from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'campuses', views.CampusViewSet, basename='campus')
router.register(r'rooms', views.RoomViewSet, basename='room')
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'comments', views.CommentViewSet, basename='comment')
router.register(r'profiles', views.UserCommunityProfileViewSet, basename='profile')
router.register(r'notifications', views.CommunityNotificationViewSet, basename='notification')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'presence', views.PresenceViewSet, basename='presence')

app_name = 'community'

urlpatterns = [
    # Include router URLs directly (removed extra 'api/' prefix)
    path('', include(router.urls)),
    
    # Additional custom endpoints can be added here if needed
    # path('custom-endpoint/', views.custom_view, name='custom_endpoint'),
] 