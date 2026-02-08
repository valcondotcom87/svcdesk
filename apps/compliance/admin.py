from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    ComplianceFramework, ComplianceRequirement, ImmutableAuditLog,
    IncidentResponsePlan, VulnerabilityTracking, ComplianceCheckpoint
)


@admin.register(ComplianceFramework)
class ComplianceFrameworkAdmin(admin.ModelAdmin):
    list_display = ('framework', 'status_badge', 'progress_bar', 'version', 'created_at')
    list_filter = ('framework', 'status', 'created_at')
    search_fields = ('framework', 'description')
    readonly_fields = ('created_at', 'updated_at', 'progress_bar')
    fieldsets = (
        ('Framework Information', {
            'fields': ('framework', 'description', 'status', 'version')
        }),
        ('Progress Tracking', {
            'fields': ('progress_percentage', 'progress_bar')
        }),
        ('Dates', {
            'fields': ('target_certification_date', 'certification_date', 'expiry_date')
        }),
        ('Responsibility', {
            'fields': ('responsible_person', 'approval_status', 'approved_by')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def status_badge(self, obj):
        color_map = {
            'planned': '#FFA500',
            'in_progress': '#1E90FF',
            'implemented': '#32CD32',
            'certified': '#00AA00',
            'expired': '#DC143C'
        }
        color = color_map.get(obj.status, '#808080')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def progress_bar(self, obj):
        percentage = obj.progress_percentage or 0
        return format_html(
            '<div style="width:100%; background-color: #ddd; border-radius: 3px; overflow: hidden;">'
            '<div style="width: {}%; background-color: #4CAF50; height: 20px; text-align: center; color: white; font-size: 12px;">'
            '{}%</div></div>',
            percentage, percentage
        )
    progress_bar.short_description = 'Progress'


@admin.register(ComplianceRequirement)
class ComplianceRequirementAdmin(admin.ModelAdmin):
    list_display = ('requirement_id', 'title', 'framework_link', 'status_badge', 'due_date')
    list_filter = ('framework', 'status', 'due_date')
    search_fields = ('requirement_id', 'title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Requirement Details', {
            'fields': ('framework', 'requirement_id', 'title', 'description', 'status')
        }),
        ('Risk & Evidence', {
            'fields': ('risk_level', 'evidence_url', 'evidence_notes')
        }),
        ('Dates', {
            'fields': ('due_date', 'completion_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def framework_link(self, obj):
        url = reverse('admin:compliance_complianceframework_change', args=[obj.framework.id])
        return format_html('<a href="{}">{}</a>', url, obj.framework.get_framework_display())
    framework_link.short_description = 'Framework'

    def status_badge(self, obj):
        color_map = {
            'not_started': '#808080',
            'in_progress': '#FFA500',
            'implemented': '#32CD32',
            'verified': '#00AA00',
            'non_applicable': '#A9A9A9'
        }
        color = color_map.get(obj.status, '#808080')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(ImmutableAuditLog)
class ImmutableAuditLogAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'action_badge', 'timestamp', 'severity_badge', 'hash_chain_valid_badge', 'content_type')
    list_filter = ('action', 'severity', 'timestamp', 'hash_chain_valid')
    search_fields = ('user__email', 'action', 'object_repr')
    readonly_fields = (
        'user', 'action', 'timestamp', 'object_id', 'content_type',
        'data_hash', 'previous_hash', 'hash_chain_valid',
        'old_values', 'new_values', 'changes_made',
        'ip_address', 'user_agent', 'description'
    )
    fieldsets = (
        ('User & Action', {
            'fields': ('user', 'action', 'timestamp')
        }),
        ('Object Information', {
            'fields': ('content_type', 'object_id', 'object_repr')
        }),
        ('Hash Chain (Immutable)', {
            'fields': ('data_hash', 'previous_hash', 'hash_chain_valid'),
            'description': 'SHA-256 hash chain for tamper detection'
        }),
        ('Changes', {
            'fields': ('old_values', 'new_values', 'changes_made')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'severity', 'description', 'approval_status', 'approved_by'),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return 'System'
    user_link.short_description = 'User'

    def action_badge(self, obj):
        color_map = {
            'create': '#4CAF50',
            'update': '#2196F3',
            'delete': '#F44336',
            'view': '#9C27B0',
            'login': '#FF9800',
            'logout': '#795548',
            'security_event': '#D32F2F',
        }
        color = color_map.get(obj.action, '#808080')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_action_display()
        )
    action_badge.short_description = 'Action'

    def severity_badge(self, obj):
        color_map = {
            'low': '#4CAF50',
            'medium': '#FFC107',
            'high': '#FF5722',
            'critical': '#D32F2F'
        }
        color = color_map.get(obj.severity, '#808080')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'

    def hash_chain_valid_badge(self, obj):
        if obj.hash_chain_valid:
            return format_html('<span style="color: green; font-weight: bold;">✓ Valid</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Invalid</span>')
    hash_chain_valid_badge.short_description = 'Hash Valid'


@admin.register(IncidentResponsePlan)
class IncidentResponsePlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'incident_type', 'severity_badge', 'created_at')
    list_filter = ('incident_type', 'severity', 'created_at')
    search_fields = ('name', 'description', 'incident_type')
    readonly_fields = ('created_at', 'updated_at', 'version')
    fieldsets = (
        ('Plan Information', {
            'fields': ('name', 'incident_type', 'description', 'severity')
        }),
        ('Procedures', {
            'fields': (
                'detection_procedures', 'initial_response',
                'escalation_path', 'investigation_procedures',
                'recovery_procedures'
            )
        }),
        ('SLA Tracking', {
            'fields': ('detection_sla_duration', 'response_sla_duration', 'resolution_sla_duration')
        }),
        ('Contacts', {
            'fields': ('primary_contact', 'secondary_contacts')
        }),
        ('Communication & Review', {
            'fields': ('communication_template', 'post_incident_review')
        }),
        ('Version & Approval', {
            'fields': ('version', 'approval_status', 'approved_by', 'last_reviewed', 'next_review_date'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def severity_badge(self, obj):
        color_map = {
            'low': '#4CAF50',
            'medium': '#FFC107',
            'high': '#FF5722',
            'critical': '#D32F2F'
        }
        color = color_map.get(obj.severity, '#808080')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'


@admin.register(VulnerabilityTracking)
class VulnerabilityTrackingAdmin(admin.ModelAdmin):
    list_display = ('vulnerability_id', 'title', 'severity_badge', 'status_badge', 'discovery_date', 'target_remediation_date')
    list_filter = ('severity', 'status', 'discovery_date', 'affected_system')
    search_fields = ('vulnerability_id', 'title', 'affected_system', 'cve_reference')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Vulnerability Information', {
            'fields': ('vulnerability_id', 'title', 'description', 'affected_system', 'cve_reference')
        }),
        ('Discovery Information', {
            'fields': ('discovery_date', 'discovered_by', 'scan_tool', 'initial_severity')
        }),
        ('Status & Severity', {
            'fields': ('status', 'severity', 'current_status_notes')
        }),
        ('Remediation', {
            'fields': (
                'remediation_plan', 'remediation_effort',
                'target_remediation_date', 'actual_remediation_date',
                'responsible_person', 'verification_steps'
            )
        }),
        ('Risk Acceptance', {
            'fields': (
                'risk_acceptance_justification', 'accepted_by',
                'acceptance_date', 'acceptance_expiry_date'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def severity_badge(self, obj):
        color_map = {
            'low': '#4CAF50',
            'medium': '#FFC107',
            'high': '#FF5722',
            'critical': '#D32F2F'
        }
        color = color_map.get(obj.severity, '#808080')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'

    def status_badge(self, obj):
        color_map = {
            'open': '#F44336',
            'acknowledged': '#FF9800',
            'in_progress': '#2196F3',
            'resolved': '#4CAF50',
            'accepted_risk': '#9C27B0',
            'closed': '#795548'
        }
        color = color_map.get(obj.status, '#808080')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(ComplianceCheckpoint)
class ComplianceCheckpointAdmin(admin.ModelAdmin):
    list_display = ('name', 'checkpoint_type', 'planned_date', 'compliance_score_badge', 'status_badge', 'assigned_to')
    list_filter = ('checkpoint_type', 'status', 'planned_date', 'frameworks')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Checkpoint Information', {
            'fields': ('name', 'checkpoint_type', 'description', 'frameworks')
        }),
        ('Scheduling', {
            'fields': ('planned_date', 'actual_completion_date', 'frequency')
        }),
        ('Status & Findings', {
            'fields': ('status', 'compliance_score', 'issues_identified', 'issues_resolved')
        }),
        ('Remediation', {
            'fields': ('remediation_required', 'remediation_deadline')
        }),
        ('Evidence', {
            'fields': ('evidence_attached', 'assigned_to')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def compliance_score_badge(self, obj):
        if obj.compliance_score >= 80:
            color = '#4CAF50'
        elif obj.compliance_score >= 60:
            color = '#FFC107'
        else:
            color = '#F44336'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}%</span>',
            color, obj.compliance_score
        )
    compliance_score_badge.short_description = 'Compliance Score'

    def status_badge(self, obj):
        color_map = {
            'planned': '#9C27B0',
            'in_progress': '#2196F3',
            'completed': '#4CAF50',
            'issues_found': '#FF5722'
        }
        color = color_map.get(obj.status, '#808080')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
