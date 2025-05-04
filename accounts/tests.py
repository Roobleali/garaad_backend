from django.test import TestCase, Client
from django.urls import reverse
from .models import User, EmailVerification
import json

class SignupTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('register_user')

    def test_signup_and_email_verification(self):
        # Test signup
        signup_data = {
            'username': 'testuser',
            'email': 'salutict@gmail.com',
            'password': 'testpass123',
            'age': 25
        }
        response = self.client.post(
            self.signup_url,
            data=json.dumps(signup_data),
            content_type='application/json'
        )
        
        print("Signup Response:", response.content)
        self.assertEqual(response.status_code, 201)

        # Verify user was created
        user = User.objects.get(email='salutict@gmail.com')
        self.assertFalse(user.is_email_verified)

        # Verify that a verification code was created
        verification = EmailVerification.objects.filter(user=user).first()
        self.assertIsNotNone(verification)
        print("Verification Code:", verification.code)

        # Test email verification
        verify_url = reverse('verify_email')
        verify_data = {
            'email': 'salutict@gmail.com',
            'code': verification.code
        }
        response = self.client.post(
            verify_url,
            data=json.dumps(verify_data),
            content_type='application/json'
        )
        
        print("Verification Response:", response.content)
        self.assertEqual(response.status_code, 200)

        # Verify user's email is now verified
        user.refresh_from_db()
        self.assertTrue(user.is_email_verified) 