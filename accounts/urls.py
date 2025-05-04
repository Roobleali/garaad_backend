from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('login/', views.custom_login, name='custom_login'),
    path('signup/', csrf_exempt(views.signup_view), name='signup'),
    path('profile/', views.profile_view, name='profile'),
    path('student-registration/', views.student_registration, name='student_registration'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('onboarding/status/', views.onboarding_status, name='onboarding_status'),
    path('onboarding/complete/', views.complete_onboarding, name='complete_onboarding'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
]
