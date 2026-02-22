from rest_framework import serializers
from apps.knowledge.models import KnowledgeArticle


class KnowledgeArticleListSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = KnowledgeArticle
        fields = [
            'id', 'title', 'category', 'status', 'status_display',
            'owner', 'owner_name', 'version', 'updated_at'
        ]


class KnowledgeArticleDetailSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = KnowledgeArticle
        fields = [
            'id', 'organization', 'title', 'summary', 'content', 'category',
            'status', 'status_display', 'owner', 'owner_name', 'tags',
            'csf_function', 'csf_category', 'iso_control', 'nist_control',
            'review_notes', 'version', 'published_at', 'created_at', 'updated_at',
            'created_by', 'updated_by'
        ]
        read_only_fields = ['created_at', 'updated_at']


class KnowledgeArticleCreateUpdateSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        status = attrs.get('status')
        if status in ['published', 'archived']:
            raise serializers.ValidationError({
                'status': 'Use publish/archive actions for lifecycle changes.'
            })
        return attrs

    def update(self, instance, validated_data):
        bump_fields = [
            'title', 'summary', 'content', 'category', 'tags',
            'csf_function', 'csf_category', 'iso_control', 'nist_control'
        ]
        should_bump = False
        for field in bump_fields:
            if field in validated_data and validated_data[field] != getattr(instance, field):
                should_bump = True
                break

        if should_bump:
            validated_data['version'] = instance.version + 1

        return super().update(instance, validated_data)

    class Meta:
        model = KnowledgeArticle
        fields = [
            'title', 'summary', 'content', 'category', 'status',
            'owner', 'tags', 'csf_function', 'csf_category',
            'iso_control', 'nist_control'
        ]
