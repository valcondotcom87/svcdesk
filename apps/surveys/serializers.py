"""
Survey & Feedback Serializers - REST API serializers for customer surveys and feedback
"""
from rest_framework import serializers
from apps.surveys.models import (
    Survey, SurveyQuestion, SurveyResponse, SurveyAnswer, Feedback
)


class SurveyQuestionSerializer(serializers.ModelSerializer):
    """Serializer for survey questions"""
    class Meta:
        model = SurveyQuestion
        fields = [
            'id', 'survey', 'question_text', 'question_type', 'is_required',
            'options', 'order'
        ]


class SurveyAnswerSerializer(serializers.ModelSerializer):
    """Serializer for survey answers"""
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    
    class Meta:
        model = SurveyAnswer
        fields = [
            'id', 'survey_response', 'question', 'question_text', 'answer_text',
            'rating_value'
        ]


class SurveyResponseListSerializer(serializers.ModelSerializer):
    """Lightweight survey response list serializer"""
    respondent_name = serializers.CharField(source='respondent.get_full_name', read_only=True)
    
    class Meta:
        model = SurveyResponse
        fields = [
            'id', 'survey', 'respondent', 'respondent_name', 'overall_score',
            'submitted_at'
        ]


class SurveyResponseDetailSerializer(serializers.ModelSerializer):
    """Full survey response detail serializer with answers"""
    respondent_name = serializers.CharField(source='respondent.get_full_name', read_only=True)
    
    # Nested serializers
    answers = SurveyAnswerSerializer(many=True, read_only=True, source='surveyanswer_set')
    
    class Meta:
        model = SurveyResponse
        fields = [
            'id', 'survey', 'respondent', 'respondent_name', 'answers',
            'overall_score', 'comments', 'submitted_at'
        ]


class SurveyResponseCreateSerializer(serializers.ModelSerializer):
    """Serializer for submitting survey responses"""
    answers = SurveyAnswerSerializer(many=True, write_only=True)
    
    class Meta:
        model = SurveyResponse
        fields = ['survey', 'respondent', 'answers', 'overall_score', 'comments']
    
    def create(self, validated_data):
        answers_data = validated_data.pop('answers', [])
        survey_response = SurveyResponse.objects.create(**validated_data)
        
        for answer_data in answers_data:
            SurveyAnswer.objects.create(survey_response=survey_response, **answer_data)
        
        return survey_response


class SurveyListSerializer(serializers.ModelSerializer):
    """Lightweight survey list serializer"""
    question_count = serializers.SerializerMethodField()
    response_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Survey
        fields = [
            'id', 'title', 'description', 'survey_type', 'question_count',
            'response_count', 'is_active', 'created_at'
        ]
    
    def get_question_count(self, obj):
        return obj.surveyquestion_set.count()
    
    def get_response_count(self, obj):
        return obj.surveyresponse_set.count()


class SurveyDetailSerializer(serializers.ModelSerializer):
    """Full survey detail serializer with questions and responses"""
    # Nested serializers
    questions = SurveyQuestionSerializer(many=True, read_only=True, source='surveyquestion_set')
    responses = SurveyResponseListSerializer(many=True, read_only=True, source='surveyresponse_set')
    
    class Meta:
        model = Survey
        fields = [
            'id', 'organization', 'title', 'description', 'survey_type',
            'target_audience', 'questions', 'responses', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SurveyCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating surveys"""
    class Meta:
        model = Survey
        fields = [
            'title', 'description', 'survey_type', 'target_audience', 'is_active'
        ]


class FeedbackListSerializer(serializers.ModelSerializer):
    """Lightweight feedback list serializer"""
    provider_name = serializers.CharField(source='provider.get_full_name', read_only=True)
    rating_display = serializers.CharField(source='get_rating_display', read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'provider', 'provider_name', 'rating', 'rating_display',
            'feedback_type', 'created_at'
        ]


class FeedbackDetailSerializer(serializers.ModelSerializer):
    """Full feedback detail serializer"""
    provider_name = serializers.CharField(source='provider.get_full_name', read_only=True)
    rating_display = serializers.CharField(source='get_rating_display', read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'organization', 'provider', 'provider_name', 'feedback_text',
            'rating', 'rating_display', 'feedback_type', 'related_ticket',
            'has_been_reviewed', 'review_notes', 'created_at'
        ]
        read_only_fields = ['created_at']


class FeedbackCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating feedback"""
    class Meta:
        model = Feedback
        fields = [
            'provider', 'feedback_text', 'rating', 'feedback_type', 'related_ticket'
        ]
