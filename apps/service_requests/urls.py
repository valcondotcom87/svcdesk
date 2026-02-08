from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.service_requests import viewsets as views

router = DefaultRouter()
router.register(r'service-requests', views.ServiceRequestViewSet, basename='servicerequest')
router.register(r'service-categories', views.ServiceCategoryViewSet, basename='servicecategory')
router.register(r'services', views.ServiceViewSet, basename='service')

urlpatterns = [
    path('', include(router.urls)),
]
