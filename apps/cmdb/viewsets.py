"""
CMDB ViewSets - REST API viewsets for configuration management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.cmdb.models import CICategory, ConfigurationItem as CI, CIAttribute, CIRelationship
from apps.cmdb.serializers import (
    CICategorySerializer, CIListSerializer, CIDetailSerializer,
    CICreateUpdateSerializer, CIAttributeSerializer, CIRelationshipSerializer
)


class CICategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for CI categories"""
    queryset = CICategory.objects.all()
    serializer_class = CICategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']


class CIViewSet(viewsets.ModelViewSet):
    """ViewSet for configuration items"""
    queryset = CI.objects.filter(deleted_at__isnull=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'category', 'status', 'owner']
    search_fields = ['name', 'serial_number', 'asset_tag']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
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


class CIAttributeValueViewSet(viewsets.ModelViewSet):
    """ViewSet for CI attribute values (uses CIAttribute model)"""
    queryset = CIAttribute.objects.all()
    serializer_class = CIAttributeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ci']
    ordering = ['id']


class CIRelationshipViewSet(viewsets.ModelViewSet):
    """ViewSet for CI relationships"""
    queryset = CIRelationship.objects.all()
    serializer_class = CIRelationshipSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['source_ci', 'target_ci', 'relationship_type']
    ordering = ['id']
