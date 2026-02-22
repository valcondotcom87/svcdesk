from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.notifications import views

router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'notification-templates', views.NotificationTemplateViewSet, basename='notificationtemplate')

urlpatterns = [
    path('', include(router.urls)),
]
