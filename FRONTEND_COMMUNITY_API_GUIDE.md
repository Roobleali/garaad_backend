# Garaad Community System – Frontend Integration Guide

## API Base URL

```
/api/community/api/
```

All endpoints require JWT authentication. Add the token to the `Authorization` header:

```
Authorization: Bearer <your_token>
```

---

## 🏫 Campus (Tribe) Endpoints

### List All Campuses (Tribes)
```
GET /campuses/
```
- Returns all subject-based communities (Physics, Math, Crypto, AI, Fitness, etc.)
- Somali UI: Use `name_somali`, `description_somali`, and `subject_display_somali` fields

### Join a Campus
```
POST /campuses/{slug}/join/
```
- Join a campus (tribe)

### Leave a Campus
```
POST /campuses/{slug}/leave/
```
- Leave a campus (tribe)

### Get Campus Rooms
```
GET /campuses/{slug}/rooms/
```
- List all rooms (e.g., General, Study, Social) in a campus

---

## 🏠 Room Endpoints

### List Rooms
```
GET /rooms/?campus={slug}
```
- List all rooms in a campus

### Get Room Posts
```
GET /rooms/{id}/posts/
```
- Get all posts in a room (paginated)

---

## 📝 Post Endpoints

### List Posts
```
GET /posts/?campus={slug}&room={id}
```
- Filter by campus or room

### Create Post
```
POST /posts/
{
  "title": "Cinwaan",
  "content": "Qoraal faahfaahsan",
  "room_id": 1,
  "language": "so",
  "post_type": "text"
}
```
- Somali UI: Use Somali for all labels and error messages

### Like/Unlike Post
```
POST /posts/{id}/like/
```

---

## 💬 Comment & Reply Endpoints

### List Comments
```
GET /comments/?post={post_id}
```

### Create Comment or Reply
```
POST /comments/
{
  "content": "Faallo ama jawaab",
  "post_id": "uuid",
  "parent_comment_id": "uuid" // Optional for replies
}
```

### Like/Unlike Comment
```
POST /comments/{id}/like/
```

---

## 👤 User Profile & Gamification

### Get User Profile (with XP, League, Community Points)
```
GET /profiles/me/
```
- Returns:
  - `community_points`, `badge_level`, `total_posts`, `total_comments`, `total_likes_received`, `total_likes_given`
  - XP, league, streak, badges (from `/accounts/user_profile/` endpoint)

### Leaderboard
```
GET /profiles/leaderboard/
```
- Top users by community points

---

## 🔔 Notifications

### List Notifications
```
GET /notifications/
```

### Mark Notification as Read
```
POST /notifications/{id}/mark_read/
```

---

## Somali UI Requirements
- All user-facing text, labels, and error messages **must be in Somali**
- Use `name_somali`, `description_somali`, and other Somali fields for display
- Example labels: "Qoraal cusub", "Faallo", "Jecel", "Ka qaybgal"
- Campus = "Qabiil" or "Koox Mawduuc"
- Room = "Qayb"
- Post = "Qoraal"
- Comment = "Faallo"
- Like = "Jecel"

---

## Example Somali UI Labels
| English         | Somali           |
|-----------------|------------------|
| Post            | Qoraal           |
| Comment         | Faallo           |
| Like            | Jecel            |
| Join            | Ka qaybgal       |
| Leave           | Ka bax           |
| General         | Guud             |
| Study           | Waxbarasho       |
| Social          | Bulshada         |
| AI              | Hankhulka Macluumaadka |
| Fitness         | Jirka iyo Caafimaadka |

---

## Tips for Frontend Integration
- Always use Somali fields for display
- Use `/profiles/me/` for community stats and `/accounts/user_profile/` for XP/league
- Use the `subject_tag` to filter or categorize posts by tribe (campus)
- All endpoints are RESTful and return JSON
- Use JWT authentication for all requests

---

## For More Details
See the backend repo docs or ask the backend team for API schema or additional Somali translations. 