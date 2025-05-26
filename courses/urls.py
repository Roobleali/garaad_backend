from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, CourseViewSet, LessonViewSet,
    ProblemViewSet, UserProgressViewSet, CourseEnrollmentViewSet,
    LeaderboardViewSet, DailyChallengeViewSet, UserChallengeProgressViewSet,
    UserLevelViewSet, AchievementViewSet, UserAchievementViewSet,
    CulturalEventViewSet, UserCulturalProgressViewSet, CommunityContributionViewSet,
    LeagueViewSet, LessonContentBlockViewSet, UserRewardViewSet, UserNotificationViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'problems', ProblemViewSet)
router.register(r'user-progress', UserProgressViewSet)
router.register(r'enrollments', CourseEnrollmentViewSet)
router.register(r'leaderboard', LeaderboardViewSet)
router.register(r'daily-challenges', DailyChallengeViewSet)
router.register(r'challenge-progress', UserChallengeProgressViewSet)
router.register(r'user-levels', UserLevelViewSet)
router.register(r'achievements', AchievementViewSet)
router.register(r'user-achievements', UserAchievementViewSet)
router.register(r'cultural-events', CulturalEventViewSet)
router.register(r'cultural-progress', UserCulturalProgressViewSet)
router.register(r'community-contributions', CommunityContributionViewSet)
router.register(r'leagues', LeagueViewSet, basename='league')
router.register(r'lesson-content-blocks', LessonContentBlockViewSet)
router.register(r'user-rewards', UserRewardViewSet, basename='userreward')
router.register(r'notifications', UserNotificationViewSet, basename='usernotification')

urlpatterns = [
    path('', include(router.urls)),
]
