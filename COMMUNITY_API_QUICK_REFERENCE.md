# Community API Quick Reference

## 🔗 Base URL
```
https://api.garaad.org/api/community/
```

## 🔐 Authentication
```javascript
headers: {
  'Authorization': 'Bearer <your_jwt_token>',
  'Content-Type': 'application/json'
}
```

## 📋 Essential Endpoints

### 🏫 Campuses (Tribes)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/campuses/` | List all campuses |
| `GET` | `/campuses/{slug}/` | Get campus details |
| `POST` | `/campuses/{slug}/join/` | Join campus |
| `POST` | `/campuses/{slug}/leave/` | Leave campus |

### 📝 Posts
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/posts/` | List posts (with filters) |
| `POST` | `/posts/` | Create new post |
| `GET` | `/posts/{id}/` | Get post details |
| `POST` | `/posts/{id}/like/` | Like/unlike post |

### 💬 Comments
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/comments/?post={id}` | List comments for post |
| `POST` | `/comments/` | Create comment/reply |
| `POST` | `/comments/{id}/like/` | Like/unlike comment |

### 👤 User Profile
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/profiles/me/` | Get user profile |
| `GET` | `/profiles/leaderboard/` | Get leaderboard |

### 🔔 Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/notifications/` | List notifications |
| `POST` | `/notifications/{id}/mark_read/` | Mark as read |
| `POST` | `/notifications/mark_all_read/` | Mark all as read |

## 🚀 Quick Examples

### Create Post
```javascript
const createPost = async (data) => {
  const response = await fetch('https://api.garaad.org/api/community/posts/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      title: "My Question",
      content: "I need help with...",
      room_id: 1,
      language: "en",
      post_type: "question"
    })
  });
  return response.json();
};
```

### Join Campus
```javascript
const joinCampus = async (slug) => {
  const response = await fetch(`https://api.garaad.org/api/community/campuses/${slug}/join/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  return response.json();
};
```

### Get User Profile
```javascript
const getUserProfile = async () => {
  const response = await fetch('https://api.garaad.org/api/community/profiles/me/', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  return response.json();
};
```

## 📊 Response Fields

### Post Object
```json
{
  "id": "uuid",
  "title": "Post Title",
  "content": "Post content...",
  "user": {
    "id": 1,
    "username": "user123",
    "first_name": "Ahmed",
    "last_name": "Hassan"
  },
  "likes_count": 5,
  "comments_count": 3,
  "user_has_liked": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Campus Object
```json
{
  "slug": "physics-campus",
  "name": "Physics",
  "name_somali": "Fiisikis",
  "member_count": 145,
  "post_count": 89,
  "is_member": true
}
```

### User Profile Object
```json
{
  "community_points": 1250,
  "badge_level": "expert",
  "badge_level_display": "Expert",
  "total_posts": 15,
  "total_comments": 45
}
```

## 🔍 Query Parameters

### Posts Filtering
- `?room=1` - Filter by room ID
- `?campus=physics-campus` - Filter by campus slug
- `?post_type=question` - Filter by post type
- `?search=quantum` - Search in title/content

### Campuses Filtering
- `?subject_tag=physics` - Filter by subject
- `?search=quantum` - Search in names/descriptions

## ⚠️ Common Errors

| Status | Error | Solution |
|--------|-------|----------|
| `401` | Authentication credentials were not provided | Add JWT token to headers |
| `403` | You do not have permission | User not member of campus |
| `404` | Not found | Check URL/ID exists |
| `400` | Bad request | Check request body format |

## 🎯 Post Types
- `text` - Regular post
- `question` - Question post
- `announcement` - Announcement
- `poll` - Poll
- `media` - Media post

## 🌍 Languages
- `so` - Somali (default)
- `en` - English
- `ar` - Arabic

## 📱 Frontend Integration Tips

1. **Use Somali fields for UI**: `name_somali`, `description_somali`
2. **Handle loading states**: Show spinners during API calls
3. **Error handling**: Display user-friendly error messages
4. **Real-time updates**: Poll for new notifications
5. **Pagination**: Handle `next`/`previous` URLs in responses

## 🔗 Full Documentation
See `FRONTEND_COMMUNITY_INTEGRATION_GUIDE.md` for complete documentation with React examples and detailed implementation guidance. 