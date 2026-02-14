from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from apps.knowledge.models import KnowledgeArticle
from apps.core.permissions import HasPermission
from apps.knowledge.serializers import (
    KnowledgeArticleListSerializer,
    KnowledgeArticleDetailSerializer,
    KnowledgeArticleCreateUpdateSerializer,
)


class KnowledgeArticleViewSet(viewsets.ModelViewSet):
    """ViewSet for knowledge articles."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'owner']
    search_fields = ['title', 'summary', 'content', 'tags']
    ordering_fields = ['updated_at', 'title', 'status', 'version']
    ordering = ['-updated_at']

    def get_queryset(self):
        user = self.request.user
        queryset = KnowledgeArticle.objects.filter(deleted_at__isnull=True)

        if not user.is_authenticated:
            return queryset.filter(status='published')

        if user.is_superuser:
            return queryset

        return queryset.filter(organization_id=user.organization_id)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action == 'create':
            class CanCreateKnowledge(HasPermission):
                required_permission = 'knowledge.create'
            return [CanCreateKnowledge()]
        if self.action in ['update', 'partial_update', 'submit_review']:
            class CanUpdateKnowledge(HasPermission):
                required_permission = 'knowledge.update'
            return [CanUpdateKnowledge()]
        if self.action in ['publish', 'archive']:
            class CanPublishKnowledge(HasPermission):
                required_permission = 'knowledge.publish'
            return [CanPublishKnowledge()]
        if self.action == 'destroy':
            class CanDeleteKnowledge(HasPermission):
                required_permission = 'knowledge.delete'
            return [CanDeleteKnowledge()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'list':
            return KnowledgeArticleListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return KnowledgeArticleCreateUpdateSerializer
        return KnowledgeArticleDetailSerializer

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def submit_review(self, request, pk=None):
        article = self.get_object()
        if article.status not in ['draft', 'archived']:
            return Response(
                {'detail': 'Only draft or archived articles can be submitted for review.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        notes = str(request.data.get('notes', '') or '').strip()
        article.status = 'review'
        if notes:
            article.review_notes = notes
        article.updated_by = request.user
        article.save(update_fields=['status', 'review_notes', 'updated_by', 'updated_at'])
        return Response({'detail': 'Article submitted for review.'})

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        article = self.get_object()
        if article.status != 'review':
            return Response(
                {'detail': 'Only articles in review can be published.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not article.summary:
            return Response(
                {'detail': 'Summary is required before publishing.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not article.category:
            return Response(
                {'detail': 'Category is required before publishing.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not article.tags:
            return Response(
                {'detail': 'Tags are required before publishing.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not article.csf_function:
            return Response(
                {'detail': 'CSF function is required before publishing.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not article.iso_control:
            return Response(
                {'detail': 'ISO control is required before publishing.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not article.nist_control:
            return Response(
                {'detail': 'NIST control is required before publishing.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        notes = str(request.data.get('notes', '') or '').strip()
        article.status = 'published'
        article.published_at = timezone.now()
        if notes:
            article.review_notes = notes
        article.updated_by = request.user
        article.save(update_fields=['status', 'review_notes', 'published_at', 'updated_by', 'updated_at'])
        return Response({'detail': 'Article published.'})

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        article = self.get_object()
        if article.status != 'published':
            return Response(
                {'detail': 'Only published articles can be archived.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        notes = str(request.data.get('notes', '') or '').strip()
        article.status = 'archived'
        if notes:
            article.review_notes = notes
        article.updated_by = request.user
        article.save(update_fields=['status', 'review_notes', 'updated_by', 'updated_at'])
        return Response({'detail': 'Article archived.'})
