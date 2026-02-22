"""
CORS and OPTIONS request handling middleware
Handles CORS preflight (OPTIONS) requests and applies CORS headers to all responses
"""
from django.http import HttpResponse


class CORSOptionsMiddleware:
    """
    Middleware to handle CORS preflight (OPTIONS) requests and apply CORS headers to all responses
    Must be placed early in the MIDDLEWARE list, before DjangoMiddleware
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract the origin from the request headers
        origin = request.META.get('HTTP_ORIGIN', '*')
        
        # Handle OPTIONS requests for CORS preflight
        if request.method == 'OPTIONS':
            response = HttpResponse(status=200)
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken'
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Max-Age'] = '3600'
            return response
        
        response = self.get_response(request)
        
        # Apply CORS headers to all responses
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken'
        response['Access-Control-Allow-Credentials'] = 'true'
        
        return response
