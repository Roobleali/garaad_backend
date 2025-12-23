from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinLengthValidator
from django.utils.text import slugify
import uuid

User = get_user_model()


class Campus(models.Model):
    """
    Subject-based campuses where users are grouped (e.g., Physics, Math, Crypto)
    """
    SUBJECT_CHOICES = [
        ('physics', 'Fiisigis'),  # Physics in Somali
        ('math', 'Xisaab'),      # Math in Somali  
        ('crypto', 'Qarsoodiga'), # Crypto in Somali
        ('biology', 'Bayooloji'), # Biology in Somali
        ('chemistry', 'Kimistar'), # Chemistry in Somali
        ('history', 'Taariikh'),  # History in Somali
        ('literature', 'Suugaan'), # Literature in Somali
        ('technology', 'Tignoolajiyada'), # Technology in Somali
        ('business', 'Ganacsi'),  # Business in Somali
        ('islamic_studies', 'Casharo Diinta'), # Islamic Studies in Somali
        ('ai', 'Hankhulka Macluumaadka'), # AI in Somali
        ('fitness', 'Jirka iyo Caafimaadka'), # Fitness in Somali
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    subject_tag = models.CharField(max_length=50, choices=SUBJECT_CHOICES, unique=True)
    icon = models.CharField(max_length=50, default='📚', help_text="Emoji or icon class")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    color_code = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color for campus theme")
    
    # Campus statistics
    member_count = models.PositiveIntegerField(default=0)
    post_count = models.PositiveIntegerField(default=0)
    
    # Campus settings
    is_active = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False, help_text="Require admin approval to join")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Campus'
        verbose_name_plural = 'Campuses'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_subject_display_somali(self):
        """Get Somali display name for subject"""
        return dict(self.SUBJECT_CHOICES).get(self.subject_tag, self.subject_tag)


class Room(models.Model):
    """
    Rooms within campuses for more specific discussions (e.g., "Garaad HQ", "Study Group")
    """
    ROOM_TYPES = [
        ('general', 'Guud'),        # General in Somali
        ('study', 'Waxbarasho'),    # Study in Somali
        ('chat', 'Sheeko'),         # Chat in Somali
        ('voice', 'Cod'),           # Voice in Somali
        ('announcement', 'Ogeysiis'),# Announcement in Somali
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='general')
    is_private = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Statistics
    member_count = models.PositiveIntegerField(default=0)
    post_count = models.PositiveIntegerField(default=0)
    
    icon = models.CharField(max_length=50, default='hashtag') # For UI icons
    
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['campus__name', 'order', 'name']
        unique_together = ['campus', 'name']
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'

    def __str__(self):
        return f"{self.campus.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class CampusMembership(models.Model):
    """
    Track user membership in campuses
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='memberships')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_moderator = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # User stats in this campus
    posts_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    likes_received = models.PositiveIntegerField(default=0)
    reputation_score = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'campus']
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.username} - {self.campus.name}"


class Post(models.Model):
    """
    Posts within rooms
    """
    POST_TYPES = [
        ('text', 'Qoraal'),         # Text in Somali
        ('question', 'Su\'aal'),     # Question in Somali  
        ('announcement', 'Ogeysiis'), # Announcement in Somali
        ('poll', 'Codbixin'),       # Poll in Somali
        ('media', 'Sawir/Muuqaal'), # Media in Somali
    ]
    
    LANGUAGE_CHOICES = [
        ('so', 'Somali'),
        ('en', 'English'),
        ('ar', 'Arabic'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_posts')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='posts')
    
    # Content
    title = models.CharField(max_length=200, validators=[MinLengthValidator(5)])
    content = models.TextField(validators=[MinLengthValidator(10)])
    language = models.CharField(max_length=3, choices=LANGUAGE_CHOICES, default='so')
    post_type = models.CharField(max_length=15, choices=POST_TYPES, default='text')
    
    # Optional media
    image = models.ImageField(upload_to='community/posts/', null=True, blank=True)
    video_url = models.URLField(null=True, blank=True, help_text="YouTube, Vimeo, etc.")
    
    # Post metadata
    is_pinned = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    is_edited = models.BooleanField(default=False)
    
    # Engagement metrics
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-last_activity']
        indexes = [
            models.Index(fields=['room', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-last_activity']),
        ]

    def __str__(self):
        return f"{self.title[:50]}... - {self.user.username}"

    def update_last_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])


class Comment(models.Model):
    """
    Comments on posts
    """
    LANGUAGE_CHOICES = [
        ('so', 'Somali'),
        ('en', 'English'), 
        ('ar', 'Arabic'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Content
    content = models.TextField(validators=[MinLengthValidator(2)])
    language = models.CharField(max_length=3, choices=LANGUAGE_CHOICES, default='so')
    
    # Comment metadata
    is_approved = models.BooleanField(default=True)
    is_edited = models.BooleanField(default=False)
    
    # Engagement
    likes_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title[:30]}..."

    @property
    def is_reply(self):
        return self.parent_comment is not None

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new:
            # Update post's comment count and last activity
            self.post.comments_count = self.post.comments.count()
            self.post.update_last_activity()
            self.post.save(update_fields=['comments_count'])


class Like(models.Model):
    """
    Likes for posts and comments
    """
    CONTENT_TYPES = [
        ('post', 'Post'),
        ('comment', 'Comment'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_likes')
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    
    # Use generic foreign key approach for flexibility
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # Ensure user can only like a post once
            models.UniqueConstraint(
                fields=['user', 'post'], 
                condition=models.Q(post__isnull=False),
                name='unique_post_like'
            ),
            # Ensure user can only like a comment once  
            models.UniqueConstraint(
                fields=['user', 'comment'],
                condition=models.Q(comment__isnull=False), 
                name='unique_comment_like'
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'content_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        if self.post:
            return f"{self.user.username} liked post: {self.post.title[:30]}..."
        elif self.comment:
            return f"{self.user.username} liked comment by {self.comment.user.username}"
        return f"{self.user.username} liked {self.content_type}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new:
            # Update like counts
            if self.post:
                self.post.likes_count = self.post.likes.count()
                self.post.save(update_fields=['likes_count'])
            elif self.comment:
                self.comment.likes_count = self.comment.likes.count()
                self.comment.save(update_fields=['likes_count'])


class UserCommunityProfile(models.Model):
    """
    Extended profile for community features
    """
    BADGE_LEVELS = [
        ('dhalinyaro', 'Garaad Dhalinyaro'),    # Young Garaad
        ('dhexe', 'Garaad Dhexe'),              # Middle Garaad  
        ('sare', 'Garaad Sare'),                # Senior Garaad
        ('weyne', 'Garaad Weyne'),              # Great Garaad
        ('hogaamiye', 'Garaad Hogaamiye'),      # Leader Garaad
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='community_profile')
    
    # Community points and badges
    community_points = models.PositiveIntegerField(default=0)
    badge_level = models.CharField(max_length=20, choices=BADGE_LEVELS, default='dhalinyaro')
    
    # Community stats
    total_posts = models.PositiveIntegerField(default=0)
    total_comments = models.PositiveIntegerField(default=0)
    total_likes_received = models.PositiveIntegerField(default=0)
    total_likes_given = models.PositiveIntegerField(default=0)
    
    # Community preferences
    preferred_language = models.CharField(
        max_length=3,
        choices=[('so', 'Somali'), ('en', 'English'), ('ar', 'Arabic')],
        default='so'
    )
    email_notifications = models.BooleanField(default=True)
    mention_notifications = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Community Profile'
        verbose_name_plural = 'User Community Profiles'

    def __str__(self):
        return f"{self.user.username} - {self.get_badge_level_display()}"

    def add_points(self, points):
        """Add community points and check for badge level up"""
        self.community_points += points
        self.update_badge_level()
        self.save()

    def update_badge_level(self):
        """Update badge level based on points"""
        if self.community_points >= 5000:
            self.badge_level = 'hogaamiye'
        elif self.community_points >= 2000:
            self.badge_level = 'weyne'
        elif self.community_points >= 1000:
            self.badge_level = 'sare'
        elif self.community_points >= 500:
            self.badge_level = 'dhexe'
        else:
            self.badge_level = 'dhalinyaro'


class CommunityNotification(models.Model):
    """
    Notifications for community interactions
    """
    NOTIFICATION_TYPES = [
        ('post_like', 'Qofka Soo Jeclaystay Qoraalkaaga'),      # Someone liked your post
        ('comment_like', 'Qofka Soo Jeclaystay Faalladaada'),   # Someone liked your comment
        ('post_comment', 'Qofka Ka Faalleeyay Qoraalkaaga'),    # Someone commented on your post
        ('comment_reply', 'Qofka Kaa Jawaabay Faalladaada'),    # Someone replied to your comment
        ('mention', 'Qofka Ku Soo Magacaabay'),                 # Someone mentioned you
        ('new_campus_member', 'Xubin Cusub Campus-ka'),         # New member joined campus
        ('campus_announcement', 'Ogeysiis Campus'),             # Campus announcement
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_community_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    # Content references
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, null=True, blank=True)
    
    # Notification content
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Metadata
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.recipient.username}"


class Message(models.Model):
    """
    Discord-style real-time messages within a room
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_messages')
    content = models.TextField()
    
    # Support for simple attachments (URLs)
    attachment_url = models.URLField(max_length=500, null=True, blank=True)
    attachment_type = models.CharField(max_length=20, null=True, blank=True) # image, video, file
    
    # Reply functionality
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    
    # Metadata
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room', 'created_at']),
        ]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"


class Presence(models.Model):
    """
    Track user real-time status
    """
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('idle', 'Fadhi'),      # Idle/Sitting in Somali
        ('dnd', 'Ha Iwaxyeelin'), # Don't disturb in Somali
        ('offline', 'Offline'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='presence')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='offline')
    custom_status = models.CharField(max_length=100, blank=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"