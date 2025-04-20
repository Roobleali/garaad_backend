from django.db import models
from django.utils.text import slugify
from django.conf import settings


class Category(models.Model):
    """
    Represents a category of courses.
    """
    id = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.CharField(max_length=255)
    in_progress = models.BooleanField(default=False)
    course_ids = models.JSONField(default=list, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "categories"


class Course(models.Model):
    """
    Represents a course within a category.
    """
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    is_new = models.BooleanField(default=False)
    progress = models.IntegerField(default=0)
    description = models.TextField()
    thumbnail = models.URLField(blank=True, null=True)
    author_id = models.CharField(max_length=255)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Lesson(models.Model):
    """
    Represents a lesson within a course. Basic lesson info.
    """
    course = models.ForeignKey(
        Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    lesson_number = models.PositiveIntegerField(default=1)
    estimated_time = models.PositiveIntegerField(
        help_text="Estimated time in minutes", default=10)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        ordering = ['course', 'lesson_number']

    def get_next_lesson(self):
        """Returns the next lesson in the course or None if this is the last lesson"""
        try:
            return Lesson.objects.filter(
                course=self.course,
                lesson_number__gt=self.lesson_number
            ).order_by('lesson_number').first()
        except Lesson.DoesNotExist:
            return None


class LessonContentBlock(models.Model):
    """
    A lesson is composed of multiple ordered content blocks
    (text, image, interactive, example, problem, etc.).
    """
    BLOCK_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('interactive', 'Interactive'),
        ('example', 'Example'),
        ('problem', 'Problem'),
        ('code', 'Code'),
    )

    lesson = models.ForeignKey(
        Lesson, related_name='content_blocks', on_delete=models.CASCADE)
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPES)
    content = models.JSONField(help_text="JSON content depends on block_type")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lesson.title} - {self.get_block_type_display()} Block #{self.order}"

    class Meta:
        ordering = ['lesson', 'order']
        verbose_name = "Lesson Content Block"
        verbose_name_plural = "Lesson Content Blocks"


class Problem(models.Model):
    """
    Reusable question entity (used in lessons or practice sets).
    """
    QUESTION_TYPES = (
        ('multiple_choice', 'Multiple Choice'),
        ('single_choice', 'Single Choice'),
        ('true_false', 'True/False'),
        ('fill_blank', 'Fill in the Blank'),
        ('matching', 'Matching'),
        ('open_ended', 'Open Ended'),
        ('math_expression', 'Math Expression'),
        ('code', 'Coding Problem'),
    )

    DIFFICULTY_LEVELS = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    )

    question_text = models.TextField()
    image = models.URLField(blank=True, null=True, help_text="URL to an image associated with the question")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    options = models.JSONField(
        null=True, blank=True, help_text="Answer options for applicable question types")
    correct_answer = models.JSONField(
        help_text="Correct answer(s) in format appropriate for question_type")
    explanation = models.TextField(
        blank=True, help_text="Explanation of the answer")
    difficulty = models.CharField(
        max_length=12, choices=DIFFICULTY_LEVELS, default='intermediate')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.question_text[:50]}..."

    class Meta:
        ordering = ['created_at']


class Hint(models.Model):
    """
    Gradual hints for a problem.
    """
    problem = models.ForeignKey(
        Problem, related_name='hints', on_delete=models.CASCADE)
    content = models.TextField()
    order = models.PositiveIntegerField(
        default=0, help_text="Order in which hints are revealed")

    def __str__(self):
        return f"Hint #{self.order} for Problem {self.problem.id}"

    class Meta:
        ordering = ['problem', 'order']
        unique_together = ['problem', 'order']


class SolutionStep(models.Model):
    """
    Step-by-step solution to a problem.
    """
    problem = models.ForeignKey(
        Problem, related_name='solution_steps', on_delete=models.CASCADE)
    explanation = models.TextField()
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Solution Step #{self.order} for Problem {self.problem.id}"

    class Meta:
        ordering = ['problem', 'order']
        unique_together = ['problem', 'order']


class PracticeSet(models.Model):
    """
    Group of extra practice problems for a lesson/course.
    """
    PRACTICE_TYPES = (
        ('lesson', 'Lesson Practice'),
        ('course', 'Course Review'),
        ('mixed', 'Mixed Practice'),
        ('challenge', 'Challenge Problems'),
    )

    DIFFICULTY_LEVELS = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('mixed', 'Mixed Levels'),
    )

    title = models.CharField(max_length=255)
    lesson = models.ForeignKey(
        Lesson, related_name='practice_sets', on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(
        Course, related_name='practice_sets', on_delete=models.CASCADE, null=True, blank=True)
    practice_type = models.CharField(max_length=20, choices=PRACTICE_TYPES)
    difficulty_level = models.CharField(
        max_length=12, choices=DIFFICULTY_LEVELS, default='intermediate')
    is_randomized = models.BooleanField(
        default=False, help_text="Whether problems should be presented in random order")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        # Ensure either lesson or course is provided, but not both
        if (self.lesson is None and self.course is None) or (self.lesson is not None and self.course is not None):
            raise ValidationError(
                "Either lesson or course must be provided, but not both.")

    def __str__(self):
        related_to = self.lesson.title if self.lesson else self.course.title
        return f"{self.title} ({related_to})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Practice Set"
        verbose_name_plural = "Practice Sets"


class PracticeSetProblem(models.Model):
    """
    Join table to assign problems to sets with ordering.
    """
    practice_set = models.ForeignKey(
        PracticeSet, related_name='practice_set_problems', on_delete=models.CASCADE)
    problem = models.ForeignKey(
        Problem, related_name='practice_set_problems', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.practice_set.title} - Problem #{self.order}"

    class Meta:
        ordering = ['practice_set', 'order']
        unique_together = ['practice_set', 'problem', 'order']
        verbose_name = "Practice Set Problem"
        verbose_name_plural = "Practice Set Problems"


# New User Progress and Rewards Models

class UserProgress(models.Model):
    """
    Tracks a user's progress on each lesson.
    """
    STATUS_CHOICES = (
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='progress', on_delete=models.CASCADE)
    lesson = models.ForeignKey(
        Lesson, related_name='user_progress', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='not_started')
    # Optional score for practice-enabled lessons
    score = models.PositiveIntegerField(blank=True, null=True)
    last_visited_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['user', 'lesson']
        verbose_name = "User Progress"
        verbose_name_plural = "User Progress"

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} ({self.status})"

    def mark_as_in_progress(self):
        """Mark lesson as in progress if not already completed"""
        if self.status != 'completed':
            self.status = 'in_progress'
            self.save()

    def mark_as_completed(self, score=None):
        """Mark lesson as completed with optional score"""
        if self.status != 'completed':
            from django.utils import timezone
            self.status = 'completed'
            if score is not None:
                self.score = score
            self.completed_at = timezone.now()
            self.save()

            # Create reward for completing a lesson
            UserReward.objects.create(
                user=self.user,
                reward_type='points',
                reward_name='Lesson Completion',
                value=10
            )

            # Update leaderboard
            LeaderboardEntry.update_points(self.user)

            # Update course enrollment progress
            CourseEnrollment.update_progress(
                self.user, self.lesson.course)


class CourseEnrollment(models.Model):
    """
    Tracks which course the user is enrolled in and their progress.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course, related_name='enrollments', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress_percent = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.progress_percent}%)"

    @classmethod
    def update_progress(cls, user, course):
        """Update progress percentage based on completed lessons"""
        # Get or create enrollment
        enrollment, created = cls.objects.get_or_create(
            user=user,
            course=course
        )

        # Count total lessons in the course
        total_lessons = Lesson.objects.filter(course=course).count()

        if total_lessons > 0:
            # Count completed lessons
            completed_lessons = UserProgress.objects.filter(
                user=user,
                lesson__course=course,
                status='completed'
            ).count()

            # Calculate percentage
            enrollment.progress_percent = int(
                (completed_lessons / total_lessons) * 100)
            enrollment.save()

            # Check if course completed (100%) - give a reward
            if enrollment.progress_percent == 100:
                UserReward.objects.create(
                    user=user,
                    reward_type='badge',
                    reward_name=f'Course Completed: {course.title}',
                    value=1
                )
                # Update leaderboard
                LeaderboardEntry.update_points(user)

        return enrollment

    @classmethod
    def enroll_user(cls, user, course):
        """Enroll a user in a course if not already enrolled"""
        enrollment, created = cls.objects.get_or_create(
            user=user,
            course=course
        )
        return enrollment


class UserReward(models.Model):
    """
    Tracks points and badges for motivational gamification.
    """
    REWARD_TYPES = (
        ('points', 'Points'),
        ('badge', 'Badge'),
        ('streak', 'Streak'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='rewards', on_delete=models.CASCADE)
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES)
    reward_name = models.CharField(max_length=255)
    value = models.PositiveIntegerField(default=0)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-awarded_at']

    def __str__(self):
        return f"{self.user.username} - {self.reward_name} ({self.value})"

    @classmethod
    def award_practice_completion(cls, user, practice_set, score):
        """Award points for completing a practice set with full marks"""
        if score == 100:
            reward = cls.objects.create(
                user=user,
                reward_type='points',
                reward_name='Perfect Score on Practice',
                value=15
            )
            # Update leaderboard
            LeaderboardEntry.update_points(user)
            return reward
        return None


class LeaderboardEntry(models.Model):
    """
    Tracks total user points for competition and visibility.
    """
    TIME_PERIODS = (
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('all_time', 'All Time'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='leaderboard_entries', on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0)
    time_period = models.CharField(max_length=20, choices=TIME_PERIODS)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'time_period']
        verbose_name = "Leaderboard Entry"
        verbose_name_plural = "Leaderboard Entries"

    def __str__(self):
        return f"{self.user.username} - {self.time_period} ({self.points} points)"

    @classmethod
    def update_points(cls, user):
        """Update leaderboard entries for all time periods for a user"""
        from django.utils import timezone
        from datetime import timedelta

        # Calculate points for each time period
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # All time points
        all_time_points = UserReward.objects.filter(
            user=user,
            reward_type='points'
        ).aggregate(total=models.Sum('value'))['total'] or 0

        # Weekly points
        weekly_points = UserReward.objects.filter(
            user=user,
            reward_type='points',
            awarded_at__gte=week_ago
        ).aggregate(total=models.Sum('value'))['total'] or 0

        # Monthly points
        monthly_points = UserReward.objects.filter(
            user=user,
            reward_type='points',
            awarded_at__gte=month_ago
        ).aggregate(total=models.Sum('value'))['total'] or 0

        # Update or create entries
        cls.objects.update_or_create(
            user=user,
            time_period='all_time',
            defaults={'points': all_time_points}
        )

        cls.objects.update_or_create(
            user=user,
            time_period='weekly',
            defaults={'points': weekly_points}
        )

        cls.objects.update_or_create(
            user=user,
            time_period='monthly',
            defaults={'points': monthly_points}
        )
