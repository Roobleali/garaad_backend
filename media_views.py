from django.http import FileResponse, JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
import os
import mimetypes
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serve_media_file(request, file_path):
    """
    Serve media files with authentication
    URL pattern: /api/media/<path:file_path>
    """
    return _serve_file_internal(file_path)

def _serve_file_internal(file_path):
    """
    Internal helper to serve files
    """
    try:
        # Construct the full file path
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        # Security check - ensure the path is within MEDIA_ROOT
        media_root_abs = os.path.abspath(settings.MEDIA_ROOT)
        file_path_abs = os.path.abspath(full_path)
        
        if not file_path_abs.startswith(media_root_abs):
            logger.warning(f"Attempted directory traversal: {file_path}")
            return Response(
                {'error': 'Invalid file path'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if file exists
        if not os.path.exists(full_path):
            logger.info(f"File not found: {file_path}")
            return Response(
                {'error': 'File not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if it's actually a file (not a directory)
        if not os.path.isfile(full_path):
            logger.warning(f"Path is not a file: {file_path}")
            return Response(
                {'error': 'Invalid file path'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Determine content type based on file extension
        content_type, _ = mimetypes.guess_type(full_path)
        if not content_type:
            # Default content types for common file extensions
            ext = os.path.splitext(full_path)[1].lower()
            content_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
                '.svg': 'image/svg+xml',
                '.pdf': 'application/pdf',
                '.mp4': 'video/mp4',
                '.webm': 'video/webm',
                '.mp3': 'audio/mpeg',
                '.wav': 'audio/wav'
            }
            content_type = content_types.get(ext, 'application/octet-stream')
        
        # Get file size for headers
        file_size = os.path.getsize(full_path)
        
        # Create response with file
        response = FileResponse(open(full_path, 'rb'))
        response['Content-Type'] = content_type
        response['Content-Length'] = file_size
        
        # Cache headers for better performance
        # Cache for 1 year for images, 1 hour for other files
        if content_type.startswith('image/'):
            response['Cache-Control'] = 'public, max-age=31536000, immutable'
        else:
            response['Cache-Control'] = 'public, max-age=3600'
        
        # Add CORS headers if needed
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET'
        response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        
        return response
        
    except PermissionError:
        logger.error(f"Permission denied accessing file: {file_path}")
        return Response(
            {'error': 'Permission denied'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    except Exception as e:
        logger.error(f"Error serving file {file_path}: {str(e)}")
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Allow public access to profile pictures
def serve_profile_picture(request, filename):
    """
    Specific endpoint for profile pictures
    URL pattern: /api/media/profile_pics/<filename>
    """
    file_path = f"profile_pics/{filename}"
    return _serve_file_internal(file_path)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serve_community_post_image(request, filename):
    """
    Specific endpoint for community post images
    URL pattern: /api/media/community/posts/<filename>
    """
    file_path = f"community/posts/{filename}"
    return _serve_file_internal(file_path)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serve_course_image(request, filename):
    """
    Specific endpoint for course images
    URL pattern: /api/media/courses/<filename>
    """
    file_path = f"courses/{filename}"
    return _serve_file_internal(file_path)


# Health check endpoint for media serving
@api_view(['GET'])
def media_health_check(request):
    """
    Health check endpoint for media serving
    """
    try:
        # Check if MEDIA_ROOT exists and is accessible
        if not os.path.exists(settings.MEDIA_ROOT):
            return Response(
                {'status': 'error', 'message': 'MEDIA_ROOT does not exist'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Check if we can read from MEDIA_ROOT
        if not os.access(settings.MEDIA_ROOT, os.R_OK):
            return Response(
                {'status': 'error', 'message': 'Cannot read from MEDIA_ROOT'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'status': 'healthy',
            'media_root': settings.MEDIA_ROOT,
            'media_url': settings.MEDIA_URL,
            'message': 'Media serving is operational'
        })
        
    except Exception as e:
        logger.error(f"Media health check failed: {str(e)}")
        return Response(
            {'status': 'error', 'message': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 