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
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="courses")
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
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
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
    Represents a lesson within a module.
    """
    module = models.ForeignKey(Module, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField()
    progress = models.IntegerField(default=0)
    type = models.CharField(max_length=50)
    problem = models.JSONField()  # Stores question, example, options, solution, explanation
    language_options = models.JSONField(default=list)
    narration = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.module.title} - {self.title}"

    class Meta:
        ordering = ['module', 'id']
