"""
Change Management Serializers - REST API serializers for change management
"""
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.changes.models import (
    Change, CABMember, ChangeApproval, ChangeImpactAnalysis, ChangeLog
)
from apps.organizations.models import Organization


class ChangeLogSerializer(serializers.ModelSerializer):
    """Serializer for change logs"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ChangeLog
        fields = [
            'id', 'change', 'action', 'field_changed', 'old_value', 'new_value',
            'description', 'created_by', 'created_by_name', 'created_at'
        ]


class CABMemberSerializer(serializers.ModelSerializer):
    """Serializer for CAB members"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = CABMember
        fields = ['id', 'change', 'user', 'user_name', 'role', 'is_mandatory']


class ChangeApprovalSerializer(serializers.ModelSerializer):
    """Serializer for change approvals"""
    cab_member_name = serializers.CharField(source='cab_member.user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ChangeApproval
        fields = [
            'id', 'change', 'cab_member', 'cab_member_name', 'status', 'status_display',
            'comments', 'decided_at', 'created_at'
        ]


class ChangeImpactAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for change impact analysis"""
    class Meta:
        model = ChangeImpactAnalysis
        fields = [
            'id', 'change', 'affected_cis', 'affected_incidents',
            'estimated_downtime_minutes', 'estimated_users_impacted',
            'dependency_analysis', 'risk_score'
        ]


class ChangeListSerializer(serializers.ModelSerializer):
    """Lightweight change list serializer"""
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_change_type_display', read_only=True)
    impact_display = serializers.CharField(source='get_impact_level_display', read_only=True)
    
    class Meta:
        model = Change
        fields = [
            'id', 'ticket_number', 'title', 'category', 'requester', 'requester_name',
            'implementation_owner', 'change_type', 'type_display', 'status',
            'status_display', 'impact_level', 'impact_display',
            'implementation_date', 'backout_date', 'created_at'
        ]


class ChangeDetailSerializer(serializers.ModelSerializer):
    """Full change detail serializer with nested relations"""
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    implementation_owner_name = serializers.CharField(source='implementation_owner.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_change_type_display', read_only=True)
    impact_display = serializers.CharField(source='get_impact_level_display', read_only=True)
    
    # Nested serializers
    cab_members = CABMemberSerializer(many=True, read_only=True)
    approvals = ChangeApprovalSerializer(many=True, read_only=True)
    impact_analysis = ChangeImpactAnalysisSerializer(read_only=True)
    change_log = ChangeLogSerializer(many=True, read_only=True, source='logs')
    
    class Meta:
        model = Change
        fields = [
            'id', 'organization', 'ticket_number', 'title', 'description',
            'requester', 'requester_name', 'implementation_owner', 'implementation_owner_name',
            'change_type', 'type_display', 'status', 'status_display',
            'impact_level', 'impact_display', 'category',
            'implementation_date', 'backout_date', 'estimated_duration_minutes',
            'affected_services', 'risk_assessment', 'risk_mitigation',
            'implementation_plan', 'backout_plan', 'success_criteria', 'test_results',
            'completed_date', 'actual_duration_minutes', 'completion_notes',
            'cab_members', 'approvals', 'impact_analysis', 'change_log',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['ticket_number', 'created_at', 'updated_at']


class ChangeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating changes"""
    cab_members = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
        write_only=True
    )

    class Meta:
        model = Change
        fields = [
            'title', 'description', 'change_type', 'category', 'requester',
            'implementation_owner', 'impact_level', 'implementation_date',
            'backout_date', 'estimated_duration_minutes', 'affected_services',
            'risk_assessment', 'risk_mitigation', 'implementation_plan',
            'backout_plan', 'success_criteria', 'test_results', 'cab_members'
        ]
        extra_kwargs = {
            'category': {'required': False, 'allow_blank': True},
            'requester': {'required': False, 'allow_null': True},
            'implementation_owner': {'required': False, 'allow_null': True},
        }

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)

        category = attrs.get('category') if 'category' in attrs else getattr(instance, 'category', '')
        change_type = attrs.get('change_type') if 'change_type' in attrs else getattr(instance, 'change_type', None)
        impact_level = attrs.get('impact_level') if 'impact_level' in attrs else getattr(instance, 'impact_level', None)
        implementation_date = attrs.get('implementation_date') if 'implementation_date' in attrs else getattr(instance, 'implementation_date', None)
        backout_date = attrs.get('backout_date') if 'backout_date' in attrs else getattr(instance, 'backout_date', None)
        affected_services = attrs.get('affected_services') if 'affected_services' in attrs else getattr(instance, 'affected_services', '')
        risk_assessment = attrs.get('risk_assessment') if 'risk_assessment' in attrs else getattr(instance, 'risk_assessment', '')
        risk_mitigation = attrs.get('risk_mitigation') if 'risk_mitigation' in attrs else getattr(instance, 'risk_mitigation', '')
        implementation_plan = attrs.get('implementation_plan') if 'implementation_plan' in attrs else getattr(instance, 'implementation_plan', '')
        backout_plan = attrs.get('backout_plan') if 'backout_plan' in attrs else getattr(instance, 'backout_plan', '')
        success_criteria = attrs.get('success_criteria') if 'success_criteria' in attrs else getattr(instance, 'success_criteria', '')
        cab_members = attrs.get('cab_members')

        errors = {}
        if not category or not str(category).strip():
            errors['category'] = 'Category is required for ITIL change classification.'
        if not change_type:
            errors['change_type'] = 'Change type is required.'
        if not impact_level:
            errors['impact_level'] = 'Impact level is required.'
        if not implementation_date:
            errors['implementation_date'] = 'Planned start date is required.'
        if not backout_date:
            errors['backout_date'] = 'Planned end date is required.'
        if not affected_services or not str(affected_services).strip():
            errors['affected_services'] = 'Affected CI/service is required.'
        if not risk_assessment or not str(risk_assessment).strip():
            errors['risk_assessment'] = 'Risk assessment is required.'
        if not risk_mitigation or not str(risk_mitigation).strip():
            errors['risk_mitigation'] = 'Risk mitigation is required.'
        if not implementation_plan or not str(implementation_plan).strip():
            errors['implementation_plan'] = 'Implementation plan is required.'
        if not backout_plan or not str(backout_plan).strip():
            errors['backout_plan'] = 'Backout plan is required.'
        if not success_criteria or not str(success_criteria).strip():
            errors['success_criteria'] = 'Test/validation plan is required.'
        if instance is None:
            if not cab_members:
                errors['cab_members'] = 'At least one CAB member is required.'
        elif cab_members is not None and len(cab_members) == 0:
            errors['cab_members'] = 'At least one CAB member is required.'

        if errors:
            raise ValidationError(errors)

        return attrs
    
    def create(self, validated_data):
        cab_members = validated_data.pop('cab_members', [])
        # Generate ticket number
        org = validated_data.get('organization')
        if not org:
            request = self.context.get('request')
            user = getattr(request, 'user', None)
            user_org = getattr(user, 'organization', None) if user else None
            if user_org:
                org = Organization.objects.filter(name=user_org.name).first()
            if not org and user and user.is_superuser:
                org = Organization.objects.filter(is_active=True).first()
            if not org:
                raise ValidationError({'organization': 'Organization is required to create a change.'})
            validated_data['organization'] = org
        count = Change.objects.filter(organization=org).count()
        validated_data['ticket_number'] = f"{org.slug.upper()}-CHG-{count + 1:05d}"

        change = super().create(validated_data)

        if cab_members:
            for user_id in cab_members:
                CABMember.objects.get_or_create(
                    change=change,
                    user_id=user_id,
                    defaults={'role': 'Member', 'is_mandatory': False}
                )

        return change

    def update(self, instance, validated_data):
        cab_members = validated_data.pop('cab_members', None)
        change = super().update(instance, validated_data)

        if cab_members is not None:
            change.cab_members.all().delete()
            for user_id in cab_members:
                CABMember.objects.get_or_create(
                    change=change,
                    user_id=user_id,
                    defaults={'role': 'Member', 'is_mandatory': False}
                )

        return change


class ChangeActionSerializer(serializers.Serializer):
    """Serializer for change actions"""
    action = serializers.ChoiceField(
        choices=['submit', 'approve', 'reject', 'implement', 'complete', 'cancel']
    )
    comments = serializers.CharField(required=False, allow_blank=True)
