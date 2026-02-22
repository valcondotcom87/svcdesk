"""
Core Custom Exceptions
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF
    Returns consistent error response format
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the response format
        custom_response_data = {
            'success': False,
            'error': {
                'code': exc.__class__.__name__,
                'message': str(exc),
                'details': response.data if isinstance(response.data, dict) else {'detail': response.data}
            }
        }
        response.data = custom_response_data
    
    return response


class ITSMException(Exception):
    """Base exception for ITSM application"""
    pass


class SLABreachException(ITSMException):
    """Raised when SLA is breached"""
    pass


class WorkflowException(ITSMException):
    """Raised when workflow execution fails"""
    pass


class ValidationException(ITSMException):
    """Raised when validation fails"""
    pass
