"""
Problem ViewSets - REST API viewsets for problem management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.problems.models import Problem, RootCauseAnalysis, KnownErrorDatabase as KEDB
from apps.problems.serializers import (
    ProblemListSerializer, ProblemDetailSerializer, ProblemCreateUpdateSerializer,
    RCASerializer, KEDBSerializer
)


class ProblemViewSet(viewsets.ModelViewSet):
    """ViewSet for problem management"""
    queryset = Problem.objects.filter(deleted_at__isnull=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'owner', 'category']
    search_fields = ['problem_number', 'title']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ProblemListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProblemCreateUpdateSerializer
        return ProblemDetailSerializer
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return Problem.objects.filter(deleted_at__isnull=True)
        return Problem.objects.filter(organization_id=user.organization_id, deleted_at__isnull=True)
    
    def perform_create(self, serializer):
        """Set organization and created_by"""
        serializer.save(organization=self.request.user.organization, created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_rca(self, request, pk=None):
        """Add root cause analysis to problem"""
        problem = self.get_object()
        
        rca_data = {
            'problem': problem.id,
            'investigation_summary': request.data.get('investigation_summary'),
            'root_cause': request.data.get('root_cause'),
            'contributing_factors': request.data.get('contributing_factors'),
            'analyzed_by': request.user.id
        }
        
        serializer = RCASerializer(data=rca_data)
        if serializer.is_valid():
            serializer.save()
            problem.investigation_status = 'completed'
            problem.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_kedb(self, request, pk=None):
        """Add known error to problem"""
        problem = self.get_object()
        
        kedb_data = {
            'problem': problem.id,
            'known_error_title': request.data.get('known_error_title'),
            'error_description': request.data.get('error_description'),
            'workaround': request.data.get('workaround'),
            'permanent_fix': request.data.get('permanent_fix')
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
    ordering = ['-analysis_date']


class KEDBViewSet(viewsets.ModelViewSet):
    """ViewSet for Known Error Database"""
    queryset = KEDB.objects.all()
    serializer_class = KEDBSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['problem']
    search_fields = ['known_error_title', 'error_description']
