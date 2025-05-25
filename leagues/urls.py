from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'leagues', views.LeagueViewSet, basename='league')

urlpatterns = [
    path('', include(router.urls)),
] 