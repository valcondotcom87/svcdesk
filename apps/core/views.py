"""
Core Views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API root endpoint
    Returns available endpoints and API information
    """
    return Response({
        'name': 'ITSM API v1',
        'description': 'IT Service Management System API - ITIL v4 Compliant',
        'version': '1.0.0',
        'endpoints': {
            'health': request.build_absolute_uri('/api/v1/health/'),
            'compliance': {
                'frameworks': request.build_absolute_uri('/api/v1/compliance/frameworks/'),
                'requirements': request.build_absolute_uri('/api/v1/compliance/requirements/'),
                'audit-logs': request.build_absolute_uri('/api/v1/compliance/audit-logs/'),
                'incident-plans': request.build_absolute_uri('/api/v1/compliance/incident-plans/'),
                'vulnerabilities': request.build_absolute_uri('/api/v1/compliance/vulnerabilities/'),
                'checkpoints': request.build_absolute_uri('/api/v1/compliance/checkpoints/'),
            },
            'auth': {
                'login': request.build_absolute_uri('/api/v1/auth/login/'),
                'logout': request.build_absolute_uri('/api/v1/auth/logout/'),
                'token-refresh': request.build_absolute_uri('/api/v1/auth/token/refresh/'),
            }
        },
        'documentation': {
            'swagger': request.build_absolute_uri('/api/docs/'),
            'redoc': request.build_absolute_uri('/api/redoc/'),
            'schema': request.build_absolute_uri('/api/schema/'),
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint
    Returns system health status
    """
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return Response({
            'status': 'healthy',
            'database': 'connected',
            'message': 'ITSM System is running'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
