from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('signin/', views.SigninView.as_view(), name='signin'),
]
