# Streak API Documentation

## Overview
The Streak API allows you to track user progress, manage daily activities, and handle energy-based interactions in the learning system. The system includes features like streak counting, energy management, and daily activity tracking.

## Authentication
All endpoints require Bearer token authentication. Include the following header with your requests:
```
Authorization: Bearer <your_access_token>
```

## Base URL
```
https://api.garaad.org/api/
```
For local development:
```
http://localhost:8001/api/
```

## Endpoints

### 1. Get Streak Status
Retrieves the user's current streak information, including energy levels and daily activity history.

**Endpoint:** `GET /api/streaks/`

**Response Example:**
```json
{
  "userId": "user_12345",
  "username": "abdullahi",
  "currentStreak": 14,
  "maxStreak": 20,
  "lessonsCompleted": 26,
  "problemsToNextStreak": 3,
  "energy": {
    "current": 2,
    "max": 3,
    "next_update": "2025-05-23T18:00:00Z"
  },
  "dailyActivity": [
    {
      "date": "2025-05-17",
      "day": "Sat",
      "status": "complete",
      "problemsSolved": 5,
      "lessonIds": ["lesson_101", "lesson_102"],
      "isToday": false
    },
    {
      "date": "2025-05-18",
      "day": "Sun",
      "status": "none",
      "problemsSolved": 0,
      "lessonIds": [],
      "isToday": false
    }
    // ... more days
  ]
}
```

### 2. Update Streak Progress
Records the number of problems solved and lessons completed for the current day.

**Endpoint:** `POST /api/streaks/`

**Request Body:**
```json
{
  "problemsSolved": 3,
  "lessonIds": ["lesson_108"]
}
```

**Response Example:**
```json
{
  "message": "Streak updated",
  "currentStreak": 15,
  "energy": {
    "current": 2,
    "max": 3,
    "next_update": "2025-05-23T18:00:00Z"
  },
  "dailyActivity": [
    {
      "date": "2025-05-23",
      "day": "Fri",
      "status": "complete",
      "problemsSolved": 3,
      "lessonIds": ["lesson_108"],
      "isToday": true
    }
  ]
}
```

## Status Codes
- `200 OK`: Request successful
- `400 Bad Request`: Invalid input or not enough energy
- `401 Unauthorized`: Invalid or missing authentication token
- `500 Internal Server Error`: Server error

## Energy System
The energy system works as follows:
- Each user starts with 3 energy points
- Energy regenerates at a rate of 1 point every 4 hours
- Maximum energy is 3 points
- Each problem-solving activity consumes 1 energy point
- The `next_update` field in responses indicates when the next energy point will be available

## Activity Status
Daily activity can have three states:
- `"none"`: No problems solved (0 problems)
- `"partial"`: Some progress (1-2 problems)
- `"complete"`: Daily goal achieved (3+ problems)

## Streak Rules
1. Streaks increment when:
   - User completes activities on consecutive days
   - At least 3 problems are solved in a day

2. Streaks reset when:
   - User misses a day
   - No problems are solved in a day

3. Problems to next streak:
   - Starts at 3 problems
   - Decreases by 1 when completing 3+ problems in a day
   - Minimum is 1 problem

## Error Handling
The API may return error responses in the following format:

```json
{
  "error": "Not enough energy to perform this action",
  "energy": {
    "current": 0,
    "max": 3,
    "next_update": "2025-05-23T18:00:00Z"
  }
}
```

## Implementation Example (React)
```typescript
// Example using axios
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api';

// Get streak status
const getStreakStatus = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/streaks/`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching streak:', error);
    throw error;
  }
};

// Update streak progress
const updateStreak = async (problemsSolved: number, lessonIds: string[]) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/streaks/`,
      {
        problemsSolved,
        lessonIds
      },
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error updating streak:', error);
    throw error;
  }
};
```

## Best Practices
1. Always check energy levels before attempting problem-solving activities
2. Handle the `next_update` time to show users when more energy will be available
3. Update the UI immediately after successful streak updates
4. Implement proper error handling for all API calls
5. Cache streak status and update periodically rather than on every user action

## Rate Limiting
- The API implements rate limiting to prevent abuse
- Standard rate limit: 100 requests per minute per user
- Exceeding the rate limit will return a 429 Too Many Requests response

## Websocket Events (Coming Soon)
Real-time updates for:
- Energy regeneration
- Streak status changes
- Daily activity completion

For any questions or issues, please contact the backend team at backend@garaad.org 