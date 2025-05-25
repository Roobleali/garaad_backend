# Garaad Gamification Endpoints Documentation

## Core Endpoints and Data Flow

### 1. Problem Solving Flow

#### GET `/api/problems/{problem_id}/`
- **Purpose**: Get problem details before solving
- **Response**: Problem data including XP value
- **Connected to**: Problem solving flow

#### POST `/api/problems/{problem_id}/solve/`
- **Purpose**: Mark problem as solved and trigger XP/stats updates
- **Request Body**: 
```json
{
    "answer": "user_answer",
    "attempt_number": 1
}
```
- **Response**: 
```json
{
    "success": true,
    "xp_earned": 10,
    "streak_updated": false,
    "problems_solved_today": 1,
    "next_streak_problem": 2,
    "energy": {
        "current": 3,
        "max": 3,
        "next_update": "2024-03-20T15:00:00Z"
    }
}
```
- **Triggers**:
  1. Updates UserProblem record
  2. Updates UserProgress
  3. Checks streak conditions
  4. Updates XP totals
  5. Updates league standings

### 2. Streak Management

#### GET `/api/gamification/streak/`
- **Purpose**: Get current streak status
- **Response**: 
```json
{
    "current_streak": 5,
    "max_streak": 10,
    "problems_solved_today": 2,
    "problems_to_next_streak": 1,
    "energy": {
        "current": 3,
        "max": 3,
        "next_update": "2024-03-20T15:00:00Z"
    }
}
```
- **Connected to**: 
  - Problem solving flow
  - Energy system
  - Daily activity tracking

#### POST `/api/gamification/use_energy/`
- **Purpose**: Use energy to maintain streak
- **Response**: 
```json
{
    "success": true,
    "remaining_energy": 2,
    "message": "Waad ku mahadsantahay ilaalinta xariggaaga"
}
```
- **Connected to**: 
  - Streak system
  - Energy management

### 3. Progress Tracking

#### GET `/api/gamification/progress/`
- **Purpose**: Get comprehensive user progress
- **Response**: 
```json
{
    "xp": {
        "total": 1000,
        "daily": 50,
        "weekly": 300,
        "monthly": 1200
    },
    "problems": {
        "total_solved": 100,
        "solved_today": 3,
        "solved_this_week": 15
    }
}
```
- **Connected to**: 
  - Problem solving flow
  - Streak system
  - League system

### 4. League System

#### GET `/api/gamification/league/`
- **Purpose**: Get current league status
- **Response**: 
```json
{
    "current_league": {
        "id": 1,
        "name": "Biyo",
        "somali_name": "Biyo",
        "min_xp": 0,
        "rank": 15
    },
    "next_league": {
        "id": 2,
        "name": "Geesi",
        "somali_name": "Geesi",
        "min_xp": 1000,
        "points_needed": 500
    }
}
```
- **Connected to**: 
  - XP system
  - Weekly rankings
  - League promotions

#### GET `/api/gamification/league/{league_id}/leaderboard/`
- **Purpose**: Get league rankings
- **Query Parameters**:
  - `time_period`: weekly/monthly/all_time
  - `limit`: number of entries
- **Response**: 
```json
{
    "league": {
        "id": 1,
        "name": "Biyo"
    },
    "time_period": "weekly",
    "standings": [
        {
            "rank": 1,
            "user": {
                "id": 1,
                "name": "username"
            },
            "points": 1000,
            "streak": 5,
            "problems_solved": 20
        }
    ],
    "my_standing": {
        "rank": 15,
        "points": 500,
        "streak": 3,
        "problems_solved": 10
    }
}
```
- **Connected to**: 
  - League system
  - Weekly points
  - User standings

### 5. Notification System

#### GET `/api/notifications/`
- **Purpose**: Get user's notifications
- **Response**: 
```json
{
    "count": 5,
    "results": [
        {
            "id": 1,
            "type": "streak",
            "title": "First Streak!",
            "message": "Waad ku mahadsantahay bilowga xariggaaga!",
            "data": {
                "streak_days": 1,
                "xp_earned": 20
            },
            "is_read": false,
            "created_at": "2024-03-20T10:00:00Z"
        }
    ]
}
```

#### GET `/api/notifications/unread_count/`
- **Purpose**: Get count of unread notifications
- **Response**: 
```json
{
    "unread_count": 3
}
```

#### POST `/api/notifications/{id}/mark_read/`
- **Purpose**: Mark a specific notification as read
- **Response**: 
```json
{
    "message": "Notification marked as read"
}
```

#### POST `/api/notifications/mark_all_read/`
- **Purpose**: Mark all notifications as read
- **Response**: 
```json
{
    "message": "All notifications marked as read"
}
```

### Notification Types and Events

1. **Streak Updates**
   - First streak achieved
   - Streak maintained
   - Streak milestone (7, 30, 100 days)
   - Streak reset

2. **League Promotions**
   - League promotion achieved
   - XP earned for promotion

3. **Energy Updates**
   - Energy used
   - Energy restored

4. **Milestone Achievements**
   - Streak milestones
   - XP milestones
   - Problem solving milestones

## Data Flow Between Endpoints

### 1. Problem Solving Flow
```
POST /api/problems/{id}/solve/
    ↓
Updates UserProblem
    ↓
Updates UserProgress
    ↓
Checks Streak Conditions
    ↓
Updates XP Totals
    ↓
Updates League Standings
```

### 2. Streak Management Flow
```
GET /api/gamification/streak/
    ↓
Checks Daily Activity
    ↓
Updates Streak Count
    ↓
POST /api/gamification/use_energy/
    ↓
Updates Energy System
```

### 3. League Progression Flow
```
GET /api/gamification/league/
    ↓
Checks XP Thresholds
    ↓
Updates League Status
    ↓
GET /api/gamification/league/{id}/leaderboard/
    ↓
Updates Rankings
```

## WebSocket Events

### 1. Problem Solved Event
```json
{
    "event": "problem_solved",
    "user_id": 1,
    "problem_id": 1,
    "xp_earned": 10,
    "timestamp": "2024-03-20T10:00:00Z"
}
```

### 2. Streak Updated Event
```json
{
    "event": "streak_updated",
    "user_id": 1,
    "new_streak": 5,
    "xp_earned": 20,
    "timestamp": "2024-03-20T10:00:00Z"
}
```

### 3. League Promotion Event
```json
{
    "event": "league_promotion",
    "user_id": 1,
    "old_league": "Biyo",
    "new_league": "Geesi",
    "timestamp": "2024-03-20T10:00:00Z"
}
```

## Error Responses

### 1. Authentication Error
```json
{
    "error": "Authentication failed",
    "detail": "Invalid or expired token"
}
```

### 2. Insufficient Energy
```json
{
    "error": "Insufficient energy",
    "detail": "Ma haysato tamar",
    "energy": {
        "current": 0,
        "max": 3,
        "next_update": "2024-03-20T15:00:00Z"
    }
}
```

### 3. League Requirements Not Met
```json
{
    "error": "League requirements not met",
    "detail": "Need 500 more XP for promotion",
    "current_xp": 500,
    "required_xp": 1000
}
```

## Rate Limiting

- Problem submissions: 10 per minute
- Energy usage: 1 per 4 hours
- API calls: 100 per minute 