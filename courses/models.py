from django.db import models
from django.utils.text import slugify


class Course(models.Model):
    """
    Represents a course in the learning management system.
    """
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    thumbnail = models.URLField(blank=True, null=True)
    level = models.CharField(
        max_length=20, choices=LEVEL_CHOICES, default='beginner')
    category = models.CharField(max_length=100)
    # This could be a ForeignKey to User model in a real system
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
    Represents a module (chapter) within a course.
    """
    course = models.ForeignKey(
        Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        ordering = ['course', 'order']
        unique_together = [['course', 'order']]


class Lesson(models.Model):
    """
    Represents a lesson within a module.
    """
    TYPE_CHOICES = (
        ('lesson', 'Lesson'),
        ('exercise', 'Exercise'),
    )

    module = models.ForeignKey(
        Module, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default='lesson')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.module.title} - {self.title}"

    class Meta:
        ordering = ['module', 'order']
        unique_together = [['module', 'order']]


class Exercise(models.Model):
    """
    Represents an exercise related to a lesson.
    """
    TYPE_CHOICES = (
        ('multiple_choice', 'Multiple Choice'),
        ('input', 'Input'),
        ('code', 'Code'),
        ('true_false', 'True/False'),
    )

    lesson = models.ForeignKey(
        Lesson, related_name='exercises', on_delete=models.CASCADE)
    question = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    choices = models.JSONField(
        null=True, blank=True, help_text="Options for multiple choice questions")
    correct_answer = models.TextField()
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Exercise for {self.lesson.title}"

    class Meta:
        ordering = ['lesson', 'created_at']
