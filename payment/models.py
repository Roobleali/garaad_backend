from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import uuid
import json

User = get_user_model()

class Order(models.Model):
    """
    Order model to track all payment transactions and subscriptions
    """
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('waafi', 'Waafi'),
        ('zaad', 'Zaad'),
        ('evcplus', 'EVCPlus'),
        ('sahal', 'Sahal'),
        ('credit_card', 'Credit Card'),
        ('bank_account', 'Bank Account'),
        ('admin', 'Admin'),  # For manual admin updates
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('SOS', 'Somali Shilling'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    
    # Payment details
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    # Status and timestamps
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Waafi payment specific fields
    waafi_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    waafi_reference_id = models.CharField(max_length=100, null=True, blank=True)
    waafi_issuer_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    waafi_order_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Additional data (for storing webhook data, etc.)
    metadata = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    
    # Customer info (for receipt generation)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    customer_phone = models.CharField(max_length=20, null=True, blank=True)
    
    # Notes and description
    description = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)  # For admin use
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['waafi_transaction_id']),
            models.Index(fields=['waafi_reference_id']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.email} - {self.total_amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        if not self.customer_name and self.user:
            self.customer_name = f"{self.user.first_name} {self.user.last_name}".strip()
        if not self.customer_email and self.user:
            self.customer_email = self.user.email
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Generate a unique order number"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        return f"GRD-{timestamp}-{str(uuid.uuid4())[:8].upper()}"
    
    def mark_as_paid(self):
        """Mark order as paid and update timestamp"""
        self.status = 'completed'
        self.paid_at = timezone.now()
        self.save()
    
    def get_receipt_data(self):
        """Get formatted data for receipt generation"""
        return {
            'order_number': self.order_number,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'total_amount': str(self.total_amount),
            'currency': self.currency,
            'payment_method': self.get_payment_method_display(),
            'paid_at': self.paid_at.strftime('%Y-%m-%d %H:%M:%S') if self.paid_at else None,
            'description': self.description,
            'items': [item.get_receipt_data() for item in self.items.all()]
        }


class OrderItem(models.Model):
    """
    Individual items within an order (e.g., subscription plans, features)
    """
    ITEM_TYPE_CHOICES = [
        ('subscription', 'Subscription'),
        ('feature', 'Feature'),
        ('course', 'Course'),
        ('other', 'Other'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Pricing
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Subscription specific fields
    subscription_type = models.CharField(max_length=20, null=True, blank=True)  # monthly, yearly, lifetime
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    
    # Additional metadata
    metadata = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.total_price} {self.order.currency}"
    
    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
    
    def get_receipt_data(self):
        """Get formatted data for receipt generation"""
        return {
            'name': self.name,
            'description': self.description,
            'unit_price': str(self.unit_price),
            'quantity': self.quantity,
            'total_price': str(self.total_price),
            'subscription_type': self.subscription_type,
            'subscription_start_date': self.subscription_start_date.strftime('%Y-%m-%d') if self.subscription_start_date else None,
            'subscription_end_date': self.subscription_end_date.strftime('%Y-%m-%d') if self.subscription_end_date else None,
        }


class PaymentWebhook(models.Model):
    """
    Store webhook data from payment providers (Waafi, etc.)
    """
    WEBHOOK_STATUS_CHOICES = [
        ('received', 'Received'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
        ('duplicate', 'Duplicate'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=50)  # waafi, stripe, etc.
    event_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=WEBHOOK_STATUS_CHOICES, default='received')
    
    # Webhook data
    raw_data = models.JSONField(encoder=DjangoJSONEncoder)
    processed_data = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    
    # Related order (if processed successfully)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Processing info
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['provider', 'event_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.provider} - {self.event_type} - {self.status}"
    
    def mark_as_processed(self, order=None):
        """Mark webhook as processed"""
        self.status = 'processed'
        self.processed_at = timezone.now()
        if order:
            self.order = order
        self.save()
    
    def mark_as_failed(self, error_message):
        """Mark webhook as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.save()
