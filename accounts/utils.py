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
            "subject": "Xaqiiji Emailkaaga - Garaad",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <img src="https://garaad.org/static/images/logo.png" alt="Garaad Logo" style="max-width: 150px; height: auto;">
                </div>
                
                <h2 style="color: #2C3E50; text-align: center; margin-bottom: 25px; font-size: 24px;">Ku soo dhowow Garaad!</h2>
                
                <p style="color: #34495E; font-size: 16px; line-height: 1.6; margin-bottom: 20px;">
                    Waad ku mahadsantahay inaad is diiwaangelisay. Fadlan isticmaal koodka soo socda si aad u xaqiijiso cinwaanka emailkaaga:
                </p>
                
                <div style="background-color: #F8F9FA; padding: 25px; border-radius: 8px; text-align: center; margin: 25px 0; border: 2px dashed #3498DB;">
                    <h1 style="color: #3498DB; margin: 0; font-size: 32px; letter-spacing: 5px;">{code}</h1>
                </div>
                
                <div style="background-color: #F1F8FF; padding: 15px; border-radius: 6px; margin: 20px 0;">
                    <p style="color: #2C3E50; margin: 0; font-size: 14px;">
                        <strong>Xasuuso:</strong> Number sireedkan wuxuu dhacayaa 24 saac gudahood.
                    </p>
                </div>
                
                <p style="color: #7F8C8D; font-size: 14px; line-height: 1.5; margin: 25px 0;">
                    Haddii aadan codsanin xaqiijintan, fadlan iska dhaaf emailkaan.
                </p>
                
                <div style="border-top: 1px solid #ECF0F1; margin-top: 30px; padding-top: 20px; text-align: center;">
                    <p style="color: #7F8C8D; margin: 0; font-size: 14px;">
                        Mahadsanid,<br>
                        <strong style="color: #2C3E50;">Kooxda Garaad</strong>
                    </p>
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