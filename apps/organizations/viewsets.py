"""
Organizations ViewSets
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions import HasPermission
from django_filters.rest_framework import DjangoFilterBackend

from apps.organizations.models import Department, DepartmentMember, ModuleCategory
from apps.organizations.serializers import DepartmentSerializer, DepartmentMemberSerializer, ModuleCategorySerializer


class CanManageCategories(HasPermission):
    required_permission = 'categories.manage'


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for departments"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'parent']
    search_fields = ['name', 'description']
    ordering = ['name']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Department.objects.all()
        if user.organization_id:
            return Department.objects.filter(organization_id=user.organization_id)
        return Department.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.organization_id:
            serializer.save(organization_id=user.organization_id)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add member to a department"""
        department = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'member')

        if not user_id:
            return Response({'detail': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        member, _ = DepartmentMember.objects.get_or_create(
            department=department,
            user_id=user_id,
            defaults={'role': role}
        )
        if member.role != role:
            member.role = role
            member.save(update_fields=['role'])

        serializer = DepartmentMemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DepartmentMemberViewSet(viewsets.ModelViewSet):
    """ViewSet for department members"""
    queryset = DepartmentMember.objects.all()
    serializer_class = DepartmentMemberSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['department', 'user', 'role']
    ordering = ['-joined_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return DepartmentMember.objects.all()
        if user.organization_id:
            return DepartmentMember.objects.filter(department__organization_id=user.organization_id)
        return DepartmentMember.objects.none()


class ModuleCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for per-module categories"""
    queryset = ModuleCategory.objects.all()
    serializer_class = ModuleCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'module', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['sort_order', 'name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), CanManageCategories()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ModuleCategory.objects.all()
        if user.organization_id:
            return ModuleCategory.objects.filter(organization_id=user.organization_id)
        return ModuleCategory.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.organization_id:
            serializer.save(organization_id=user.organization_id)
        else:
            serializer.save()
