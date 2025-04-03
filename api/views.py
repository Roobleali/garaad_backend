from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def api_root(request):
    """
    API root view that provides information about available endpoints.
    """
    return Response({
        'status': 'online',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth/',
            'hello': '/hello-world/',
        }
    }, status=status.HTTP_200_OK)
