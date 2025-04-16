from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """
    Represents a category of courses.
    """
    id = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.CharField(max_length=255)
    in_progress = models.BooleanField(default=False)
    course_ids = models.JSONField(default=list)

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
    module_ids = models.JSONField(default=list)
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


class Module(models.Model):
    """
    Represents a module within a course.
    """
    id = models.CharField(max_length=50, primary_key=True)
    course = models.ForeignKey(
        Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    lesson_ids = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        ordering = ['course', 'id']


class Lesson(models.Model):
    """
    Represents a lesson within a module. Basic lesson info.
    """
    module = models.ForeignKey(
        Module, related_name='lessons', on_delete=models.CASCADE)
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
        return f"{self.module.title} - {self.title}"

    class Meta:
        ordering = ['module', 'lesson_number']


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
    Group of extra practice problems for a lesson/module.
    """
    PRACTICE_TYPES = (
        ('lesson', 'Lesson Practice'),
        ('module', 'Module Review'),
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
    module = models.ForeignKey(
        Module, related_name='practice_sets', on_delete=models.CASCADE, null=True, blank=True)
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
        # Ensure either lesson or module is provided, but not both
        if (self.lesson is None and self.module is None) or (self.lesson is not None and self.module is not None):
            raise ValidationError(
                "Either lesson or module must be provided, but not both.")

    def __str__(self):
        related_to = self.lesson.title if self.lesson else self.module.title
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
