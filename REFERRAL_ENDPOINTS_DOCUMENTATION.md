# Referral System API Endpoints

## 📋 **Overview**

The referral system provides endpoints for managing user referrals, tracking referral points, and handling referral codes. All endpoints require authentication unless specified otherwise.

## 🔗 **Base URL**
```
https://your-domain.com/api/auth/
```

## 📊 **Endpoints Summary**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/referrals/` | Get user's referral data and referred users | ✅ |
| `GET` | `/referral-stats/` | Get referral statistics | ✅ |
| `POST` | `/signup/` | Register user with optional referral code | ❌ |

---

## 🔍 **Detailed Endpoints**

### **1. Get Referral Data**
**`GET /api/auth/referrals/`**

Returns comprehensive referral data for the authenticated user.

**Headers:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Response:**
```json
{
  "referral_code": "abc12345",
  "referral_points": 50,
  "referral_count": 3,
  "referred_users": [
    {
      "id": 2,
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "created_at": "2025-07-05T10:30:00Z"
    },
    {
      "id": 3,
      "username": "jane_smith",
      "email": "jane@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "created_at": "2025-07-05T11:15:00Z"
    }
  ]
}
```

**Response Fields:**
- `referral_code` (string): User's unique 8-character referral code
- `referral_points` (integer): Total points earned from referrals
- `referral_count` (integer): Number of users referred
- `referred_users` (array): List of users referred by this user

---

### **2. Get Referral Statistics**
**`GET /api/auth/referral-stats/`**

Returns summary statistics without detailed user information.

**Headers:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Response:**
```json
{
  "referral_code": "abc12345",
  "referral_points": 50,
  "referral_count": 3,
  "referred_by": "mary_jones",
  "is_referred_user": true
}
```

**Response Fields:**
- `referral_code` (string): User's unique referral code
- `referral_points` (integer): Total points earned from referrals
- `referral_count` (integer): Number of users referred
- `referred_by` (string|null): Username of user who referred this user
- `is_referred_user` (boolean): Whether this user was referred by someone

---

### **3. Register User with Referral**
**`POST /api/auth/signup/`**

Register a new user with optional referral code.

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepassword123",
  "age": 25,
  "referral_code": "abc12345"
}
```

**Request Fields:**
- `username` (string, required): Unique username
- `email` (string, required): Valid email address
- `password` (string, required): Secure password
- `age` (integer, required): User's age (1-120)
- `referral_code` (string, optional): Valid referral code

**Response (Success):**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 4,
    "username": "newuser",
    "email": "newuser@example.com",
    "first_name": "",
    "last_name": "",
    "is_premium": false,
    "has_completed_onboarding": false,
    "profile": null,
    "age": 25,
    "referral_code": "def67890",
    "referral_points": 0,
    "referral_count": 0,
    "referred_by_username": "existinguser"
  },
  "message": "User registered successfully. Please check your email for verification."
}
```

**Response (Error - Invalid Referral Code):**
```json
{
  "referral_code": ["Invalid referral code"]
}
```

---

## 🔧 **User Profile Endpoint (Includes Referral Data)**

### **Get User Profile with Referral Info**
**`GET /api/auth/profile/`**

Returns user profile including referral information.

**Headers:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Response:**
```json
{
  "id": 1,
  "username": "existinguser",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_premium": false,
  "has_completed_onboarding": true,
  "profile": {
    "created_at": "2025-07-01T10:00:00Z",
    "updated_at": "2025-07-05T12:00:00Z"
  },
  "age": 25,
  "referral_code": "abc12345",
  "referral_points": 50,
  "referral_count": 3,
  "referred_by_username": null,
  "xp": 150,
  "streak": {
    "current": 5,
    "max": 10,
    "energy": 3
  },
  "league": {
    "id": 2,
    "name": "Intermediate",
    "min_xp": 100
  },
  "badges": [
    {
      "reward_name": "First Referral",
      "awarded_at": "2025-07-02T15:30:00Z"
    }
  ],
  "notification_preferences": {
    "email_notifications": true,
    "push_notifications": false
  }
}
```

---

## 🎯 **Usage Examples**

### **1. Get User's Referral Data**
```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  https://your-domain.com/api/auth/referrals/
```

### **2. Get Referral Statistics**
```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  https://your-domain.com/api/auth/referral-stats/
```

### **3. Register User with Referral Code**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "securepassword123",
    "age": 25,
    "referral_code": "abc12345"
  }' \
  https://your-domain.com/api/auth/signup/
```

### **4. Get User Profile (Includes Referral Data)**
```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  https://your-domain.com/api/auth/profile/
```

---

## 🔐 **Authentication**

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

To get a token, use the login endpoint:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }' \
  https://your-domain.com/api/auth/signin/
```

---

## 📊 **Referral System Features**

### **Automatic Features:**
- ✅ **Unique Referral Codes**: Every user gets a unique 8-character code
- ✅ **Referral Tracking**: Users can be linked to their referrers
- ✅ **Points System**: Referrers earn 10 points per successful referral
- ✅ **Validation**: Invalid referral codes are rejected during signup

### **Referral Code Format:**
- 8 characters long
- Alphanumeric (lowercase letters and numbers)
- Unique across all users
- Automatically generated for new users

### **Points System:**
- 10 points awarded per successful referral
- Points are automatically added when someone uses your referral code
- Points can be used for gamification features

---

## 🚨 **Error Responses**

### **Invalid Referral Code**
```json
{
  "referral_code": ["Invalid referral code"]
}
```

### **Unauthorized Access**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### **User Not Found**
```json
{
  "detail": "Not found."
}
```

---

## 🔄 **Referral Flow**

1. **User A** registers and gets a referral code (e.g., "abc12345")
2. **User A** shares their referral code with friends
3. **User B** registers using User A's referral code
4. **User A** automatically gets 10 referral points
5. **User B** is linked to User A in the system
6. Both users can view their referral relationship

---

## 📈 **Monitoring and Analytics**

You can track referral performance by:
- Monitoring referral counts per user
- Tracking points earned from referrals
- Analyzing referral conversion rates
- Identifying top referrers

The system provides all necessary data through the API endpoints for building referral analytics dashboards. 