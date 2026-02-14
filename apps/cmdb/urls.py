from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.cmdb import viewsets as views

router = DefaultRouter()
router.register(r'config-items', views.CIViewSet, basename='configurationitem')
router.register(r'ci-categories', views.CICategoryViewSet, basename='cicategory')
router.register(r'ci-relationships', views.CIRelationshipViewSet, basename='cirelationship')

urlpatterns = [
    path('', include(router.urls)),
]
