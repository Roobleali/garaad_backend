# Admin Dashboard API Endpoints

## Overview
This document provides complete documentation for the LMS Admin Dashboard API endpoints. These endpoints provide comprehensive analytics and monitoring capabilities for administrators to manage the LMS platform.

## Authentication
All admin endpoints require JWT authentication with admin/staff privileges.

### Getting Admin Access Token
```http
POST /api/auth/signin/
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_superuser": true
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### Using the Token
Include the access token in all admin API requests:
```http
Authorization: Bearer {access_token}
```

---

## API Endpoints

### 1. Complete Dashboard Overview
**Get comprehensive dashboard data with all metrics**

```http
GET /api/admin/dashboard/
Authorization: Bearer {access_token}
```

**Response Structure:**
```json
{
  "success": true,
  "data": {
    "overview": { /* High-level platform stats */ },
    "users": { /* User analytics and management */ },
    "courses": { /* Course and content statistics */ },
    "learning": { /* Learning progress and engagement */ },
    "engagement": { /* User retention and engagement */ },
    "revenue": { /* Revenue and subscription data */ },
    "system": { /* System health and database stats */ },
    "recent_activity": { /* Recent user activities */ },
    "top_performers": { /* Leaderboards and top users */ },
    "alerts": [ /* System alerts and notifications */ ]
  },
  "generated_at": "2025-06-30T13:24:28.385656+00:00"
}
```

**Sample Response:**
```json
{
  "success": true,
  "data": {
    "overview": {
      "total_users": 156,
      "total_courses": 12,
      "total_lessons": 48,
      "total_problems": 324,
      "active_users": 89,
      "new_users_week": 23,
      "completion_rate": 78.5,
      "total_enrollments": 342
    },
    "users": {
      "total_users": 156,
      "premium_users": 45,
      "free_users": 111,
      "subscription_breakdown": {
        "monthly": 20,
        "yearly": 15,
        "lifetime": 10
      },
      "active_users": {
        "today": 34,
        "week": 89,
        "month": 134
      },
      "engagement_levels": {
        "high": 25,
        "medium": 45,
        "low": 35
      }
    }
  }
}
```

---

### 2. User Analytics
**Detailed user management and analytics**

```http
GET /api/admin/users/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_users": 156,
    "premium_users": 45,
    "free_users": 111,
    "subscription_breakdown": {
      "monthly": 20,
      "yearly": 15,
      "lifetime": 10
    },
    "active_users": {
      "today": 34,
      "week": 89,
      "month": 134
    },
    "engagement_levels": {
      "high": 25,
      "medium": 45,
      "low": 35
    },
    "new_registrations": {
      "today": 5,
      "week": 23,
      "month": 67
    },
    "recent_active_users": [
      {
        "id": 123,
        "username": "student_user",
        "email": "student@example.com",
        "last_login": "2025-06-30T12:30:00Z",
        "is_premium": true
      }
    ]
  }
}
```

---

### 3. Course Analytics
**Course and content performance statistics**

```http
GET /api/admin/courses/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "courses": {
      "total_courses": 12,
      "published_courses": 10,
      "total_lessons": 48,
      "total_problems": 324,
      "enrollments": {
        "total": 342,
        "unique_users": 156,
        "completed": 89,
        "in_progress": 234,
        "not_started": 19
      },
      "avg_progress": 67.8,
      "popular_courses": [
        {
          "id": 1,
          "title": "Introduction to Python",
          "enrollment_count": 89
        },
        {
          "id": 2,
          "title": "Web Development Basics",
          "enrollment_count": 76
        }
      ],
      "content_engagement": {
        "lessons_completed": 1247,
        "problems_solved": 5632
      }
    },
    "learning": {
      "today_activity": {
        "total_users": 34,
        "total_problems": 127,
        "complete_sessions": 45,
        "partial_sessions": 23
      },
      "xp_stats": {
        "total_xp": 45670,
        "avg_xp": 292.7,
        "max_xp": 1250
      },
      "streak_stats": {
        "avg_streak": 5.2,
        "max_streak": 45,
        "users_with_streaks": 78
      }
    }
  }
}
```

---

### 4. Revenue Report
**Revenue and subscription analytics**

```http
GET /api/admin/revenue/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "subscription_breakdown": {
      "monthly": 20,
      "yearly": 15,
      "lifetime": 10,
      "total_premium": 45
    },
    "new_premium_month": 8,
    "active_subscriptions": 42,
    "estimated_revenue": {
      "mrr": 2450.0,
      "arr": 29400.0
    },
    "conversion_rate": 28.8,
    "churn_indicators": {
      "expired_subscriptions": 3
    }
  }
}
```

---

### 5. Real-time User Activity
**Live user activity monitoring**

```http
GET /api/admin/activity/
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `period` (optional): `today`, `week`, `month` (default: `today`)
- `limit` (optional): Number of results to return (default: `50`)

```http
GET /api/admin/activity/?period=week&limit=100
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "active_users": [
      {
        "user_id": 123,
        "username": "student_user",
        "email": "student@example.com",
        "is_premium": true,
        "last_activity": "2025-06-30",
        "total_problems": 15,
        "activity_days": 5,
        "streak": 7
      }
    ],
    "recent_activities": [
      {
        "user_id": 123,
        "username": "student_user",
        "email": "student@example.com",
        "is_premium": true,
        "date": "2025-06-30",
        "status": "complete",
        "problems_solved": 8,
        "lesson_ids": [1, 2, 3]
      }
    ],
    "time_period": "week",
    "total_active_users": 89
  }
}
```

---

## Error Handling

### Authentication Errors
```json
{
  "error": "Access denied. Admin privileges required."
}
```
**Status Code:** `403 Forbidden`

### Server Errors
```json
{
  "error": "Failed to generate dashboard data",
  "detail": "Specific error message"
}
```
**Status Code:** `500 Internal Server Error`

### Invalid Token
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```
**Status Code:** `401 Unauthorized`

---

## Data Models

### User Engagement Levels
- **High**: Users with streak ≥ 7 days
- **Medium**: Users with streak 3-6 days  
- **Low**: Users with streak 1-2 days or no streak

### Activity Status
- **complete**: Session fully completed
- **partial**: Session partially completed
- **none**: No activity

### Subscription Types
- **monthly**: $9.99/month subscription
- **yearly**: $99.99/year subscription  
- **lifetime**: $299.99 one-time payment
- **free**: No subscription

---

## Frontend Integration Examples

### React Hook Example
```javascript
import { useState, useEffect } from 'react';

const useAdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const token = localStorage.getItem('adminToken');
        const response = await fetch('/api/admin/dashboard/', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch dashboard data');
        }

        const data = await response.json();
        setDashboardData(data.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return { dashboardData, loading, error };
};
```

### Vue.js Composable Example
```javascript
import { ref, onMounted } from 'vue';

export function useAdminDashboard() {
  const dashboardData = ref(null);
  const loading = ref(true);
  const error = ref(null);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('adminToken');
      const response = await fetch('/api/admin/dashboard/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      const data = await response.json();
      dashboardData.value = data.data;
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  onMounted(fetchDashboardData);

  return {
    dashboardData,
    loading,
    error,
    refetch: fetchDashboardData
  };
}
```

### Vanilla JavaScript Example
```javascript
class AdminDashboard {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl;
    this.token = token;
  }

  async request(endpoint) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  async getDashboardOverview() {
    return this.request('/api/admin/dashboard/');
  }

  async getUserAnalytics() {
    return this.request('/api/admin/users/');
  }

  async getCourseAnalytics() {
    return this.request('/api/admin/courses/');
  }

  async getRevenueReport() {
    return this.request('/api/admin/revenue/');
  }

  async getUserActivity(period = 'today', limit = 50) {
    return this.request(`/api/admin/activity/?period=${period}&limit=${limit}`);
  }
}

// Usage
const dashboard = new AdminDashboard('https://your-api.com', 'your-jwt-token');
const data = await dashboard.getDashboardOverview();
```

---

## Rate Limiting
- Admin endpoints are rate-limited to **100 requests per minute** per user
- If rate limit is exceeded, API returns `429 Too Many Requests`

## Security Notes
- All endpoints require valid JWT tokens with admin privileges
- Tokens expire after 15 minutes (configurable)
- Use HTTPS in production
- Store tokens securely (not in localStorage for production)

---

## Support
For technical support or questions about the Admin Dashboard API, contact the development team or refer to the main API documentation. 