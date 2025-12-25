from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'replies', views.ReplyViewSet, basename='reply')

app_name = 'community'

urlpatterns = [
    # Main router URLs
    path('', include(router.urls)),
    
    # Profile endpoint for frontend
    path('profiles/me/', views.PostViewSet.as_view({'get': 'me'}), name='profile-me'),
    
    # Category-specific posts endpoint
    # GET/POST /api/community/categories/{category_id}/posts/
    re_path(
        r'^categories/(?P<category_id>[^/]+)/posts/?$',
        views.PostViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='category-posts'
    ),
]