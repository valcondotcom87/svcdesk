from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.problems import viewsets as views

router = DefaultRouter()
router.register(r'problems', views.ProblemViewSet, basename='problem')

urlpatterns = [
    path('', include(router.urls)),
]
