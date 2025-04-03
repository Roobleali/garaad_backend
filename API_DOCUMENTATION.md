# Garaad Backend API Documentation

This document provides a comprehensive guide to the Garaad Backend API, including authentication, available endpoints, request formats, and response formats.

## Base URL

For local development:
```
http://localhost:8000/
```

For production:
```
https://api.garaad.org/
```

## Authentication

The API uses JWT (JSON Web Token) for authentication. Most endpoints require authentication.

### Authentication Headers

For protected endpoints, include the JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Lifecycle

- Access tokens are valid for 15 minutes
- Refresh tokens are valid for 1 day
- Use the refresh endpoint to get a new access token before it expires

## API Endpoints

### Authentication Endpoints

#### 1. User Registration with Onboarding

**Endpoint:** `POST /api/signup/`

**Description:** Registers a new user and creates onboarding information in a single request.

**Request Body:**
```json
{
  "name": "User Full Name",
  "email": "user@example.com",
  "password": "securepassword123",
  "goal": "Horumarinta xirfadaha",
  "learning_approach": "Waxbarasho shaqsiyeed",
  "topic": "Xisaab",
  "math_level": "Bilowga",
  "minutes_per_day": 30
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "User Full Name",
    "email": "user@example.com",
    "first_name": "User",
    "last_name": "Full Name",
    "is_premium": false,
    "has_completed_onboarding": true
  },
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5..."
  }
}
```

**Errors:**
- 400 Bad Request: If validation fails (e.g., email already exists, invalid data)

#### 2. User Login

**Endpoint:** `POST /api/signin/`

**Description:** Authenticates a user and returns tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "username": "User Full Name",
    "email": "user@example.com",
    "first_name": "User",
    "last_name": "Full Name",
    "is_premium": false,
    "has_completed_onboarding": true
  },
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5..."
  }
}
```

**Errors:**
- 401 Unauthorized: If credentials are invalid

#### 3. Token Refresh

**Endpoint:** `POST /api/auth/refresh/`

**Description:** Get a new access token using a refresh token.

**Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5..."
}
```

**Errors:**
- 401 Unauthorized: If refresh token is invalid or expired

### User Profile

#### 1. Get User Profile

**Endpoint:** `GET /api/auth/profile/`

**Description:** Retrieves the authenticated user's profile information.

**Authentication Required:** Yes

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "User Full Name",
  "email": "user@example.com",
  "first_name": "User",
  "last_name": "Full Name",
  "is_premium": false
}
```

**Errors:**
- 401 Unauthorized: If not authenticated

### Onboarding

#### 1. Get Onboarding Status

**Endpoint:** `GET /api/auth/onboarding/status/`

**Description:** Checks if a user has completed onboarding.

**Authentication Required:** Yes

**Response (200 OK):**
```json
{
  "has_completed_onboarding": true
}
```

**Errors:**
- 401 Unauthorized: If not authenticated

#### 2. Complete Onboarding

**Endpoint:** `POST /api/auth/onboarding/complete/`

**Description:** Submit onboarding information for an existing user.

**Authentication Required:** Yes

**Request Body:**
```json
{
  "goal": "Horumarinta xirfadaha",
  "learning_approach": "Waxbarasho shaqsiyeed",
  "topic": "Xisaab",
  "math_level": "Bilowga",
  "minutes_per_day": 30
}
```

**Response (200 OK):**
```json
{
  "goal": "Horumarinta xirfadaha",
  "learning_approach": "Waxbarasho shaqsiyeed",
  "topic": "Xisaab",
  "math_level": "Bilowga",
  "minutes_per_day": 30,
  "has_completed_onboarding": true
}
```

**Errors:**
- 400 Bad Request: If validation fails
- 401 Unauthorized: If not authenticated

### Student Profile

#### 1. Register Student Profile

**Endpoint:** `POST /api/auth/student/register/`

**Description:** Create a student profile for an authenticated user.

**Authentication Required:** Yes

**Request Body:**
```json
{
  "preferred_study_time": ["morning", "evening"],
  "subjects": ["math", "science"],
  "proficiency_level": "Intermediate",
  "study_frequency": 3
}
```

**Response (201 Created):**
```json
{
  "preferred_study_time": ["morning", "evening"],
  "subjects": ["math", "science"],
  "proficiency_level": "Intermediate",
  "study_frequency": 3
}
```

**Errors:**
- 400 Bad Request: If validation fails or profile already exists
- 401 Unauthorized: If not authenticated

### Other Endpoints

#### 1. API Root

**Endpoint:** `GET /api/`

**Description:** Returns information about available API endpoints.

**Authentication Required:** No

**Response (200 OK):**
```json
{
  "status": "online",
  "version": "1.0.0",
  "endpoints": {
    "auth": "/api/auth/",
    "hello": "/hello-world/",
    "signup": "/api/signup/",
    "signin": "/api/signin/"
  }
}
```

#### 2. Hello World

**Endpoint:** `GET /hello-world/`

**Description:** A simple endpoint that returns "Hello, World!"

**Authentication Required:** No

**Response (200 OK):**
```
Hello, World!
```

## Common Error Responses

### 400 Bad Request
```json
{
  "field_name": [
    "Error message about this field"
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

## Integration Guide for Frontend Developers

### Authentication Flow

1. **Registration:**
   - Call the signup endpoint with user details and onboarding information
   - Store the returned access and refresh tokens securely (e.g., in HttpOnly cookies or localStorage)

2. **Login:**
   - Call the signin endpoint with email and password
   - Store the returned tokens

3. **Making Authenticated Requests:**
   - Include the access token in the Authorization header for every protected request
   - `Authorization: Bearer <access_token>`

4. **Token Refresh:**
   - When the access token expires, use the refresh token to get a new one
   - Implement token refresh before access token expiration (e.g., after 14 minutes for a 15-minute token)

### Error Handling

- Always handle 400, 401, and 404 errors appropriately in your frontend
- Display validation errors to the user in a friendly format
- Redirect to login page on 401 errors (after attempting token refresh)

### Example: User Registration Flow

```javascript
// Example using fetch API
async function registerUser(userData) {
  try {
    const response = await fetch('http://localhost:8000/api/signup/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(JSON.stringify(errorData));
    }
    
    const data = await response.json();
    
    // Store tokens
    localStorage.setItem('accessToken', data.tokens.access);
    localStorage.setItem('refreshToken', data.tokens.refresh);
    
    return data.user;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
}
```

### Example: Making Authenticated Requests

```javascript
async function fetchUserProfile() {
  try {
    const accessToken = localStorage.getItem('accessToken');
    
    const response = await fetch('http://localhost:8000/api/auth/profile/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    });
    
    if (response.status === 401) {
      // Token expired, try to refresh
      await refreshToken();
      return fetchUserProfile(); // Retry with new token
    }
    
    if (!response.ok) {
      throw new Error('Failed to fetch profile');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Profile fetch error:', error);
    throw error;
  }
}

async function refreshToken() {
  const refreshToken = localStorage.getItem('refreshToken');
  
  const response = await fetch('http://localhost:8000/api/auth/refresh/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh: refreshToken }),
  });
  
  if (!response.ok) {
    // Refresh failed, redirect to login
    window.location.href = '/login';
    throw new Error('Session expired');
  }
  
  const data = await response.json();
  localStorage.setItem('accessToken', data.access);
  return data.access;
}
```

## Development Guidelines

1. Always validate input on the frontend before sending to API
2. Implement proper error handling for all API calls
3. Use the token refresh mechanism to maintain session
4. Securely store tokens (HttpOnly cookies are preferred in production)
5. Log out users when refresh token expires or is invalid 