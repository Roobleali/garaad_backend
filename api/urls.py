from django.urls import path
from . import views
from .views import SignupView, SigninView

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/signin/', SigninView.as_view(), name='signin'),
    path('streaks/', views.streak_view, name='streaks'),
]
