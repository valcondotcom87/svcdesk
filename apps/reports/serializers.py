"""
Report Serializers - REST API serializers for reporting and analytics
"""
from rest_framework import serializers
from apps.reports.models import (
    Report, ReportSchedule, ReportExecution, Dashboard, DashboardWidget
)


class ReportScheduleSerializer(serializers.ModelSerializer):
    """Serializer for report schedules"""
    class Meta:
        model = ReportSchedule
        fields = [
            'id', 'report', 'frequency', 'is_active', 'next_run',
            'last_run', 'recipients'
        ]


class ReportExecutionSerializer(serializers.ModelSerializer):
    """Serializer for report executions"""
    executed_by_name = serializers.CharField(source='executed_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ReportExecution
        fields = [
            'id', 'report', 'executed_by', 'executed_by_name', 'status',
            'status_display', 'started_at', 'completed_at', 'output_file',
            'error_message'
        ]


class ReportListSerializer(serializers.ModelSerializer):
    """Lightweight report list serializer"""
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'description', 'report_type', 'owner', 'owner_name',
            'created_at', 'last_executed'
        ]


class ReportDetailSerializer(serializers.ModelSerializer):
    """Full report detail serializer with nested relations"""
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    # Nested serializers
    schedule = ReportScheduleSerializer(read_only=True)
    executions = ReportExecutionSerializer(many=True, read_only=True, source='execution_set')
    
    class Meta:
        model = Report
        fields = [
            'id', 'organization', 'name', 'description', 'report_type',
            'owner', 'owner_name', 'query_definition', 'filters', 'columns',
            'schedule', 'executions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ReportCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating reports"""
    class Meta:
        model = Report
        fields = [
            'name', 'description', 'report_type', 'owner',
            'query_definition', 'filters', 'columns'
        ]


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Serializer for dashboard widgets"""
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'dashboard', 'widget_type', 'title', 'data_source',
            'position_x', 'position_y', 'width', 'height', 'configuration'
        ]


class DashboardListSerializer(serializers.ModelSerializer):
    """Lightweight dashboard list serializer"""
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'name', 'description', 'owner', 'owner_name',
            'is_default', 'created_at'
        ]


class DashboardDetailSerializer(serializers.ModelSerializer):
    """Full dashboard detail serializer with widgets"""
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    # Nested serializers
    widgets = DashboardWidgetSerializer(many=True, read_only=True, source='dashboardwidget_set')
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'organization', 'name', 'description', 'owner', 'owner_name',
            'layout_configuration', 'is_default', 'widgets', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DashboardCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating dashboards"""
    class Meta:
        model = Dashboard
        fields = ['name', 'description', 'owner', 'layout_configuration', 'is_default']
