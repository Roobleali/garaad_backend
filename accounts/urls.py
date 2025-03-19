from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # rJWT authentication endpoints
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.EmailTokenObtainPairView.as_view(), name='login'),
    path('refresh/', views.CustomTokenRefreshView.as_view(), name='refresh'),
    path('profile/', views.profile_view, name='profile'),
    
    # Student profile endpoint
    path('student/register/', views.student_registration, name='student_registration'),

    # Onboarding endpoints
    path('onboarding/status/', views.onboarding_status, name='onboarding_status'),
    path('onboarding/complete/', views.complete_onboarding, name='complete_onboarding'),
]
