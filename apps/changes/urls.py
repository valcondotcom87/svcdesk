from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.changes import viewsets as views

router = DefaultRouter()
router.register(r'changes', views.ChangeViewSet, basename='change')

urlpatterns = [
    path('', include(router.urls)),
]
