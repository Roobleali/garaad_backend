from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Payment, Subscription
from .serializers import PaymentSerializer, SubscriptionSerializer
from .services import WaafipayService

# Create your views here.

class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling payments
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    queryset = Payment.objects.none()

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def initiate(self, request):
        """
        Initiate a payment with Waafipay
        """
        payment_type = request.data.get('payment_type', 'local')
        if payment_type not in ['local', 'diaspora']:
            return Response(
                {'error': 'Invalid payment type'},
                status=status.HTTP_400_BAD_REQUEST
            )

        waafipay = WaafipayService()
        result = waafipay.initiate_payment(request.user, payment_type)

        return Response({
            'payment': PaymentSerializer(result['payment']).data,
            'waafipay_payload': result['payload']
        })

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        Verify payment status
        """
        payment = self.get_object()
        if payment.status == 'completed':
            return Response({
                'message': 'Payment already completed',
                'payment': PaymentSerializer(payment).data
            })

        waafipay = WaafipayService()
        success = waafipay.verify_payment(payment)

        if success:
            return Response({
                'message': 'Payment verified successfully',
                'payment': PaymentSerializer(payment).data
            })
        else:
            return Response({
                'message': 'Payment verification failed',
                'payment': PaymentSerializer(payment).data
            }, status=status.HTTP_400_BAD_REQUEST)

class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing subscriptions
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.none()

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Get current user's subscription
        """
        subscription = get_object_or_404(Subscription, user=request.user)
        return Response(SubscriptionSerializer(subscription).data)

    @action(detail=False, methods=['post'])
    def toggle_auto_renew(self, request):
        """
        Toggle auto-renewal of subscription
        """
        subscription = get_object_or_404(Subscription, user=request.user)
        subscription.auto_renew = not subscription.auto_renew
        subscription.save()
        return Response(SubscriptionSerializer(subscription).data)
