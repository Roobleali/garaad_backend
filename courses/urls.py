from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, CourseViewSet, LessonViewSet,
    LessonContentBlockViewSet, ProblemViewSet,
    PracticeSetViewSet, PracticeSetProblemViewSet,
    UserProgressViewSet, CourseEnrollmentViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'lesson-content-blocks', LessonContentBlockViewSet, basename='lesson-content-block')
router.register(r'problems', ProblemViewSet, basename='problem')
router.register(r'practice-sets', PracticeSetViewSet, basename='practice-set')
router.register(r'practice-set-problems', PracticeSetProblemViewSet, basename='practice-set-problem')
router.register(r'user-progress', UserProgressViewSet, basename='user-progress')
router.register(r'enrollments', CourseEnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
]
