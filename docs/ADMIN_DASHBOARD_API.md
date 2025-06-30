# Admin Dashboard API Documentation

## Overview
The Admin Dashboard API provides comprehensive analytics and metrics for the Garaad LMS platform. These endpoints are restricted to staff and superuser accounts only.

## Base URL
```
http://your-domain.com/api/
```

## Authentication
All admin endpoints require:
1. Valid JWT authentication token
2. User must have `is_staff=True` or `is_superuser=True`

```http
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. Complete Dashboard Data
Get all dashboard metrics in a single request.

```http
GET /api/admin/dashboard/
```

**Response Structure:**
```json
{
  "success": true,
  "data": {
    "overview": {
      "total_users": 1250,
      "total_courses": 15,
      "total_lessons": 120,
      "total_problems": 850,
      "active_users": 324,
      "new_users_week": 45,
      "completion_rate": 67.5,
      "total_enrollments": 2150
    },
    "users": {
      "total_users": 1250,
      "premium_users": 187,
      "free_users": 1063,
      "subscription_breakdown": {
        "monthly": 120,
        "yearly": 45,
        "lifetime": 22
      },
      "active_users": {
        "today": 89,
        "week": 324,
        "month": 756
      },
      "engagement_levels": {
        "high": 156,
        "medium": 234,
        "low": 198
      },
      "new_registrations": {
        "today": 5,
        "week": 45,
        "month": 234
      },
      "recent_active_users": [...]
    },
    "courses": {
      "total_courses": 15,
      "published_courses": 12,
      "total_lessons": 120,
      "total_problems": 850,
      "enrollments": {
        "total": 2150,
        "unique_users": 1050,
        "completed": 467,
        "in_progress": 1234,
        "not_started": 449
      },
      "avg_progress": 45.8,
      "popular_courses": [...],
      "content_engagement": {
        "lessons_completed": 5678,
        "problems_solved": 23450
      }
    },
    "learning": {
      "today_activity": {
        "total_users": 89,
        "total_problems": 456,
        "complete_sessions": 67,
        "partial_sessions": 22
      },
      "week_stats": {
        "total_problems": 3456,
        "active_users": 324,
        "complete_days": 567
      },
      "problem_types": [
        {"question_type": "multiple_choice", "count": 520},
        {"question_type": "diagram", "count": 330}
      ],
      "xp_stats": {
        "total_xp": 456789,
        "avg_xp": 365.4,
        "max_xp": 5670
      },
      "streak_stats": {
        "avg_streak": 4.5,
        "max_streak": 45,
        "users_with_streaks": 567
      },
      "top_streaks": [...]
    },
    "engagement": {
      "retention": {
        "daily": 45.6,
        "weekly": 32.8
      },
      "notification_engagement": 67.5,
      "league_participation": 78.9,
      "achievement_rate": 23.4,
      "engagement_breakdown": {
        "high_engagers": 156,
        "medium_engagers": 234,
        "low_engagers": 198,
        "inactive": 662
      }
    },
    "revenue": {
      "subscription_breakdown": {
        "monthly": 120,
        "yearly": 45,
        "lifetime": 22,
        "total_premium": 187
      },
      "new_premium_month": 23,
      "active_subscriptions": 165,
      "estimated_revenue": {
        "mrr": 1575.0,
        "arr": 18900.0
      },
      "conversion_rate": 14.96,
      "churn_indicators": {
        "expired_subscriptions": 12
      }
    },
    "system": {
      "database_stats": {
        "users": 1250,
        "courses": 15,
        "lessons": 120,
        "problems": 850,
        "enrollments": 2150,
        "user_progress": 5678,
        "daily_activities": 12345,
        "notifications": 6789,
        "streaks": 890,
        "achievements": 25,
        "user_achievements": 2345
      },
      "recent_activity": {
        "new_users_week": 45,
        "lessons_completed_week": 234,
        "notifications_sent_week": 567
      },
      "last_updated": "2024-01-15T10:30:00Z"
    },
    "recent_activity": {
      "recent_users": [...],
      "recent_completions": [...],
      "recent_achievements": [...],
      "recent_streaks": [...]
    },
    "top_performers": {
      "top_xp_users": [...],
      "top_streak_users": [...],
      "popular_courses": [...],
      "popular_lessons": [...]
    },
    "alerts": [
      {
        "type": "warning",
        "title": "Expired Subscriptions",
        "message": "12 users have expired premium subscriptions",
        "count": 12
      }
    ]
  },
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### 2. User Analytics
Get detailed user statistics and analytics.

```http
GET /api/admin/users/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_users": 1250,
    "premium_users": 187,
    "free_users": 1063,
    "subscription_breakdown": {
      "monthly": 120,
      "yearly": 45,
      "lifetime": 22
    },
    "active_users": {
      "today": 89,
      "week": 324,
      "month": 756
    },
    "engagement_levels": {
      "high": 156,
      "medium": 234,
      "low": 198
    },
    "new_registrations": {
      "today": 5,
      "week": 45,
      "month": 234
    },
    "recent_active_users": [
      {
        "id": 123,
        "username": "user123",
        "email": "user@example.com",
        "last_login": "2024-01-15T09:45:00Z",
        "is_premium": true
      }
    ]
  }
}
```

### 3. Course Analytics
Get course and learning analytics.

```http
GET /api/admin/courses/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "courses": {
      "total_courses": 15,
      "published_courses": 12,
      "total_lessons": 120,
      "total_problems": 850,
      "enrollments": {
        "total": 2150,
        "unique_users": 1050,
        "completed": 467,
        "in_progress": 1234,
        "not_started": 449
      },
      "avg_progress": 45.8,
      "popular_courses": [
        {
          "id": 1,
          "title": "Advanced Mathematics",
          "enrollment_count": 234
        }
      ],
      "content_engagement": {
        "lessons_completed": 5678,
        "problems_solved": 23450
      }
    },
    "learning": {
      "today_activity": {
        "total_users": 89,
        "total_problems": 456,
        "complete_sessions": 67,
        "partial_sessions": 22
      },
      "week_stats": {
        "total_problems": 3456,
        "active_users": 324,
        "complete_days": 567
      },
      "problem_types": [
        {"question_type": "multiple_choice", "count": 520},
        {"question_type": "diagram", "count": 330}
      ],
      "xp_stats": {
        "total_xp": 456789,
        "avg_xp": 365.4,
        "max_xp": 5670
      },
      "streak_stats": {
        "avg_streak": 4.5,
        "max_streak": 45,
        "users_with_streaks": 567
      },
      "top_streaks": [
        {
          "user__username": "topuser",
          "current_streak": 45,
          "max_streak": 67,
          "xp": 5670
        }
      ]
    }
  }
}
```

### 4. Revenue Report
Get subscription and revenue analytics.

```http
GET /api/admin/revenue/
```

**Response:**
```json
{
  "success": true,
  "data": {
    "subscription_breakdown": {
      "monthly": 120,
      "yearly": 45,
      "lifetime": 22,
      "total_premium": 187
    },
    "new_premium_month": 23,
    "active_subscriptions": 165,
    "estimated_revenue": {
      "mrr": 1575.0,
      "arr": 18900.0
    },
    "conversion_rate": 14.96,
    "churn_indicators": {
      "expired_subscriptions": 12
    }
  }
}
```

### 5. User Activity Monitoring
Get real-time user activity data.

```http
GET /api/admin/activity/?period=week&limit=50
```

**Query Parameters:**
- `period`: `today`, `week`, `month` (default: `today`)
- `limit`: Number of users to return (default: `50`)

**Response:**
```json
{
  "success": true,
  "data": {
    "active_users": [
      {
        "user_id": 123,
        "username": "activeuser",
        "email": "user@example.com",
        "is_premium": true,
        "last_activity": "2024-01-15",
        "total_problems": 45,
        "activity_days": 5,
        "streak": 7
      }
    ],
    "recent_activities": [
      {
        "user_id": 123,
        "username": "activeuser",
        "email": "user@example.com",
        "is_premium": true,
        "date": "2024-01-15",
        "status": "complete",
        "problems_solved": 5,
        "lesson_ids": [1, 2, 3]
      }
    ],
    "time_period": "week",
    "total_active_users": 324
  }
}
```

## Key Features

### 📊 Complete Analytics Suite
- **User Management**: Total users, premium/free breakdown, active users
- **Course Analytics**: Enrollments, completion rates, popular courses  
- **Learning Metrics**: Daily activity, XP distribution, streaks
- **Revenue Tracking**: MRR, ARR, conversion rates, churn analysis
- **System Monitoring**: Database stats, recent activity, alerts

### 🔍 Real-time Monitoring
- Live user activity tracking
- Recent registrations and completions
- Performance alerts and warnings
- Top performers identification

### 📈 Advanced Metrics
- User engagement levels (high/medium/low)
- Retention rates (daily/weekly)
- Achievement completion rates
- League participation analytics

## Error Handling
All endpoints return appropriate HTTP status codes and error messages for debugging and user feedback.

## Security
- Staff/superuser authentication required
- Rate limiting applied
- Sensitive data properly handled

This admin dashboard provides everything you need to monitor and manage your LMS platform effectively! 