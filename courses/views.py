from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils import timezone
from datetime import timedelta
from .models import (
    Category, Course, Lesson, LessonContentBlock,
    Problem, Hint, SolutionStep,
    UserProgress, CourseEnrollment, UserReward, LeaderboardEntry,
    DailyChallenge, UserChallengeProgress, UserLevel,
    Achievement, UserAchievement,
    CulturalEvent, UserCulturalProgress, CommunityContribution,
    UserNotification
)
from leagues.models import UserLeague, League  # Import from leagues app
from .serializers import (
    CategorySerializer, CourseSerializer, CourseListSerializer,
    LessonSerializer, LessonContentBlockSerializer,
    ProblemSerializer, HintSerializer, SolutionStepSerializer,
    UserProgressSerializer, UserProgressUpdateSerializer,
    CourseEnrollmentSerializer, UserRewardSerializer,
    LeaderboardEntrySerializer, LessonWithNextSerializer,
    CourseWithProgressSerializer,
    DailyChallengeSerializer, UserChallengeProgressSerializer,
    UserLevelSerializer, AchievementSerializer, UserAchievementSerializer,
    CulturalEventSerializer, UserCulturalProgressSerializer, CommunityContributionSerializer,
    UserLeagueSerializer, LeagueSerializer, UserNotificationSerializer
)
from django.core.exceptions import ValidationError
from .services import LearningProgressService, LeagueService
from django.core.cache import cache
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from api.models import Streak


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
        Override retrieve to include problem XP information
        """
        lesson = self.get_object()
        response = super().retrieve(request, *args, **kwargs)

        # Add problem XP information
        problems = Problem.objects.filter(lesson=lesson)
        problem_xp_info = []
        for problem in problems:
            xp_value = 10
            if isinstance(problem.content, dict):
                xp_value = problem.content.get('points', 10)
            elif hasattr(problem, 'xp'):
                xp_value = problem.xp
            problem_xp_info.append({
                'id': problem.id,
                'xp_value': xp_value,
                'question_type': problem.question_type
            })
        
        response.data['problem_xp_info'] = problem_xp_info
        response.data['total_possible_xp'] = sum(p['xp_value'] for p in problem_xp_info)

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
        Calculate XP based on completed problems and update streak.
        """
        try:
            lesson = self.get_object()
            completed_problems = request.data.get('completed_problems', [])
            total_score = request.data.get('total_score', 0)

            # Ensure the user is enrolled in the course
            CourseEnrollment.enroll_user(request.user, lesson.course)

            # Calculate XP from completed problems
            problems = Problem.objects.filter(lesson=lesson)
            earned_xp = 0
            for problem in problems:
                if problem.id in completed_problems:
                    if isinstance(problem.content, dict):
                        earned_xp += problem.content.get('points', 5)
                    elif hasattr(problem, 'xp'):
                        earned_xp += problem.xp
                    else:
                        earned_xp += 5

            # Add bonus XP for perfect score
            if total_score == 100:
                earned_xp += 50  # Bonus XP for perfect score

            # Get or create progress record
            progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                lesson=lesson,
                defaults={'status': 'in_progress'}
            )

            # Update progress
            progress.mark_as_completed()
            progress.score = total_score
            progress.completed_at = timezone.now()
            progress.save()

            # Award XP and update streak
            streak, _ = Streak.objects.get_or_create(user=request.user)
            streak.award_xp(earned_xp, 'problem_completion')
            streak.update_streak(len(completed_problems), [lesson.id])

            # Check for achievements
            self._check_lesson_achievements(request.user, lesson)

            return Response({
                'status': 'success',
                'message': 'Lesson completed successfully',
                'earned_xp': earned_xp,
                'total_score': total_score,
                'streak': {
                    'current_streak': streak.current_streak,
                    'max_streak': streak.max_streak,
                    'streak_charges': streak.current_energy
                }
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _check_lesson_achievements(self, user, lesson):
        """Check and award achievements for lesson completion."""
        try:
            # Check for first lesson completion
            completed_lessons = UserProgress.objects.filter(
                user=user,
                status='completed'
            ).count()
            
            if completed_lessons == 1:
                # Award first lesson achievement
                achievement = Achievement.objects.get(
                    achievement_type='first_lesson'
                )
                UserAchievement.objects.get_or_create(
                    user=user,
                    achievement=achievement
                )
            
            # Check for course completion
            course = lesson.course
            total_lessons = course.lessons.count()
            completed_course_lessons = UserProgress.objects.filter(
                user=user,
                lesson__course=course,
                status='completed'
            ).count()
            
            if completed_course_lessons == total_lessons:
                # Award course completion achievement
                achievement = Achievement.objects.get(
                    achievement_type='course_completion'
                )
                UserAchievement.objects.get_or_create(
                    user=user,
                    achievement=achievement
                )
        except Exception as e:
            print(f"Error checking achievements: {str(e)}")
            # Don't raise the exception, just log it

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
                'content': problem.content,
                'xp_value': problem.content.get('points', problem.xp)  # Add XP value
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
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['content']
    ordering_fields = ['order']

    def get_queryset(self):
        queryset = LessonContentBlock.objects.all()
        lesson_id = self.request.query_params.get('lesson', None)
        if lesson_id is not None:
            queryset = queryset.filter(lesson_id=lesson_id)
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a new content block, with special handling for problem blocks.
        """
        try:
            # For problem blocks, ensure content is an empty dict
            if request.data.get('block_type') == 'problem':
                request.data['content'] = {}

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit_answer(self, request, pk=None):
        """
        Submit an answer to a problem and handle rewards.
        """
        problem = self.get_object()
        user = request.user
        answer = request.data.get('answer')
        
        if not answer:
            return Response(
                {'error': 'Answer is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if answer is correct
        is_correct = self._check_answer(problem, answer)
        
        # Get or create user progress for the lesson
        if problem.lesson:
            progress, created = UserProgress.objects.get_or_create(
                user=user,
                lesson=problem.lesson,
                defaults={'status': 'in_progress'}
            )

            # Update progress if answer is correct
            if is_correct:
                # Award XP for correct answer
                xp_reward = 10  # Base XP for correct answer
                user_level = UserLevel.objects.get_or_create(user=user)[0]
                user_level.add_experience(xp_reward)

                # Award streak points
                streak_reward = 5  # Base streak points
                UserReward.objects.create(
                    user=user,
                    reward_type='streak',
                    reward_name='Problem Solved',
                    value=streak_reward,
                    lesson=problem.lesson
                )

                # Update lesson progress
                progress.mark_as_completed()

                # Check for achievements
                self._check_problem_achievements(user, problem)

        return Response({
            'is_correct': is_correct,
            'xp_earned': xp_reward if is_correct else 0,
            'streak_points': streak_reward if is_correct else 0
        })

    def _check_answer(self, problem, answer):
        """
        Check if the submitted answer is correct.
        """
        if problem.question_type == 'multiple_choice':
            return answer in problem.correct_answer
        elif problem.question_type == 'single_choice':
            return answer == problem.correct_answer
        elif problem.question_type == 'true_false':
            return answer == problem.correct_answer
        elif problem.question_type == 'fill_blank':
            return answer.lower().strip() == problem.correct_answer.lower().strip()
        elif problem.question_type == 'matching':
            return set(answer) == set(problem.correct_answer)
        elif problem.question_type == 'open_ended':
            # For open-ended questions, you might want to implement more sophisticated checking
            return answer.lower().strip() in problem.correct_answer.lower().strip()
        elif problem.question_type == 'math_expression':
            # For math expressions, you might want to implement math expression comparison
            return answer == problem.correct_answer
        elif problem.question_type == 'code':
            # For code problems, you might want to implement code execution and comparison
            return answer == problem.correct_answer
        return False

    def _check_problem_achievements(self, user, problem):
        """
        Check and award achievements related to problem solving.
        """
        # Check for perfect score achievement
        if problem.lesson:
            lesson_problems = Problem.objects.filter(lesson=problem.lesson)
            solved_problems = UserProgress.objects.filter(
                user=user,
                lesson=problem.lesson,
                status='completed'
            ).count()
            
            if solved_problems == lesson_problems.count():
                achievement = Achievement.objects.filter(
                    achievement_type='perfect_score',
                    level_required__lte=user.level.level
                ).first()
                
                if achievement:
                    UserAchievement.objects.get_or_create(
                        user=user,
                        achievement=achievement
                    )


class UserProgressViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user progress. 
    Only authenticated users can access their own progress.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProgressSerializer
    queryset = UserProgress.objects.none()  # Required for DRF router

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
    queryset = CourseEnrollment.objects.none()

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
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['reward_name', 'lesson__title', 'course__title']
    ordering_fields = ['awarded_at', 'value']
    queryset = UserReward.objects.none()

    def get_queryset(self):
        """
        Ensure users can only see their own rewards.
        Optionally filter by lesson or course.
        """
        queryset = UserReward.objects.filter(user=self.request.user)
        
        # Filter by lesson
        lesson_id = self.request.query_params.get('lesson_id')
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)
            
        # Filter by course
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
            
        return queryset


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing the leaderboard.
    """
    serializer_class = LeaderboardEntrySerializer
    queryset = LeaderboardEntry.objects.none()

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


class DailyChallengeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing daily challenges.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DailyChallengeSerializer
    queryset = DailyChallenge.objects.none()

    def get_queryset(self):
        """Get today's challenge and past challenges"""
        today = timezone.now().date()
        return DailyChallenge.objects.filter(challenge_date__lte=today)

    @action(detail=True, methods=['post'])
    def submit_attempt(self, request, pk=None):
        """Submit an attempt for a daily challenge"""
        challenge = self.get_object()
        progress, created = UserChallengeProgress.objects.get_or_create(
            user=request.user,
            challenge=challenge
        )
        
        if progress.completed:
            return Response(
                {"detail": "Challenge already completed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Increment attempts
        progress.attempts += 1
        
        # Check if the attempt is correct (implement your logic here)
        is_correct = True  # Replace with actual validation
        
        if is_correct:
            progress.completed = True
            progress.completed_at = timezone.now()
            progress.score = challenge.points_reward
            
            # Award points and update level
            UserReward.award_challenge_completion(
                request.user, challenge, progress.score
            )
            
            # Check for achievements
            self._check_challenge_achievements(request.user)
        
        progress.save()
        return Response(UserChallengeProgressSerializer(progress).data)

    def _check_challenge_achievements(self, user):
        """Check and award achievements related to challenges"""
        completed_challenges = UserChallengeProgress.objects.filter(
            user=user, completed=True
        ).count()
        
        # Award achievements based on number of completed challenges
        if completed_challenges == 1:
            self._award_achievement(user, 'first_challenge')
        elif completed_challenges == 7:
            self._award_achievement(user, 'weekly_challenge_master')
        elif completed_challenges == 30:
            self._award_achievement(user, 'monthly_challenge_master')

    def _award_achievement(self, user, achievement_type):
        """Award an achievement to a user"""
        try:
            achievement = Achievement.objects.get(
                achievement_type=achievement_type
            )
            UserAchievement.objects.get_or_create(
                user=user,
                achievement=achievement
            )
        except Achievement.DoesNotExist:
            pass


class UserLevelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user levels and experience.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserLevelSerializer
    queryset = UserLevel.objects.none()

    def get_queryset(self):
        return UserLevel.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get the top users by level"""
        top_users = UserLevel.objects.order_by('-level', '-experience_points')[:10]
        return Response(UserLevelSerializer(top_users, many=True).data)


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing achievements.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AchievementSerializer
    queryset = Achievement.objects.none()

    def get_queryset(self):
        user_level = UserLevel.objects.get(user=self.request.user)
        return Achievement.objects.filter(level_required__lte=user_level.level)

    @action(detail=False, methods=['get'])
    def user_achievements(self, request):
        """Get achievements earned by the current user"""
        achievements = UserAchievement.objects.filter(user=request.user)
        return Response(UserAchievementSerializer(achievements, many=True).data)


class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user achievements (earned achievements).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserAchievementSerializer
    queryset = UserAchievement.objects.none()

    def get_queryset(self):
        return UserAchievement.objects.filter(user=self.request.user)


class CulturalEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing cultural events.
    """
    serializer_class = CulturalEventSerializer
    permission_classes = [IsAuthenticated]
    queryset = CulturalEvent.objects.none()

    def get_queryset(self):
        """Get active cultural events"""
        return CulturalEvent.objects.filter(
            is_active=True,
            event_date__gte=timezone.now().date()
        )

    @action(detail=True, methods=['post'])
    def participate(self, request, pk=None):
        """Participate in a cultural event"""
        event = self.get_object()
        progress, created = UserCulturalProgress.objects.get_or_create(
            user=request.user,
            event=event
        )
        
        if progress.completed:
            return Response(
                {"detail": "Already participated in this event"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark as completed and award points
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.points_earned = event.points_reward
        progress.save()
        
        # Update user level
        user_level = UserLevel.objects.get(user=request.user)
        user_level.add_experience(event.points_reward)
        
        return Response(UserCulturalProgressSerializer(progress).data)


class CommunityContributionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing community contributions.
    """
    serializer_class = CommunityContributionSerializer
    permission_classes = [IsAuthenticated]
    queryset = CommunityContribution.objects.none()

    def get_queryset(self):
        """Get user's contributions"""
        return CommunityContribution.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a new contribution"""
        contribution = serializer.save(user=self.request.user)
        
        # Award points based on contribution type
        points = {
            'content': 50,
            'translation': 75,
            'help': 100,
            'feedback': 25,
            'cultural': 150
        }.get(contribution.contribution_type, 0)
        
        contribution.points_awarded = points
        contribution.save()
        
        # Update user level
        user_level = UserLevel.objects.get(user=self.request.user)
        user_level.add_experience(points)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a contribution (admin only)"""
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff can verify contributions"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        contribution = self.get_object()
        contribution.verified = True
        contribution.verified_by = request.user
        contribution.save()
        
        # Award bonus points for verification
        bonus_points = 50
        contribution.points_awarded += bonus_points
        contribution.save()
        
        # Update user level
        user_level = UserLevel.objects.get(user=contribution.user)
        user_level.add_experience(bonus_points)
        
        return Response(CommunityContributionSerializer(contribution).data)


class UserChallengeProgressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user challenge progress.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserChallengeProgressSerializer
    queryset = UserChallengeProgress.objects.none()

    def get_queryset(self):
        """
        Return challenge progress for the authenticated user.
        """
        return UserChallengeProgress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Create a new challenge progress entry for the authenticated user.
        """
        serializer.save(user=self.request.user)


class LeagueViewSet(viewsets.ViewSet):
    """
    ViewSet for managing leagues and streaks.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get current user's league status"""
        try:
            user_league = UserLeague.objects.get(user=request.user)
            serializer = UserLeagueSerializer(user_league)
            return Response(serializer.data)
        except UserLeague.DoesNotExist:
            # Create new league entry if doesn't exist
            user_league = LeagueService._get_or_create_user_league(request.user)
            serializer = UserLeagueSerializer(user_league)
            return Response(serializer.data)

    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    @method_decorator(vary_on_cookie)  # Vary cache by user
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get leaderboard standings with caching"""
        time_period = request.query_params.get('time_period', 'weekly')
        league_id = request.query_params.get('league')
        
        # Generate cache key
        cache_key = f'leaderboard_{time_period}_{league_id}'
        user_rank_key = f'user_rank_{request.user.id}_{time_period}_{league_id}'
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        cached_rank = cache.get(user_rank_key)
        
        if cached_data and cached_rank is not None:
            return Response({
                'standings': cached_data,
                'my_rank': cached_rank
            })
        
        # If not in cache, get from database
        entries = LeaderboardEntry.objects.filter(time_period=time_period)
        if league_id:
            # Get all users in the specified league
            league_users = UserLeague.objects.filter(current_league_id=league_id).values_list('user_id', flat=True)
            # Filter leaderboard entries by those users
            entries = entries.filter(user_id__in=league_users)
        
        entries = entries.order_by('-points')[:100]  # Top 100
        serializer = LeaderboardEntrySerializer(entries, many=True)
        
        # Calculate user's rank
        try:
            user_entry = LeaderboardEntry.objects.get(
                user=request.user,
                time_period=time_period
            )
            user_rank = LeaderboardEntry.objects.filter(
                time_period=time_period,
                points__gt=user_entry.points
            ).count() + 1
        except LeaderboardEntry.DoesNotExist:
            user_rank = 0
        
        # Prepare response data
        response_data = {
            'standings': serializer.data,
            'my_rank': user_rank
        }
        
        # Cache the results
        cache.set(cache_key, serializer.data, 60 * 5)  # Cache for 5 minutes
        cache.set(user_rank_key, user_rank, 60 * 5)  # Cache for 5 minutes
        
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def streak(self, request):
        """Get user's streak information"""
        try:
            user_league = UserLeague.objects.get(user=request.user)
            return Response({
                'current_streak': user_league.current_streak,
                'max_streak': user_league.max_streak,
                'streak_charges': user_league.streak_charges,
                'last_activity': user_league.last_activity_date
            })
        except UserLeague.DoesNotExist:
            return Response({
                'current_streak': 0,
                'max_streak': 0,
                'streak_charges': 0,
                'last_activity': None
            })

    @action(detail=False, methods=['post'])
    def use_streak_charge(self, request):
        """Use a streak charge to maintain streak"""
        try:
            user_league = UserLeague.objects.get(user=request.user)
            if user_league.use_streak_charge():
                return Response({
                    'success': True,
                    'message': 'Waad ku mahadsantahay ilaalinta xariggaaga',
                    'remaining_charges': user_league.streak_charges
                })
            return Response({
                'success': False,
                'message': 'Ma haysato charge xarig ah'
            }, status=status.HTTP_400_BAD_REQUEST)
        except UserLeague.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Ma jiraan league-kaaga'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def achievements(self, request):
        """Get user's achievements"""
        achievements = UserAchievement.objects.filter(user=request.user)
        serializer = UserAchievementSerializer(achievements, many=True)
        return Response(serializer.data)


class UserCulturalProgressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user cultural progress.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserCulturalProgressSerializer
    queryset = UserCulturalProgress.objects.none()

    def get_queryset(self):
        return UserCulturalProgress.objects.filter(user=self.request.user)


class UserNotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserNotificationSerializer
    queryset = UserNotification.objects.none()

    def get_queryset(self):
        return UserNotification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'message': 'All notifications marked as read'})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})
