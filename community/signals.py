from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import (
    Post, Comment, Like, UserCommunityProfile, 
    CommunityNotification, CampusMembership
)
from .utils import CommunityGamification

User = get_user_model()


@receiver(post_save, sender=Post)
def handle_post_creation(sender, instance, created, **kwargs):
    """
    Handle post creation: award points and update stats
    """
    if created and instance.is_approved:
        # Award points for post creation
        result = CommunityGamification.handle_post_creation(instance)
        
        # Update user community profile stats
        profile, profile_created = UserCommunityProfile.objects.get_or_create(
            user=instance.user
        )
        profile.total_posts += 1
        profile.save()
        
        # Update campus membership stats
        try:
            membership = CampusMembership.objects.get(
                user=instance.user,
                campus=instance.room.campus,
                is_active=True
            )
            membership.posts_count += 1
            membership.save()
        except CampusMembership.DoesNotExist:
            pass
        
        # Update room post count
        instance.room.post_count = instance.room.posts.filter(is_approved=True).count()
        instance.room.save(update_fields=['post_count'])
        
        # Update campus post count
        instance.room.campus.post_count = Post.objects.filter(
            room__campus=instance.room.campus,
            is_approved=True
        ).count()
        instance.room.campus.save(update_fields=['post_count'])


@receiver(post_save, sender=Comment)
def handle_comment_creation(sender, instance, created, **kwargs):
    """
    Handle comment creation: award points, update stats, and create notifications
    """
    if created and instance.is_approved:
        # Award points for comment creation
        result = CommunityGamification.handle_comment_creation(instance)
        
        # Update user community profile stats
        profile, profile_created = UserCommunityProfile.objects.get_or_create(
            user=instance.user
        )
        profile.total_comments += 1
        profile.save()
        
        # Update campus membership stats
        try:
            membership = CampusMembership.objects.get(
                user=instance.user,
                campus=instance.post.room.campus,
                is_active=True
            )
            membership.comments_count += 1
            membership.save()
        except CampusMembership.DoesNotExist:
            pass
        
        # Create notification for post owner (if not commenting on own post)
        if instance.user != instance.post.user:
            notification_type = 'comment_reply' if instance.parent_comment else 'post_comment'
            
            if instance.parent_comment:
                # Reply to comment
                title = 'Qof ayaa kaa jawaabay faalladaada'  # Someone replied to your comment
                message = f'{instance.user.username} ayaa kaa jawaabay: "{instance.content[:50]}..."'
                recipient = instance.parent_comment.user
            else:
                # Comment on post
                title = 'Qof ayaa ka faalleeyay qoraalkaaga'  # Someone commented on your post
                message = f'{instance.user.username} ayaa qoray: "{instance.content[:50]}..."'
                recipient = instance.post.user
            
            CommunityNotification.objects.create(
                recipient=recipient,
                sender=instance.user,
                notification_type=notification_type,
                post=instance.post,
                comment=instance,
                title=title,
                message=message
            )
        
        # Update post's comment count and last activity
        instance.post.comments_count = instance.post.comments.filter(is_approved=True).count()
        instance.post.update_last_activity()
        instance.post.save(update_fields=['comments_count'])


@receiver(post_save, sender=Like)
def handle_like_creation(sender, instance, created, **kwargs):
    """
    Handle like creation: award points and create notifications
    """
    if created:
        # Determine content owner
        content_owner = None
        content_title = ""
        notification_type = ""
        
        if instance.post:
            content_owner = instance.post.user
            content_title = instance.post.title
            notification_type = 'post_like'
            
            # Update post like count
            instance.post.likes_count = instance.post.likes.count()
            instance.post.save(update_fields=['likes_count'])
            
        elif instance.comment:
            content_owner = instance.comment.user
            content_title = f"faallo ku saabsan '{instance.comment.post.title[:30]}...'"
            notification_type = 'comment_like'
            
            # Update comment like count
            instance.comment.likes_count = instance.comment.likes.count()
            instance.comment.save(update_fields=['likes_count'])
            
            # Check for helpful comment bonus
            CommunityGamification.check_helpful_comment_bonus(instance.comment)
        
        # Award points to content owner (if not liking own content)
        if content_owner and content_owner != instance.user:
            CommunityGamification.handle_like_received(content_owner, instance.user)
            
            # Update user community profile stats
            profile, profile_created = UserCommunityProfile.objects.get_or_create(
                user=content_owner
            )
            profile.total_likes_received += 1
            profile.save()
            
            # Update liker's stats
            liker_profile, liker_created = UserCommunityProfile.objects.get_or_create(
                user=instance.user
            )
            liker_profile.total_likes_given += 1
            liker_profile.save()
            
            # Create notification
            titles = {
                'post_like': 'Qof ayaa jeclaystay qoraalkaaga',      # Someone liked your post
                'comment_like': 'Qof ayaa jeclaystay faalladaada',   # Someone liked your comment
            }
            
            title = titles.get(notification_type, 'Qof ayaa ku jeclaystay')
            message = f'{instance.user.username} ayaa jeclaystay {content_title}'
            
            CommunityNotification.objects.create(
                recipient=content_owner,
                sender=instance.user,
                notification_type=notification_type,
                post=instance.post,
                comment=instance.comment,
                title=title,
                message=message
            )


@receiver(post_delete, sender=Like)
def handle_like_deletion(sender, instance, **kwargs):
    """
    Handle like deletion (unlike): update counts
    """
    # Update like counts
    if instance.post:
        instance.post.likes_count = max(0, instance.post.likes_count - 1)
        instance.post.save(update_fields=['likes_count'])
        
        # Update content owner's stats
        if instance.post.user != instance.user:
            try:
                profile = UserCommunityProfile.objects.get(user=instance.post.user)
                profile.total_likes_received = max(0, profile.total_likes_received - 1)
                profile.save()
            except UserCommunityProfile.DoesNotExist:
                pass
    
    elif instance.comment:
        instance.comment.likes_count = max(0, instance.comment.likes_count - 1)
        instance.comment.save(update_fields=['likes_count'])
        
        # Update content owner's stats
        if instance.comment.user != instance.user:
            try:
                profile = UserCommunityProfile.objects.get(user=instance.comment.user)
                profile.total_likes_received = max(0, profile.total_likes_received - 1)
                profile.save()
            except UserCommunityProfile.DoesNotExist:
                pass
    
    # Update liker's stats
    try:
        liker_profile = UserCommunityProfile.objects.get(user=instance.user)
        liker_profile.total_likes_given = max(0, liker_profile.total_likes_given - 1)
        liker_profile.save()
    except UserCommunityProfile.DoesNotExist:
        pass


@receiver(post_save, sender=CampusMembership)
def handle_campus_membership(sender, instance, created, **kwargs):
    """
    Handle campus membership changes: update member counts and create notifications
    """
    # Update campus member count
    instance.campus.member_count = instance.campus.memberships.filter(is_active=True).count()
    instance.campus.save(update_fields=['member_count'])
    
    if created and instance.is_active:
        # Create welcome notification for new member
        CommunityNotification.objects.create(
            recipient=instance.user,
            sender=instance.user,  # Self-notification
            notification_type='new_campus_member',
            campus=instance.campus,
            title=f'Ku soo dhaweeyay {instance.campus.name}!',  # Welcome to campus
            message=f'Waad ku guuleysatay inaad ku biirto {instance.campus.name}. Ku soo biir wadahadalka oo la wadaag macluumaadka!'
        )
        
        # Notify moderators of new member
        moderators = CampusMembership.objects.filter(
            campus=instance.campus,
            is_moderator=True,
            is_active=True
        ).exclude(user=instance.user)
        
        for mod_membership in moderators:
            CommunityNotification.objects.create(
                recipient=mod_membership.user,
                sender=instance.user,
                notification_type='new_campus_member',
                campus=instance.campus,
                title=f'Xubin cusub ayaa ku biiray {instance.campus.name}',  # New member joined
                message=f'{instance.user.username} ayaa ku biiray campus-ka. Ku soo dhaweeyay!'
            )


@receiver(post_save, sender=UserCommunityProfile)
def handle_profile_update(sender, instance, created, **kwargs):
    """
    Handle community profile updates: check for badge level changes
    """
    if not created:
        # Check if badge level should be updated based on points
        new_badge = CommunityGamification.calculate_badge_level(instance.community_points)
        if new_badge != instance.badge_level:
            old_badge = instance.badge_level
            instance.badge_level = new_badge
            instance.save(update_fields=['badge_level'])
            
            # Create badge level up notification
            CommunityGamification.create_badge_notification(instance.user, new_badge, old_badge)


# Auto-create community profile for new users
@receiver(post_save, sender=User)
def create_community_profile(sender, instance, created, **kwargs):
    """
    Auto-create community profile for new users
    """
    if created:
        UserCommunityProfile.objects.create(
            user=instance,
            community_points=0,
            badge_level='dhalinyaro',
            preferred_language='so'  # Default to Somali
        )


# Content moderation signals
@receiver(post_save, sender=Post)
def handle_post_approval_change(sender, instance, **kwargs):
    """
    Handle post approval status changes
    """
    if hasattr(instance, '_state') and not instance._state.adding:
        # This is an update, check if approval status changed
        try:
            old_instance = Post.objects.get(pk=instance.pk)
        except Post.DoesNotExist:
            return
        
        if not old_instance.is_approved and instance.is_approved:
            # Post was just approved
            CommunityNotification.objects.create(
                recipient=instance.user,
                sender=instance.user,  # System notification
                notification_type='post_approved',
                post=instance,
                title='Qoraalkaaga waa la ansixiyay!',  # Your post was approved
                message=f'Qoraalkaaga "{instance.title}" waa la ansixiyay oo hadda waa la arki karaa.'
            )
        elif old_instance.is_approved and not instance.is_approved:
            # Post was disapproved
            CommunityNotification.objects.create(
                recipient=instance.user,
                sender=instance.user,  # System notification
                notification_type='post_disapproved',
                post=instance,
                title='Qoraalkaaga waa la diiday',  # Your post was disapproved
                message=f'Qoraalkaaga "{instance.title}" waa la diiday. Fadlan ku celi si waafaqsan xeerarka bulshada.'
            )


@receiver(post_save, sender=Comment)
def handle_comment_approval_change(sender, instance, **kwargs):
    """
    Handle comment approval status changes
    """
    if hasattr(instance, '_state') and not instance._state.adding:
        # This is an update, check if approval status changed
        try:
            old_instance = Comment.objects.get(pk=instance.pk)
        except Comment.DoesNotExist:
            return
        
        if not old_instance.is_approved and instance.is_approved:
            # Comment was just approved
            CommunityNotification.objects.create(
                recipient=instance.user,
                sender=instance.user,  # System notification
                notification_type='comment_approved',
                comment=instance,
                post=instance.post,
                title='Faalladaada waa la ansixiyay!',  # Your comment was approved
                message=f'Faalladaada ku saabsan "{instance.post.title}" waa la ansixiyay.'
            )
        elif old_instance.is_approved and not instance.is_approved:
            # Comment was disapproved
            CommunityNotification.objects.create(
                recipient=instance.user,
                sender=instance.user,  # System notification
                notification_type='comment_disapproved',
                comment=instance,
                post=instance.post,
                title='Faalladaada waa la diiday',  # Your comment was disapproved
                message=f'Faalladaada ku saabsan "{instance.post.title}" waa la diiday.'
            ) 