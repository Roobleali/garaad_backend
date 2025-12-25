# Community API Reference

## Base URL
```
https://api.garaad.org/api/community
```

## Authentication
All endpoints (except GET for posts) require JWT authentication:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

## Endpoints

### 1. List Posts in a Category
```http
GET /categories/{category_id}/posts/
```

**Response:**
```json
[
  {
    "id": 1,
    "category": "physics",
    "author": {
      "id": 112,
      "username": "abdishakuuralimohamed",
      "profile_picture": "/media/profile_pics/...",
      "first_name": "Abdishakuur",
      "last_name": "Ali"
    },
    "content": "Post content here",
    "created_at": "2025-12-25T20:00:00Z",
    "updated_at": "2025-12-25T20:00:00Z",
    "is_edited": false,
    "images": [],
    "replies": [
      {
        "id": 1,
        "author": {...},
        "content": "Reply content",
        "created_at": "2025-12-25T20:05:00Z",
        "updated_at": "2025-12-25T20:05:00Z",
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

### 2. Create a Post
```http
POST /categories/{category_id}/posts/
```

**Request Body:**
```json
{
  "content": "Your post content here"
}
```

**Response:** Full post object (same as above)

---

### 3. Update a Post
```http
PATCH /posts/{post_id}/
```

**Request Body:**
```json
{
  "content": "Updated content"
}
```

**Note:** Automatically marks `is_edited: true`

---

### 4. Delete a Post
```http
DELETE /posts/{post_id}/
```

**Response:** `204 No Content`

---

### 5. React to a Post
```http
POST /posts/{post_id}/react/
```

**Request Body:**
```json
{
  "type": "like"
}
```

**Valid types:** `"like"`, `"fire"`, `"insight"`

**Response:**
```json
{
  "action": "added",
  "type": "like"
}
```
or
```json
{
  "action": "removed",
  "type": "like"
}
```

**Note:** Toggles the reaction. If user already reacted with that type, it removes it.

---

### 6. Reply to a Post
```http
POST /posts/{post_id}/reply/
```

**Request Body:**
```json
{
  "content": "Your reply here"
}
```

**Response:**
```json
{
  "id": 2,
  "author": {...},
  "content": "Your reply here",
  "created_at": "2025-12-25T20:10:00Z",
  "updated_at": "2025-12-25T20:10:00Z",
  "is_edited": false
}
```

---

### 7. Update a Reply
```http
PATCH /replies/{reply_id}/
```

**Request Body:**
```json
{
  "content": "Updated reply"
}
```

---

### 8. Delete a Reply
```http
DELETE /replies/{reply_id}/
```

**Response:** `204 No Content`

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "This category does not have community features enabled."
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

---

## Example: Fetch and Display Posts

```javascript
async function loadPosts(categoryId, accessToken) {
  const response = await fetch(
    `https://api.garaad.org/api/community/categories/${categoryId}/posts/`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    }
  );
  
  if (!response.ok) {
    throw new Error('Failed to load posts');
  }
  
  const posts = await response.json();
  return posts;
}
```

## Example: Create a Post

```javascript
async function createPost(categoryId, content, accessToken) {
  const response = await fetch(
    `https://api.garaad.org/api/community/categories/${categoryId}/posts/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content })
    }
  );
  
  if (!response.ok) {
    throw new Error('Failed to create post');
  }
  
  const newPost = await response.json();
  return newPost;
}
```

## Example: React to a Post

```javascript
async function toggleReaction(postId, reactionType, accessToken) {
  const response = await fetch(
    `https://api.garaad.org/api/community/posts/${postId}/react/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ type: reactionType })
    }
  );
  
  if (!response.ok) {
    throw new Error('Failed to toggle reaction');
  }
  
  const result = await response.json();
  return result; // { action: "added" | "removed", type: "like" }
}
```
