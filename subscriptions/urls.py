from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),
] 