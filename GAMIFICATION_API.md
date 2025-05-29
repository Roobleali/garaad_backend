# Gamification & Retention API Guide

This document explains all endpoints and logic for the gamification and retention system. It is designed for frontend developers to easily integrate and provide a smooth, engaging user experience.

---

## Table of Contents
- [User Progress & XP](#user-progress--xp)
- [Streaks](#streaks)
- [Leagues](#leagues)
- [Leaderboard](#leaderboard)
- [Rewards & Badges](#rewards--badges)
- [Notifications (In-App & Email)](#notifications-in-app--email)
- [Profile Gamification Data](#profile-gamification-data)
- [Email Reminder System](#email-reminder-system)
- [Best Practices](#best-practices)

---

## User Progress & XP

### Lesson Progress
- **Endpoint:** `GET /api/lms/user-progress/`
- **Description:** List all lesson progress for the authenticated user.
- **Response:**
```json
[
  {
    "lesson": 1,
    "lesson_title": "Intro to Crypto",
    "status": "completed",
    "score": 95,
    "completed_at": "2025-05-20T12:00:00Z"
  },
  ...
]
```

### Mark Lesson Complete
- **Endpoint:** `POST /api/lms/lessons/{id}/complete/`
- **Body:** `{ "completed_problems": [1,2,3], "total_score": 100 }`
- **Response:** XP earned, streak, and updated progress.

---

## Streaks
- **Endpoint:** `GET /api/league/leagues/streak/`
- **Description:** Get current streak, max streak, and streak charges.
- **Response:**
```json
{
  "current_streak": 5,
  "max_streak": 10,
  "streak_charges": 2,
  "last_activity": "2025-05-25"
}
```

- **Use Streak Charge:** `POST /api/league/leagues/use_streak_charge/`

---

## Leagues
- **Endpoint:** `GET /api/league/leagues/status/`
- **Description:** Get user's current league, XP, rank, and next league info.
- **Response:**
```json
{
  "current_league": { "id": 1, "name": "Biyo", "min_xp": 0 },
  "current_points": 1200,
  "weekly_rank": 3,
  "streak": { ... },
  "next_league": { "id": 2, "name": "Geesi", "min_xp": 2000, "points_needed": 800 }
}
```

---

## Leaderboard
- **Endpoint:** `GET /api/league/leagues/leaderboard/?time_period=weekly&league={id}`
- **Description:** Get top users in the league and your own standing.
- **Response:**
```json
{
  "standings": [
    { "rank": 1, "user": { "id": 76, "name": "Rooble Cali" }, "points": 1500, "streak": 7 },
    ...
  ],
  "my_standing": { "rank": 3, "points": 1200, "streak": 5 }
}
```

---

## Rewards & Badges
- **Endpoint:** `GET /api/lms/user-rewards/`
- **Description:** List all rewards (XP, badges, etc.) earned by the user.
- **Response:**
```json
[
  {
    "reward_type": "points",
    "reward_name": "Lesson Completion",
    "value": 10,
    "awarded_at": "2025-05-22T08:40:08Z",
    "lesson_title": "Horudhaca ZooCash",
    "course_title": "Lacagaha 'Cryptocurrency'"
  },
  ...
]
```

---

## Notifications (In-App & Email)
- **Endpoint:** `GET /api/lms/notifications/`
- **Description:** List all notifications for the user (in-app and email reminders).
- **Mark All Read:** `POST /api/lms/notifications/mark_all_read/`
- **Unread Count:** `GET /api/lms/notifications/unread_count/`
- **Response:**
```json
[
  {
    "title": "Waqtiga Waxbarashada!",
    "message": "Waa waqtigii waxbarasho...",
    "is_read": false,
    "created_at": "2025-05-26T10:00:00Z"
  },
  ...
]
```

---

## Profile Gamification Data
- **Endpoint:** `GET /api/auth/profile/`
- **Description:** Returns all gamification data for the user profile.
- **Response:**
```json
{
  "xp": 40,
  "streak": { "current": 1, "max": 1, "energy": 2 },
  "league": { "id": 1, "name": "Biyo", "min_xp": 0 },
  "badges": [],
  "notification_preferences": {}
}
```

---

## Email Reminder System
- **How it works:**
  - Users receive daily/weekly reminder emails based on their study preferences and streaks.
  - Emails are sent automatically by the backend (no frontend action needed).
  - Users can see all reminders in the notifications endpoint as well.

---

## Best Practices for Frontend
- Always show the user's streak, XP, and league on the dashboard/profile.
- Use the notifications endpoint to show reminders and motivational messages.
- Encourage users to maintain streaks and climb the leaderboard.
- Show badges and rewards as soon as they are earned.
- Use the profile endpoint to get all gamification data in one call.

---

## FAQ
- **Q: How do I know if a user has a new notification?**
  - Use `GET /api/lms/notifications/unread_count/`.
- **Q: How do I show the user's current streak and league?**
  - Use `GET /api/auth/profile/` or the dedicated streak/league endpoints.
- **Q: How are reminder emails sent?**
  - The backend sends them automatically based on user activity and preferences.

---

For any questions or to request new gamification features, contact the backend team. 