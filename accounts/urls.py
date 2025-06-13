from django.urls import path
from . import views

urlpatterns = [
    path('signin/', views.custom_login, name='custom_login'),
    path('signup/', views.register_user, name='register_user'),
    path('profile/', views.user_profile, name='user_profile'),
    path('update-premium/', views.update_premium_status, name='update_premium_status'),
    path('refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification_email'),
]
