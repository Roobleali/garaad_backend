from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from api.views import SignupView, SigninView

urlpatterns = [
    # Authentication endpoints
    path('signup/', SignupView.as_view(), name='auth_signup'),
    path('signin/', SigninView.as_view(), name='auth_signin'),

    # JWT refresh endpoint
    path('refresh/', views.CustomTokenRefreshView.as_view(), name='refresh'),
    path('profile/', views.profile_view, name='profile'),

    # Student profile endpoint
    path('student/register/', views.student_registration,
         name='student_registration'),
]
