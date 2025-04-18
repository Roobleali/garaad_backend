from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.db import connections
from django.db.utils import OperationalError
import json

# Simple hello world view

def hello_world(request):
    return HttpResponse("Hello, World!")

# Health check view
def health_check(request):
    """Health check endpoint for App Runner"""
    response_data = {
        "status": "healthy",
        "version": "1.0.0"
    }
    return HttpResponse(
        json.dumps(response_data),
        status=200,
        content_type="application/json"
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    # Comment out or remove conflicting lines
    # path('accounts/', include('allauth.urls')),
    # Updated path to match frontend API calls
    path('api/', include('api.urls')),
    path('api/auth/', include('accounts.urls')),
    # Learning Management System API
    path('api/lms/', include('courses.urls')),

    # Add hello-world endpoint
    path('hello-world/', hello_world, name='hello_world'),
    path('', health_check, name='health_check'),
    path('health/', health_check, name='health_check_alt'),
]
