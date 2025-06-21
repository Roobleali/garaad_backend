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
            "subject": "Xaqiiji Emailkaaga - Garaad ✅",
            "html": f"""
            <div style=\"font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; background: linear-gradient(135deg, #f8fafc 0%, #e0e7ef 100%); border-radius: 16px; box-shadow: 0 4px 16px rgba(44, 62, 80, 0.08);\">
                <div style=\"text-align: center; margin-bottom: 24px;\">
                    <img src=\"https://www.garaad.org/favicon.ico">
                    <h1 style=\"color: #3498DB; font-size: 2rem; margin: 0;\">Garaad 📚</h1>
                </div>
                <div style=\"text-align: center; margin-bottom: 20px;\">
                    <span style=\"font-size: 2.5rem;\">✅📧</span>
                </div>
                <h2 style=\"color: #2C3E50; text-align: center; margin-bottom: 18px; font-size: 1.5rem;\">Ku soo dhowow Garaad!</h2>
                <p style=\"color: #34495E; font-size: 1.1rem; line-height: 1.7; margin-bottom: 18px; text-align: center;\">
                    Waad ku mahadsantahay inaad is diiwaangelisay. <br>Fadlan isticmaal koodka hoose si aad u xaqiijiso cinwaanka emailkaaga:
                </p>
                <div style=\"background: #eaf6fb; padding: 28px 0; border-radius: 10px; text-align: center; margin: 24px 0; border: 2px dashed #3498DB;\">
                    <span style=\"font-size: 2.2rem; color: #3498DB; font-weight: bold; letter-spacing: 8px;\">{code}</span>
                </div>
                <div style=\"background: #fffbe6; padding: 14px; border-radius: 8px; margin: 18px 0; text-align: center;\">
                    <span style=\"font-size: 1.1rem; color: #e67e22;\">⏰ <strong>Xasuuso:</strong> Koodhkani wuxuu dhacayaa 10 daqiiqo gudahood.</span>
                </div>
                <p style=\"color: #7F8C8D; font-size: 1rem; line-height: 1.5; margin: 22px 0; text-align: center;\">
                    Haddii aadan codsanin xaqiijintan, fadlan iska dhaaf emailkaan.
                </p>
                <div style=\"border-top: 1px solid #ECF0F1; margin-top: 28px; padding-top: 18px; text-align: center;\">
                    <span style=\"font-size: 1.1rem; color: #2C3E50;\">Mahadsanid, <span style=\"font-weight: bold;\">Kooxda Garaad</span> 🙏</span>
                </div>
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