from rest_framework import serializers
from .models import Order, OrderItem, PaymentWebhook
from django.contrib.auth import get_user_model

User = get_user_model()


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model"""
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'item_type', 'name', 'description', 'unit_price', 
            'quantity', 'total_price', 'subscription_type', 
            'subscription_start_date', 'subscription_end_date', 
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model"""
    items = OrderItemSerializer(many=True, read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    
    # Somali translations for status
    status_somali = serializers.SerializerMethodField()
    payment_method_somali = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'total_amount', 'currency', 'currency_display',
            'payment_method', 'payment_method_display', 'payment_method_somali',
            'status', 'status_display', 'status_somali', 'created_at', 'updated_at', 
            'paid_at', 'waafi_transaction_id', 'waafi_reference_id', 
            'waafi_issuer_transaction_id', 'waafi_order_id', 'customer_name', 
            'customer_email', 'customer_phone', 'description', 'items'
        ]
        read_only_fields = [
            'id', 'order_number', 'created_at', 'updated_at', 'paid_at',
            'waafi_transaction_id', 'waafi_reference_id', 
            'waafi_issuer_transaction_id', 'waafi_order_id'
        ]
    
    def get_status_somali(self, obj):
        """Get Somali translation for order status"""
        status_translations = {
            'pending': 'Sugaya',
            'processing': 'Waa la socda',
            'completed': 'Dhammaystiran',
            'failed': 'Fashilmay',
            'cancelled': 'La joojiyay',
            'refunded': 'Dib loo celiyay'
        }
        return status_translations.get(obj.status, obj.status)
    
    def get_payment_method_somali(self, obj):
        """Get Somali translation for payment method"""
        method_translations = {
            'waafi': 'Waafi',
            'zaad': 'Zaad',
            'evcplus': 'EVCPlus',
            'sahal': 'Sahal',
            'credit_card': 'Kaadhka Deynta',
            'bank_account': 'Bangiga',
            'admin': 'Maamulka'
        }
        return method_translations.get(obj.payment_method, obj.payment_method)


class OrderHistorySerializer(serializers.ModelSerializer):
    """Simplified serializer for order history listing"""
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    
    # Somali translations
    status_somali = serializers.SerializerMethodField()
    payment_method_somali = serializers.SerializerMethodField()
    
    # Item count and subscription info
    items_count = serializers.SerializerMethodField()
    subscription_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'total_amount', 'currency', 'currency_display',
            'payment_method', 'payment_method_display', 'payment_method_somali',
            'status', 'status_display', 'status_somali', 'created_at', 'paid_at',
            'description', 'items_count', 'subscription_info'
        ]
    
    def get_status_somali(self, obj):
        """Get Somali translation for order status"""
        status_translations = {
            'pending': 'Sugaya',
            'processing': 'Waa la socda',
            'completed': 'Dhammaystiran',
            'failed': 'Fashilmay',
            'cancelled': 'La joojiyay',
            'refunded': 'Dib loo celiyay'
        }
        return status_translations.get(obj.status, obj.status)
    
    def get_payment_method_somali(self, obj):
        """Get Somali translation for payment method"""
        method_translations = {
            'waafi': 'Waafi',
            'zaad': 'Zaad',
            'evcplus': 'EVCPlus',
            'sahal': 'Sahal',
            'credit_card': 'Kaadhka Deynta',
            'bank_account': 'Bangiga',
            'admin': 'Maamulka'
        }
        return method_translations.get(obj.payment_method, obj.payment_method)
    
    def get_items_count(self, obj):
        """Get the number of items in the order"""
        return obj.items.count()
    
    def get_subscription_info(self, obj):
        """Get subscription information if any"""
        subscription_items = obj.items.filter(item_type='subscription')
        if subscription_items.exists():
            item = subscription_items.first()
            return {
                'type': item.subscription_type,
                'start_date': item.subscription_start_date,
                'end_date': item.subscription_end_date,
                'name': item.name
            }
        return None


class CreateOrderSerializer(serializers.ModelSerializer):
    """Serializer for creating new orders"""
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = [
            'total_amount', 'currency', 'payment_method', 'description',
            'customer_name', 'customer_email', 'customer_phone', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order


class PaymentWebhookSerializer(serializers.ModelSerializer):
    """Serializer for PaymentWebhook model"""
    
    class Meta:
        model = PaymentWebhook
        fields = [
            'id', 'provider', 'event_type', 'status', 'raw_data', 
            'processed_data', 'processed_at', 'error_message', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReceiptSerializer(serializers.Serializer):
    """Serializer for receipt data"""
    order_number = serializers.CharField()
    customer_name = serializers.CharField()
    customer_email = serializers.EmailField()
    total_amount = serializers.CharField()
    currency = serializers.CharField()
    payment_method = serializers.CharField()
    paid_at = serializers.CharField()
    description = serializers.CharField()
    items = serializers.ListField()
    
    # Additional receipt fields
    company_name = serializers.CharField(default='Garaad')
    company_address = serializers.CharField(default='Hargeisa, Somaliland')
    company_email = serializers.CharField(default='info@garaad.org')
    receipt_date = serializers.CharField()
    
    def to_representation(self, instance):
        """Add computed fields for receipt"""
        data = super().to_representation(instance)
        
        # Add receipt-specific translations
        data['receipt_title'] = 'Rasiidka Bixinta'  # Payment Receipt
        data['order_label'] = 'Lambarka Dalbashada'  # Order Number
        data['customer_label'] = 'Macaamiilka'  # Customer
        data['amount_label'] = 'Qiimaha'  # Amount
        data['method_label'] = 'Habka Bixinta'  # Payment Method
        data['date_label'] = 'Taariikh'  # Date
        data['description_label'] = 'Sharaxaad'  # Description
        data['items_label'] = 'Shayada'  # Items
        data['thank_you_message'] = 'Waad ku mahadsantahay inaad Garaad isticmaasho!'
        
        return data


class OrderStatsSerializer(serializers.Serializer):
    """Serializer for order statistics"""
    total_orders = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    completed_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    failed_orders = serializers.IntegerField()
    
    # Monthly breakdown
    monthly_stats = serializers.ListField()
    
    # Payment method breakdown
    payment_method_stats = serializers.DictField()
    
    # Currency breakdown
    currency_stats = serializers.DictField()
    
    # Recent orders
    recent_orders = OrderHistorySerializer(many=True) 