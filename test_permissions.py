#!/usr/bin/env python
"""
Test script to verify community permissions work correctly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from rest_framework.test import force_authenticate
from community.views import PostViewSet
from community.permissions import CanCreateContent
import uuid

User = get_user_model()

def test_permissions():
    """Test that permissions work correctly"""
    print("Testing community permissions...")
    
    # Create a test user with unique username
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    user, created = User.objects.get_or_create(
        email=f'{unique_username}@example.com',
        defaults={
            'username': unique_username,
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    print(f"Using test user: {user.username}")
    
    # Create request factory
    factory = RequestFactory()
    
    # Test POST request to create post
    request = factory.post('/api/community/posts/', {
        'title': 'Test Post',
        'content': 'This is a test post content',
        'room_id': 1,
        'language': 'so',
        'post_type': 'text'
    })
    
    # Authenticate the request
    force_authenticate(request, user=user)
    
    # Ensure request.user is set
    request.user = user
    
    # Test permission
    permission = CanCreateContent()
    has_permission = permission.has_permission(request, None)
    
    print(f"User authenticated: {request.user.is_authenticated}")
    print(f"Has permission to create post: {has_permission}")
    
    if has_permission:
        print("✅ Permission test PASSED - Users can now create posts!")
    else:
        print("❌ Permission test FAILED")
    
    return has_permission

if __name__ == '__main__':
    test_permissions() 