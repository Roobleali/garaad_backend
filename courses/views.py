from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import (
    Category, Course, Lesson, LessonContentBlock,
    Problem, UserProgress, UserReward
)
from .serializers import (
    CategorySerializer, CourseSerializer, LessonSerializer,
    LessonContentBlockSerializer, ProblemSerializer,
    UserProgressSerializer, UserRewardSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

class LessonContentBlockViewSet(viewsets.ModelViewSet):
    queryset = LessonContentBlock.objects.all()
    serializer_class = LessonContentBlockSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['content']

class ProblemViewSet(viewsets.ModelViewSet):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['question_text']
    ordering_fields = ['created_at']

    def create(self, request, *args, **kwargs):
        try:
            # Ensure content is a dictionary if empty array is provided
            if 'content' in request.data and request.data['content'] == []:
                request.data['content'] = {}
            
            # Validate options and correct_answer for multiple choice questions
            if request.data.get('question_type') in ['multiple_choice', 'single_choice']:
                options = request.data.get('options', [])
                correct_answer = request.data.get('correct_answer', [])
                
                if not options:
                    return Response(
                        {'error': 'Options are required for multiple choice questions'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if not correct_answer:
                    return Response(
                        {'error': 'Correct answer is required for multiple choice questions'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Validate option IDs
                option_ids = {opt.get('id') for opt in options}
                for answer in correct_answer:
                    if answer.get('id') not in option_ids:
                        return Response(
                            {'error': f"Answer ID '{answer.get('id')}' not found in options"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
                # For single choice, ensure only one correct answer
                if request.data.get('question_type') == 'single_choice' and len(correct_answer) > 1:
                    return Response(
                        {'error': 'Single choice questions can only have one correct answer'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            try:
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            except ValidationError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except serializers.ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserProgressViewSet(viewsets.ModelViewSet):
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username']

class UserRewardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserReward.objects.all()
    serializer_class = UserRewardSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username'] 