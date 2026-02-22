from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.knowledge import viewsets as views

router = DefaultRouter()
router.register(r'articles', views.KnowledgeArticleViewSet, basename='knowledge-article')

urlpatterns = [
    path('', include(router.urls)),
]
