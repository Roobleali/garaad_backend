from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Comment out or remove conflicting lines
    # path('accounts/', include('allauth.urls')),
    path('api/auth/', include('accounts.urls')),  # Updated path to match frontend API calls
]