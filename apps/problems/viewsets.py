"""
Problem ViewSets - REST API viewsets for problem management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from apps.problems.models import Problem, RootCauseAnalysis, KnownErrorDatabase as KEDB
from apps.problems.serializers import (
    ProblemListSerializer, ProblemDetailSerializer, ProblemCreateUpdateSerializer,
    RCASerializer, KEDBSerializer
)
from apps.organizations.models import Organization
from apps.core.permissions import permission_required


class ProblemViewSet(viewsets.ModelViewSet):
    """ViewSet for problem management"""
    queryset = Problem.objects.filter(deleted_at__isnull=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'owner', 'category']
    search_fields = ['ticket_number', 'title', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_permissions(self):
        action_map = {
            'list': 'problems.view',
            'retrieve': 'problems.view',
            'create': 'problems.create',
            'update': 'problems.update',
            'partial_update': 'problems.update',
            'destroy': 'problems.update',
            'add_rca': 'problems.add_rca',
            'add_kedb': 'problems.add_kedb',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProblemListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ProblemCreateUpdateSerializer
        return ProblemDetailSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Problem.objects.filter(deleted_at__isnull=True)

        if user.is_superuser:
            return queryset

        queryset = queryset.filter(organization_id=user.organization_id)

        if user.role == 'end_user':
            return queryset.filter(Q(owner=user) | Q(created_by=user))

        return queryset

    def get_object(self):
        problem = super().get_object()
        user = self.request.user

        if not user.is_superuser and user.role == 'end_user':
            if problem.owner_id != user.id and problem.created_by_id != user.id:
                raise PermissionDenied('End users can only access their own problems.')

        return problem

    def perform_create(self, serializer):
        organization = self._resolve_organization()
        if not organization:
            raise ValidationError({'organization': 'User does not belong to an organization.'})
        owner = serializer.validated_data.get('owner') or self.request.user
        serializer.save(organization=organization, owner=owner, created_by=self.request.user)

    def _resolve_organization(self):
        user = self.request.user
        user_org = getattr(user, 'organization', None)
        if user_org:
            matched = Organization.objects.filter(name=user_org.name).first()
            if matched:
                return matched
        if user.is_superuser:
            return Organization.objects.filter(is_active=True).first()
        return None

    @action(detail=True, methods=['post'])
    def add_rca(self, request, pk=None):
        """Add root cause analysis to problem"""
        problem = self.get_object()

        rca_data = {
            'problem': problem.id,
            'investigation_method': request.data.get('investigation_method', ''),
            'five_whys': request.data.get('five_whys', ''),
            'contributing_factors': request.data.get('contributing_factors', ''),
            'lessons_learned': request.data.get('lessons_learned', '')
        }

        serializer = RCASerializer(data=rca_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_kedb(self, request, pk=None):
        """Add known error to problem"""
        problem = self.get_object()

        kedb_data = {
            'organization': problem.organization_id,
            'problem': problem.id,
            'title': request.data.get('title', problem.title),
            'description': request.data.get('description', problem.description),
            'error_code': request.data.get('error_code', f"KEDB-{problem.ticket_number}"),
            'symptoms': request.data.get('symptoms', ''),
            'workaround': request.data.get('workaround', ''),
            'permanent_solution': request.data.get('permanent_solution', '')
        }

        serializer = KEDBSerializer(data=kedb_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RCAViewSet(viewsets.ModelViewSet):
    """ViewSet for Root Cause Analysis"""
    queryset = RootCauseAnalysis.objects.all()
    serializer_class = RCASerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['problem']
    ordering = ['-created_at']

    def get_permissions(self):
        action_map = {
            'list': 'problems.view',
            'retrieve': 'problems.view',
            'create': 'problems.add_rca',
            'update': 'problems.add_rca',
            'partial_update': 'problems.add_rca',
            'destroy': 'problems.add_rca',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]


class KEDBViewSet(viewsets.ModelViewSet):
    """ViewSet for Known Error Database"""
    queryset = KEDB.objects.all()
    serializer_class = KEDBSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['problem']
    search_fields = ['title', 'description', 'error_code']

    def get_permissions(self):
        action_map = {
            'list': 'problems.view',
            'retrieve': 'problems.view',
            'create': 'problems.add_kedb',
            'update': 'problems.add_kedb',
            'partial_update': 'problems.add_kedb',
            'destroy': 'problems.add_kedb',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]
