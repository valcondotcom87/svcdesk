"""
Core Middleware
"""
import logging
from threading import local
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)
_thread_locals = local()


def get_current_request():
    return getattr(_thread_locals, 'request', None)


def get_current_user():
    request = get_current_request()
    if not request or not hasattr(request, 'user'):
        return None
    if not request.user.is_authenticated:
        return None
    return request.user


class CurrentUserMiddleware(MiddlewareMixin):
    """Store current request for audit logging."""

    def process_request(self, request):
        _thread_locals.request = request
        return None

    def process_response(self, request, response):
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response

    def process_exception(self, request, exception):
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return None


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
