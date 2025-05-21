from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'courses', views.CourseViewSet)
router.register(r'lessons', views.LessonViewSet)
router.register(r'problems', views.ProblemViewSet)
router.register(r'progress', views.UserProgressViewSet, basename='progress')
router.register(r'enrollments', views.CourseEnrollmentViewSet, basename='enrollment')
router.register(r'rewards', views.UserRewardViewSet, basename='reward')
router.register(r'leaderboard', views.LeaderboardViewSet, basename='leaderboard')
router.register(r'challenges', views.DailyChallengeViewSet, basename='challenge')
router.register(r'levels', views.UserLevelViewSet, basename='level')
router.register(r'achievements', views.AchievementViewSet, basename='achievement')
router.register(r'cultural-events', views.CulturalEventViewSet, basename='cultural-event')
router.register(r'contributions', views.CommunityContributionViewSet, basename='contribution')

urlpatterns = [
    path('', include(router.urls)),
]
