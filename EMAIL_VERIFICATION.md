# Email Verification System Documentation

## Overview
The email verification system uses Resend API to send verification emails to users upon registration. This helps prevent fraud and ensures that users provide valid email addresses.

 
## API Endpoints

### 1. Signup with Email Verification
```http
POST /api/auth/signup/
Content-Type: application/json

{
    "username": "string",
    "email": "string",
    "password": "string",
    "age": number
}
```

Response (201 Created):
```json
{
    "token": "string",
    "user": {
        "id": number,
        "username": "string",
        "email": "string",
        "first_name": "string",
        "last_name": "string",
        "is_premium": boolean,
        "has_completed_onboarding": boolean,
        "profile": null,
        "age": number
    }
}
```

### 2. Verify Email
```http
POST /api/auth/verify-email/
Content-Type: application/json

{
    "email": "string",
    "code": "string"
}
```

Response (200 OK):
```json
{
    "message": "Email verified successfully"
}
```

### 3. Resend Verification Email
```http
POST /api/auth/resend-verification/
Content-Type: application/json

{
    "email": "string"
}
```

Response (200 OK):
```json
{
    "message": "Verification email sent successfully"
}
```

## Database Models

### User Model
```python
class User(AbstractUser):
    # ... other fields ...
    is_email_verified = models.BooleanField(default=False)
```

### EmailVerification Model
```python
class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
```

## Flow

1. **User Registration**:
   - User submits signup form
   - System creates user account
   - System generates verification code
   - System sends verification email
   - User account is created with `is_email_verified=False`

2. **Email Verification**:
   - User receives email with verification code
   - User submits code through verification endpoint
   - System validates code and marks email as verified
   - User account is updated with `is_email_verified=True`

3. **Resend Verification**:
   - If user doesn't receive email or code expires
   - User can request new verification email
   - System generates new code and sends new email

## Security Features

1. **Code Expiration**: Verification codes expire after 24 hours
2. **One-time Use**: Codes can only be used once
3. **Rate Limiting**: Prevents abuse of verification endpoints
4. **Email Validation**: Ensures valid email format
5. **Domain Verification**: In production, emails are sent from verified domains

## Testing

### Development Testing
In development mode (`RESEND_TEST_MODE=True`):
- All verification emails are sent to the test email address
- No domain verification required
- Use Resend's test API key

### Production Testing
In production mode (`RESEND_TEST_MODE=False`):
- Emails are sent to actual user email addresses
- Domain must be verified with Resend
- Use production API key

## Error Handling

Common error responses:

1. **Invalid Code**:
```json
{
    "error": "Invalid verification code"
}
```

2. **Expired Code**:
```json
{
    "error": "Invalid or expired verification code"
}
```

3. **Already Verified**:
```json
{
    "error": "Email is already verified"
}
```

4. **Email Sending Failed**:
```json
{
    "error": "Failed to send verification email: [error details]"
}
```

## Maintenance

1. **Cleanup**: Implement a periodic task to clean up expired verification codes
2. **Monitoring**: Monitor email delivery rates and verification success rates
3. **Logging**: Check logs for any email sending failures
4. **API Key Rotation**: Regularly rotate Resend API keys for security

## Troubleshooting

1. **Emails Not Sending**:
   - Check Resend API key
   - Verify domain in production
   - Check email quotas
   - Review error logs

2. **Verification Codes Not Working**:
   - Check code expiration
   - Verify code format
   - Check database for code existence

3. **Production Issues**:
   - Verify domain settings
   - Check DNS records
   - Monitor API usage
   - Review error logs 