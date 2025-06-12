from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Subscription

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_subscription(sender, instance, created, **kwargs):
    """Create a subscription instance when a new user is created"""
    if created:
        Subscription.objects.create(user=instance) 