from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import SignupView, SigninView

router = DefaultRouter()
router.register(r'gamification', views.GamificationViewSet, basename='gamification')

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/signin/', SigninView.as_view(), name='signin'),
    path('streaks/', views.streak_view, name='streaks'),
    path('league/', include('leagues.urls')),
    path('', include(router.urls)),
]
