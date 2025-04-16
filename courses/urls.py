from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, CourseViewSet, ModuleViewSet, LessonViewSet,
    LessonContentBlockViewSet, ProblemViewSet, PracticeSetViewSet,
    PracticeSetProblemViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'modules', ModuleViewSet, basename='module')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'content-blocks', LessonContentBlockViewSet,
                basename='content-block')
router.register(r'problems', ProblemViewSet, basename='problem')
router.register(r'practice-sets', PracticeSetViewSet, basename='practice-set')
router.register(r'practice-set-problems',
                PracticeSetProblemViewSet, basename='practice-set-problem')

urlpatterns = [
    path('', include(router.urls)),
]
