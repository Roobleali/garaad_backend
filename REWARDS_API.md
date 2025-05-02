# Rewards API Documentation

## Overview
The Rewards API allows you to retrieve and manage user rewards earned through course completion, lesson completion, and other achievements in the learning platform.

## Base URL
```
https://api.garaad.org/api/lms
```

## Authentication
All endpoints require Bearer token authentication. Include the following header with your requests:
```
Authorization: Bearer <your_access_token>
```

## Endpoints

### List User Rewards
```
GET /rewards/
```

Retrieves all rewards for the authenticated user.

#### Query Parameters
- `lesson_id` (optional): Filter rewards by specific lesson ID
- `course_id` (optional): Filter rewards by specific course ID
- `search` (optional): Search rewards by name (e.g., "completion", "badge")

#### Response Format
```json
[
  {
    "id": integer,
    "user": integer,
    "reward_type": string,      // "points", "badge", or "streak"
    "reward_name": string,      // Description of the reward
    "value": integer,           // Points value or badge count
    "awarded_at": string,       // ISO 8601 datetime
    "lesson": {                 // null if not associated with a lesson
      "id": integer,
      "title": string
    },
    "course": {                 // null if not associated with a course
      "id": integer,
      "title": string
    }
  }
]
```

#### Example Responses

1. All Rewards
```json
GET /rewards/
[
  {
    "id": 18,
    "user": 10,
    "reward_type": "badge",
    "reward_name": "Course Completed: Lacagta loo yaqaan 'Cryptocurrency'",
    "value": 1,
    "awarded_at": "2025-04-30T13:51:59.763227Z",
    "lesson": null,
    "course": null
  }
]
```

2. Filtered by Lesson
```json
GET /rewards/?lesson_id=1
[
  {
    "id": 17,
    "user": 10,
    "reward_type": "points",
    "reward_name": "Lesson Completion",
    "value": 10,
    "awarded_at": "2025-04-30T13:51:57.826828Z",
    "lesson": {
      "id": 1,
      "title": "Introduction to Cryptocurrency"
    },
    "course": null
  }
]
```

## Reward Types

### Points
- Awarded for completing lessons
- Default value: 10 points per lesson completion
- Can be awarded for perfect scores on practice sets

### Badges
- Awarded for completing courses
- Special achievements (course completion, streak milestones)
- Value is typically 1 for achievement unlocked

### Streaks
- Awarded for consistent daily learning
- Value represents the number of consecutive days

## Management Commands

### Reset User Rewards and Progress
To reset all rewards and progress for a specific user, use the following management command:

```bash
python manage.py reset_rewards <user_id>
```

This command will:
1. Delete all rewards for the specified user
2. Remove all lesson progress records
3. Reset progress in course enrollments to 0

## Error Responses

### Authentication Error
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Invalid Token
```json
{
  "detail": "Given token not valid for any token type"
}
```

### Resource Not Found
```json
{
  "detail": "Not found."
}
```

## Best Practices
1. Always include authentication token in requests
2. Use filtering parameters to reduce payload size
3. Monitor the `awarded_at` field for reward tracking
4. Use search functionality for specific reward types 