"""
ITSM Project URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from apps.core import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API Documentation Schema
schema_view = get_schema_view(
    openapi.Info(
        title="ITSM API",
        default_version='v1',
        description="IT Service Management System API - ITIL v4 Compliant",
        terms_of_service="https://www.itsm.com/terms/",
        contact=openapi.Contact(email="api@itsm.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[],  # Will be updated to include specific patterns below
)

# Fallback schema view for compatibility - returns minimal schema
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def minimal_schema_view(request):
    """Minimal schema endpoint for API documentation compatibility."""
    schema = {
        "swagger": "2.0",
        "info": {
            "title": "ITSM API",
            "version": "v1",
            "description": "IT Service Management System API - ITIL v4 Compliant",
            "contact": {"email": "api@itsm.com"},
            "license": {"name": "MIT License"}
        },
        "paths": {
            "/api/v1/health/": {
                "get": {
                    "summary": "Health Check",
                    "responses": {"200": {"description": "System is healthy"}}
                }
            },
            "/api/v1/compliance/frameworks/": {
                "get": {
                    "summary": "List Compliance Frameworks",
                    "responses": {"200": {"description": "List of frameworks"}}
                }
            }
        }
    }
    return Response(schema)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Authentication
    path('api/v1/auth/', include('itsm_api.auth_urls')),
    
    # API v1
    path('api/v1/', include([
        # Root endpoint
        path('', views.api_root, name='api-root'),
        
        # Core modules
        path('organizations/', include('apps.organizations.urls')),
        path('incidents/', include('apps.incidents.urls')),
        path('service-requests/', include('apps.service_requests.urls')),
        path('problems/', include('apps.problems.urls')),
        path('changes/', include('apps.changes.urls')),
        path('cmdb/', include('apps.cmdb.urls')),
        path('assets/', include('apps.assets.urls')),
        path('sla/', include('apps.sla.urls')),
        path('knowledge/', include('apps.knowledge.urls')),
        
        # User Management (Users, Teams, Organizations, Roles)
        path('', include('apps.users.urls')),
        path('workflows/', include('apps.workflows.urls')),
        # path('notifications/', include('apps.notifications.urls')),
        # path('reports/', include('apps.reports.urls')),
        path('audit/', include('apps.audit.urls')),
        path('compliance/', include('apps.compliance.urls')),  # Compliance Module (Phase 4)
        
        # Health check
        path('health/', include('apps.core.urls')),
    ])),
    
    # API Documentation (Swagger) - Using fallback minimal schema
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', minimal_schema_view, name='schema-json'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# Custom admin site configuration
admin.site.site_header = "ITSM Administration"
admin.site.site_title = "ITSM Admin Portal"
admin.site.index_title = "Welcome to ITSM Administration"
