"""
Email Verification Setup for Garaad Backend

This file contains all the necessary code and configurations for setting up
email verification using Resend API in the Garaad backend.
"""

import os
import random
import string
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.urls import path
from rest_framework.response import Response
from decouple import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Resend API Configuration
RESEND_API_KEY = config('RESEND_API_KEY', default='re_Shq6E56u_5RoR96gXtidwjKHCdVseWu4e')
FROM_EMAIL = config('FROM_EMAIL', default='noreply@garaad.org')
RESEND_TEST_MODE = config('RESEND_TEST_MODE', default=False, cast=bool)

# Import EmailVerification model from accounts app
from accounts.models import EmailVerification

# Email Sending Function
def send_verification_email(user):
    """
    Send a verification email to the user.
    
    Args:
        user: User instance to send verification email to
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Generate verification code
        code = EmailVerification.generate_code()
        
        # Save verification code
        verification = EmailVerification.objects.create(
            user=user,
            code=code
        )
        
        # Prepare email data
        subject = 'Xaqiiji Emailkaaga - Garaad'
        
        # Render HTML template
        context = {
            'verification_code': code,
            'site_url': getattr(settings, 'SITE_URL', 'https://garaad.org'),
        }
        
        html_message = render_to_string('emails/email_verification.html', context)
        
        # Fallback text message
        text_message = f"""
        Ku soo dhowow Garaad!

        Koodkaaga xaqiijinta waa: {code}

        Koodkaan wuxuu dhacayaa 24 saac gudahood.

        Haddii aadan codsanin xaqiijintan, fadlan iska dhaaf emailkaan.

        Mahadsanid,
        Kooxda Garaad
        """
        
        # Log attempt
        logger.info(f"Attempting to send verification email to {user.email} from {FROM_EMAIL}")
        
        # Send email using Resend API
        import resend
        resend.api_key = RESEND_API_KEY
        
        params = {
            "from": FROM_EMAIL,
            "to": user.email,
            "subject": subject,
            "html": html_message,
            "text": text_message
        }
        
        # Log email data
        logger.info(f"Sending email with data: {params}")
        
        # Send email
        response = resend.Emails.send(params)
        
        # Log response
        logger.info(f"Resend API Response Status: {response.status_code}")
        logger.info(f"Resend API Response: {response.text}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
        # Clean up verification code if email sending fails
        if 'verification' in locals():
            verification.delete()
        return False

# Email Verification View
def verify_email(request):
    """
    Verify user's email using the provided code.
    
    Args:
        request: HTTP request containing email and verification code
        
    Returns:
        Response: JSON response indicating success or failure
    """
    email = request.data.get('email')
    code = request.data.get('code')
    
    if not email or not code:
        return Response(
            {'error': 'Email and verification code are required'},
            status=400
        )
    
    try:
        user = get_user_model().objects.get(email=email)
        
        if user.is_email_verified:
            return Response(
                {'error': 'Email is already verified'},
                status=400
            )
        
        verification = EmailVerification.objects.filter(
            user=user,
            code=code,
            is_used=False
        ).first()
        
        if not verification:
            return Response(
                {'error': 'Invalid verification code'},
                status=400
            )
        
        if verification.is_expired():
            return Response(
                {'error': 'Invalid or expired verification code'},
                status=400
            )
        
        # Mark email as verified
        user.is_email_verified = True
        user.save()
        
        # Mark verification code as used
        verification.is_used = True
        verification.save()
        
        return Response(
            {'message': 'Email verified successfully'},
            status=200
        )
        
    except get_user_model().DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=404
        )
    except Exception as e:
        logger.error(f"Error verifying email: {str(e)}")
        return Response(
            {'error': 'An error occurred while verifying email'},
            status=500
        )

# Resend Verification Email View
def resend_verification_email(request):
    """
    Resend verification email to user.
    
    Args:
        request: HTTP request containing email
        
    Returns:
        Response: JSON response indicating success or failure
    """
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'error': 'Email is required'},
            status=400
        )
    
    try:
        user = get_user_model().objects.get(email=email)
        
        if user.is_email_verified:
            return Response(
                {'error': 'Email is already verified'},
                status=400
            )
        
        # Delete any existing unused verification codes
        EmailVerification.objects.filter(
            user=user,
            is_used=False
        ).delete()
        
        # Send new verification email
        if send_verification_email(user):
            return Response(
                {'message': 'Verification email sent successfully'},
                status=200
            )
        else:
            return Response(
                {'error': 'Failed to send verification email'},
                status=500
            )
            
    except get_user_model().DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=404
        )
    except Exception as e:
        logger.error(f"Error resending verification email: {str(e)}")
        return Response(
            {'error': 'An error occurred while resending verification email'},
            status=500
        )

# URL Patterns
urlpatterns = [
    path('verify-email/', verify_email, name='verify_email'),
    path('resend-verification/', resend_verification_email, name='resend_verification_email'),
]

# Settings Configuration
EMAIL_VERIFICATION_SETTINGS = {
    'RESEND_API_KEY': RESEND_API_KEY,
    'FROM_EMAIL': FROM_EMAIL,
    'RESEND_TEST_MODE': RESEND_TEST_MODE,
    'CODE_EXPIRY_HOURS': 24,
    'CODE_LENGTH': 6,
}

# Usage Instructions
"""
To use this email verification system:

1. Add to settings.py:
   from email_verification_setup import EMAIL_VERIFICATION_SETTINGS
   settings.update(EMAIL_VERIFICATION_SETTINGS)

2. Add to urls.py:
   from email_verification_setup import urlpatterns as email_verification_urls
   urlpatterns += email_verification_urls

3. Add to models.py:
   from email_verification_setup import EmailVerification

4. Add to views.py:
   from email_verification_setup import send_verification_email

5. Set environment variables:
   RESEND_API_KEY=your_api_key
   FROM_EMAIL=your_email
   RESEND_TEST_MODE=True/False
""" 