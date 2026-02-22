from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.organizations import viewsets as views

router = DefaultRouter()
router.register(r'departments', views.DepartmentViewSet, basename='department')
router.register(r'department-members', views.DepartmentMemberViewSet, basename='departmentmember')
router.register(r'module-categories', views.ModuleCategoryViewSet, basename='module-category')

urlpatterns = [
    path('', include(router.urls)),
]
