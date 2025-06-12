from rest_framework import serializers
from django.utils import timezone
from .models import Payment, Subscription

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'amount', 'currency', 'payment_type',
            'transaction_id', 'waafipay_reference', 'status',
            'error_message', 'created_at'
        ]
        read_only_fields = ['user', 'transaction_id', 'waafipay_reference', 'status', 'error_message', 'created_at']

class SubscriptionSerializer(serializers.ModelSerializer):
    is_valid = serializers.BooleanField(read_only=True)
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'is_active', 'start_date', 'end_date',
            'auto_renew', 'subscription_type', 'is_valid',
            'days_remaining', 'created_at'
        ]
        read_only_fields = ['user', 'is_active', 'start_date', 'end_date', 'created_at']

    def get_days_remaining(self, obj):
        if not obj.end_date:
            return 0
        if not obj.is_valid():
            return 0
        delta = obj.end_date - timezone.now()
        return max(0, delta.days) 