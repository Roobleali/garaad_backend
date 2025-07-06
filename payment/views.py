from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime, timedelta
import json
import logging
from decimal import Decimal

from .models import Order, OrderItem, PaymentWebhook
from .serializers import (
    OrderSerializer, OrderHistorySerializer, CreateOrderSerializer,
    PaymentWebhookSerializer, ReceiptSerializer, OrderStatsSerializer
)

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders and order history
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter orders by current user"""
        return Order.objects.filter(user=self.request.user).prefetch_related('items')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return CreateOrderSerializer
        elif self.action == 'list':
            return OrderHistorySerializer
        return OrderSerializer
    
    def perform_create(self, serializer):
        """Set the user when creating an order"""
        serializer.save(user=self.request.user)
    
    def list(self, request):
        """
        List user's order history with filtering and pagination
        """
        queryset = self.get_queryset()
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by payment method
        payment_method = request.query_params.get('payment_method')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        # Filter by date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        # Search by order number or description
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Pagination
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = queryset.count()
        orders = queryset[start:end]
        
        serializer = self.get_serializer(orders, many=True)
        
        return Response({
            'success': True,
            'data': {
                'orders': serializer.data,
                'pagination': {
                    'total_count': total_count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size
                }
            }
        })
    
    @action(detail=True, methods=['get'])
    def receipt(self, request, pk=None):
        """
        Generate and return receipt data for an order
        """
        try:
            order = self.get_object()
            
            if order.status != 'completed':
                return Response({
                    'success': False,
                    'error': 'Rasiidka kaliya waa la heli karaa dalbashada dhammaystiran'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            receipt_data = order.get_receipt_data()
            receipt_data['receipt_date'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            
            serializer = ReceiptSerializer(receipt_data)
            
            return Response({
                'success': True,
                'data': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error generating receipt for order {pk}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Khalad ayaa dhacay rasiidka soo saarka'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def download_receipt(self, request, pk=None):
        """
        Download receipt as PDF (simplified version - returns HTML for now)
        """
        try:
            order = self.get_object()
            
            if order.status != 'completed':
                return Response({
                    'success': False,
                    'error': 'Rasiidka kaliya waa la heli karaa dalbashada dhammaystiran'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # For now, return HTML receipt. In production, you'd generate PDF
            receipt_data = order.get_receipt_data()
            receipt_data['receipt_date'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # You can create a receipt template later
            html_content = f"""
            <html>
            <head>
                <title>Rasiidka Bixinta - {order.order_number}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .details {{ margin: 20px 0; }}
                    .items {{ margin: 20px 0; }}
                    .total {{ font-weight: bold; font-size: 18px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Garaad</h1>
                    <h2>Rasiidka Bixinta</h2>
                </div>
                <div class="details">
                    <p><strong>Lambarka Dalbashada:</strong> {order.order_number}</p>
                    <p><strong>Macaamiilka:</strong> {order.customer_name}</p>
                    <p><strong>Taariikh:</strong> {order.paid_at.strftime('%Y-%m-%d %H:%M:%S') if order.paid_at else 'N/A'}</p>
                    <p><strong>Habka Bixinta:</strong> {order.get_payment_method_display()}</p>
                </div>
                <div class="items">
                    <h3>Shayada:</h3>
                    <ul>
                        {''.join([f"<li>{item.name} - {item.total_price} {order.currency}</li>" for item in order.items.all()])}
                    </ul>
                </div>
                <div class="total">
                    <p>Wadarta: {order.total_amount} {order.currency}</p>
                </div>
                <div style="text-align: center; margin-top: 30px;">
                    <p>Waad ku mahadsantahay inaad Garaad isticmaasho!</p>
                </div>
            </body>
            </html>
            """
            
            return HttpResponse(html_content, content_type='text/html')
            
        except Exception as e:
            logger.error(f"Error downloading receipt for order {pk}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Khalad ayaa dhacay rasiidka soo deegista'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get order statistics for the current user
        """
        try:
            queryset = self.get_queryset()
            
            # Basic stats
            total_orders = queryset.count()
            completed_orders = queryset.filter(status='completed').count()
            pending_orders = queryset.filter(status='pending').count()
            failed_orders = queryset.filter(status='failed').count()
            
            # Total amount spent
            total_amount = queryset.filter(status='completed').aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0.00')
            
            # Monthly breakdown (last 12 months)
            monthly_stats = []
            for i in range(12):
                month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
                month_end = month_start + timedelta(days=31)
                
                month_orders = queryset.filter(
                    created_at__gte=month_start,
                    created_at__lt=month_end
                ).count()
                
                month_amount = queryset.filter(
                    created_at__gte=month_start,
                    created_at__lt=month_end,
                    status='completed'
                ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
                
                monthly_stats.append({
                    'month': month_start.strftime('%Y-%m'),
                    'orders': month_orders,
                    'amount': float(month_amount)
                })
            
            # Payment method breakdown
            payment_methods = queryset.values('payment_method').annotate(
                count=Count('id')
            )
            payment_method_stats = {pm['payment_method']: pm['count'] for pm in payment_methods}
            
            # Currency breakdown
            currencies = queryset.values('currency').annotate(
                count=Count('id'),
                total=Sum('total_amount')
            )
            currency_stats = {
                curr['currency']: {
                    'count': curr['count'],
                    'total': float(curr['total'] or 0)
                } for curr in currencies
            }
            
            # Recent orders
            recent_orders = queryset.order_by('-created_at')[:5]
            
            stats_data = {
                'total_orders': total_orders,
                'total_amount': total_amount,
                'completed_orders': completed_orders,
                'pending_orders': pending_orders,
                'failed_orders': failed_orders,
                'monthly_stats': monthly_stats,
                'payment_method_stats': payment_method_stats,
                'currency_stats': currency_stats,
                'recent_orders': recent_orders
            }
            
            serializer = OrderStatsSerializer(stats_data)
            
            return Response({
                'success': True,
                'data': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error getting order stats: {str(e)}")
            return Response({
                'success': False,
                'error': 'Khalad ayaa dhacay xogta soo bandhigista'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_subscription_order(request):
    """
    Create an order for subscription purchase
    """
    try:
        user = request.user
        subscription_type = request.data.get('subscription_type')
        payment_method = request.data.get('payment_method', 'waafi')
        
        if not subscription_type or subscription_type not in ['monthly', 'yearly', 'lifetime']:
            return Response({
                'success': False,
                'error': 'Nooca ishtiraakka waa lagama maarmaan'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Define subscription prices
        prices = {
            'monthly': {'USD': 9.99, 'EUR': 8.99, 'SOS': 500},
            'yearly': {'USD': 99.99, 'EUR': 89.99, 'SOS': 5000},
            'lifetime': {'USD': 299.99, 'EUR': 269.99, 'SOS': 15000}
        }
        
        currency = request.data.get('currency', 'USD')
        if currency not in prices[subscription_type]:
            return Response({
                'success': False,
                'error': 'Lacagta la doortay ma la taageerayo'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        amount = prices[subscription_type][currency]
        
        # Create order
        order = Order.objects.create(
            user=user,
            total_amount=amount,
            currency=currency,
            payment_method=payment_method,
            description=f'Garaad {subscription_type.title()} Subscription'
        )
        
        # Create order item
        subscription_names = {
            'monthly': 'Ishtiraak Bishii',
            'yearly': 'Ishtiraak Sannadkii',
            'lifetime': 'Ishtiraak Daa\'im'
        }
        
        start_date = timezone.now()
        end_date = None
        if subscription_type == 'monthly':
            end_date = start_date + timedelta(days=30)
        elif subscription_type == 'yearly':
            end_date = start_date + timedelta(days=365)
        
        OrderItem.objects.create(
            order=order,
            item_type='subscription',
            name=subscription_names[subscription_type],
            description=f'Ishtiraak Garaad {subscription_type}',
            unit_price=amount,
            quantity=1,
            total_price=amount,
            subscription_type=subscription_type,
            subscription_start_date=start_date,
            subscription_end_date=end_date
        )
        
        serializer = OrderSerializer(order)
        
        return Response({
            'success': True,
            'message': 'Dalbashada waa la sameeyay si guul leh',
            'data': serializer.data
        })
        
    except Exception as e:
        logger.error(f"Error creating subscription order: {str(e)}")
        return Response({
            'success': False,
            'error': 'Khalad ayaa dhacay dalbashada abuurista'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def waafi_webhook(request):
    """
    Handle Waafi payment webhooks
    """
    try:
        # Log the webhook data
        webhook_data = request.data
        logger.info(f"Received Waafi webhook: {webhook_data}")
        
        # Create webhook record
        webhook = PaymentWebhook.objects.create(
            provider='waafi',
            event_type='payment_notification',
            raw_data=webhook_data
        )
        
        # Process the webhook
        if 'transferInfo' in webhook_data:
            transfer_info = webhook_data['transferInfo']
            reference_id = transfer_info.get('referenceId')
            transaction_id = transfer_info.get('transferId')
            transfer_status = transfer_info.get('transferStatus')
            amount = transfer_info.get('amount')
            
            # Find the order by reference ID
            try:
                order = Order.objects.get(waafi_reference_id=reference_id)
                
                # Update order with Waafi transaction details
                order.waafi_transaction_id = transaction_id
                order.waafi_issuer_transaction_id = transfer_info.get('transferCode')
                order.metadata.update({
                    'waafi_webhook_data': webhook_data,
                    'processed_at': timezone.now().isoformat()
                })
                
                # Check if payment was successful (status 3 = completed)
                if transfer_status == '3':
                    order.mark_as_paid()
                    
                    # Update user's premium status if it's a subscription order
                    subscription_items = order.items.filter(item_type='subscription')
                    if subscription_items.exists():
                        item = subscription_items.first()
                        user = order.user
                        user.is_premium = True
                        user.subscription_type = item.subscription_type
                        user.subscription_start_date = item.subscription_start_date
                        user.subscription_end_date = item.subscription_end_date
                        user.save()
                        
                        logger.info(f"Updated premium status for user {user.email}")
                    
                    webhook.mark_as_processed(order)
                    logger.info(f"Successfully processed payment for order {order.order_number}")
                    
                elif transfer_status in ['4', '5']:  # Failed or cancelled
                    order.status = 'failed'
                    order.save()
                    webhook.mark_as_processed(order)
                    logger.info(f"Payment failed for order {order.order_number}")
                
            except Order.DoesNotExist:
                webhook.mark_as_failed(f"Order not found with reference ID: {reference_id}")
                logger.warning(f"Order not found with reference ID: {reference_id}")
        
        return Response({
            'success': True,
            'message': 'Webhook processed successfully'
        })
        
    except Exception as e:
        logger.error(f"Error processing Waafi webhook: {str(e)}")
        if 'webhook' in locals():
            webhook.mark_as_failed(str(e))
        
        return Response({
            'success': False,
            'error': 'Webhook processing failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
