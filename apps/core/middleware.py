"""
Core Middleware
"""
import logging
import uuid
from threading import local
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)
_thread_locals = local()


def get_current_request():
    return getattr(_thread_locals, 'request', None)


def get_request_id():
    return getattr(_thread_locals, 'request_id', None)


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
        if hasattr(_thread_locals, 'request_id'):
            del _thread_locals.request_id
        return response

    def process_exception(self, request, exception):
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        if hasattr(_thread_locals, 'request_id'):
            del _thread_locals.request_id
        return None


class RequestIdMiddleware(MiddlewareMixin):
    """Attach a request id to each request for traceability."""

    def process_request(self, request):
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        _thread_locals.request_id = request_id
        request.request_id = request_id
        return None

    def process_response(self, request, response):
        request_id = getattr(request, 'request_id', None) or get_request_id()
        if request_id:
            response['X-Request-ID'] = request_id
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests
    """
    
    def process_request(self, request):
        """
        Log request details
        """
        request_id = getattr(request, 'request_id', None) or get_request_id()
        logger.info(
            "Request received",
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.path,
                'remote_addr': request.META.get('REMOTE_ADDR'),
            }
        )
        return None
    
    def process_response(self, request, response):
        """
        Log response status
        """
        request_id = getattr(request, 'request_id', None) or get_request_id()
        logger.info(
            "Response sent",
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
            }
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
