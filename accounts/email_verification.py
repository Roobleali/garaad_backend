import resend
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
import secrets
import os

User = get_user_model()

def generate_verification_token():
    """Generate a secure random token for email verification"""
    return secrets.token_urlsafe(32)

def send_verification_email(email, token):
    """Send verification email using Resend"""
    resend.api_key = os.getenv('RESEND_API_KEY', 're_brvqbBuG_MSigpR5NYVfP3zpUjSeeNagE')
    
    # Get the base URL from settings or use a default
    base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')
    verification_url = f"{base_url}/api/verify-email/{token}"
    
    try:
        r = resend.Emails.send({
            "from": "info@garaad.org",
            "to": email,
            "subject": "Verify your Garaad account",
            "html": f"""
                <h2>Welcome to Garaad!</h2>
                <p>Please click the link below to verify your email address:</p>
                <p><a href="{verification_url}">Verify Email Address</a></p>
                <p>If you did not create an account, please ignore this email.</p>
            """
        })
        return True
    except Exception as e:
        print(f"Error sending verification email: {str(e)}")
        return False

def store_verification_token(email, token):
    """Store the verification token in cache with 24 hour expiry"""
    cache_key = f"email_verification_{token}"
    cache.set(cache_key, email, timeout=86400)  # 24 hours

def verify_email_token(token):
    """Verify the email token and activate the user account"""
    cache_key = f"email_verification_{token}"
    email = cache.get(cache_key)
    
    if not email:
        return False, "Invalid or expired verification token"
    
    try:
        user = User.objects.get(email=email)
        user.is_active = True
        user.save()
        cache.delete(cache_key)
        return True, "Email verified successfully"
    except User.DoesNotExist:
        return False, "User not found" 