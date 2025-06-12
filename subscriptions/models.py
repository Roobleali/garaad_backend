from django.db import models
from django.conf import settings
from django.utils import timezone

class Subscription(models.Model):
    """
    Represents a user's subscription status
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    is_active = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)
    subscription_type = models.CharField(
        max_length=20,
        choices=[
            ('local', 'Local'),
            ('diaspora', 'Diaspora')
        ],
        default='local'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s subscription"

    def is_valid(self):
        """Check if subscription is active and not expired"""
        if not self.is_active:
            return False
        if not self.end_date:
            return False
        return timezone.now() <= self.end_date

    def extend_subscription(self, months=1):
        """Extend subscription by specified number of months"""
        if not self.end_date or self.end_date < timezone.now():
            self.start_date = timezone.now()
            self.end_date = self.start_date + timezone.timedelta(days=30*months)
        else:
            self.end_date += timezone.timedelta(days=30*months)
        self.is_active = True
        self.save()

class Payment(models.Model):
    """
    Represents a payment transaction using Waafipay
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_type = models.CharField(
        max_length=20,
        choices=[
            ('local', 'Local'),
            ('diaspora', 'Diaspora')
        ],
        default='local'
    )
    transaction_id = models.CharField(max_length=100, unique=True)
    waafipay_reference = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s payment - {self.transaction_id}"

    class Meta:
        ordering = ['-created_at']
