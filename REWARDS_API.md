# Rewards API Documentation

## Overview
The Rewards API provides endpoints for managing user rewards, points, and badges in the learning management system. All endpoints require authentication using JWT tokens.

## Base URL
```
/api/lms/rewards/
```

## Endpoints

### List User Rewards
```http
GET /api/lms/rewards/
```

**Purpose**: Retrieves all rewards earned by the authenticated user.

**Authentication**: Required (Bearer Token)

**Query Parameters**:
- `lesson_id`: Filter rewards by specific lesson
- `course_id`: Filter rewards by specific course
- `search`: Search in reward names, lesson titles, and course titles
- `ordering`: Order by `awarded_at` or `value` (e.g., `ordering=-awarded_at` for newest first)

**Response**:
```json
{
  "count": number,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": "string",
      "user": "string",
      "reward_type": "string",  // "points", "badge", or "streak"
      "reward_name": "string",
      "value": number,
      "awarded_at": "datetime",
      "lesson": "string",  // lesson ID
      "lesson_title": "string",
      "course": "string",  // course ID
      "course_title": "string"
    }
  ]
}
```

## Reward Types

The system supports three types of rewards:

1. **Points**
   - Awarded for completing lessons (10 points)
   - Awarded for perfect scores on practice sets (15 points)

2. **Badges**
   - Awarded for completing courses
   - Custom achievement badges

3. **Streaks**
   - Tracks user's learning streak

## Reward Triggers

Rewards are automatically awarded in the following scenarios:

1. **Lesson Completion**
   - 10 points awarded when a lesson is marked as completed
   - Includes reference to the specific lesson and its course

2. **Course Completion**
   - Badge awarded when a course is 100% completed
   - Badge name format: "Course Completed: {course_title}"
   - Includes reference to the specific course

3. **Perfect Practice Score**
   - 15 points awarded for achieving 100% on practice sets
   - Includes reference to the specific lesson and its course

## Integration with Leaderboard

All points earned through rewards are automatically reflected in the leaderboard system, which tracks:
- All-time points
- Weekly points
- Monthly points

## Common Response Status Codes

- 200: Success
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error

## Notes

1. All endpoints require authentication using JWT tokens
2. Rewards are read-only - they are automatically awarded by the system
3. Points are automatically aggregated for leaderboard calculations
4. All dates are returned in ISO 8601 format
5. Pagination is supported on list endpoints
6. You can filter rewards by lesson or course using query parameters
7. Search functionality is available for reward names, lesson titles, and course titles 