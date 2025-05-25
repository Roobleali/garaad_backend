# Garaad API Documentation

## Base URL
- Development: `http://127.0.0.1:8000`
- Production: `https://api.garaad.org`

## Authentication
All endpoints require JWT authentication. Include the token in the request header:
```http
Authorization: Bearer <your_jwt_token>
```

## League System API

### Get League Status
```http
GET /api/league/leagues/status/
```

Returns the current user's league status, including current league, points, rank, and streak information.

#### Response
```json
{
    "current_league": {
        "id": 1,
        "name": "Bronze",
        "somali_name": "Bronze",
        "description": "Starting league",
        "min_xp": 0,
        "order": 1,
        "icon": "bronze.png"
    },
    "current_points": 150,
    "weekly_rank": 5,
    "streak": {
        "current_streak": 3,
        "max_streak": 5,
        "streak_charges": 2,
        "last_activity_date": "2024-03-20"
    },
    "next_league": {
        "id": 2,
        "name": "Silver",
        "somali_name": "Silver",
        "min_xp": 500,
        "points_needed": 350
    }
}
```

### Get Leaderboard
```http
GET /api/league/leagues/leaderboard/
```

Returns the leaderboard standings with optional filtering.

#### Query Parameters
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| time_period | string | 'weekly', 'monthly', or 'all_time' | 'weekly' |
| league | string | League ID to filter by | null |

#### Response
```json
{
    "time_period": "weekly",
    "league": "1",
    "standings": [
        {
            "rank": 1,
            "user": {
                "id": 1,
                "name": "user1"
            },
            "points": 1000,
            "streak": 5
        }
    ],
    "my_standing": {
        "rank": 5,
        "points": 500,
        "streak": 3
    }
}
```

### List All Leagues
```http
GET /api/league/leagues/
```

Returns a list of all available leagues.

#### Response
```json
[
    {
        "id": 1,
        "name": "Bronze",
        "somali_name": "Bronze",
        "description": "Starting league",
        "min_xp": 0,
        "order": 1,
        "icon": "bronze.png"
    }
]
```

### Get League Details
```http
GET /api/league/leagues/{id}/
```

Returns details of a specific league.

#### Response
```json
{
    "id": 1,
    "name": "Bronze",
    "somali_name": "Bronze",
    "description": "Starting league",
    "min_xp": 0,
    "order": 1,
    "icon": "bronze.png"
}
```

## Gamification API

### Get Gamification Status
```http
GET /api/gamification/status/
```

Returns complete gamification status including XP, streak, and league information.

#### Response
```json
{
    "xp": {
        "total": 1000,
        "daily": 50,
        "weekly": 200,
        "monthly": 500
    },
    "streak": {
        "current": 3,
        "max": 5,
        "energy": 2,
        "problems_to_next": 2
    },
    "league": {
        "current": {
            "id": 1,
            "name": "Bronze",
            "somali_name": "Bronze",
            "min_xp": 0
        },
        "next": {
            "id": 2,
            "name": "Silver",
            "somali_name": "Silver",
            "min_xp": 500,
            "points_needed": 350
        }
    },
    "rank": {
        "weekly": 5
    }
}
```

### Use Energy
```http
POST /api/gamification/use_energy/
```

Uses one energy point to maintain streak.

#### Response
```json
{
    "success": true,
    "remaining_energy": 1,
    "message": "Waad ku mahadsantahay ilaalinta xariggaaga"
}
```

## Notifications API

### List Notifications
```http
GET /api/notifications/
```

Returns list of user's notifications.

#### Response
```json
[
    {
        "id": 1,
        "type": "streak",
        "title": "Streak Update",
        "message": "Waad ku mahadsantahay ilaalinta xariggaaga",
        "data": {
            "streak_days": 3
        },
        "is_read": false,
        "created_at": "2024-03-20T10:00:00Z"
    }
]
```

### Get Unread Count
```http
GET /api/notifications/unread_count/
```

Returns count of unread notifications.

#### Response
```json
{
    "unread_count": 5
}
```

### Mark Notification as Read
```http
POST /api/notifications/{id}/mark_read/
```

Marks a specific notification as read.

#### Response
```json
{
    "message": "Notification marked as read"
}
```

### Mark All Notifications as Read
```http
POST /api/notifications/mark_all_read/
```

Marks all notifications as read.

#### Response
```json
{
    "message": "All notifications marked as read"
}
```

## Error Responses

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

### 400 Bad Request
```json
{
    "detail": "Invalid request parameters."
}
```

## TypeScript Interfaces

```typescript
interface League {
    id: number;
    name: string;
    somali_name: string;
    description: string;
    min_xp: number;
    order: number;
    icon: string;
}

interface LeagueStatus {
    current_league: League;
    current_points: number;
    weekly_rank: number;
    streak: {
        current_streak: number;
        max_streak: number;
        streak_charges: number;
        last_activity_date: string;
    };
    next_league: {
        id: number;
        name: string;
        somali_name: string;
        min_xp: number;
        points_needed: number;
    } | null;
}

interface LeaderboardStanding {
    rank: number;
    user: {
        id: number;
        name: string;
    };
    points: number;
    streak: number;
}

interface LeaderboardResponse {
    time_period: 'weekly' | 'monthly' | 'all_time';
    league: string | null;
    standings: LeaderboardStanding[];
    my_standing: LeaderboardStanding;
}

interface Notification {
    id: number;
    type: 'streak' | 'league' | 'milestone' | 'energy' | 'welcome' | 'reminder' | 'achievement' | 'competition' | 'social';
    title: string;
    message: string;
    data: Record<string, any>;
    is_read: boolean;
    created_at: string;
}
```

## Example Usage

```typescript
// Fetch league status
const getLeagueStatus = async (): Promise<LeagueStatus> => {
    const response = await fetch('https://api.garaad.org/api/league/leagues/status/', {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });
    return response.json();
};

// Fetch leaderboard
const getLeaderboard = async (
    timePeriod: 'weekly' | 'monthly' | 'all_time',
    leagueId?: string
): Promise<LeaderboardResponse> => {
    const params = new URLSearchParams({
        time_period: timePeriod,
        ...(leagueId && { league: leagueId })
    });
    const response = await fetch(
        `https://api.garaad.org/api/league/leagues/leaderboard/?${params}`,
        {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        }
    );
    return response.json();
};

// Get notifications
const getNotifications = async (): Promise<Notification[]> => {
    const response = await fetch('https://api.garaad.org/api/notifications/', {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });
    return response.json();
};
```

## XP System

### XP Awarding Rules
XP is automatically awarded in the following scenarios:

1. **Problem Solving**
   - Each problem solved awards 5 XP
   - Maximum 20 XP per day from problems

2. **Streak Maintenance**
   - First streak: 20 XP
   - Daily streak continuation: 20 XP
   - Streak milestones:
     - 7 days: 50 XP bonus
     - 30 days: 50 XP bonus
     - 100 days: 50 XP bonus

3. **League Promotions**
   - Automatic XP tracking for league progression
   - League thresholds:
     - Bronze: 0 XP
     - Silver: 500 XP
     - Gold: 1000 XP
     - Platinum: 2000 XP
     - Diamond: 5000 XP

### XP Tracking
XP is tracked in multiple time periods:
- Total XP (lifetime)
- Daily XP (resets at midnight)
- Weekly XP (resets on Mondays)
- Monthly XP (resets on 1st of month)

### XP Reset Schedule
- Daily XP: Resets at midnight
- Weekly XP: Resets on Mondays
- Monthly XP: Resets on 1st of month

### XP and League Progression
When a user reaches the XP threshold for the next league:
1. User is automatically promoted
2. A league promotion notification is sent
3. League ranking is updated
4. New league benefits are unlocked

### Example XP Flow
```typescript
interface XPUpdate {
    total: number;
    daily: number;
    weekly: number;
    monthly: number;
    next_league?: {
        name: string;
        points_needed: number;
    };
}

// Example XP update after solving problems
const xpUpdate: XPUpdate = {
    total: 150,
    daily: 20,
    weekly: 50,
    monthly: 100,
    next_league: {
        name: "Silver",
        points_needed: 350
    }
};
``` 