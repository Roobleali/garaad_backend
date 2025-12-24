from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Post(models.Model):
    """
    Community post within a category.
    Simple, clean, no over-engineering.
    """
    category = models.ForeignKey(
        'courses.Category',
        related_name="community_posts",
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_posts'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]

    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}..."


class PostImage(models.Model):
    """
    Optional image attachments for posts.
    """
    post = models.ForeignKey(
        Post,
        related_name="images",
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="community/posts/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for post {self.post.id}"


class Reply(models.Model):
    """
    One-level replies to posts.
    No nested threading - keeps it simple.
    """
    post = models.ForeignKey(
        Post,
        related_name="replies",
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_replies'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
        verbose_name_plural = "Replies"
        indexes = [
            models.Index(fields=['post', 'created_at']),
        ]

    def __str__(self):
        return f"{self.author.username} replied: {self.content[:50]}..."


class Reaction(models.Model):
    """
    Controlled reactions to posts.
    No karma, no noise - just clean engagement.
    """
    REACTION_CHOICES = [
        ("like", "Like"),
        ("fire", "Fire"),
        ("insight", "Insight"),
    ]

    post = models.ForeignKey(
        Post,
        related_name="reactions",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_reactions'
    )
    type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user", "type")
        indexes = [
            models.Index(fields=['post', 'type']),
        ]

    def __str__(self):
        return f"{self.user.username} {self.type} on post {self.post.id}"