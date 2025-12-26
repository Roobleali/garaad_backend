# Garaad API Documentation (V2 - Simplified Architecture)

This document provides the definitive guide for the frontend team to interact with the Garaad backend.

## 🏗️ Architecture Overview

The API is built on **Django REST Framework (DRF)** with the following core principles:
- **Authentication:** Bearer tokens (JWT). Use `/api/auth/signin/` to get tokens.
- **Primary Keys:** Most new community models use **UUID v4** as IDs. Older models use integer IDs.
- **State Management:** Backend is the source of truth. Use WebSockets only for real-time notifications, not for core state synchronization.

---

## 🔐 Authentication

All protected endpoints require the `Authorization` header:
`Authorization: Bearer <access_token>`

---

## 🔥 Gamification & Streaks

### 1. Get Status
`GET /api/gamification/status/`
Returns the user's current level, identity, energy, and streak.

**Response Snippet:**
```json
{
    "identity": "explorer",
    "next_action": {
        "title": "Sii wad barashada",
        "action_type": "solve",
        "priority": "normal"
    },
    "streak": { "count": 5 }
}
```

### 2. Update Activity
`POST /api/activity/update/`
Update progress after solving problems or finishing lessons.

**Request Body:**
```json
{
    "action_type": "solve",
    "problems_solved": 1,
    "energy_spent": 1,
    "lesson_ids": ["lesson-uuid-1"]
}
```

---

## 👥 Community (V2)

### 1. Get Categories (Campuses)
`GET /api/community/categories/`
Lists all categories where community features are enabled.

### 2. List Posts (by Category)
`GET /api/community/categories/{categoryId}/posts/`
Returns a flat list of posts for a specific category.

### 3. Create Post
`POST /api/community/posts/`
**Body:** `{ "category": "{category_id}", "content": "Hello Garaad!" }`

### 4. React to Post
`POST /api/community/posts/{postId}/react/`
**Body:** `{ "type": "like" }` (Note: Toggles on/off automatically).

### 5. Reply to Post
`POST /api/community/posts/{postId}/reply/`
**Body:** `{ "content": "Great post!" }`

### 6. My Community Profile
`GET /api/community/profiles/me/`
Returns user stats and basic info.

### 7. View Other User Profile
`GET /api/community/profiles/{userId}/`
Returns a specific user's stats (posts, replies) and basic info.

---

## 🔌 WebSockets

**URL:** `wss://api.garaad.org/ws/community/`

Connect to receive real-time updates for:
- `post_created`: New post in a category.
- `reply_created`: New reply to a post.
- `reaction_updated`: Total counts changed.

**Payload Format:**
```json
{
    "type": "event_type",
    "data": { ... }
}
```

---

## ⚠️ Important Implementation Notes

1. **UUIDs:** Post, Reply, and Reaction IDs are strings (UUIDs). Do not parse them as integers.
2. **Category IDs:** Category IDs (e.g., `stem`, `ai`) are custom strings, not integers.
3. **Optimistic UI:** Implement optimistic updates for reactions and replies. The backend is fast, but user perception is faster!
