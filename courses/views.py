from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils import timezone
from .models import (
    Category, Course, Lesson, LessonContentBlock,
    Problem, Hint, SolutionStep,
    UserProgress, CourseEnrollment, UserReward, LeaderboardEntry
)
from .serializers import (
    CategorySerializer, CourseSerializer, CourseListSerializer,
    LessonSerializer, LessonContentBlockSerializer,
    ProblemSerializer, HintSerializer, SolutionStepSerializer,
    UserProgressSerializer, UserProgressUpdateSerializer,
    CourseEnrollmentSerializer, UserRewardSerializer,
    LeaderboardEntrySerializer, LessonWithNextSerializer,
    CourseWithProgressSerializer
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


class LessonViewSet(viewsets.ModelViewSet):
    """
    API endpoint for lessons.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

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
        course_id = self.request.query_params.get('course', None)
        if course_id is not None:
            queryset = queryset.filter(course_id=course_id)
        return queryset

    def get_object(self):
        """
        Override to ensure lesson belongs to the specified course
        """
        course_id = self.request.query_params.get('course', None)
        if not course_id:
            return super().get_object()

        lesson = super().get_object()
        if str(lesson.course_id) != str(course_id):
            raise Http404("Lesson not found in this course")
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
            CourseEnrollment.enroll_user(request.user, lesson.course)

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
        CourseEnrollment.enroll_user(request.user, lesson.course)

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

    @action(detail=True, methods=['get'])
    def content(self, request, pk=None):
        """
        Get all content (blocks and problems) for a lesson in order.
        """
        lesson = self.get_object()
        
        # Get all content blocks and problems
        blocks = LessonContentBlock.objects.filter(lesson=lesson).order_by('order')
        problems = Problem.objects.filter(lesson=lesson).order_by('order')
        
        # Combine and sort by order
        content = []
        for block in blocks:
            content.append({
                'type': 'block',
                'id': block.id,
                'order': block.order,
                'block_type': block.block_type,
                'content': block.content
            })
        
        for problem in problems:
            content.append({
                'type': 'problem',
                'id': problem.id,
                'order': problem.order,
                'question_type': problem.question_type,
                'question_text': problem.question_text,
                'content': problem.content
            })
        
        # Sort by order
        content.sort(key=lambda x: x['order'])
        
        return Response(content)

    @action(detail=True, methods=['get'])
    def next_content(self, request, pk=None):
        """
        Get the next content item after the specified order.
        """
        lesson = self.get_object()
        current_order = request.query_params.get('order', 0)
        
        # Get next block or problem
        next_block = LessonContentBlock.objects.filter(
            lesson=lesson, order__gt=current_order
        ).order_by('order').first()
        
        next_problem = Problem.objects.filter(
            lesson=lesson, order__gt=current_order
        ).order_by('order').first()
        
        # Determine which is next
        if next_block and next_problem:
            next_item = next_block if next_block.order < next_problem.order else next_problem
        else:
            next_item = next_block or next_problem
        
        if not next_item:
            return Response({'detail': 'No more content'}, status=status.HTTP_404_NOT_FOUND)
        
        if isinstance(next_item, LessonContentBlock):
            return Response({
                'type': 'block',
                'id': next_item.id,
                'order': next_item.order,
                'block_type': next_item.block_type,
                'content': next_item.content
            })
        else:
            return Response({
                'type': 'problem',
                'id': next_item.id,
                'order': next_item.order,
                'question_type': next_item.question_type,
                'question_text': next_item.question_text,
                'content': next_item.content
            })

    @action(detail=True, methods=['get'])
    def previous_content(self, request, pk=None):
        """
        Get the previous content item before the specified order.
        """
        lesson = self.get_object()
        current_order = request.query_params.get('order', 0)
        
        # Get previous block or problem
        prev_block = LessonContentBlock.objects.filter(
            lesson=lesson, order__lt=current_order
        ).order_by('-order').first()
        
        prev_problem = Problem.objects.filter(
            lesson=lesson, order__lt=current_order
        ).order_by('-order').first()
        
        # Determine which is previous
        if prev_block and prev_problem:
            prev_item = prev_block if prev_block.order > prev_problem.order else prev_problem
        else:
            prev_item = prev_block or prev_problem
        
        if not prev_item:
            return Response({'detail': 'No previous content'}, status=status.HTTP_404_NOT_FOUND)
        
        if isinstance(prev_item, LessonContentBlock):
            return Response({
                'type': 'block',
                'id': prev_item.id,
                'order': prev_item.order,
                'block_type': prev_item.block_type,
                'content': prev_item.content
            })
        else:
            return Response({
                'type': 'problem',
                'id': prev_item.id,
                'order': prev_item.order,
                'question_type': prev_item.question_type,
                'question_text': prev_item.question_text,
                'content': prev_item.content
            })


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
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
