from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Course, Module, Lesson, Exercise
from .serializers import (
    CourseSerializer, CourseListSerializer, ModuleSerializer,
    LessonSerializer, ExerciseSerializer, SubmitExerciseSerializer
)


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Course instances.
    """
    queryset = Course.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'category']
    ordering_fields = ['created_at', 'title']

    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        return CourseSerializer


class ModuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Module instances.
    """
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

    @action(detail=False, methods=['get'], url_path='course/(?P<course_id>[^/.]+)')
    def course_modules(self, request, course_id=None):
        """
        Return all modules for a specific course.
        """
        modules = Module.objects.filter(course_id=course_id).order_by('order')
        serializer = self.get_serializer(modules, many=True)
        return Response(serializer.data)


class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Lesson instances.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    @action(detail=False, methods=['get'], url_path='module/(?P<module_id>[^/.]+)')
    def module_lessons(self, request, module_id=None):
        """
        Return all lessons for a specific module.
        """
        lessons = Lesson.objects.filter(module_id=module_id).order_by('order')
        serializer = self.get_serializer(lessons, many=True)
        return Response(serializer.data)


class ExerciseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Exercise instances.
    """
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

    @action(detail=False, methods=['get'], url_path='lesson/(?P<lesson_id>[^/.]+)')
    def lesson_exercises(self, request, lesson_id=None):
        """
        Return all exercises for a specific lesson.
        """
        exercises = Exercise.objects.filter(lesson_id=lesson_id)
        serializer = self.get_serializer(exercises, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], serializer_class=SubmitExerciseSerializer)
    def submit(self, request, pk=None):
        """
        Submit an answer to an exercise.
        """
        exercise = self.get_object()
        serializer = SubmitExerciseSerializer(data=request.data)

        if serializer.is_valid():
            submitted_answer = serializer.validated_data['answer']
            is_correct = submitted_answer.lower() == exercise.correct_answer.lower()

            return Response({
                'is_correct': is_correct,
                'correct_answer': exercise.correct_answer if is_correct else None,
                'explanation': exercise.explanation
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
