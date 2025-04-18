from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.db import connections
from django.db.utils import OperationalError

# Simple hello world view


def hello_world(request):
    return HttpResponse("Hello, World!")

# Health check view
def health_check(request):
    try:
        # Test database connection
        db_conn = connections['default']
        db_conn.cursor()
        
        return HttpResponse(
            "OK - Database connected",
            status=200,
            content_type="text/plain"
        )
    except OperationalError:
        return HttpResponse(
            "Database unavailable",
            status=500,
            content_type="text/plain"
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
    path('', health_check, name='health_check'),  # Root path for App Runner health check
    path('health/', health_check, name='health_check_alt'),
]
