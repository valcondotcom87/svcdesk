from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.reports import views

router = DefaultRouter()
router.register(r'reports', views.ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]
