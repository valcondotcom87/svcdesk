"""
Core Middleware
"""
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests
    """
    
    def process_request(self, request):
        """
        Log request details
        """
        logger.info(
            f"Request: {request.method} {request.path} "
            f"from {request.META.get('REMOTE_ADDR')}"
        )
        return None
    
    def process_response(self, request, response):
        """
        Log response status
        """
        logger.info(
            f"Response: {request.method} {request.path} "
            f"Status: {response.status_code}"
        )
        return response


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to handle multi-tenancy
    Sets current organization based on request
    """
    
    def process_request(self, request):
        """
        Set current organization from request
        """
        # Get organization from user or header
        if hasattr(request, 'user') and request.user.is_authenticated:
            if hasattr(request.user, 'organization'):
                request.organization = request.user.organization
        
        return None
