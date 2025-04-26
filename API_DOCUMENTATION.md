# Garaad LMS API Documentation

## Base URL
```
https://api.garaad.org/api/
```

## Authentication
All endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### Authentication

#### Sign Up with Onboarding
```http
POST /api/auth/signup/
```
**Purpose**: Register a new user and create onboarding information in a single request.

Request Body:
```json
{
  "name": "User Full Name",
  "email": "user@example.com",
  "password": "securepassword123",
  "age": 25,
  "goal": "Horumarinta xirfadaha",
  "learning_approach": "Waxbarasho shaqsiyeed",
  "topic": "Xisaab",
  "math_level": "Bilowga",
  "minutes_per_day": 30
}
```

#### Sign In
```http
POST /api/auth/signin/
```
**Purpose**: Authenticate user and get access tokens.

Request Body:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

Response:
```json
{
  "user": {
    "id": "string",
    "email": "string",
    "name": "string",
    "age": number
  },
  "onboarding": {
    "goal": "string",
    "learning_approach": "string",
    "topic": "string",
    "math_level": "string",
    "minutes_per_day": number
  },
  "tokens": {
    "refresh": "string",
    "access": "string"
  }
}
```

#### Token Refresh
```http
POST /api/auth/refresh/
```
**Purpose**: Get a new access token using a refresh token.

Request Body:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5..."
}
```

### User Profile

#### Get User Profile
```http
GET /api/auth/profile/
```
**Purpose**: Retrieve the authenticated user's profile information.

Response:
```json
{
  "id": "string",
  "email": "string",
  "name": "string",
  "age": number
}
```

#### Update User Profile
```http
PUT /api/auth/profile/
```
**Purpose**: Update user profile information including qabiil and laan.

Request Body:
```json
{
  "qabiil": "string",
  "laan": "string"
}
```

 

### Learning Management System (LMS)

#### Categories

##### List Categories
```http
GET /api/lms/categories/
```
**Purpose**: Get all available course categories.

Response:
```json
{
  "count": number,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "image": "string",
      "in_progress": boolean,
      "courses": [
        {
          "id": "string",
          "title": "string",
          "description": "string",
          "thumbnail": "string",
          "is_new": boolean,
          "progress": number,
          "is_published": boolean
        }
      ]
    }
  ]
}
```

#### Courses

##### List Courses
```http
GET /api/lms/courses/
```
**Purpose**: Get all available courses.

Response:
```json
{
  "count": number,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": "string",
      "title": "string",
      "slug": "string",
      "description": "string",
      "thumbnail": "string",
      "is_new": boolean,
      "progress": number,
      "author_id": "string",
      "is_published": boolean,
      "category": "string",
      "modules": [
        {
          "id": "string",
          "title": "string",
          "description": "string",
          "lessons": [
            {
              "id": "string",
              "title": "string",
              "slug": "string",
              "lesson_number": number,
              "estimated_time": number,
              "is_published": boolean
            }
          ]
        }
      ]
    }
  ]
}
```

#### Lessons

##### Get Lesson Content
```http
GET /api/lms/lessons/{id}/content/
```
**Purpose**: Get all content (blocks and problems) for a lesson.

Response:
```json
[
  {
    "type": "block",
    "id": "string",
    "order": number,
    "block_type": "string",
    "content": {}
  },
  {
    "type": "problem",
    "id": "string",
    "order": number,
    "question_type": "string",
    "question_text": "string",
    "content": {}
  }
]
```

##### Get Next Content
```http
GET /api/lms/lessons/{id}/next_content/?order={current_order}
```
**Purpose**: Get the next content item after the specified order.

Response:
```json
{
  "type": "block|problem",
  "id": "string",
  "order": number,
  "block_type|question_type": "string",
  "content": {},
  "question_text": "string"
}
```

#### User Progress

##### Get User Progress
```http
GET /api/lms/progress/
```
**Purpose**: Get progress for all lessons.

Response:
```json
{
  "count": number,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": "string",
      "user": "string",
      "lesson": "string",
      "lesson_title": "string",
      "module_title": "string",
      "status": "string",
      "score": number,
      "last_visited_at": "datetime",
      "completed_at": "datetime"
    }
  ]
}
```

##### Update Progress
```http
PATCH /api/lms/progress/{id}/
```
**Purpose**: Update progress for a specific lesson.

Request Body:
```json
{
  "status": "string",
  "score": number
}
```

#### Leaderboard

##### Get Leaderboard
```http
GET /api/lms/leaderboard/
```
**Purpose**: Get the current leaderboard rankings.

Query Parameters:
- `time_period`: "all_time" | "weekly" | "monthly" (default: "all_time")
- `limit`: number (default: 10)

Response:
```json
{
  "count": number,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": "string",
      "user": "string",
      "username": "string",
      "points": number,
      "time_period": "string",
      "last_updated": "datetime",
      "user_info": {
        "email": "string",
        "first_name": "string",
        "last_name": "string",
        "stats": {
          "total_points": number,
          "completed_lessons": number,
          "enrolled_courses": number,
          "current_streak": number,
          "badges_count": number
        },
        "badges": [
          {
            "id": "string",
            "reward_name": "string",
            "value": number,
            "awarded_at": "datetime"
          }
        ]
      }
    }
  ]
}
```

## Common Response Status Codes

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error

## Notes

1. All endpoints require authentication using JWT tokens
2. For POST/PATCH requests, only include the fields you want to update
3. All IDs are strings
4. Dates are returned in ISO 8601 format
5. For nested resources, you can use the ID to fetch more details
6. Pagination is supported on all list endpoints
7. Filtering and searching capabilities are available on most endpoints

## Error Handling

All error responses follow this format:
```json
{
  "error": "string",
  "detail": "string"
}
```


