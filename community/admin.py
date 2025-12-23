from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Q
from .models import (
    Campus, Room, CampusMembership, Post, Comment, Like, 
    UserCommunityProfile, CommunityNotification
)


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject_tag', 'member_count', 
                   'post_count', 'is_active', 'created_at')
    list_filter = ('subject_tag', 'is_active', 'requires_approval', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('member_count', 'post_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Macluumaadka Asaasiga ah', {  # Basic Information
            'fields': ('name', 'subject_tag', 'icon', 'color_code')
        }),
        ('Sharaxaad', {  # Description
            'fields': ('description',)
        }),
        ('Dejinta', {  # Settings
            'fields': ('slug', 'is_active', 'requires_approval', 'created_by')
        }),
        ('Tirakoobka', {  # Statistics
            'fields': ('member_count', 'post_count'),
            'classes': ('collapse',)
        }),
        ('Waqti', {  # Time
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            actual_member_count=Count('memberships', filter=Q(memberships__is_active=True)),
            actual_post_count=Count('rooms__posts', filter=Q(rooms__posts__is_approved=True))
        )


@admin.register(Room) 
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'campus', 'room_type', 'member_count', 
                   'post_count', 'is_active', 'is_private')
    list_filter = ('room_type', 'is_active', 'is_private', 'campus__subject_tag')
    search_fields = ('name', 'description', 'campus__name')
    readonly_fields = ('member_count', 'post_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Macluumaadka Asaasiga ah', {
            'fields': ('name', 'campus', 'room_type')
        }),
        ('Sharaxaad', {
            'fields': ('description',)
        }),
        ('Dejinta', {
            'fields': ('is_active', 'is_private', 'max_members', 'created_by')
        }),
        ('Tirakoobka', {
            'fields': ('member_count', 'post_count'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CampusMembership)
class CampusMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'campus', 'is_moderator', 'is_active', 
                   'posts_count', 'comments_count', 'joined_at')
    list_filter = ('is_moderator', 'is_active', 'campus__subject_tag', 'joined_at')
    search_fields = ('user__username', 'user__email', 'campus__name')
    readonly_fields = ('joined_at', 'posts_count', 'comments_count', 'likes_received')
    
    fieldsets = (
        ('Xubin', {  # Member
            'fields': ('user', 'campus')
        }),
        ('Maamul', {  # Management
            'fields': ('is_moderator', 'is_active')
        }),
        ('Tirakoobka', {
            'fields': ('posts_count', 'comments_count', 'likes_received', 'reputation_score'),
            'classes': ('collapse',)
        }),
    )


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('user', 'created_at', 'likes_count')
    fields = ('user', 'content', 'is_approved', 'likes_count', 'created_at')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title_short', 'user', 'room', 'post_type', 'language',
                   'likes_count', 'comments_count', 'is_approved', 'created_at')
    list_filter = ('post_type', 'language', 'is_approved', 'is_pinned', 
                  'is_featured', 'room__campus__subject_tag')
    search_fields = ('title', 'content', 'user__username')
    readonly_fields = ('id', 'likes_count', 'comments_count', 'views_count', 
                      'created_at', 'updated_at', 'last_activity')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Qoraal', {  # Post
            'fields': ('user', 'room', 'title', 'content', 'language', 'post_type')
        }),
        ('Media', {
            'fields': ('image', 'video_url'),
            'classes': ('collapse',)
        }),
        ('Maamul', {  # Management
            'fields': ('is_approved', 'is_pinned', 'is_featured', 'is_edited')
        }),
        ('Tirakoobka', {
            'fields': ('likes_count', 'comments_count', 'views_count'),
            'classes': ('collapse',)
        }),
        ('Waqti', {
            'fields': ('created_at', 'updated_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [CommentInline]
    
    def title_short(self, obj):
        return obj.title[:50] + "..." if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Cinwaan'  # Title in Somali
    
    actions = ['approve_posts', 'disapprove_posts', 'pin_posts', 'unpin_posts']
    
    def approve_posts(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} qoraal oo la ansixiyay.')  # X posts approved
    approve_posts.short_description = 'Ansix qoraallada la doortay'  # Approve selected posts
    
    def disapprove_posts(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} qoraal oo la diiday.')  # X posts disapproved
    disapprove_posts.short_description = 'Diid qoraallada la doortay'  # Disapprove selected posts
    
    def pin_posts(self, request, queryset):
        updated = queryset.update(is_pinned=True)
        self.message_user(request, f'{updated} qoraal oo la qabsaday.')  # X posts pinned
    pin_posts.short_description = 'Qabso qoraallada la doortay'  # Pin selected posts
    
    def unpin_posts(self, request, queryset):
        updated = queryset.update(is_pinned=False)
        self.message_user(request, f'{updated} qoraal oo laga qabsaday.')  # X posts unpinned
    unpin_posts.short_description = 'Ka qabso qoraallada la doortay'  # Unpin selected posts


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content_short', 'user', 'post_title', 'is_reply', 
                   'likes_count', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'language', 'post__room__campus__subject_tag', 'created_at')
    search_fields = ('content', 'user__username', 'post__title')
    readonly_fields = ('id', 'likes_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Faallo', {  # Comment
            'fields': ('user', 'post', 'parent_comment', 'content', 'language')
        }),
        ('Maamul', {
            'fields': ('is_approved', 'is_edited')
        }),
        ('Tirakoobka', {
            'fields': ('likes_count',),
            'classes': ('collapse',)
        }),
    )
    
    def content_short(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_short.short_description = 'Faallo'  # Comment in Somali
    
    def post_title(self, obj):
        return obj.post.title[:50] + "..." if len(obj.post.title) > 50 else obj.post.title
    post_title.short_description = 'Qoraal'  # Post in Somali
    
    def is_reply(self, obj):
        return obj.parent_comment is not None
    is_reply.boolean = True
    is_reply.short_description = 'Jawaab'  # Reply in Somali
    
    actions = ['approve_comments', 'disapprove_comments']
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} faallo oo la ansixiyay.')
    approve_comments.short_description = 'Ansix faallooyinka la doortay'
    
    def disapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} faallo oo la diiday.')
    disapprove_comments.short_description = 'Diid faallooyinka la doortay'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'content_title', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
    
    def content_title(self, obj):
        if obj.post:
            return f"Post: {obj.post.title[:30]}..."
        elif obj.comment:
            return f"Comment: {obj.comment.content[:30]}..."
        return "Unknown"
    content_title.short_description = 'Waxa la jeclaystay'  # What was liked


@admin.register(UserCommunityProfile)
class UserCommunityProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge_level', 'community_points', 'total_posts', 
                   'total_comments', 'total_likes_received')
    list_filter = ('badge_level', 'preferred_language', 'email_notifications')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Isticmaalaha', {  # User
            'fields': ('user',)
        }),
        ('Dhibco & Sharaf', {  # Points & Honor
            'fields': ('community_points', 'badge_level')
        }),
        ('Tirakoobka', {
            'fields': ('total_posts', 'total_comments', 'total_likes_received', 'total_likes_given')
        }),
        ('Doorashada', {  # Preferences
            'fields': ('preferred_language', 'email_notifications', 'mention_notifications')
        }),
    )


@admin.register(CommunityNotification)
class CommunityNotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'sender', 'title_short', 
                   'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'title', 'message')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Ogeysiis', {  # Notification
            'fields': ('recipient', 'sender', 'notification_type')
        }),
        ('Waxa ku saabsan', {  # Related to
            'fields': ('post', 'comment', 'campus')
        }),
        ('Qoraal', {  # Content
            'fields': ('title', 'message')
        }),
        ('Xaalad', {  # Status
            'fields': ('is_read',)
        }),
    )
    
    def title_short(self, obj):
        return obj.title[:50] + "..." if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Cinwaan'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} ogeysiis oo loo calaamadeeyay inay akhristay.')
    mark_as_read.short_description = 'Calaamadee sida la akhriyay'
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} ogeysiis oo loo calaamadeeyay inaysan akhriyin.')
    mark_as_unread.short_description = 'Calaamadee sida aan la akhriyin'


# Custom admin site configuration
admin.site.site_header = 'Maamulka Bulshada Garaad'  # Garaad Community Management
admin.site.site_title = 'Maamulka Bulshada'         # Community Management
admin.site.index_title = 'Bogga Maamulka Bulshada'   # Community Management Page 