from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


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
    A lesson is composed of multiple ordered content blocks.
    Each block can be text, code, image, etc., or can reference a problem.
    This is the central model for organizing lesson content.
    """
    BLOCK_TYPES = [
        ('text', 'Text Block'),
        ('example', 'Example Block'),
        ('code', 'Code Block'),
        ('image', 'Image Block'),
        ('video', 'Video Block'),
        ('quiz', 'Quiz Block'),
        ('problem', 'Problem Block'),  # References Problem model
    ]

    lesson = models.ForeignKey(
        Lesson, related_name='content_blocks', on_delete=models.CASCADE)
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPES)
    order = models.PositiveIntegerField(default=0)
    content = models.JSONField(default=dict, blank=True, null=True)
    problem = models.ForeignKey(
        'Problem', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        help_text="Reference to a Problem for problem-type blocks"
    )

    class Meta:
        ordering = ['lesson', 'order']
        verbose_name = "Lesson Content Block"
        verbose_name_plural = "Lesson Content Blocks"

    # Default content for different block types
    default_content = {
        'text': {
            'text': '',
            'format': 'markdown'
        },
        'example': {
            'title': '',
            'description': '',
            'code': '',
            'language': 'python',
            'explanation': None
        },
        'code': {
            'code': '',
            'language': 'python',
            'explanation': None
        },
        'image': {
            'url': '',
            'caption': None,
            'width': None,
            'height': None,
            'alt_text': None
        },
        'video': {
            'url': '',
            'title': '',
            'description': None,
            'duration': None
        },
        'quiz': {
            'question': '',
            'options': [],
            'correct_answer': 0,
            'explanation': None
        },
        'problem': {
            'introduction': '',
            'show_hints': True,
            'show_solution': False,
            'attempts_allowed': 3,
            'points': 10
        }
    }

    # Content validators for each block type
    type_validators = {
        'text': {
            'text': str,
            'format': str
        },
        'example': {
            'title': str,
            'description': str,
            'code': str,
            'language': str,
            'explanation': (str, type(None))
        },
        'code': {
            'code': str,
            'language': str,
            'explanation': (str, type(None))
        },
        'image': {
            'url': str,
            'caption': (str, type(None)),
            'width': (int, type(None)),
            'height': (int, type(None)),
            'alt_text': (str, type(None))
        },
        'video': {
            'url': str,
            'title': str,
            'description': (str, type(None)),
            'duration': (int, type(None))
        },
        'quiz': {
            'question': str,
            'options': list,
            'correct_answer': int,
            'explanation': (str, type(None))
        },
        'problem': {
            'introduction': str,
            'show_hints': bool,
            'show_solution': bool,
            'attempts_allowed': int,
            'points': int
        }
    }

    @property
    def default_problem_content(self):
        """Default content structure for problem blocks"""
        return {
            "introduction": "",  # Optional text to show before the problem
            "show_hints": True,  # Whether to show hints button
            "show_solution": False,  # Whether to show solution button
            "attempts_allowed": 3,  # Number of attempts allowed
            "points": 10  # Points awarded for correct solution
        }

    def get_complete_content(self):
        """
        Get the complete content for this block, including problem data if it's a problem block
        """
        if self.block_type == 'problem' and self.problem:
            return {
                # Include the display settings from content
                "introduction": self.content.get('introduction', ''),
                "show_hints": self.content.get('show_hints', True),
                "show_solution": self.content.get('show_solution', False),
                "attempts_allowed": self.content.get('attempts_allowed', 3),
                "points": self.content.get('points', 10),
                # Include the actual problem data
                "problem_data": {
                    "id": self.problem.id,
                    "question_text": self.problem.question_text,
                    "question_type": self.problem.question_type,
                    "options": self.problem.options,
                    "content": self.problem.content,
                    "diagram_config": self.problem.diagram_config if self.problem.question_type == 'diagram' else None
                }
            }
        return self.content

    def clean(self):
        """Validate the model before saving"""
        super().clean()
        
        # Ensure content is a dictionary
        if not isinstance(self.content, dict):
            raise ValidationError({
                'content': 'Content must be a dictionary'
            })
            
        # Initialize content if empty
        if not self.content:
            self.content = {}
            
        # Validate content structure
        self.validate_content()
        
        return self.content

    def validate_content(self):
        """Validate content structure based on block_type"""
        if not isinstance(self.content, dict):
            raise ValidationError({
                'content': 'Content must be a dictionary'
            })

        # Get validators for this block type
        validators = self.type_validators.get(self.block_type)
        if not validators:
            return  # No specific validation for this block type

        # Merge with default content
        default_content = self.default_content.get(self.block_type, {})
        for key, value in default_content.items():
            if key not in self.content:
                self.content[key] = value

        # Validate types for each field
        for field, expected_type in validators.items():
            if field not in self.content:
                raise ValidationError({
                    'content': f'Missing required field: {field}'
                })

            value = self.content[field]
            
            # Handle fields that can accept multiple types
            if isinstance(expected_type, tuple):
                if not any(isinstance(value, t) for t in expected_type if t is not type(None) or value is None):
                    type_names = ' or '.join(t.__name__ for t in expected_type)
                    raise ValidationError({
                        'content': f'Field {field} must be of type {type_names}'
                    })
            else:
                if not isinstance(value, expected_type):
                    raise ValidationError({
                        'content': f'Field {field} must be of type {expected_type.__name__}'
                    })

    def save(self, *args, **kwargs):
        """
        Override save method to validate content before saving
        """
        if not self.content:
            # Initialize with default content for the block type
            self.content = self.default_content.get(self.block_type, {})
        else:
            # Validate content
            self.validate_content()
            # Merge with default content
            default = self.default_content.get(self.block_type, {})
            self.content = {**default, **self.content}
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.lesson.title} - {self.get_block_type_display()} Block #{self.order}"


def get_default_content():
    return {
        "metadata": {
            "difficulty": "medium",
            "estimated_time": 10,
            "tags": ["algebra", "equations"]
        },
        "hints": [
            {
                "text": "Consider breaking down the problem into smaller steps",
                "order": 1
            }
        ],
        "steps": [
            {
                "text": "First, identify the known variables",
                "order": 1
            },
            {
                "text": "Then, set up the equation",
                "order": 2
            }
        ],
        "feedback": {
            "correct": "Great job! You've mastered this concept.",
            "incorrect": "Let's review the steps and try again."
        }
    }

def get_default_diagram_config():
    return {
        "type": "scale-weight",
        "parameters": {
            "weight": 40,
            "items": [
                {
                    "type": "square",
                    "count": 4,
                    "color": "#3498db",
                    "size": 20
                }
            ],
            "scale": {
                "width": 300,
                "height": 200,
                "color": "#2c3e50"
            }
        },
        "interactive": True,
        "controls": [
            {
                "type": "slider",
                "name": "weight",
                "label": "Total Weight",
                "min": 0,
                "max": 100,
                "step": 1,
                "default": 40
            },
            {
                "type": "slider",
                "name": "items_count",
                "label": "Number of Items",
                "min": 1,
                "max": 10,
                "step": 1,
                "default": 4
            }
        ],
        "animations": {
            "weight_change": {
                "duration": 500,
                "easing": "easeInOut"
            },
            "item_addition": {
                "duration": 300,
                "easing": "easeOut"
            }
        },
        "styles": {
            "background": "#f8f9fa",
            "text_color": "#2c3e50",
            "font_family": "Arial, sans-serif",
            "font_size": "14px"
        }
    }

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
        ('diagram', 'Diagram Problem'),
    )

    lesson = models.ForeignKey(
        Lesson, related_name='problems', on_delete=models.CASCADE, null=True, blank=True)
    which = models.TextField(blank=True, null=True, help_text="Additional text field before question")
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    options = models.JSONField(
        null=True, blank=True, help_text="Answer options for applicable question types")
    correct_answer = models.JSONField(
        help_text="Correct answer(s) in format appropriate for question_type")
    explanation = models.TextField(
        blank=True, help_text="Explanation of the answer")
    order = models.PositiveIntegerField(default=0)
    content = models.JSONField(default=dict, blank=True, null=True)
    diagram_config = models.JSONField(default=get_default_diagram_config, blank=True)
    img = models.URLField(blank=True, null=True, help_text="URL of an image associated with the problem")
    xp = models.PositiveIntegerField(default=10, help_text="XP awarded for solving this problem")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['lesson', 'order']
        unique_together = ['lesson', 'order']

    def clean(self):
        """
        Validate the problem data before saving
        """
        super().clean()
        
        # Initialize empty fields if needed
        if not self.content or self.content == []:
            self.content = {}
        
        # Validate multiple choice questions
        if self.question_type in ['multiple_choice', 'single_choice']:
            # Initialize options and correct_answer if empty
            if not self.options:
                self.options = []
            if not self.correct_answer:
                self.correct_answer = []
            
            # Validate options
            if not self.options:
                raise ValidationError({
                    'options': 'Options are required for multiple choice questions'
                })
            
            # Validate each option
            for option in self.options:
                if not isinstance(option, dict):
                    raise ValidationError({
                        'options': 'Each option must be a dictionary'
                    })
                if 'id' not in option or 'text' not in option:
                    raise ValidationError({
                        'options': 'Each option must have an id and text field'
                    })
            
            # Validate correct_answer
            if not self.correct_answer:
                raise ValidationError({
                    'correct_answer': 'Correct answer is required for multiple choice questions'
                })
            
            # For single choice, ensure only one correct answer
            if self.question_type == 'single_choice' and len(self.correct_answer) > 1:
                raise ValidationError({
                    'correct_answer': 'Single choice questions can only have one correct answer'
                })
            
            # Validate correct_answer IDs exist in options
            option_ids = {opt.get('id') for opt in self.options}
            for answer in self.correct_answer:
                if not isinstance(answer, dict):
                    raise ValidationError({
                        'correct_answer': 'Each answer must be a dictionary'
                    })
                if 'id' not in answer:
                    raise ValidationError({
                        'correct_answer': 'Each answer must have an id field'
                    })
                if answer.get('id') not in option_ids:
                    raise ValidationError({
                        'correct_answer': f"Answer ID '{answer.get('id')}' not found in options"
                    })

    def save(self, *args, **kwargs):
        if not self.order and self.lesson:
            # Get the highest order number for this lesson
            last_order = Problem.objects.filter(lesson=self.lesson).aggregate(
                models.Max('order'))['order__max'] or 0
            # Get the highest order number from content blocks
            last_content_order = LessonContentBlock.objects.filter(
                lesson=self.lesson).aggregate(models.Max('order'))['order__max'] or 0
            # Set order to the next available number
            self.order = max(last_order, last_content_order) + 1
        
        # Initialize content if empty or None
        if self.content is None or self.content == []:
            self.content = {}
        
        # Initialize diagram_config if it's a diagram problem
        if self.question_type == 'diagram' and not self.diagram_config:
            self.diagram_config = get_default_diagram_config()
        
        # Run validation
        self.clean()
        
        super().save(*args, **kwargs)

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
    score = models.PositiveIntegerField(blank=True, null=True)
    last_visited_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    problems_solved = models.PositiveIntegerField(default=0)
    total_xp_earned = models.PositiveIntegerField(default=0)
    streak_updated = models.BooleanField(default=False)

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
        """Mark the lesson as completed and award XP"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if score is not None:
            self.score = score
        
        # Calculate total XP from solved problems
        solved_problems = Problem.objects.filter(
            lesson=self.lesson,
            userproblem__user=self.user,
            userproblem__solved=True
        )
        self.total_xp_earned = sum(problem.xp for problem in solved_problems)
        
        self.save()
        
        # Update user's streak and XP
        streak, _ = Streak.objects.get_or_create(user=self.user)
        streak.award_xp(self.total_xp_earned, 'lesson_completion')
        
        # Update course progress
        CourseEnrollment.update_progress(self.user, self.lesson.course)


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
                    value=1,
                    course=course
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
        ('achievement', 'Achievement'),
        ('challenge', 'Challenge'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='rewards', on_delete=models.CASCADE)
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES)
    reward_name = models.CharField(max_length=255)
    value = models.PositiveIntegerField(default=0)
    awarded_at = models.DateTimeField(auto_now_add=True)
    lesson = models.ForeignKey(
        'Lesson', related_name='rewards', on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(
        'Course', related_name='rewards', on_delete=models.SET_NULL, null=True, blank=True)
    challenge = models.ForeignKey(
        'DailyChallenge', related_name='rewards', on_delete=models.SET_NULL, null=True, blank=True)
    achievement = models.ForeignKey(
        'Achievement', related_name='rewards', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-awarded_at']

    def __str__(self):
        return f"{self.user.username} - {self.reward_name}"

    @classmethod
    def award_practice_completion(cls, user, practice_set, score):
        """Award points for completing a practice set with full marks"""
        if score == 100:
            reward = cls.objects.create(
                user=user,
                reward_type='points',
                reward_name='Perfect Score on Practice',
                value=15,
                lesson=practice_set.lesson if hasattr(practice_set, 'lesson') else None,
                course=practice_set.lesson.course if hasattr(practice_set, 'lesson') else None
            )
            # Update leaderboard
            LeaderboardEntry.update_points(user)
            return reward
        return None

    @classmethod
    def award_challenge_completion(cls, user, challenge, score):
        """Award points for completing a daily challenge"""
        reward = cls.objects.create(
            user=user,
            reward_type='challenge',
            reward_name=f"Daily Challenge: {challenge.title}",
            value=challenge.points_reward,
            challenge=challenge
        )
        # Update user level experience
        user_level, _ = UserLevel.objects.get_or_create(user=user)
        user_level.add_experience(challenge.points_reward)
        return reward


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

# Default content structures for different block types
default_content = {
    'text': {
        'text': '',
        'style': None
    },
    'example': {
        'title': '',
        'description': '',
        'code': '',
        'language': 'python',
        'explanation': None
    },
    'code': {
        'code': '',
        'language': 'python',
        'explanation': None
    },
    'image': {
        'url': '',
        'caption': None,
        'width': None,
        'height': None,
        'alt_text': None
    },
    'video': {
        'url': '',
        'title': '',
        'description': None,
        'duration': None
    },
    'quiz': {
        'question': '',
        'options': [],
        'correct_answer': 0,
        'explanation': None
    }
}

# Block type specific content validators
content_validators = {
    'text': {
        'text': str,
        'style': (str, type(None))
    },
    'example': {
        'title': str,
        'description': str,
        'code': str,
        'language': str,
        'explanation': (str, type(None))
    },
    'code': {
        'code': str,
        'language': str,
        'explanation': (str, type(None))
    },
    'image': {
        'url': str,
        'caption': (str, type(None)),
        'width': (int, type(None)),
        'height': (int, type(None)),
        'alt_text': (str, type(None))
    },
    'video': {
        'url': str,
        'title': str,
        'description': (str, type(None)),
        'duration': (int, type(None))
    },
    'quiz': {
        'question': str,
        'options': list,
        'correct_answer': int,
        'explanation': (str, type(None))
    }
}

def validate_content(self, content):
    """
    Validates the content structure based on block type.
    """
    if not isinstance(content, dict):
        raise ValidationError('Content must be a dictionary')

    block_type = content.get('block_type')
    if not block_type:
        raise ValidationError('block_type is required')

    if block_type not in self.default_content:
        raise ValidationError(f'Invalid block_type: {block_type}')

    # Get validators for this block type
    validators = self.content_validators[block_type]
    default = self.default_content[block_type]

    # Merge with defaults for any missing fields
    content_data = {**default, **content}

    # Validate each field's type
    for field, expected_type in validators.items():
        value = content_data.get(field)
        
        if isinstance(expected_type, tuple):
            # Handle fields that can accept multiple types
            if value is not None and not isinstance(value, expected_type):
                raise ValidationError(
                    f'Field {field} must be one of types {expected_type}, got {type(value)}'
                )
        else:
            # Handle fields with a single expected type
            if not isinstance(value, expected_type):
                raise ValidationError(
                    f'Field {field} must be of type {expected_type}, got {type(value)}'
                )

    return content_data

class DailyChallenge(models.Model):
    """
    Daily challenges that users can complete for extra points and rewards.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    challenge_date = models.DateField(unique=True)
    points_reward = models.PositiveIntegerField(default=50)
    problem = models.ForeignKey(
        Problem, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Optional problem to solve for the challenge"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional course to complete for the challenge"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional lesson to complete for the challenge"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-challenge_date']
        verbose_name = "Daily Challenge"
        verbose_name_plural = "Daily Challenges"

    def __str__(self):
        return f"{self.title} - {self.challenge_date}"

class UserChallengeProgress(models.Model):
    """
    Tracks user progress on daily challenges.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='challenge_progress', 
        on_delete=models.CASCADE
    )
    challenge = models.ForeignKey(
        DailyChallenge, 
        related_name='user_progress', 
        on_delete=models.CASCADE
    )
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(default=0)
    attempts = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['user', 'challenge']
        verbose_name = "User Challenge Progress"
        verbose_name_plural = "User Challenge Progress"

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"

class UserLevel(models.Model):
    """
    Tracks user levels and experience points.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='level',
        on_delete=models.CASCADE
    )
    level = models.PositiveIntegerField(default=1)
    experience_points = models.PositiveIntegerField(default=0)
    experience_to_next_level = models.PositiveIntegerField(default=100)
    last_level_up = models.DateTimeField(auto_now=True)
    clan = models.CharField(max_length=100, blank=True, null=True, help_text="User's clan affiliation")
    region = models.CharField(max_length=100, blank=True, null=True, help_text="User's region in Somalia")
    language_preference = models.CharField(
        max_length=10,
        choices=[('so', 'Somali'), ('en', 'English')],
        default='so'
    )

    def __str__(self):
        return f"{self.user.username} - Level {self.level}"

    def add_experience(self, points):
        """Add experience points and handle level ups"""
        self.experience_points += points
        while self.experience_points >= self.experience_to_next_level:
            self.level_up()
        self.save()

    def level_up(self):
        """Handle level up logic"""
        self.level += 1
        self.experience_points -= self.experience_to_next_level
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
        self.last_level_up = timezone.now()

class CommunityContribution(models.Model):
    """
    Tracks user contributions to the community.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='contributions',
        on_delete=models.CASCADE
    )
    contribution_type = models.CharField(
        max_length=50,
        choices=[
            ('content', 'Educational Content'),
            ('translation', 'Translation'),
            ('help', 'Helping Others'),
            ('feedback', 'Platform Feedback'),
            ('cultural', 'Cultural Content')
        ]
    )
    description = models.TextField()
    points_awarded = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='verified_contributions'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.contribution_type}"

class CulturalEvent(models.Model):
    """
    Tracks cultural events and celebrations.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    event_date = models.DateField()
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('holiday', 'Holiday'),
            ('celebration', 'Celebration'),
            ('competition', 'Competition'),
            ('workshop', 'Workshop')
        ]
    )
    points_reward = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-event_date']

    def __str__(self):
        return f"{self.name} - {self.event_date}"

class UserCulturalProgress(models.Model):
    """
    Tracks user progress in cultural activities.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='cultural_progress',
        on_delete=models.CASCADE
    )
    event = models.ForeignKey(
        CulturalEvent,
        related_name='participants',
        on_delete=models.CASCADE
    )
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    points_earned = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['user', 'event']

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"

class Achievement(models.Model):
    """
    Defines achievements that users can earn.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    icon = models.CharField(max_length=255, help_text="Icon identifier for the achievement")
    points_reward = models.PositiveIntegerField(default=100)
    level_required = models.PositiveIntegerField(default=1)
    achievement_type = models.CharField(
        max_length=50,
        choices=[
            ('course_completion', 'Course Completion'),
            ('streak_milestone', 'Streak Milestone'),
            ('challenge_completion', 'Challenge Completion'),
            ('level_milestone', 'Level Milestone'),
            ('perfect_score', 'Perfect Score'),
            ('early_adopter', 'Early Adopter'),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['level_required', 'points_reward']

    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    """
    Tracks which achievements users have earned.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='achievements',
        on_delete=models.CASCADE
    )
    achievement = models.ForeignKey(
        Achievement,
        related_name='user_achievements',
        on_delete=models.CASCADE
    )
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'achievement']
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"

class UserNotification(models.Model):
    """
    Handles user notifications for streaks, achievements, and learning reminders
    """
    NOTIFICATION_TYPES = (
        ('streak_reminder', 'Streak Reminder'),
        ('achievement_earned', 'Achievement Earned'),
        ('daily_goal', 'Daily Goal Reminder'),
        ('league_update', 'League Update'),
        ('challenge_available', 'Challenge Available'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notifications', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)  # For email notifications
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)  # For scheduled notifications

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.notification_type} - {self.created_at}"

    @classmethod
    def create_streak_reminder(cls, user, streak_count):
        """Create a streak reminder notification"""
        from django.utils import timezone
        
        # Calculate user's local midnight
        user_profile = user.student_profile
        preferred_times = user_profile.get_preferred_study_time()
        
        # Default to evening if no preference set
        reminder_hour = 20  # 8 PM default
        if preferred_times:
            # Use the last preferred time slot as reminder
            reminder_hour = int(preferred_times[-1].split(':')[0])
        
        # Schedule notification 2 hours before preferred time
        scheduled_time = timezone.now().replace(
            hour=max(0, reminder_hour - 2),
            minute=0,
            second=0,
            microsecond=0
        )
        
        return cls.objects.create(
            user=user,
            notification_type='streak_reminder',
            title='Ilaaligaaga Waxbarashada!',
            message=f'Waxaa kuu hadhay {streak_count} maalmood oo aad ilaalisid. Soo gal maanta oo dhammaystir casharkaaga!',
            scheduled_for=scheduled_time
        )

    @classmethod
    def create_achievement_notification(cls, user, achievement):
        """Create an achievement earned notification"""
        return cls.objects.create(
            user=user,
            notification_type='achievement_earned',
            title=f'Hambalyo! {achievement.name}',
            message=f'Waad dhammaystirtay "{achievement.description}". Waad heshay {achievement.points_reward} dhibcood!',
        )

    @classmethod
    def create_league_update(cls, user, league_position, league_name):
        """Create a league update notification"""
        return cls.objects.create(
            user=user,
            notification_type='league_update',
            title='Warbixin Tartanka!',
            message=f'Waad ku guulaysatay booska {league_position} tartanka {league_name}!',
        )

class League(models.Model):
    """
    Represents a league level in the competitive system.
    """
    LEVELS = (
        ('hydrogen', 'Hydrogen'),
        ('lithium', 'Lithium'),
        ('carbon', 'Carbon'),
        ('neon', 'Neon'),
        ('titanium', 'Titanium'),
        ('xenon', 'Xenon'),
        ('barium', 'Barium'),
        ('neodymium', 'Neodymium'),
        ('tungsten', 'Tungsten'),
        ('einsteinium', 'Einsteinium'),
    )

    level = models.CharField(max_length=20, choices=LEVELS, unique=True)
    promotion_threshold = models.PositiveIntegerField(default=15)
    stay_threshold = models.PositiveIntegerField(default=10)
    demotion_threshold = models.PositiveIntegerField(default=5)
    min_xp = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['min_xp']

    def __str__(self):
        return self.get_level_display()

    @classmethod
    def get_league_for_xp(cls, xp):
        """Get the appropriate league for a user's XP"""
        return cls.objects.filter(min_xp__lte=xp).order_by('-min_xp').first()

    @classmethod
    def get_next_league(cls, current_league):
        """Get the next league level"""
        if not current_league:
            return cls.objects.first()
        
        leagues = list(cls.objects.all().order_by('min_xp'))
        current_index = leagues.index(current_league)
        
        if current_index < len(leagues) - 1:
            return leagues[current_index + 1]
        return None

    @classmethod
    def get_previous_league(cls, current_league):
        """Get the previous league level"""
        if not current_league:
            return None
        
        leagues = list(cls.objects.all().order_by('min_xp'))
        current_index = leagues.index(current_league)
        
        if current_index > 0:
            return leagues[current_index - 1]
        return None

class UserProblem(models.Model):
    """
    Tracks a user's progress on individual problems.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='solved_problems', 
        on_delete=models.CASCADE
    )
    problem = models.ForeignKey(
        Problem, 
        related_name='user_solutions', 
        on_delete=models.CASCADE
    )
    solved = models.BooleanField(default=False)
    solved_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'problem']
        ordering = ['-solved_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.problem.question_text[:50]}"
    
    def mark_as_solved(self):
        """Mark problem as solved and award XP"""
        if not self.solved:
            self.solved = True
            self.solved_at = timezone.now()
            self.xp_earned = self.problem.xp
            self.save()
            
            # Update lesson progress
            progress, _ = UserProgress.objects.get_or_create(
                user=self.user,
                lesson=self.problem.lesson
            )
            progress.problems_solved += 1
            progress.total_xp_earned += self.xp_earned
            
            # Update streak after 2-3 problems
            if progress.problems_solved in [2, 3] and not progress.streak_updated:
                streak, _ = Streak.objects.get_or_create(user=self.user)
                streak.update_streak(1, [self.problem.lesson.id])
                progress.streak_updated = True
            
            progress.save()
            
            # Award XP
            streak, _ = Streak.objects.get_or_create(user=self.user)
            streak.award_xp(self.xp_earned, 'problem')
            
            # Update league standings
            from leagues.models import UserLeague
            user_league, _ = UserLeague.objects.get_or_create(user=self.user, defaults={'current_league': League.objects.first()})
            user_league.update_weekly_points(self.xp_earned)
            
            return True
        return False
