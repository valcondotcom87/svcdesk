from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.assets import viewsets as views

router = DefaultRouter()
router.register(r'asset-categories', views.AssetCategoryViewSet, basename='asset-category')
router.register(r'assets', views.AssetViewSet, basename='asset')
router.register(r'asset-depreciation', views.AssetDepreciationViewSet, basename='asset-depreciation')
router.register(r'asset-maintenance', views.AssetMaintenanceViewSet, basename='asset-maintenance')
router.register(r'asset-transfers', views.AssetTransferViewSet, basename='asset-transfer')

urlpatterns = [
    path('', include(router.urls)),
]
