# Gamification API Documentation

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

### 1. User Rewards

#### List User Rewards
```http
GET /rewards/
```

Retrieves all rewards for the authenticated user.

**Query Parameters:**
- `lesson_id` (optional): Filter rewards by specific lesson
- `course_id` (optional): Filter rewards by specific course
- `search` (optional): Search rewards by name
- `ordering` (optional): Order by 'awarded_at' or 'value'

**Response:**
```json
[
  {
    "id": 1,
    "user": 1,
    "reward_type": "points",  // "points", "badge", "streak", "achievement", "challenge"
    "reward_name": "Lesson Completion",
    "value": 10,
    "awarded_at": "2025-04-30T13:51:57Z",
    "lesson": {
      "id": 1,
      "title": "Introduction"
    },
    "course": {
      "id": 1,
      "title": "Mathematics"
    }
  }
]
```

### 2. Leaderboard

#### Get Leaderboard
```http
GET /leaderboard/
```

Retrieves the current leaderboard standings.

**Query Parameters:**
- `time_period`: Filter by time period ("all_time", "weekly", "monthly")
- `limit`: Number of entries to return (default: 10)

**Response:**
```json
[
  {
    "id": 1,
    "username": "user1",
    "points": 1500,
    "time_period": "all_time",
    "last_updated": "2025-04-30T13:51:57Z",
    "user_info": {
      "badges": [
        {
          "id": 1,
          "reward_name": "Course Master",
          "value": 1,
          "awarded_at": "2025-04-30T13:51:57Z"
        }
      ],
      "streak": {
        "current": 5,
        "max": 10
      },
      "total_points": 1500,
      "completed_lessons": 25,
      "enrolled_courses": 3
    }
  }
]
```

#### Get User's Rank
```http
GET /leaderboard/my_rank/
```

Retrieves the authenticated user's rank and surrounding entries.

**Query Parameters:**
- `time_period`: Time period to check rank for ("all_time", "weekly", "monthly")

**Response:**
```json
{
  "rank": 5,
  "points": 1200,
  "entries_above": [
    {
      "username": "user1",
      "points": 1500
    }
  ],
  "entries_below": [
    {
      "username": "user3",
      "points": 1000
    }
  ],
  "user_info": {
    // Same as leaderboard user_info
  }
}
```

### 3. Daily Challenges

#### List Daily Challenges
```http
GET /challenges/
```

Retrieves today's and past challenges.

**Response:**
```json
[
  {
    "id": 1,
    "title": "Daily Math Challenge",
    "description": "Complete 5 math problems",
    "challenge_date": "2025-04-30",
    "points_reward": 50
  }
]
```

#### Submit Challenge Attempt
```http
POST /challenges/{challenge_id}/submit_attempt/
```

Submit an attempt for a daily challenge.

**Response:**
```json
{
  "id": 1,
  "completed": true,
  "completed_at": "2025-04-30T13:51:57Z",
  "score": 100,
  "attempts": 1
}
```

### 4. User Level

#### Get User Level
```http
GET /levels/
```

Retrieves the authenticated user's level information.

**Response:**
```json
{
  "id": 1,
  "user": 1,
  "level": 5,
  "experience_points": 750,
  "experience_to_next_level": 1000,
  "clan": "Hawiye",
  "region": "Mogadishu",
  "language_preference": "so"
}
```

#### Get Level Leaderboard
```http
GET /levels/leaderboard/
```

Retrieves top users by level.

**Response:**
```json
[
  {
    "id": 1,
    "user": {
      "username": "user1"
    },
    "level": 10,
    "experience_points": 2500
  }
]
```

### 5. Achievements

#### List Available Achievements
```http
GET /achievements/
```

Retrieves all achievements available to the user based on their current level.

**Response:**
```json
[
  {
    "id": 1,
    "name": "First Lesson",
    "description": "Complete your first lesson",
    "icon": "lesson-1",
    "points_reward": 100,
    "level_required": 1,
    "achievement_type": "course_completion"
  }
]
```

#### Get User Achievements
```http
GET /achievements/user_achievements/
```

Retrieves achievements earned by the authenticated user.

**Response:**
```json
[
  {
    "id": 1,
    "achievement": {
      "id": 1,
      "name": "First Lesson",
      "description": "Complete your first lesson",
      "icon": "lesson-1",
      "points_reward": 100,
      "level_required": 1,
      "achievement_type": "course_completion"
    },
    "earned_at": "2025-04-30T13:51:57Z"
  }
]
```

### 6. Cultural Events

#### List Cultural Events
```http
GET /cultural-events/
```

Retrieves active cultural events.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Eid Celebration",
    "description": "Join our virtual Eid celebration",
    "event_date": "2025-05-01",
    "event_type": "celebration",
    "points_reward": 100,
    "is_active": true
  }
]
```

#### Participate in Event
```http
POST /cultural-events/{event_id}/participate/
```

Participate in a cultural event.

**Response:**
```json
{
  "id": 1,
  "completed": true,
  "completed_at": "2025-04-30T13:51:57Z",
  "points_earned": 100
}
```

### 7. Community Contributions

#### List Contributions
```http
GET /contributions/
```

Retrieves the authenticated user's contributions.

**Response:**
```json
[
  {
    "id": 1,
    "contribution_type": "cultural",
    "description": "Shared traditional Somali poetry",
    "points_awarded": 150,
    "created_at": "2025-04-30T13:51:57Z",
    "verified": true,
    "verified_by": {
      "username": "admin"
    }
  }
]
```

#### Create Contribution
```http
POST /contributions/
```

Create a new community contribution.

**Request Body:**
```json
{
  "contribution_type": "cultural",
  "description": "Shared traditional Somali poetry"
}
```

**Response:**
```json
{
  "id": 1,
  "contribution_type": "cultural",
  "description": "Shared traditional Somali poetry",
  "points_awarded": 150,
  "created_at": "2025-04-30T13:51:57Z",
  "verified": false
}
```

#### Verify Contribution (Admin Only)
```http
POST /contributions/{contribution_id}/verify/
```

Verify a community contribution (admin only).

**Response:**
```json
{
  "id": 1,
  "contribution_type": "cultural",
  "description": "Shared traditional Somali poetry",
  "points_awarded": 200,  // Including bonus points
  "created_at": "2025-04-30T13:51:57Z",
  "verified": true,
  "verified_by": {
    "username": "admin"
  }
}
```

## Points System

### Point Values
- Lesson Completion: 10 points
- Perfect Practice Score: 15 points
- Daily Challenge: 50 points
- Cultural Event Participation: 100 points
- Community Contributions:
  - Content: 50 points
  - Translation: 75 points
  - Help: 100 points
  - Feedback: 25 points
  - Cultural: 150 points
  - Verification Bonus: 50 points

## Achievement Types
- `course_completion`: Completing courses
- `streak_milestone`: Reaching streak milestones
- `challenge_completion`: Completing daily challenges
- `level_milestone`: Reaching level milestones
- `perfect_score`: Getting perfect scores
- `early_adopter`: Early platform adoption

## Time Periods
- `all_time`: All-time statistics
- `weekly`: Last 7 days
- `monthly`: Last 30 days
