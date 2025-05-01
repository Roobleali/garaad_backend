from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, CourseViewSet, LessonViewSet,
    LessonContentBlockViewSet, ProblemViewSet,
    UserProgressViewSet, UserRewardViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'content-blocks', LessonContentBlockViewSet)
router.register(r'problems', ProblemViewSet)
router.register(r'progress', UserProgressViewSet)
router.register(r'rewards', UserRewardViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
