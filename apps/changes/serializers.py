"""
Change Management Serializers - REST API serializers for change management
"""
from rest_framework import serializers
from apps.changes.models import (
    Change, CABMember, ChangeApproval, ChangeImpactAnalysis, ChangeLog
)


class ChangeLogSerializer(serializers.ModelSerializer):
    """Serializer for change logs"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = ChangeLog
        fields = ['id', 'change', 'action', 'description', 'user', 'user_name', 'timestamp']


class CABMemberSerializer(serializers.ModelSerializer):
    """Serializer for CAB members"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = CABMember
        fields = ['id', 'change', 'user', 'user_name', 'role', 'role_display']


class ChangeApprovalSerializer(serializers.ModelSerializer):
    """Serializer for change approvals"""
    approver_name = serializers.CharField(source='approver.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ChangeApproval
        fields = [
            'id', 'change', 'approver', 'approver_name', 'status', 'status_display',
            'comments', 'approval_date', 'approval_order'
        ]


class ChangeImpactAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for change impact analysis"""
    class Meta:
        model = ChangeImpactAnalysis
        fields = [
            'id', 'change', 'analysis_summary', 'affected_cis', 'affected_services',
            'risk_level', 'risk_mitigation', 'rollback_plan', 'affected_users_count',
            'analysis_date', 'analyzed_by'
        ]


class ChangeListSerializer(serializers.ModelSerializer):
    """Lightweight change list serializer"""
    initiator_name = serializers.CharField(source='initiator.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_change_type_display', read_only=True)
    
    class Meta:
        model = Change
        fields = [
            'id', 'change_number', 'title', 'initiator', 'initiator_name',
            'change_type', 'type_display', 'status', 'status_display',
            'scheduled_start', 'scheduled_end', 'created_at'
        ]


class ChangeDetailSerializer(serializers.ModelSerializer):
    """Full change detail serializer with nested relations"""
    initiator_name = serializers.CharField(source='initiator.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_change_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    # Nested serializers
    cab_members = CABMemberSerializer(many=True, read_only=True, source='cabmember_set')
    approvals = ChangeApprovalSerializer(many=True, read_only=True, source='approval_set')
    impact_analysis = ChangeImpactAnalysisSerializer(read_only=True)
    change_log = ChangeLogSerializer(many=True, read_only=True, source='changelog_set')
    
    class Meta:
        model = Change
        fields = [
            'id', 'organization', 'change_number', 'title', 'description',
            'initiator', 'initiator_name', 'assigned_to', 'assigned_to_name',
            'change_type', 'type_display', 'status', 'status_display',
            'priority', 'priority_display', 'category',
            'business_justification', 'implementation_plan', 'rollback_plan',
            'scheduled_start', 'scheduled_end', 'actual_start', 'actual_end',
            'estimated_cost', 'actual_cost',
            'approval_required', 'risk_assessment', 'testing_plan',
            'cab_members', 'approvals', 'impact_analysis', 'change_log',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['change_number', 'created_at', 'updated_at']


class ChangeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating changes"""
    class Meta:
        model = Change
        fields = [
            'title', 'description', 'change_type', 'category', 'initiator',
            'assigned_to', 'priority', 'business_justification',
            'implementation_plan', 'rollback_plan', 'scheduled_start',
            'scheduled_end', 'estimated_cost'
        ]
    
    def create(self, validated_data):
        # Generate change number
        org = validated_data.get('organization')
        count = Change.objects.filter(organization=org).count()
        validated_data['change_number'] = f"{org.slug.upper()}-CHG-{count + 1:05d}"
        
        return super().create(validated_data)


class ChangeActionSerializer(serializers.Serializer):
    """Serializer for change actions"""
    action = serializers.ChoiceField(
        choices=['submit', 'approve', 'reject', 'implement', 'complete', 'cancel']
    )
    comments = serializers.CharField(required=False, allow_blank=True)
