# Garaad LMS API Documentation

## Base URL
```
https://api.garaad.org/api/lms/
```

## Authentication
All endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Categories

#### List Categories
```http
GET /categories/
```
**Purpose**: Similar to Brilliant.org's topic browsing, this endpoint allows users to explore different subject areas and find courses that interest them. It provides a hierarchical view of learning paths, helping users discover content based on their interests.

Response:
```json
{
    "count": 1,
    "next": null,
    "previous": null,
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

### Courses

#### List Courses
```http
GET /courses/
```
**Purpose**: Like Brilliant.org's course catalog, this endpoint provides a comprehensive view of available courses. It includes course details, progress tracking, and module structure, enabling users to:
- Browse available courses
- Track their progress
- See course structure before enrolling
- Discover new content

Response:
```json
{
    "count": 1,
    "next": null,
    "previous": null,
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

### Modules

#### Get Module
```http
GET /modules/{id}/
```
**Purpose**: Similar to Brilliant.org's module structure, this endpoint provides:
- Module overview
- Lesson organization
- Learning path structure
- Progress tracking within the module

Response:
```json
{
    "id": "string",
    "title": "string",
    "description": "string",
    "course": "string",
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
```

### Lessons

#### Get Lesson Content
```http
GET /lessons/{id}/
```
**Purpose**: Similar to Brilliant.org's lesson pages, this endpoint provides the core learning content. It delivers:
- Structured lesson content
- Interactive elements
- Progress tracking
- Estimated completion time
- Content blocks for different types of learning materials

Response:
```json
{
    "id": "string",
    "title": "string",
    "slug": "string",
    "module": "string",
    "lesson_number": number,
    "estimated_time": number,
    "is_published": boolean,
    "content_blocks": [
        {
            "id": "string",
            "block_type": "string",
            "content": {},
            "order": number
        }
    ]
}
```

### Content Blocks

#### Get Content Block
```http
GET /content-blocks/{id}/
```
**Purpose**: Similar to Brilliant.org's interactive content elements, this endpoint provides:
- Different types of content (text, video, interactive)
- Structured learning materials
- Ordered content presentation
- Rich media support

Response:
```json
{
    "id": "string",
    "block_type": "string",
    "content": {},
    "order": number,
    "lesson": "string"
}
```

### Problems

#### Get Problem
```http
GET /problems/{id}/
```
**Purpose**: Like Brilliant.org's practice problems, this endpoint provides:
- Interactive problem content
- Multiple question types
- Hints and solutions
- Difficulty levels
- Immediate feedback

Response:
```json
{
    "id": "string",
    "question_text": "string",
    "image": "string",
    "question_type": "string",
    "options": {},
    "correct_answer": {},
    "explanation": "string",
    "difficulty": "string",
    "hints": [
        {
            "id": "string",
            "content": "string",
            "order": number
        }
    ],
    "solution_steps": [
        {
            "id": "string",
            "explanation": "string",
            "order": number
        }
    ]
}
```

### Practice Sets

#### Get Practice Set
```http
GET /practice-sets/{id}/
```
**Purpose**: Like Brilliant.org's practice problem sets, this endpoint provides:
- Interactive problem sets
- Immediate feedback
- Difficulty levels
- Randomized questions
- Progress tracking
- Problem explanations

Response:
```json
{
    "id": "string",
    "title": "string",
    "practice_type": "string",
    "difficulty_level": "string",
    "is_randomized": boolean,
    "practice_set_problems": [
        {
            "id": "string",
            "problem": "string",
            "order": number,
            "problem_details": {
                "id": "string",
                "question_text": "string",
                "question_type": "string",
                "options": {},
                "correct_answer": {},
                "explanation": "string",
                "difficulty": "string"
            }
        }
    ]
}
```

### Practice Set Problems

#### Get Practice Set Problem
```http
GET /practice-set-problems/{id}/
```
**Purpose**: Similar to Brilliant.org's problem organization, this endpoint:
- Links problems to practice sets
- Maintains problem order
- Provides problem details
- Enables problem navigation

Response:
```json
{
    "id": "string",
    "problem": "string",
    "order": number,
    "practice_set": "string",
    "problem_details": {
        "id": "string",
        "question_text": "string",
        "question_type": "string",
        "options": {},
        "correct_answer": {},
        "explanation": "string",
        "difficulty": "string"
    }
}
```

### User Progress

#### Get User Progress
```http
GET /progress/
```
**Purpose**: Similar to Brilliant.org's progress tracking, this endpoint:
- Tracks completion status
- Records scores
- Shows learning history
- Provides motivation through progress visualization
- Enables personalized learning paths

Response:
```json
{
    "count": 1,
    "next": null,
    "previous": null,
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

#### Update Progress
```http
PATCH /progress/{id}/
```
**Purpose**: Enables real-time progress tracking and achievement recording, similar to Brilliant.org's progress system.

Request Body:
```json
{
    "status": "string",
    "score": number
}
```

### Course Enrollments

#### List User Enrollments
```http
GET /enrollments/
```
**Purpose**: Like Brilliant.org's "My Courses" section, this endpoint:
- Shows enrolled courses
- Displays progress
- Enables quick access to ongoing learning
- Provides course completion tracking

Response:
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "string",
            "user": "string",
            "course": "string",
            "course_title": "string",
            "progress_percent": number,
            "enrolled_at": "datetime"
        }
    ]
}
```

#### Enroll in Course
```http
POST /enrollments/
```
**Purpose**: Enables users to start new courses, similar to Brilliant.org's course enrollment system.

Request Body:
```json
{
    "course": "string"
}
```

### User Rewards

#### Get User Rewards
```http
GET /rewards/
```
**Purpose**: Similar to Brilliant.org's achievement system, this endpoint:
- Tracks earned badges
- Shows points
- Displays achievements
- Provides motivation through gamification
- Rewards learning milestones

Response:
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "string",
            "user": "string",
            "reward_type": "string",
            "reward_name": "string",
            "value": number,
            "awarded_at": "datetime"
        }
    ]
}
```

### Leaderboard

#### Get Leaderboard
```http
GET /leaderboard/
```
**Purpose**: Similar to Brilliant.org's community features, this endpoint:
- Fosters healthy competition
- Shows community engagement
- Displays user achievements
- Encourages consistent learning
- Builds learning community

Response:
```json
{
    "count": 1,
    "next": null,
    "previous": null,
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
    "detail": "Error message here",
    "code": "error_code"
}
```

For validation errors:
```json
{
    "field_name": ["Error message"],
    "field_name2": ["Error message"]
}
```


