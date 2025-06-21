# Garaad Subscription API Documentation

## Overview
This document outlines the API endpoints for managing user subscriptions in the Garaad platform. All endpoints require authentication using JWT tokens.

## Base URL
```
http://127.0.0.1:8000/api/auth/
```

## Authentication
All endpoints (except login) require a Bearer token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Endpoints

### 1. Login
Get access token for authenticated requests.

```http
POST /signin/
```

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**Response:**
```json
{
    "user": {
        "id": 41,
        "username": "username",
        "email": "user@example.com",
        "first_name": "First",
        "last_name": "Last",
        "is_premium": true,
        "has_completed_onboarding": true
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
}
```

### 2. Update Premium Status
Update a user's premium subscription status.

```http
POST /update-premium/
```

**Request Body Examples:**

1. Monthly Subscription:
```json
{
    "is_premium": true,
    "subscription_type": "monthly",
    "subscription_start_date": "2024-06-13T00:00:00Z",
    "subscription_end_date": "2024-07-13T00:00:00Z"
}
```

2. Yearly Subscription:
```json
{
    "is_premium": true,
    "subscription_type": "yearly",
    "subscription_start_date": "2024-06-13T00:00:00Z",
    "subscription_end_date": "2025-06-13T00:00:00Z"
}
```

3. Lifetime Subscription:
```json
{
    "is_premium": true,
    "subscription_type": "lifetime"
}
```

4. Remove Premium Status:
```json
{
    "is_premium": false
}
```

**Response:**
```json
{
    "message": "Premium status updated successfully",
    "is_premium": true,
    "subscription_type": "monthly",
    "subscription_start_date": "2024-06-13T00:00:00+00:00",
    "subscription_end_date": "2024-07-13T00:00:00+00:00"
}
```

### 3. Get User Profile
Check user's premium status and subscription details.

```http
GET /profile/
```

**Response:**
```json
{
    "id": 41,
    "username": "username",
    "email": "user@example.com",
    "first_name": "First",
    "last_name": "Last",
    "is_premium": true,
    "subscription_type": "monthly",
    "subscription_start_date": "2024-06-13T00:00:00+00:00",
    "subscription_end_date": "2024-07-13T00:00:00+00:00"
}
```

## Subscription Types
- `monthly`: 30-day subscription
- `yearly`: 365-day subscription
- `lifetime`: Permanent subscription

## Error Responses

### 401 Unauthorized
```json
{
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Token is expired"
        }
    ]
}
```

### 400 Bad Request
```json
{
    "error": "is_premium field is required"
}
```

## Frontend Integration Guidelines

### 1. Token Management
- Store access token in memory (not localStorage)
- Store refresh token in HTTP-only cookie
- Implement token refresh logic when access token expires

### 2. Premium Status Check
- Check premium status on app load
- Verify subscription before accessing premium features
- Display subscription expiry date to users

### 3. UI Considerations
- Show different UI states for:
  - Non-premium users
  - Premium users (with expiry date)
  - Lifetime premium users
- Display subscription type and remaining time
- Show upgrade options for non-premium users

### 4. Date Handling
- All dates are in ISO 8601 format
- Use UTC timezone for consistency
- Format dates appropriately for user's locale

## Best Practices
1. Always verify premium status on the backend
2. Implement proper error handling for expired tokens
3. Cache user's premium status to reduce API calls
4. Show appropriate loading states during API calls
5. Implement proper validation for subscription dates

## Rate Limiting
- Login attempts: 5 per minute
- Premium status updates: 10 per hour
- Profile checks: 60 per hour 