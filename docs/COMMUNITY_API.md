# Community API Documentation

## Overview
Simple, clean community system built on top of existing Categories. No over-engineering, no noise.

---

## Core Concepts

- **Category**: Existing course categories can now have community features enabled
- **Post**: A message/discussion in a category
- **Reply**: One-level response to a post (no nested threading)
- **Reaction**: Controlled engagement (like, fire, insight)

---

## API Endpoints

### 1. List Posts in Category
```
GET /api/community/categories/{category_id}/posts/
```

**Response**:
```json
[
  {
    "id": 1,
    "category": "physics",
    "author": {
      "id": 123,
      "username": "student1",
      "profile_picture": "...",
      "first_name": "Ahmed",
      "last_name": "Ali"
    },
    "content": "Can someone explain quantum entanglement?",
    "created_at": "2025-12-24T20:00:00Z",
    "updated_at": "2025-12-24T20:00:00Z",
    "is_edited": false,
    "images": [],
    "replies": [
      {
        "id": 1,
        "author": {...},
        "content": "Sure! It's when two particles...",
        "created_at": "2025-12-24T20:05:00Z",
        "is_edited": false
      }
    ],
    "replies_count": 1,
    "reactions_count": {
      "like": 5,
      "fire": 2,
      "insight": 1
    },
    "user_reactions": ["like"]
  }
]
```

---

### 2. Create Post
```
POST /api/community/categories/{category_id}/posts/
```

**Request Body**:
```json
{
  "category": "physics",
  "content": "What's the difference between velocity and speed?"
}
```

**Requirements**:
- User must be authenticated
- Category must have `is_community_enabled = true`

---

### 3. Update Post
```
PATCH /api/posts/{id}/
```

**Request Body**:
```json
{
  "content": "Updated content here"
}
```

**Permissions**:
- Author can edit their own post
- Staff can edit any post
- Post will be marked as `is_edited = true`

---

### 4. Delete Post
```
DELETE /api/posts/{id}/
```

**Permissions**:
- Author can delete their own post
- Staff can delete any post

---

### 5. React to Post
```
POST /api/posts/{id}/react/
```

**Request Body**:
```json
{
  "type": "like"  // Options: "like", "fire", "insight"
}
```

**Behavior**:
- Toggle: If user already has this reaction, it will be removed
- Otherwise, reaction is added

**Response**:
```json
{
  "action": "added",  // or "removed"
  "type": "like"
}
```

---

### 6. Reply to Post
```
POST /api/posts/{id}/reply/
```

**Request Body**:
```json
{
  "content": "Great question! Here's my answer..."
}
```

**Response**:
```json
{
  "id": 42,
  "author": {...},
  "content": "Great question! Here's my answer...",
  "created_at": "2025-12-24T20:10:00Z",
  "is_edited": false
}
```

---

### 7. Update Reply
```
PATCH /api/replies/{id}/
```

**Request Body**:
```json
{
  "content": "Updated reply content"
}
```

**Permissions**:
- Author can edit their own reply
- Staff can edit any reply

---

### 8. Delete Reply
```
DELETE /api/replies/{id}/
```

**Permissions**:
- Author can delete their own reply
- Staff can delete any reply

---

## Category Updates

The existing Category model now includes:

```json
{
  "id": "physics",
  "title": "Physics",
  "description": "Learn about the laws of nature",
  "image": "...",
  "in_progress": false,
  "course_ids": [...],
  "courses": [...],
  "is_community_enabled": true,
  "community_description": "Discuss physics concepts, ask questions, and share insights",
  "posts_count": 42
}
```

---

## Permissions Summary

| Action | Authenticated | Author | Staff |
|--------|--------------|--------|-------|
| View posts/replies | ✅ | ✅ | ✅ |
| Create post | ✅ | ✅ | ✅ |
| Create reply | ✅ | ✅ | ✅ |
| React | ✅ | ✅ | ✅ |
| Edit own content | ❌ | ✅ | ✅ |
| Delete own content | ❌ | ✅ | ✅ |
| Edit any content | ❌ | ❌ | ✅ |
| Delete any content | ❌ | ❌ | ✅ |

---

## Implementation Notes

1. **No karma system** - Keep it simple
2. **No ranks** - Focus on learning, not gamification
3. **One-level replies** - No nested threading complexity
4. **Controlled reactions** - Only 3 types (like, fire, insight)
5. **Category-based** - Extends existing structure, no new concepts

---

## Migration from Old System

The old Campus/Room system has been replaced. If you have existing frontend code:

1. Replace `/api/community/campuses/` with `/api/lms/categories/`
2. Check `is_community_enabled` before showing community features
3. Use `/api/community/categories/{id}/posts/` instead of room-based endpoints
4. Update WebSocket connections (if needed) - TBD based on requirements

---

## Next Steps

1. Run migrations: `python manage.py makemigrations && python manage.py migrate`
2. Enable community on categories via admin panel
3. Test endpoints with Postman/curl
4. Update frontend to use new endpoints
