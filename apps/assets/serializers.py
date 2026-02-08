"""
Asset Management Serializers - REST API serializers for asset lifecycle management
"""
from rest_framework import serializers
from apps.assets.models import (
    Asset, AssetCategory, AssetDepreciation, AssetMaintenance, AssetTransfer
)


class AssetCategorySerializer(serializers.ModelSerializer):
    """Serializer for asset categories"""
    asset_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AssetCategory
        fields = ['id', 'name', 'description', 'asset_count', 'is_active']
    
    def get_asset_count(self, obj):
        return obj.asset_set.count()


class AssetDepreciationSerializer(serializers.ModelSerializer):
    """Serializer for asset depreciation"""
    class Meta:
        model = AssetDepreciation
        fields = [
            'id', 'asset', 'depreciation_method', 'useful_life_years',
            'current_value', 'accumulated_depreciation', 'residual_value',
            'last_calculated_at'
        ]


class AssetMaintenanceSerializer(serializers.ModelSerializer):
    """Serializer for asset maintenance"""
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    
    class Meta:
        model = AssetMaintenance
        fields = [
            'id', 'asset', 'maintenance_type', 'description', 'cost',
            'performed_by', 'performed_by_name', 'maintenance_date', 'next_due'
        ]


class AssetTransferSerializer(serializers.ModelSerializer):
    """Serializer for asset transfers"""
    from_user_name = serializers.CharField(source='from_user.get_full_name', read_only=True)
    to_user_name = serializers.CharField(source='to_user.get_full_name', read_only=True)
    
    class Meta:
        model = AssetTransfer
        fields = [
            'id', 'asset', 'from_user', 'from_user_name', 'to_user',
            'to_user_name', 'transfer_date', 'transfer_notes'
        ]


class AssetListSerializer(serializers.ModelSerializer):
    """Lightweight asset list serializer"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Asset
        fields = [
            'id', 'asset_tag', 'name', 'category', 'category_name',
            'status', 'status_display', 'current_owner', 'purchase_date'
        ]


class AssetDetailSerializer(serializers.ModelSerializer):
    """Full asset detail serializer with nested relations"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    owner_name = serializers.CharField(source='current_owner.get_full_name', read_only=True)
    
    # Nested serializers
    depreciation = AssetDepreciationSerializer(read_only=True, source='assetdepreciation')
    maintenance = AssetMaintenanceSerializer(many=True, read_only=True, source='assetmaintenance_set')
    transfers = AssetTransferSerializer(many=True, read_only=True, source='assettransfer_set')
    
    class Meta:
        model = Asset
        fields = [
            'id', 'organization', 'asset_tag', 'name', 'description',
            'category', 'category_name', 'status', 'status_display',
            'current_owner', 'owner_name', 'location', 'purchase_date',
            'cost', 'warranty_expires', 'depreciation', 'maintenance', 'transfers',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AssetCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating assets"""
    class Meta:
        model = Asset
        fields = [
            'name', 'description', 'category', 'current_owner', 'location',
            'purchase_date', 'cost', 'warranty_expires'
        ]
