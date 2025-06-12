import uuid
import requests
from django.conf import settings
from django.utils import timezone
from .models import Payment, Subscription

class WaafipayService:
    """
    Service class for handling Waafipay payment integration
    """
    def __init__(self):
        self.merchant_id = settings.WAAFIPAY_MERCHANT_ID
        self.api_key = settings.WAAFIPAY_API_KEY
        self.api_user_id = settings.WAAFIPAY_API_USER_ID
        self.is_test = settings.WAAFIPAY_TEST_MODE
        self.base_url = 'https://api.waafipay.net/asm' if not self.is_test else 'https://api-test.waafipay.net/asm'

    def _generate_transaction_id(self):
        """Generate a unique transaction ID"""
        return str(uuid.uuid4())

    def _get_amount(self, payment_type):
        """Get amount based on payment type"""
        if payment_type == 'local':
            return settings.WAAFIPAY_LOCAL_AMOUNT
        return settings.WAAFIPAY_DIASPORA_AMOUNT

    def initiate_payment(self, user, payment_type='local'):
        """
        Initiate a payment with Waafipay
        """
        amount = self._get_amount(payment_type)
        transaction_id = self._generate_transaction_id()

        # Create payment record
        payment = Payment.objects.create(
            user=user,
            amount=amount,
            payment_type=payment_type,
            transaction_id=transaction_id,
            currency='USD'
        )

        # Prepare Waafipay request
        payload = {
            'schemaVersion': '1.0',
            'requestId': transaction_id,
            'timestamp': timezone.now().isoformat(),
            'channelName': 'WEB',
            'serviceName': 'API_PURCHASE',
            'serviceParams': {
                'merchantUid': self.merchant_id,
                'apiUserId': self.api_user_id,
                'apiKey': self.api_key,
                'paymentMethod': 'MWALLET_ACCOUNT',
                'payerInfo': {
                    'accountNo': None,  # Will be provided by the user
                    'accountType': None,  # Will be provided by the user
                },
                'transactionInfo': {
                    'referenceId': transaction_id,
                    'invoiceId': transaction_id,
                    'amount': str(amount),
                    'currency': 'USD',
                    'description': f'Garaad Learning Premium Subscription - {payment_type.title()}'
                }
            }
        }

        return {
            'payment': payment,
            'payload': payload
        }

    def verify_payment(self, payment):
        """
        Verify payment status with Waafipay
        """
        url = f"{self.base_url}/verify"
        
        payload = {
            'schemaVersion': '1.0',
            'requestId': str(uuid.uuid4()),
            'timestamp': timezone.now().isoformat(),
            'channelName': 'WEB',
            'serviceName': 'API_CHECK_TXN',
            'serviceParams': {
                'merchantUid': self.merchant_id,
                'apiUserId': self.api_user_id,
                'apiKey': self.api_key,
                'referenceId': payment.transaction_id
            }
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

            if result.get('responseCode') == '2001':
                # Payment successful
                payment.status = 'completed'
                payment.waafipay_reference = result.get('serviceParams', {}).get('referenceId')
                payment.save()

                # Update user subscription
                subscription, _ = Subscription.objects.get_or_create(user=payment.user)
                subscription.extend_subscription()
                
                # Update user premium status
                user = payment.user
                user.is_premium = True
                user.save()

                return True
            else:
                # Payment failed
                payment.status = 'failed'
                payment.error_message = result.get('responseMsg')
                payment.save()
                return False

        except requests.exceptions.RequestException as e:
            payment.status = 'failed'
            payment.error_message = str(e)
            payment.save()
            return False 