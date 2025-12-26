# 🛠️ Frontend API Integration Fix Guide

This guide addresses the recent `500` and `400` errors and provides instructions for the updated Community and Activity endpoints.

## 1. User Profiles (Fixing 404/500)

We have added a dedicated endpoint to fetch other users' profiles for the community modals.

- **Endpoint**: `GET /api/community/profiles/{userId}/`
- **Parameter**: `userId` must be the UUID (string) of the user.
- **Response**:
```json
{
    "id": "u-uuid-here",
    "username": "rooble",
    "full_name": "Rooble Ali",
    "avatar": "https://api.garaad.org/media/profiles/...",
    "bio": "Software Engineer",
    "post_count": 12,
    "reply_count": 45,
    "is_premium": true
}
```

## 2. Post Reactions (Fixing 500)

The reaction system has been migrated to use UUIDs for all Post IDs. 

- **Endpoint**: `POST /api/community/posts/{postId}/react/`
- **Important**: Ensure `{postId}` is the string UUID (e.g., `c0a31eaa...`).
- **Body**:
```json
{
    "type": "like"  // Options: "like", "fire", "insight"
}
```

## 3. Activity Updates (Fixing 400)

The `/api/activity/update/` endpoint now supports **Idempotency**. If you don't send a `request_id`, or if you send one that the server doesn't expect, it might return a 400.

- **Endpoint**: `POST /api/activity/update/`
- **Recommended Body**:
```json
{
    "action_type": "solve",      // "solve", "problem_attempt", "help"
    "problems_solved": 1,
    "lesson_ids": ["lesson-123"],
    "request_id": "unique-uuid-per-click" // HIGHLY RECOMMENDED: Generate a UUID for each click to prevent double-spending/errors.
}
```
> [!TIP]
> Use a library like `uuid` to generate `request_id` locally before making the call. This ensures that even if a network timeout happens and you retry, the server won't count the activity twice.

## 4. Troubleshooting Status Codes

| Code | Meaning | Fix |
|---|---|---|
| **400** | Bad Request | Check if your JSON body matches the guide above. Ensure IDs are strings. |
| **404** | Not Found | Ensure you are using `/api/community/profiles/{id}/` instead of the old profile endpoints. |
| **500** | Server Error | This usually means the backend database is being migrated. Wait 1 minute and retry. |

---
**Current API Version**: `v2.1.0`  
**Base URL**: `https://api.garaad.org`
