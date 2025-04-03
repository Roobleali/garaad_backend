from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# Simple hello world view


def hello_world(request):
    return HttpResponse("Hello, World!")


urlpatterns = [
    path('admin/', admin.site.urls),
    # Comment out or remove conflicting lines
    # path('accounts/', include('allauth.urls')),
    # Updated path to match frontend API calls
    path('api/', include('api.urls')),
    path('api/auth/', include('accounts.urls')),

    # Add hello-world endpoint
    path('hello-world/', hello_world, name='hello_world'),
]
