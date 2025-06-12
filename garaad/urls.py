from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse, JsonResponse
from django.db import connections
from django.db.utils import OperationalError
from django.contrib.auth import get_user_model
import json

User = get_user_model()

# Simple hello world view

def hello_world(request):
    return HttpResponse("Hello, World!")

# Health check view
def health_check(request):
    """Health check endpoint for Railway"""
    try:
        # Check database connection
        db_conn = connections['default']
        db_conn.cursor()
        
        response_data = {
            "status": "healthy",
            "version": "1.0.0",
            "database": "connected"
        }
        return HttpResponse(
            json.dumps(response_data),
            status=200,
            content_type="application/json"
        )
    except OperationalError:
        response_data = {
            "status": "unhealthy",
            "version": "1.0.0",
            "database": "disconnected"
        }
        return HttpResponse(
            json.dumps(response_data),
            status=503,
            content_type="application/json"
        )
    except Exception as e:
        response_data = {
            "status": "unhealthy",
            "version": "1.0.0",
            "error": str(e)
        }
        return HttpResponse(
            json.dumps(response_data),
            status=500,
            content_type="application/json"
        )

# Temporary password reset view
def reset_admin_password(request):
    try:
        user = User.objects.get(email='info@garaad.org')
        user.set_password('new_admin_password_123')
        user.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Password has been reset to: new_admin_password_123'
        })
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Comment out or remove conflicting lines
    # path('accounts/', include('allauth.urls')),
    # Updated path to match frontend API calls
    path('api/', include('api.urls')),
    path('api/auth/', include('accounts.urls')),
    # Learning Management System API
    path('api/lms/', include('courses.urls')),
    # League and Gamification API
    path('api/leagues/', include('leagues.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),

    # Add hello-world endpoint
    path('hello-world/', hello_world, name='hello_world'),
    path('health/', health_check, name='health_check'),
    path('reset-password/', reset_admin_password, name='reset_admin_password'),
    path('', health_check, name='health_check_root'),
]
