# Garaad League System API Documentation

## Overview
The Garaad League System is inspired by traditional Somali clan leadership and learning structures, where knowledge and progress are celebrated through a hierarchical system of achievement. The system uses Somali cultural elements to make learning more engaging and meaningful.

## Base URL
```
https://api.garaad.org/api/
```

## Authentication
All endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## League Levels (Maamulka)
The league system is structured around traditional Somali clan leadership levels:

```json
{
  "levels": [
    {
      "id": "xirsi",
      "name": "Xirsi",
      "description": "The first step in your learning journey",
      "min_xp": 0
    },
    {
      "id": "garad",
      "name": "Garad",
      "description": "A respected leader in learning",
      "min_xp": 1000
    },
    {
      "id": "boqor",
      "name": "Boqor",
      "description": "A master of knowledge",
      "min_xp": 5000
    },
    {
      "id": "suldaan",
      "name": "Suldaan",
      "description": "A wise and experienced leader",
      "min_xp": 10000
    },
    {
      "id": "ugaas",
      "name": "Ugaas",
      "description": "The highest level of achievement",
      "min_xp": 20000
    }
  ]
}
```

## API Endpoints

### 1. Get League Status
```http
GET /api/leagues/status/
```

**Purpose**: Get the current user's league status, including rank, points, and streak information.

**Response**:
```json
{
  "current_league": {
    "id": "garad",
    "name": "Garad",
    "description": "A respected leader in learning",
    "min_xp": 1000
  },
  "current_points": 1500,
  "weekly_rank": 5,
  "streak": {
    "current_streak": 7,
    "max_streak": 14,
    "streak_charges": 2
  },
  "next_league": {
    "id": "boqor",
    "name": "Boqor",
    "min_xp": 5000,
    "points_needed": 3500
  }
}
```

### 2. Complete Lesson
```http
POST /api/lessons/{lesson_id}/complete/
```

**Purpose**: Mark a lesson as completed and update league progress.

**Request Body**:
```json
{
  "score": 100,
  "time_spent": 30
}
```

**Response**:
```json
{
  "progress": {
    "lesson_completed": true,
    "score": 100,
    "xp_earned": 150
  },
  "league": {
    "xp_earned": 150,
    "streak_updated": true,
    "league_changed": false,
    "current_league": "Garad",
    "current_points": 1650
  },
  "achievements": [
    {
      "id": "first_perfect",
      "name": "Maanta Wanaagsan",
      "description": "Scored 100% on your first lesson"
    }
  ]
}
```

### 3. Get Leaderboard
```http
GET /api/leagues/leaderboard/
```

**Purpose**: Get the current leaderboard standings.

**Query Parameters**:
- `time_period`: weekly, monthly, all_time (default: weekly)
- `league`: Filter by specific league (optional)

**Response**:
```json
{
  "time_period": "weekly",
  "league": "Garad",
  "standings": [
    {
      "rank": 1,
      "user": {
        "id": "user123",
        "name": "Ahmed Mohamed",
        "clan": "Hawiye",
        "region": "Mogadishu"
      },
      "points": 2500,
      "streak": 14
    }
  ],
  "my_standing": {
    "rank": 5,
    "points": 1500,
    "streak": 7
  }
}
```

### 4. Get Achievements
```http
GET /api/leagues/achievements/
```

**Purpose**: Get all available and earned achievements.

**Response**:
```json
{
  "achievements": [
    {
      "id": "first_lesson",
      "name": "Bilowga Waxbarashada",
      "description": "Complete your first lesson",
      "icon": "first_lesson.png",
      "earned": true,
      "earned_at": "2024-03-15T10:30:00Z"
    },
    {
      "id": "week_streak",
      "name": "Toddobaad Wanaagsan",
      "description": "Maintain a 7-day streak",
      "icon": "week_streak.png",
      "earned": false
    }
  ]
}
```

### 5. Get Streak Status
```http
GET /api/leagues/streak/
```

**Purpose**: Get detailed information about the user's current streak.

**Response**:
```json
{
  "current_streak": 7,
  "max_streak": 14,
  "streak_charges": 2,
  "last_activity": "2024-03-15T10:30:00Z",
  "next_reward": {
    "days_remaining": 3,
    "reward_type": "streak_charge",
    "description": "Earn a streak charge in 3 days"
  }
}
```

### 6. Use Streak Charge
```http
POST /api/leagues/streak/use_charge/
```

**Purpose**: Use a streak charge to maintain streak after missing a day.

**Response**:
```json
{
  "success": true,
  "streak_maintained": true,
  "remaining_charges": 1,
  "message": "Waad ku mahadsantahay ilaalinta xariggaaga"
}
```

## Cultural Elements

### Clan Integration
The system integrates with traditional Somali clan structures:
- Users can identify their clan (qabiil)
- Clan-based leaderboards
- Clan-specific achievements

### Regional Context
- Region-based leaderboards
- Regional learning preferences
- Local language support (Maay and Mahaa)

### Traditional Learning Elements
- Integration with traditional Somali learning methods
- Cultural achievements and rewards
- Traditional wisdom quotes and encouragement

## Error Responses

### Common Error Codes
```json
{
  "error": {
    "code": "LEAGUE_NOT_FOUND",
    "message": "Ma jiraan league-ka aad raadinayso",
    "details": "The requested league level does not exist"
  }
}
```

### Error Codes
- `LEAGUE_NOT_FOUND`: League level doesn't exist
- `INSUFFICIENT_POINTS`: Not enough points for league promotion
- `STREAK_CHARGE_LIMIT`: Maximum streak charges reached
- `INVALID_LEAGUE_TRANSITION`: Invalid league promotion/demotion

## Rate Limiting
- 100 requests per minute per user
- 1000 requests per hour per user

## WebSocket Events

### Real-time Updates
```javascript
// Connect to WebSocket
const ws = new WebSocket('wss://api.garaad.org/ws/leagues/');

// Event Types
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'league_promotion':
      // Handle league promotion
      break;
    case 'streak_update':
      // Handle streak update
      break;
    case 'achievement_earned':
      // Handle new achievement
      break;
  }
};
```

## Best Practices

1. **Error Handling**
   - Always check for error responses
   - Implement proper retry logic
   - Handle network errors gracefully

2. **Authentication**
   - Always include valid JWT token
   - Implement token refresh mechanism
   - Handle authentication errors

3. **Performance**
   - Cache frequently accessed data
   - Implement pagination for large datasets
   - Use compression for large responses

4. **Security**
   - Never expose sensitive user data
   - Validate all user inputs
   - Implement proper rate limiting

## Example Usage

### React Component Example
```javascript
const LeagueStatus = () => {
  const [leagueData, setLeagueData] = useState(null);
  
  useEffect(() => {
    const fetchLeagueStatus = async () => {
      try {
        const response = await fetch('/api/leagues/status/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        const data = await response.json();
        setLeagueData(data);
      } catch (error) {
        console.error('Error fetching league status:', error);
      }
    };
    
    fetchLeagueStatus();
  }, []);
  
  return (
    <div>
      <h2>Maamulkaaga: {leagueData?.current_league.name}</h2>
      <p>Dhibcahaaga: {leagueData?.current_points}</p>
      <p>Xariggaaga: {leagueData?.streak.current_streak} maalmood</p>
    </div>
  );
};
```

## Support
For API support and questions, contact:
- Email: api-support@garaad.org
- Phone: +252 61 234 5678
- Office Hours: 9:00 AM - 5:00 PM EAT 