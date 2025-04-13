from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Category, Course, Module, Lesson
from .serializers import (
    CategorySerializer, CourseSerializer,
    CourseListSerializer, ModuleSerializer,
    LessonSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        """
        Optionally restricts the returned categories by filtering
        against query parameters in the URL.
        """
        queryset = Category.objects.all()
        in_progress = self.request.query_params.get('in_progress', None)
        if in_progress is not None:
            queryset = queryset.filter(in_progress=in_progress == 'true')
        return queryset


class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for courses.
    """
    queryset = Course.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']

    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        return CourseSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned courses by filtering
        against query parameters in the URL.
        """
        queryset = Course.objects.all()
        category_id = self.request.query_params.get('category', None)
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """
        Update the progress of a course.
        """
        course = self.get_object()
        progress = request.data.get('progress', 0)
        course.progress = min(max(0, progress), 100)
        course.save()
        return Response({'status': 'progress updated'})


class ModuleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for modules.
    """
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned modules by filtering
        against query parameters in the URL.
        """
        queryset = Module.objects.all()
        course_id = self.request.query_params.get('course', None)
        if course_id is not None:
            queryset = queryset.filter(course_id=course_id)
        return queryset

    def get_object(self):
        """
        Override to ensure module belongs to the specified course
        """
        course_id = self.request.query_params.get('course', None)
        if not course_id:
            return super().get_object()
        
        module = super().get_object()
        if str(module.course_id) != str(course_id):
            raise Http404("Module not found in this course")
        return module

    def update(self, request, *args, **kwargs):
        """
        Update a module with validation.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Validate lesson_ids if provided
        if 'lesson_ids' in request.data:
            lesson_ids = request.data['lesson_ids']
            if not isinstance(lesson_ids, list):
                return Response(
                    {'error': 'lesson_ids must be a list'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate that all lesson IDs exist and belong to this module
            invalid_lessons = Lesson.objects.filter(
                id__in=lesson_ids
            ).exclude(module=instance).exists()
            
            if invalid_lessons:
                return Response(
                    {'error': 'One or more lesson IDs do not belong to this module'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a module and handle related lessons.
        """
        instance = self.get_object()
        
        # Check if module has any lessons
        if instance.lessons.exists():
            return Response(
                {'error': 'Cannot delete module with existing lessons. Please delete the lessons first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def update_lesson_order(self, request, pk=None):
        """
        Update the order of lessons in a module.
        """
        module = self.get_object()
        lesson_ids = request.data.get('lesson_ids', [])
        
        if not isinstance(lesson_ids, list):
            return Response(
                {'error': 'lesson_ids must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate that all lesson IDs exist and belong to this module
        invalid_lessons = Lesson.objects.filter(
            id__in=lesson_ids
        ).exclude(module=module).exists()
        
        if invalid_lessons:
            return Response(
                {'error': 'One or more lesson IDs do not belong to this module'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        module.lesson_ids = lesson_ids
        module.save()
        
        return Response({'status': 'lesson order updated'})


class LessonViewSet(viewsets.ModelViewSet):
    """
    API endpoint for lessons.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned lessons by filtering
        against query parameters in the URL.
        """
        queryset = Lesson.objects.all()
        module_id = self.request.query_params.get('module', None)
        if module_id is not None:
            queryset = queryset.filter(module_id=module_id)
        return queryset

    def get_object(self):
        """
        Override to ensure lesson belongs to the specified module
        """
        module_id = self.request.query_params.get('module', None)
        if not module_id:
            return super().get_object()
        
        lesson = super().get_object()
        if str(lesson.module_id) != str(module_id):
            raise Http404("Lesson not found in this module")
        return lesson

    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        """
        Submit an answer for a lesson and get feedback.
        """
        lesson = self.get_object()
        answer = request.data.get('answer')
        
        if not answer:
            return Response(
                {'error': 'Answer is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate the answer based on the lesson type
        problem = lesson.problem
        correct = False
        
        if lesson.type == 'multiple-choice':
            correct = answer == problem.get('solution')
        
        # Update progress if correct
        if correct:
            lesson.progress = min(lesson.progress + 25, 100)
            lesson.save()
        
        # Add feedback to the response
        serializer = self.get_serializer(lesson)
        response_data = serializer.data
        response_data['feedback'] = {
            'correct': correct,
            'explanation': problem.get('explanation'),
            'progress': lesson.progress
        }
        
        return Response(response_data)
