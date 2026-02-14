"""
CMDB ViewSets - REST API viewsets for configuration management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.cmdb.models import CICategory, ConfigurationItem as CI, CIAttribute, CIRelationship
from apps.organizations.models import Organization
from apps.cmdb.serializers import (
    CICategorySerializer, CIListSerializer, CIDetailSerializer,
    CICreateUpdateSerializer, CIAttributeSerializer, CIRelationshipSerializer
)
from apps.core.permissions import permission_required


class CICategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for CI categories"""
    queryset = CICategory.objects.all()
    serializer_class = CICategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']

    def get_permissions(self):
        action_map = {
            'list': 'cmdb.view',
            'retrieve': 'cmdb.view',
            'create': 'cmdb.update',
            'update': 'cmdb.update',
            'partial_update': 'cmdb.update',
            'destroy': 'cmdb.update',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Set organization when creating a CI category"""
        if self.request.user.organization:
            serializer.save(organization=self.request.user.organization)
        else:
            serializer.save()


class CIViewSet(viewsets.ModelViewSet):
    """ViewSet for configuration items"""
    queryset = CI.objects.filter(deleted_at__isnull=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'category', 'status', 'owner_team']
    search_fields = ['name', 'serial_number']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_permissions(self):
        action_map = {
            'list': 'cmdb.view',
            'retrieve': 'cmdb.view',
            'create': 'cmdb.create',
            'update': 'cmdb.update',
            'partial_update': 'cmdb.update',
            'destroy': 'cmdb.update',
            'add_attribute': 'cmdb.update',
            'relationships': 'cmdb.view',
            'add_relationship': 'cmdb.relationship',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return CIListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CICreateUpdateSerializer
        return CIDetailSerializer
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return CI.objects.all()
        return CI.objects.filter(organization_id=user.organization_id, deleted_at__isnull=True)

    def perform_create(self, serializer):
        """Set organization and created_by when creating a CI"""
        user = self.request.user
        organization = user.organization if hasattr(user, 'organization') else None
        if user.is_superuser and not organization:
            organization = Organization.objects.filter(is_active=True).first()
        serializer.save(
            organization=organization,
            created_by=user
        )
    
    @action(detail=True, methods=['post'])
    def add_attribute(self, request, pk=None):
        """Add attribute value to CI"""
        ci = self.get_object()
        attribute_id = request.data.get('attribute_id')
        value = request.data.get('value')
        
        try:
            attribute = CIAttribute.objects.get(id=attribute_id)
            attribute.attribute_value = value
            attribute.save()

            serializer = CIAttributeSerializer(attribute)
            return Response(serializer.data)
        except CIAttribute.DoesNotExist:
            return Response({'error': 'Attribute not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def relationships(self, request, pk=None):
        """Get all relationships for a CI"""
        ci = self.get_object()
        relationships = ci.outgoing_relationships.all()
        serializer = CIRelationshipSerializer(relationships, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_relationship(self, request, pk=None):
        """Add relationship to another CI"""
        ci = self.get_object()
        target_ci_id = request.data.get('target_ci_id')
        relationship_type = request.data.get('relationship_type')
        description = request.data.get('description', '')
        
        try:
            relationship = CIRelationship.objects.create(
                source_ci=ci,
                target_ci_id=target_ci_id,
                relationship_type=relationship_type
            )
            serializer = CIRelationshipSerializer(relationship)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CIAttributeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for CI attributes"""
    queryset = CIAttribute.objects.all()
    serializer_class = CIAttributeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['ci']
    search_fields = ['attribute_name']

    def get_permissions(self):
        action_map = {
            'list': 'cmdb.view',
            'retrieve': 'cmdb.view',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]


class CIAttributeValueViewSet(viewsets.ModelViewSet):
    """ViewSet for CI attribute values (uses CIAttribute model)"""
    queryset = CIAttribute.objects.all()
    serializer_class = CIAttributeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ci']
    ordering = ['id']

    def get_permissions(self):
        action_map = {
            'list': 'cmdb.view',
            'retrieve': 'cmdb.view',
            'create': 'cmdb.update',
            'update': 'cmdb.update',
            'partial_update': 'cmdb.update',
            'destroy': 'cmdb.update',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]


class CIRelationshipViewSet(viewsets.ModelViewSet):
    """ViewSet for CI relationships"""
    queryset = CIRelationship.objects.all()
    serializer_class = CIRelationshipSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['source_ci', 'target_ci', 'relationship_type']
    ordering = ['id']

    def get_permissions(self):
        action_map = {
            'list': 'cmdb.view',
            'retrieve': 'cmdb.view',
            'create': 'cmdb.relationship',
            'update': 'cmdb.relationship',
            'partial_update': 'cmdb.relationship',
            'destroy': 'cmdb.relationship',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        organization = user.organization if hasattr(user, 'organization') else None
        if user.is_superuser and not organization:
            organization = Organization.objects.filter(is_active=True).first()
        serializer.save(organization=organization)
