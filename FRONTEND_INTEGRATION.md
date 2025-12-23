# Garaad Backend: Frontend Integration Guide

This document provides a comprehensive overview of the Garaad API for the frontend development team.

## General Information
- **Base URL**: `http://api.garaad.org/api/` (Production) or `http://localhost:8000/api/` (Local)
- **Authentication**: All protected endpoints require a Bearer Token in the headers:
  `Authorization: Bearer <your_access_token>`

---

## 1. Authentication (`/auth/`)
Endpoints for user onboarding and session management.

- **POST** `/auth/signup/`: Register a new user.
- **POST** `/auth/signin/`: Authenticate and receive JWT tokens.
- **GET** `/auth/user/`: Get current logged-in user details.

---

## 2. Community Features (`/community/`) ✨
Recently updated to include Discord-like functionality and standardized naming.

### Campuses
- **GET** `/community/campuses/`: List all available subject-based campuses.
- **POST** `/community/campuses/{slug}/join/`: Join a campus.
- **POST** `/community/campuses/{slug}/leave/`: Leave a campus.
- **GET** `/community/campuses/{slug}/rooms/`: List rooms within a specific campus.

### Rooms & Messaging
- **GET** `/community/rooms/`: List all rooms (filtered by campus query param).
- **Valid Room Types**: `text` (Qoraal), `voice` (Cod), `announcement` (Ogeysiis), `private` (Gaar ah).
- **GET** `/community/messages/?room={room_uuid}`: Fetch messages for a specific room.
- **POST** `/community/messages/`: Send a new message.
  - Payload: `{ "room": "uuid", "content": "Hello!", "reply_to": "uuid_optional" }`

### Presence (Real-time Status)
- **GET** `/community/presence/`: Get current user's presence.
- **POST** `/community/presence/set_status/`: Update presence status.
  - Payload: `{ "status": "online", "custom_status": "Reading Physics" }`
  - Valid Statuses: `online`, `idle` (Fadhi), `dnd` (Ha Iwaxyeelin), `offline`.

### Profiles & Gamification
- **GET** `/community/profiles/me/`: Get your community stats (points, badge level).
- **GET** `/community/profiles/leaderboard/`: Get top users globally or by campus.

---

## 3. Learning Management System (`/lms/`)
- **GET** `/lms/categories/`: List subject categories.
- **GET** `/lms/courses/`: List all courses (can filter by category).
- **GET** `/lms/courses/{id}/`: Get course details and lesson list.
- **GET** `/lms/lessons/{id}/`: Get lesson content (text, video, interactive blocks).
- **POST** `/lms/lessons/{id}/complete/`: Mark lesson as finished.

---

## 4. Leagues & Gamification (`/league/`)
- **GET** `/league/leagues/`: List available leagues (Bronze, Silver, Gold).
- **GET** `/streaks/`: Get user streak information.
- **POST** `/activity/update/`: Log user activity to maintain streaks.

---

## 5. Media & Assets
Serving files is handled through specific endpoints to ensure correct permissions:
- **Profile Pics**: `/api/media/profile_pics/{filename}`
- **Community Images**: `/api/media/community/posts/{filename}`
- **Course Media**: `/api/media/courses/{filename}`

---

## 6. Error Handling
The API returns standard HTTP status codes:
- `200/201`: Success
- `400`: Bad Request (Validation errors)
- `401`: Unauthorized (Missing/Expired token)
- `403`: Forbidden (Missing permissions for campus/room)
- `404`: Not Found

For most errors, the payload will be:
```json
{ "error": "Detailed error message in Somali or English" }
```
