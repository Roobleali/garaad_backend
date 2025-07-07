import resend
from django.conf import settings
from .models import EmailVerification
from decouple import config
import logging
import requests
from django.template.loader import render_to_string
from django.urls import reverse

logger = logging.getLogger(__name__)

# Get Resend API key from environment variables
RESEND_API_KEY = config('RESEND_API_KEY')
# Get email settings from environment variables
FROM_EMAIL = config('FROM_EMAIL', default='onboarding@resend.dev')
TEST_MODE = config('RESEND_TEST_MODE', default='True') == 'True'

def send_verification_email(user):
    """
    Send a verification email to the user with a verification code using the modern template
    """
    # Generate 6-digit verification code using the model method
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
        
        # Render the email template
        context = {
            'user_email': user.email,
            'verification_code': code,
            'resend_url': f"{settings.FRONTEND_URL}/resend-verification"
        }
        
        html_content = render_to_string('emails/email_verification.html', context)
        
        # Create a plain text version
        text_content = f"""
        Ku soo dhowow Garaad!

        Koodkaaga xaqiijinta waa: {code}

        Koodkaan wuxuu dhacayaa 10 daqiiqo gudahood.

        Haddii aadan codsanin xaqiijintan, fadlan iska dhaaf emailkaan.

        Mahadsanid,
        Kooxda Garaad
        """
        
        data = {
            "from": FROM_EMAIL,
            "to": to_email,
            "subject": "Xaqiiji Emailkaaga - Garaad ⚠️",
            "html": html_content,
            "text": text_content
        }
        
        logger.info(f"Sending email with template to: {to_email}")
        
        response = requests.post(
            "https://api.resend.com/emails",
            headers=headers,
            json=data,
            timeout=30
        )
        
        logger.info(f"Resend API Response Status: {response.status_code}")
        logger.info(f"Resend API Response: {response.text}")
        
        if response.status_code == 200:
            logger.info(f"Email sent successfully to {to_email}")
            return True
        else:
            raise Exception(f"Failed to send email: Status {response.status_code}, Response: {response.text}")
            
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
        # If email sending fails, delete the verification code
        verification.delete()
        raise e

def send_resend_email(to_email, subject, html, text=None):
    """
    Send an email using Resend API. Used for notifications and gamification emails.
    """
    try:
        # Validate required environment variables
        if not RESEND_API_KEY:
            logger.error("RESEND_API_KEY is not configured")
            return False
            
        if not FROM_EMAIL:
            logger.error("FROM_EMAIL is not configured")
            return False

        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "from": FROM_EMAIL,
            "to": to_email,
            "subject": subject,
            "html": html
        }
        
        if text:
            data["text"] = text
            
        logger.info(f"Sending Resend email to: {to_email}")
        logger.info(f"Email subject: {subject}")
        logger.info(f"From email: {FROM_EMAIL}")
        logger.info(f"Test mode: {TEST_MODE}")
        
        response = requests.post(
            "https://api.resend.com/emails",
            headers=headers,
            json=data,
            timeout=30  # Add timeout
        )
        
        logger.info(f"Resend API Response Status: {response.status_code}")
        logger.info(f"Resend API Response: {response.text}")
        
        if response.status_code == 200:
            logger.info(f"Email sent successfully to {to_email}")
            return True
        else:
            logger.error(f"Failed to send email to {to_email}. Status: {response.status_code}, Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while sending email to {to_email}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error while sending email to {to_email}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Failed to send Resend email to {to_email}: {str(e)}")
        return False 