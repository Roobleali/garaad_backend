from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from .models import (
    Post, Comment, UserCommunityProfile, CommunityNotification
)

User = get_user_model()


class CommunityGamification:
    """
    Utility class for community gamification features
    """
    
    # Point values
    POINTS = {
        'post_create': 10,      # +10 for creating a post
        'comment_create': 5,    # +5 for creating a comment
        'like_received': 1,     # +1 for receiving a like
        'first_post': 20,       # Bonus for first post in a campus
        'first_comment': 10,    # Bonus for first comment
        'daily_activity': 5,    # Daily activity bonus
        'weekly_streak': 25,    # Weekly streak bonus
        'helpful_comment': 15,  # Bonus for helpful comments (liked 5+ times)
    }
    
    # Badge thresholds (in Somali)
    BADGE_THRESHOLDS = {
        'dhalinyaro': 0,        # Young Garaad (0+ points)
        'dhexe': 500,          # Middle Garaad (500+ points)
        'sare': 1000,          # Senior Garaad (1000+ points)
        'weyne': 2000,         # Great Garaad (2000+ points)
        'hogaamiye': 5000,     # Leader Garaad (5000+ points)
    }
    
    @classmethod
    def award_points(cls, user, points, reason, post=None, comment=None, campus=None):
        """
        Award points to a user and handle badge level updates
        """
        with transaction.atomic():
            profile, created = UserCommunityProfile.objects.get_or_create(
                user=user,
                defaults={
                    'community_points': 0,
                    'badge_level': 'dhalinyaro'
                }
            )
            
            old_badge = profile.badge_level
            old_points = profile.community_points
            
            # Add points
            profile.community_points += points
            
            # Update badge level
            new_badge = cls.calculate_badge_level(profile.community_points)
            profile.badge_level = new_badge
            
            profile.save()
            
            # Check if badge level changed
            if old_badge != new_badge:
                cls.create_badge_notification(user, new_badge, old_badge)
            
            # Create point award notification for significant gains
            if points >= 20:
                cls.create_points_notification(user, points, reason)
            
            return {
                'points_awarded': points,
                'total_points': profile.community_points,
                'old_badge': old_badge,
                'new_badge': new_badge,
                'badge_changed': old_badge != new_badge
            }
    
    @classmethod
    def calculate_badge_level(cls, points):
        """
        Calculate badge level based on total points
        """
        if points >= cls.BADGE_THRESHOLDS['hogaamiye']:
            return 'hogaamiye'
        elif points >= cls.BADGE_THRESHOLDS['weyne']:
            return 'weyne'
        elif points >= cls.BADGE_THRESHOLDS['sare']:
            return 'sare'
        elif points >= cls.BADGE_THRESHOLDS['dhexe']:
            return 'dhexe'
        else:
            return 'dhalinyaro'
    
    @classmethod
    def create_badge_notification(cls, user, new_badge, old_badge):
        """
        Create notification for badge level up
        """
        badge_names = {
            'dhalinyaro': 'Garaad Dhalinyaro',
            'dhexe': 'Garaad Dhexe',
            'sare': 'Garaad Sare',
            'weyne': 'Garaad Weyne',
            'hogaamiye': 'Garaad Hogaamiye',
        }
        
        title = f'Darajo cusub: {badge_names.get(new_badge, new_badge)}!'
        message = f'Hambalyo! Waad gaadhay darajo cusub ah {badge_names.get(new_badge)}. Sii wad hawlkaaga wanaagsan!'
        
        CommunityNotification.objects.create(
            recipient=user,
            sender=user,  # Self-notification
            notification_type='achievement',
            title=title,
            message=message
        )
    
    @classmethod
    def create_points_notification(cls, user, points, reason):
        """
        Create notification for significant point awards
        """
        reasons_somali = {
            'post_create': 'qoraal cusub',
            'comment_create': 'faallo cusub',
            'first_post': 'qoraalka koowaad',
            'first_comment': 'faallada koowaad',
            'helpful_comment': 'faallo faa\'iido leh',
            'daily_activity': 'hawlaha maalinta',
            'weekly_streak': 'iska xiga usbuuc',
        }
        
        reason_text = reasons_somali.get(reason, reason)
        title = f'{points} dhibco cusub!'
        message = f'Waad heeshay {points} dhibco oo cusub sababta oo ah {reason_text}. Ku sii wad!'
        
        CommunityNotification.objects.create(
            recipient=user,
            sender=user,  # Self-notification
            notification_type='points_award',
            title=title,
            message=message
        )
    
    @classmethod
    def handle_post_creation(cls, post):
        """
        Handle point awarding for post creation
        """
        user = post.user
        campus = post.room.campus
        
        # Check if this is user's first post in this campus
        user_posts_in_campus = post.room.campus.rooms.filter(
            posts__user=user,
            posts__is_approved=True
        ).count()
        
        if user_posts_in_campus == 1:  # First post
            points = cls.POINTS['post_create'] + cls.POINTS['first_post']
            reason = 'first_post'
        else:
            points = cls.POINTS['post_create']
            reason = 'post_create'
        
        return cls.award_points(user, points, reason, post=post, campus=campus)
    
    @classmethod
    def handle_comment_creation(cls, comment):
        """
        Handle point awarding for comment creation
        """
        user = comment.user
        post = comment.post
        campus = post.room.campus
        
        # Check if this is user's first comment
        user_comments_count = Comment.objects.filter(
            user=user,
            post__room__campus=campus,
            is_approved=True
        ).count()
        
        if user_comments_count == 1:  # First comment
            points = cls.POINTS['comment_create'] + cls.POINTS['first_comment']
            reason = 'first_comment'
        else:
            points = cls.POINTS['comment_create']
            reason = 'comment_create'
        
        return cls.award_points(user, points, reason, comment=comment, campus=campus)
    
    @classmethod
    def handle_like_received(cls, content_owner, liker, content_type='post'):
        """
        Handle point awarding for receiving a like
        """
        if content_owner == liker:
            return None  # No points for liking own content
        
        points = cls.POINTS['like_received']
        reason = 'like_received'
        
        return cls.award_points(content_owner, points, reason)
    
    @classmethod
    def check_helpful_comment_bonus(cls, comment):
        """
        Check if comment deserves helpful comment bonus (5+ likes)
        """
        if comment.likes_count >= 5:
            # Check if bonus already awarded (prevent duplicate bonuses)
            existing_bonus = CommunityNotification.objects.filter(
                recipient=comment.user,
                notification_type='helpful_comment_bonus',
                comment=comment
            ).exists()
            
            if not existing_bonus:
                points = cls.POINTS['helpful_comment']
                result = cls.award_points(comment.user, points, 'helpful_comment', comment=comment)
                
                # Create special notification
                CommunityNotification.objects.create(
                    recipient=comment.user,
                    sender=comment.user,
                    notification_type='helpful_comment_bonus',
                    comment=comment,
                    title='Faallo faa\'iido leh!',
                    message=f'Faalladaada waxay heshay {comment.likes_count} jeclayn! {points} dhibco oo dheeraad ah ayaad heshay.'
                )
                
                return result
        
        return None
    
    @classmethod
    def get_user_stats(cls, user, campus=None):
        """
        Get comprehensive user stats for community
        """
        try:
            profile = UserCommunityProfile.objects.get(user=user)
        except UserCommunityProfile.DoesNotExist:
            profile = UserCommunityProfile.objects.create(user=user)
        
        stats = {
            'community_points': profile.community_points,
            'badge_level': profile.badge_level,
            'badge_display': profile.get_badge_level_display(),
            'total_posts': profile.total_posts,
            'total_comments': profile.total_comments,
            'total_likes_received': profile.total_likes_received,
            'total_likes_given': profile.total_likes_given,
        }
        
        if campus:
            # Campus-specific stats
            try:
                from .models import CampusMembership
                membership = CampusMembership.objects.get(
                    user=user,
                    campus=campus,
                    is_active=True
                )
                stats.update({
                    'campus_posts': membership.posts_count,
                    'campus_comments': membership.comments_count,
                    'campus_likes_received': membership.likes_received,
                    'campus_reputation': membership.reputation_score,
                    'is_moderator': membership.is_moderator,
                    'joined_at': membership.joined_at,
                })
            except CampusMembership.DoesNotExist:
                pass
        
        return stats
    
    @classmethod
    def get_leaderboard(cls, campus=None, limit=50):
        """
        Get community leaderboard
        """
        queryset = UserCommunityProfile.objects.select_related('user')
        
        if campus:
            # Campus-specific leaderboard
            queryset = queryset.filter(
                user__campusmembership__campus=campus,
                user__campusmembership__is_active=True
            )
        
        profiles = queryset.order_by('-community_points')[:limit]
        
        leaderboard = []
        for i, profile in enumerate(profiles, 1):
            leaderboard.append({
                'rank': i,
                'user_id': profile.user.id,
                'username': profile.user.username,
                'points': profile.community_points,
                'badge_level': profile.badge_level,
                'badge_display': profile.get_badge_level_display(),
                'total_posts': profile.total_posts,
                'total_comments': profile.total_comments,
            })
        
        return leaderboard


# Convenience functions for direct use in views
def award_post_points(post):
    """Award points for post creation"""
    return CommunityGamification.handle_post_creation(post)


def award_comment_points(comment):
    """Award points for comment creation"""
    return CommunityGamification.handle_comment_creation(comment)


def award_like_points(content_owner, liker):
    """Award points for receiving a like"""
    return CommunityGamification.handle_like_received(content_owner, liker)


def check_comment_bonus(comment):
    """Check and award helpful comment bonus"""
    return CommunityGamification.check_helpful_comment_bonus(comment) 