"""
Survey ViewSets - REST API viewsets for surveys and feedback
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.surveys.models import (
    Survey, SurveyQuestion, SurveyResponse, SurveyAnswer, Feedback
)
from apps.surveys.serializers import (
    SurveyListSerializer, SurveyDetailSerializer, SurveyCreateUpdateSerializer,
    SurveyQuestionSerializer, SurveyResponseListSerializer,
    SurveyResponseDetailSerializer, SurveyResponseCreateSerializer,
    FeedbackListSerializer, FeedbackDetailSerializer, FeedbackCreateUpdateSerializer
)


class SurveyViewSet(viewsets.ModelViewSet):
    """ViewSet for surveys"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'survey_type', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return SurveyListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SurveyCreateUpdateSerializer
        return SurveyDetailSerializer
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return Survey.objects.all()
        return Survey.objects.filter(organization_id=user.organization_id)
    
    def perform_create(self, serializer):
        """Set organization"""
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Get all questions for a survey"""
        survey = self.get_object()
        questions = survey.surveyquestion_set.all()
        serializer = SurveyQuestionSerializer(questions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def responses(self, request, pk=None):
        """Get all responses for a survey"""
        survey = self.get_object()
        responses = survey.surveyresponse_set.all()
        serializer = SurveyResponseListSerializer(responses, many=True)
        return Response(serializer.data)


class SurveyQuestionViewSet(viewsets.ModelViewSet):
    """ViewSet for survey questions"""
    queryset = SurveyQuestion.objects.all()
    serializer_class = SurveyQuestionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['survey']
    ordering = ['order']


class SurveyResponseViewSet(viewsets.ModelViewSet):
    """ViewSet for survey responses"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['survey', 'respondent']
    ordering = ['-submitted_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return SurveyResponseListSerializer
        elif self.action in ['create']:
            return SurveyResponseCreateSerializer
        return SurveyResponseDetailSerializer
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return SurveyResponse.objects.all()
        return SurveyResponse.objects.filter(survey__organization_id=user.organization_id)


class FeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for feedback"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'provider', 'rating', 'feedback_type']
    search_fields = ['feedback_text']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return FeedbackListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return FeedbackCreateUpdateSerializer
        return FeedbackDetailSerializer
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return Feedback.objects.all()
        return Feedback.objects.filter(organization_id=user.organization_id)
    
    def perform_create(self, serializer):
        """Set organization"""
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def mark_reviewed(self, request, pk=None):
        """Mark feedback as reviewed"""
        feedback = self.get_object()
        review_notes = request.data.get('review_notes', '')
        
        feedback.has_been_reviewed = True
        feedback.review_notes = review_notes
        feedback.save()
        
        return Response({'detail': 'Feedback marked as reviewed'})
