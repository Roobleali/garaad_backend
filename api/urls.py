from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import SignupView, SigninView

router = DefaultRouter()
# No StreakViewSet - using function-based view instead
router.register(r'gamification', views.GamificationViewSet, basename='gamification')
router.register(r'notifications', views.NotificationViewSet, basename='notifications')

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/signin/', SigninView.as_view(), name='signin'),
    path('streaks/', views.streak_view, name='streaks'),
    path('activity/update/', views.update_activity, name='update_activity'),
    path('league/', include('leagues.urls')),
    path('', include(router.urls)),
    
    # Admin Dashboard Endpoints
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users_overview, name='admin_users_overview'),
    path('admin/courses/', views.admin_course_analytics, name='admin_course_analytics'),
    path('admin/revenue/', views.admin_revenue_report, name='admin_revenue_report'),
    path('admin/activity/', views.admin_user_activity, name='admin_user_activity'),
]
