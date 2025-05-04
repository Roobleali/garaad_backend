from django.urls import path
from . import views

urlpatterns = [
    path('signin/', views.custom_login, name='custom_login'),
    path('signup/', views.register_user, name='register_user'),
    path('profile/', views.user_profile, name='user_profile'),
    path('refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
]
