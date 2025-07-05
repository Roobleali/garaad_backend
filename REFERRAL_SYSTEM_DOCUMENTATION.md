# Referral System Documentation

## Overview

This document describes the implementation of a referral system for the Django backend. The system allows users to refer new users using unique referral codes and earn points for successful referrals.

## Features

1. **Unique Referral Codes**: Every user gets a unique 8-character alphanumeric referral code
2. **Referral Tracking**: Users can be linked to the user who referred them
3. **Points System**: Users earn points for each successful referral (default: 10 points)
4. **API Endpoints**: RESTful API endpoints to manage and retrieve referral data

## Database Schema

### User Model Extensions

The `User` model has been extended with the following fields:

```python
class User(AbstractUser):
    # ... existing fields ...
    
    # Referral System fields
    referral_code = models.CharField(max_length=8, unique=True, blank=True)
    referred_by = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='referrals'
    )
    referral_points = models.PositiveIntegerField(default=0)
```

### Model Methods

The User model includes several methods for referral management:

```python
def generate_referral_code(cls):
    """Generate a unique 8-character alphanumeric referral code"""

def award_referral_points(self, points=10):
    """Award points for successful referral"""

def get_referral_count(self):
    """Get count of users referred by this user"""

def get_referral_list(self):
    """Get list of users referred by this user"""
```

## API Endpoints

### 1. User Signup with Referral Code

**Endpoint**: `POST /api/auth/signup/`

**Request Body**:
```json
{
    "username": "new_user",
    "email": "user@example.com",
    "password": "password123",
    "age": 25,
    "referral_code": "abc123def"  // Optional referral code
}
```

**Response** (201 Created):
```json
{
    "user": {
        "id": 123,
        "username": "new_user",
        "email": "user@example.com",
        "referral_code": "xyz789uvw",
        "referral_points": 0,
        "referral_count": 0,
        "referred_by_username": "referrer_user"
    },
    "tokens": {
        "access": "...",
        "refresh": "..."
    },
    "message": "User registered successfully. Please check your email for verification."
}
```

### 2. Get Referral Data

**Endpoint**: `GET /api/auth/referrals/`

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
    "referral_code": "abc123def",
    "referral_points": 50,
    "referral_count": 5,
    "referred_users": [
        {
            "id": 124,
            "username": "referred_user1",
            "email": "user1@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "created_at": "2023-01-15T10:30:00Z"
        },
        {
            "id": 125,
            "username": "referred_user2",
            "email": "user2@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "created_at": "2023-01-16T14:20:00Z"
        }
    ]
}
```

### 3. Get Referral Statistics

**Endpoint**: `GET /api/auth/referral-stats/`

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
    "referral_code": "abc123def",
    "referral_points": 50,
    "referral_count": 5,
    "referred_by": "original_referrer",
    "is_referred_user": true
}
```

## Usage Examples

### Frontend Integration

#### Display User's Referral Code

```javascript
// Get user's referral information
fetch('/api/auth/referral-stats/', {
    headers: {
        'Authorization': `Bearer ${accessToken}`
    }
})
.then(response => response.json())
.then(data => {
    console.log('Your referral code:', data.referral_code);
    console.log('Your referral points:', data.referral_points);
    console.log('Users you referred:', data.referral_count);
});
```

#### Signup with Referral Code

```javascript
// Sign up new user with referral code
const signupData = {
    username: 'new_user',
    email: 'user@example.com',
    password: 'password123',
    age: 25,
    referral_code: 'abc123def'  // Optional
};

fetch('/api/auth/signup/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(signupData)
})
.then(response => response.json())
.then(data => {
    if (data.user) {
        console.log('User created successfully');
        console.log('New user referral code:', data.user.referral_code);
    }
});
```

#### Get List of Referred Users

```javascript
// Get detailed list of referred users
fetch('/api/auth/referrals/', {
    headers: {
        'Authorization': `Bearer ${accessToken}`
    }
})
.then(response => response.json())
.then(data => {
    console.log('Referred users:', data.referred_users);
    data.referred_users.forEach(user => {
        console.log(`- ${user.username} (${user.email})`);
    });
});
```

## Backend Integration

### Creating Users with Referrals

```python
from django.contrib.auth import get_user_model
from accounts.serializers import SignupSerializer

User = get_user_model()

# Create user with referral code
signup_data = {
    'username': 'new_user',
    'email': 'user@example.com',
    'password': 'password123',
    'age': 25,
    'referral_code': 'abc123def'
}

serializer = SignupSerializer(data=signup_data)
if serializer.is_valid():
    user = serializer.save()
    print(f"User created with referral code: {user.referral_code}")
    print(f"Referred by: {user.referred_by.username if user.referred_by else 'None'}")
```

### Manually Managing Referrals

```python
# Get user's referral statistics
user = User.objects.get(username='some_user')
referral_count = user.get_referral_count()
referral_list = user.get_referral_list()

# Award bonus points
user.award_referral_points(20)

# Get all users referred by this user
referred_users = user.referrals.all()
```

## Migration

The referral system requires a database migration to add the new fields:

```bash
python manage.py makemigrations accounts
python manage.py migrate accounts
```

**Note**: The migration includes a data migration step that automatically generates referral codes for existing users.

## Configuration

### Referral Points

The default points awarded per referral can be modified in the `award_referral_points` method call:

```python
# Award custom points
referrer.award_referral_points(15)  # Award 15 points instead of default 10
```

### Referral Code Generation

Referral codes are 8-character alphanumeric (lowercase) strings. The generation logic can be customized in the `generate_referral_code` method:

```python
@classmethod
def generate_referral_code(cls):
    """Generate a unique 8-character alphanumeric referral code"""
    while True:
        code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        if not cls.objects.filter(referral_code=code).exists():
            return code
```

## Error Handling

### Invalid Referral Code

When a user provides an invalid referral code during signup:

```json
{
    "referral_code": ["Invalid referral code"]
}
```

### Validation Errors

Standard Django validation errors are returned for other field validation issues:

```json
{
    "email": ["This field is required."],
    "username": ["Username already exists"]
}
```

## Security Considerations

1. **Referral Code Uniqueness**: The system ensures all referral codes are unique across all users
2. **Self-Referral Prevention**: Users cannot refer themselves (handled by foreign key constraint)
3. **Code Generation**: Referral codes are randomly generated and difficult to guess
4. **API Authentication**: Referral endpoints require valid JWT authentication

## Testing

A comprehensive test suite is included in `test_referral_system.py`:

```bash
# Run the test suite
python test_referral_system.py
```

The test covers:
- User creation with referral codes
- Points awarding system
- API endpoint functionality
- Error handling for invalid codes

## Future Enhancements

1. **Referral Levels**: Multi-level referral system (referrer gets points for referred user's referrals)
2. **Expiring Codes**: Optional expiration dates for referral codes
3. **Custom Codes**: Allow users to create custom referral codes
4. **Referral Analytics**: Dashboard for tracking referral performance
5. **Referral Rewards**: Different reward types (badges, premium features, etc.)

## Conclusion

The referral system provides a robust foundation for user growth through referrals. It's built with Django best practices, includes comprehensive API endpoints, and is ready for production use.

For questions or issues, please refer to the codebase or contact the development team. 