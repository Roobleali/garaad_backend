from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils import timezone
from .models import (
    Category, Course, Module, Lesson, LessonContentBlock,
    Problem, Hint, SolutionStep, PracticeSet, PracticeSetProblem,
    UserProgress, CourseEnrollment, UserReward, LeaderboardEntry, DiagrammarContent
)
from .serializers import (
    CategorySerializer, CourseSerializer, CourseListSerializer,
    ModuleSerializer, LessonSerializer, LessonContentBlockSerializer,
    ProblemSerializer, HintSerializer, SolutionStepSerializer,
    PracticeSetSerializer, PracticeSetProblemSerializer,
    UserProgressSerializer, UserProgressUpdateSerializer,
    CourseEnrollmentSerializer, UserRewardSerializer,
    LeaderboardEntrySerializer, LessonWithNextSerializer,
    CourseWithProgressSerializer
)
from .diagrammar_utils import get_feedback


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
        if self.action == 'retrieve' and self.request.user.is_authenticated:
            return CourseWithProgressSerializer
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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        """
        Enroll the authenticated user in a course.
        """
        course = self.get_object()
        enrollment = CourseEnrollment.enroll_user(
            user=request.user, course=course)
        serializer = CourseEnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LessonWithNextSerializer
        return LessonSerializer

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

    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve to mark the lesson as in progress for authenticated users
        """
        lesson = self.get_object()
        response = super().retrieve(request, *args, **kwargs)

        # If the user is authenticated, update their lesson progress
        if request.user.is_authenticated:
            # Ensure the user is enrolled in the course
            CourseEnrollment.enroll_user(request.user, lesson.module.course)

            # Get or create a progress record and mark as in progress
            progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                lesson=lesson
            )

            # Only update if the lesson isn't already completed
            if progress.status != 'completed':
                progress.mark_as_in_progress()

        return response

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        """
        Mark a lesson as completed for the authenticated user.
        Optionally include a score if the lesson has a practice component.
        """
        lesson = self.get_object()
        score = request.data.get('score', None)

        # Ensure the user is enrolled in the course
        CourseEnrollment.enroll_user(request.user, lesson.module.course)

        # Get or create progress record and mark as completed
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'status': 'in_progress'}
        )

        progress.mark_as_completed(score=score)

        # Return the updated progress and next lesson info
        serializer = LessonWithNextSerializer(
            lesson, context={'request': request})
        return Response(serializer.data)


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

    @action(detail=True, methods=['post'])
    def validate_diagrammar(self, request, pk=None):
        """
        Validates a Diagrammar state against correct answers
        """
        problem = self.get_object()
        try:
            diagrammar_content = problem.diagrammar_content
        except DiagrammarContent.DoesNotExist:
            return Response({'error': 'No Diagrammar content found'}, status=404)
            
        user_state = request.data.get('state')
        if not user_state:
            return Response({'error': 'No state provided'}, status=400)
            
        feedback = get_feedback(user_state, diagrammar_content.correct_states)
        return Response(feedback)


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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        """
        Mark a practice set as completed and award points if score is perfect.
        """
        practice_set = self.get_object()
        score = request.data.get('score', 0)

        # Award points for perfect score
        reward = None
        if score == 100:
            reward = UserReward.award_practice_completion(
                user=request.user,
                practice_set=practice_set,
                score=score
            )

        # If practice set is associated with a lesson, mark lesson as completed
        if practice_set.lesson:
            progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                lesson=practice_set.lesson
            )
            progress.mark_as_completed(score=score)

        response_data = {
            'practice_set': practice_set.id,
            'score': score,
            'completed': True
        }

        if reward:
            response_data['reward'] = {
                'points': reward.value,
                'name': reward.reward_name
            }

        return Response(response_data)


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


# New viewsets for user progress and rewards

class UserProgressViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user progress. 
    Only authenticated users can access their own progress.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProgressSerializer

    def get_queryset(self):
        """
        Ensure users can only see their own progress.
        """
        return UserProgress.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserProgressUpdateSerializer
        return UserProgressSerializer

    @action(detail=False, methods=['get'])
    def by_course(self, request):
        """
        Get all progress entries for a specific course.
        """
        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response(
                {'error': 'course_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get all lessons for this course's modules
        lesson_progress = UserProgress.objects.filter(
            user=request.user,
            lesson__module__course=course
        )

        serializer = self.get_serializer(lesson_progress, many=True)
        return Response(serializer.data)


class CourseEnrollmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for course enrollments.
    Only authenticated users can access their own enrollments.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CourseEnrollmentSerializer

    def get_queryset(self):
        """
        Ensure users can only see their own enrollments.
        """
        return CourseEnrollment.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Enroll a user in a course.
        """
        course_id = request.data.get('course')
        if not course_id:
            return Response(
                {'error': 'course is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        enrollment = CourseEnrollment.enroll_user(request.user, course)
        serializer = self.get_serializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserRewardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing user rewards.
    Only authenticated users can access their own rewards.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserRewardSerializer

    def get_queryset(self):
        """
        Ensure users can only see their own rewards.
        """
        return UserReward.objects.filter(user=self.request.user)


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing the leaderboard.
    """
    serializer_class = LeaderboardEntrySerializer

    def get_queryset(self):
        """
        Filter leaderboard by time period and limit to top users.
        """
        time_period = self.request.query_params.get('time_period', 'all_time')
        limit = int(self.request.query_params.get('limit', 10))

        if time_period not in dict(LeaderboardEntry.TIME_PERIODS):
            time_period = 'all_time'

        return LeaderboardEntry.objects.filter(
            time_period=time_period
        ).order_by('-points')[:limit]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_rank(self, request):
        """
        Get the authenticated user's rank on the leaderboard.
        """
        time_period = request.query_params.get('time_period', 'all_time')

        if time_period not in dict(LeaderboardEntry.TIME_PERIODS):
            time_period = 'all_time'

        try:
            # Get user's entry
            user_entry = LeaderboardEntry.objects.get(
                user=request.user,
                time_period=time_period
            )

            # Count users with more points
            rank = LeaderboardEntry.objects.filter(
                time_period=time_period,
                points__gt=user_entry.points
            ).count() + 1  # Add 1 to get 1-based ranking

            # Get entries around the user's rank
            above = LeaderboardEntry.objects.filter(
                time_period=time_period,
                points__gt=user_entry.points
            ).order_by('-points').values('user__username', 'points')[:3]

            below = LeaderboardEntry.objects.filter(
                time_period=time_period,
                points__lt=user_entry.points
            ).order_by('-points').values('user__username', 'points')[:3]

            # Get user's comprehensive information
            serializer = self.get_serializer(user_entry)
            user_info = serializer.data.get('user_info')

            return Response({
                'rank': rank,
                'points': user_entry.points,
                'entries_above': list(above),
                'entries_below': list(below),
                'user_info': user_info
            })

        except LeaderboardEntry.DoesNotExist:
            # User doesn't have a leaderboard entry yet
            LeaderboardEntry.update_points(request.user)
            return Response({
                'rank': 0,
                'points': 0
            })

@api_view(['POST'])
def validate_diagrammar_state(request, problem_id):
    """
    Validates a Diagrammar state against correct answers
    """
    try:
        problem = Problem.objects.get(id=problem_id)
        if problem.question_type != 'diagrammar':
            return Response(
                {'error': 'This problem is not a Diagrammar problem'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            diagrammar_content = problem.diagrammar_content.get()
        except DiagrammarContent.DoesNotExist:
            return Response(
                {'error': 'No Diagrammar content found for this problem'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        user_state = request.data.get('state')
        if not user_state:
            return Response(
                {'error': 'No state provided in request body'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        feedback = get_feedback(user_state, diagrammar_content.correct_states)
        return Response(feedback, status=status.HTTP_200_OK)
        
    except Problem.DoesNotExist:
        return Response(
            {'error': 'Problem not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
