from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.sla import views

router = DefaultRouter()
router.register(r'slas', views.SLAViewSet, basename='sla')
router.register(r'sla-targets', views.SLATargetViewSet, basename='slatarget')

urlpatterns = [
    path('', include(router.urls)),
]
