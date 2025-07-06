from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, create_subscription_order, waafi_webhook

# Create router for viewsets
router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional endpoints
    path('subscription/create/', create_subscription_order, name='create_subscription_order'),
    path('webhook/waafi/', waafi_webhook, name='waafi_webhook'),
] 