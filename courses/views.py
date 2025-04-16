from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import (
    Category, Course, Module, Lesson, LessonContentBlock,
    Problem, Hint, SolutionStep, PracticeSet, PracticeSetProblem
)
from .serializers import (
    CategorySerializer, CourseSerializer, CourseListSerializer,
    ModuleSerializer, LessonSerializer, LessonContentBlockSerializer,
    ProblemSerializer, HintSerializer, SolutionStepSerializer,
    PracticeSetSerializer, PracticeSetProblemSerializer
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
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
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


class LessonContentBlockViewSet(viewsets.ModelViewSet):
    """
    API endpoint for lesson content blocks.
    """
    queryset = LessonContentBlock.objects.all()
    serializer_class = LessonContentBlockSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned content blocks by filtering
        against query parameters in the URL.
        """
        queryset = LessonContentBlock.objects.all()
        lesson_id = self.request.query_params.get('lesson', None)
        if lesson_id is not None:
            queryset = queryset.filter(lesson_id=lesson_id)
        return queryset

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """
        Reorder content blocks within a lesson.
        """
        lesson_id = request.data.get('lesson_id')
        block_order = request.data.get('block_order', [])

        if not lesson_id or not isinstance(block_order, list):
            return Response(
                {'error': 'lesson_id and block_order list are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response(
                {'error': 'Lesson not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate that all block IDs exist and belong to this lesson
        blocks = LessonContentBlock.objects.filter(lesson=lesson)
        block_ids = set(blocks.values_list('id', flat=True))

        if not all(block_id in block_ids for block_id in block_order):
            return Response(
                {'error': 'One or more block IDs do not belong to this lesson'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the order of blocks
        for index, block_id in enumerate(block_order):
            block = blocks.get(id=block_id)
            block.order = index
            block.save()

        updated_blocks = LessonContentBlock.objects.filter(
            lesson=lesson).order_by('order')
        serializer = LessonContentBlockSerializer(updated_blocks, many=True)

        return Response(serializer.data)


class ProblemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for problems.
    """
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['question_text']
    ordering_fields = ['created_at', 'difficulty']


class PracticeSetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for practice sets.
    """
    queryset = PracticeSet.objects.all()
    serializer_class = PracticeSetSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned practice sets by filtering
        against query parameters in the URL.
        """
        queryset = PracticeSet.objects.all()

        lesson_id = self.request.query_params.get('lesson', None)
        if lesson_id is not None:
            queryset = queryset.filter(lesson_id=lesson_id)

        module_id = self.request.query_params.get('module', None)
        if module_id is not None:
            queryset = queryset.filter(module_id=module_id)

        practice_type = self.request.query_params.get('practice_type', None)
        if practice_type is not None:
            queryset = queryset.filter(practice_type=practice_type)

        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty is not None:
            queryset = queryset.filter(difficulty_level=difficulty)

        return queryset


class PracticeSetProblemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for practice set problems.
    """
    queryset = PracticeSetProblem.objects.all()
    serializer_class = PracticeSetProblemSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned practice set problems by filtering
        against query parameters in the URL.
        """
        queryset = PracticeSetProblem.objects.all()
        practice_set_id = self.request.query_params.get('practice_set', None)
        if practice_set_id is not None:
            queryset = queryset.filter(practice_set_id=practice_set_id)
        return queryset

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """
        Reorder problems within a practice set.
        """
        practice_set_id = request.data.get('practice_set_id')
        problem_order = request.data.get('problem_order', [])

        if not practice_set_id or not isinstance(problem_order, list):
            return Response(
                {'error': 'practice_set_id and problem_order list are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            practice_set = PracticeSet.objects.get(id=practice_set_id)
        except PracticeSet.DoesNotExist:
            return Response(
                {'error': 'Practice set not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate that all problem IDs exist and belong to this practice set
        set_problems = PracticeSetProblem.objects.filter(
            practice_set=practice_set)
        problem_ids = set(set_problems.values_list('id', flat=True))

        if not all(problem_id in problem_ids for problem_id in problem_order):
            return Response(
                {'error': 'One or more problem IDs do not belong to this practice set'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the order of problems
        for index, problem_id in enumerate(problem_order):
            set_problem = set_problems.get(id=problem_id)
            set_problem.order = index
            set_problem.save()

        updated_problems = PracticeSetProblem.objects.filter(
            practice_set=practice_set).order_by('order')
        serializer = PracticeSetProblemSerializer(updated_problems, many=True)

        return Response(serializer.data)
