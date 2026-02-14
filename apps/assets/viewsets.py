"""
Asset Management ViewSets - REST API viewsets for asset lifecycle management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from apps.assets.models import (
    Asset, AssetCategory, AssetDepreciation, AssetMaintenance, AssetTransfer
)
from apps.assets.serializers import (
    AssetCategorySerializer, AssetListSerializer, AssetDetailSerializer,
    AssetCreateUpdateSerializer, AssetDepreciationSerializer,
    AssetMaintenanceSerializer, AssetTransferSerializer
)
from apps.organizations.models import Organization
from apps.users.models import User
from apps.core.permissions import permission_required


class AssetCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for asset categories"""
    queryset = AssetCategory.objects.filter(is_active=True)
    serializer_class = AssetCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']

    def get_permissions(self):
        action_map = {
            'list': 'assets.view',
            'retrieve': 'assets.view',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]


class AssetViewSet(viewsets.ModelViewSet):
    """ViewSet for assets"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'category', 'status', 'current_owner']
    search_fields = ['asset_tag', 'name', 'serial_number']
    ordering_fields = ['name', 'purchase_date', 'cost']
    ordering = ['name']

    def get_permissions(self):
        action_map = {
            'list': 'assets.view',
            'retrieve': 'assets.view',
            'create': 'assets.create',
            'update': 'assets.update',
            'partial_update': 'assets.update',
            'destroy': 'assets.update',
            'transfer': 'assets.transfer',
            'record_maintenance': 'assets.maintenance',
            'transfer_history': 'assets.view',
            'maintenance_history': 'assets.view',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return AssetListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AssetCreateUpdateSerializer
        return AssetDetailSerializer
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return Asset.objects.filter(deleted_at__isnull=True)
        return Asset.objects.filter(organization_id=user.organization_id, deleted_at__isnull=True)
    
    def perform_create(self, serializer):
        """Set organization"""
        organization = self._resolve_organization()
        if not organization:
            raise ValidationError({'organization': 'User does not belong to an organization.'})
        serializer.save(organization=organization)

    def _resolve_organization(self):
        user = self.request.user
        user_org = getattr(user, 'organization', None)
        if user_org:
            matched = Organization.objects.filter(name=user_org.name).first()
            if matched:
                return matched
        if user.is_superuser:
            return Organization.objects.filter(is_active=True).first()
        return None
    
    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        """Transfer asset to another user"""
        asset = self.get_object()
        to_user_id = request.data.get('to_user_id')
        transfer_notes = request.data.get('transfer_notes', '')
        
        try:
            to_user = User.objects.get(id=to_user_id)
            
            transfer = AssetTransfer.objects.create(
                asset=asset,
                from_user=asset.current_owner,
                to_user=to_user,
                transfer_date=timezone.now(),
                transfer_notes=transfer_notes
            )
            
            asset.current_owner = to_user
            asset.save()
            
            serializer = AssetTransferSerializer(transfer)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def record_maintenance(self, request, pk=None):
        """Record maintenance for asset"""
        asset = self.get_object()
        
        maintenance_data = {
            'asset': asset.id,
            'maintenance_type': request.data.get('maintenance_type'),
            'description': request.data.get('description'),
            'cost': request.data.get('cost'),
            'performed_by': request.user.id,
            'maintenance_date': request.data.get('maintenance_date'),
            'next_due': request.data.get('next_due')
        }
        
        serializer = AssetMaintenanceSerializer(data=maintenance_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def transfer_history(self, request, pk=None):
        """Get transfer history for asset"""
        asset = self.get_object()
        transfers = asset.assettransfer_set.all()
        serializer = AssetTransferSerializer(transfers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def maintenance_history(self, request, pk=None):
        """Get maintenance history for asset"""
        asset = self.get_object()
        maintenance = asset.assetmaintenance_set.all()
        serializer = AssetMaintenanceSerializer(maintenance, many=True)
        return Response(serializer.data)


class AssetDepreciationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for asset depreciation"""
    queryset = AssetDepreciation.objects.all()
    serializer_class = AssetDepreciationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['asset', 'depreciation_method']
    ordering = ['-last_calculated_at']

    def get_permissions(self):
        action_map = {
            'list': 'assets.view',
            'retrieve': 'assets.view',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]


class AssetMaintenanceViewSet(viewsets.ModelViewSet):
    """ViewSet for asset maintenance"""
    queryset = AssetMaintenance.objects.all()
    serializer_class = AssetMaintenanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['asset', 'maintenance_type', 'performed_by']
    ordering = ['-maintenance_date']

    def get_permissions(self):
        action_map = {
            'list': 'assets.view',
            'retrieve': 'assets.view',
            'create': 'assets.maintenance',
            'update': 'assets.maintenance',
            'partial_update': 'assets.maintenance',
            'destroy': 'assets.maintenance',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]


class AssetTransferViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing asset transfers"""
    queryset = AssetTransfer.objects.all()
    serializer_class = AssetTransferSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['asset', 'from_user', 'to_user']
    ordering = ['-transfer_date']

    def get_permissions(self):
        action_map = {
            'list': 'assets.view',
            'retrieve': 'assets.view',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]
