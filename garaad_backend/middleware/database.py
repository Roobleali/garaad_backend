from django.db import connection

class DatabaseConnectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Close the database connection after each request
        connection.close()
        
        return response 