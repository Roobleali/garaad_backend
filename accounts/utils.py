import resend
from django.conf import settings
from .models import EmailVerification
from decouple import config
import logging
import requests

logger = logging.getLogger(__name__)

# Get Resend API key from environment variables
RESEND_API_KEY = config('RESEND_API_KEY')
# Get email settings from environment variables
FROM_EMAIL = config('FROM_EMAIL', default='onboarding@resend.dev')
TEST_MODE = config('RESEND_TEST_MODE', default='True') == 'True'

def send_verification_email(user):
    """
    Send a verification email to the user with a verification code
    """
    # Generate verification code
    code = EmailVerification.generate_code()
    
    # Save verification code
    verification = EmailVerification.objects.create(
        user=user,
        code=code
    )
    
    # Send email using Resend
    try:
        # In production, use the actual user's email
        # In test mode, use the test email address
        to_email = "maanc143@gmail.com" if TEST_MODE else user.email
        
        logger.info(f"Attempting to send verification email to {to_email} from {FROM_EMAIL}")
        
        # Use direct API call
        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "from": FROM_EMAIL,
            "to": to_email,
            "subject": "Verify Your Email - Garaad",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #333;">Welcome to Garaad!</h2>
                <p>Thank you for signing up. Please use the following code to verify your email address:</p>
                <div style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0;">
                    <h1 style="color: #007bff; margin: 0;">{code}</h1>
                </div>
                <p>This code will expire in 24 hours.</p>
                <p>If you didn't create an account, you can safely ignore this email.</p>
                <p>Best regards,<br>The Garaad Team</p>
            </div>
            """
        }
        
        logger.info(f"Sending email with data: {data}")
        
        response = requests.post(
            "https://api.resend.com/emails",
            headers=headers,
            json=data
        )
        
        logger.info(f"Resend API Response Status: {response.status_code}")
        logger.info(f"Resend API Response: {response.text}")
        
        if response.status_code != 200:
            raise Exception(f"Failed to send email: {response.text}")
            
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
        # If email sending fails, delete the verification code
        verification.delete()
        raise e 