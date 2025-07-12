# Garaad Community System - Frontend Integration Guide

## 🚀 Quick Start

**Base URL**: `https://api.garaad.org/api/community/`  
**Authentication**: JWT Bearer token required for all endpoints

### Authentication Setup
```javascript
const API_BASE = 'https://api.garaad.org/api/community/';

const apiCall = async (endpoint, options = {}) => {
  const token = localStorage.getItem('access_token'); // or from your auth state
  
  return fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
};
```

---

## 📱 Core Features

### 🏫 Campus System (Tribes)
- Browse subject-based communities (Physics, Math, Crypto, AI, Fitness, etc.)
- Join/leave campuses with real-time member count
- Campus-specific themes and icons
- User membership status display

### 📝 Content Management
- Create rich posts with media support
- Threaded comment system with replies
- Real-time like counts and user interactions
- Content search and filtering

### 🎯 Gamification
- Real-time point tracking and badge progression
- Leaderboards (global and campus-specific)
- Achievement notifications

### 🔔 Notifications
- Real-time notification feed
- Mark as read functionality
- Different notification types with icons

---

## 🔐 API Endpoints

### 1. Campus Management

#### List All Campuses
```javascript
// GET /campuses/
const getCampuses = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await apiCall(`campuses/?${params}`);
  return response.json();
};

// Usage examples
const allCampuses = await getCampuses();
const physicsCampuses = await getCampuses({ subject_tag: 'physics' });
const searchResults = await getCampuses({ search: 'quantum' });
```

**Response Example:**
```json
{
  "count": 6,
  "next": null,
  "previous": null,
  "results": [
    {
      "slug": "physics-campus",
      "name": "Physics",
      "name_somali": "Fiisikis",
      "description": "Advanced physics discussions",
      "description_somali": "Doodyo fiisikis oo dhammeystiran",
      "subject_tag": "physics",
      "subject_display": "Physics",
      "subject_display_somali": "Fiisikis",
      "member_count": 145,
      "post_count": 89,
      "is_member": true,
      "member_since": "2024-01-15T10:30:00Z",
      "user_role": "member"
    }
  ]
}
```

#### Get Campus Details
```javascript
// GET /campuses/{slug}/
const getCampusDetails = async (slug) => {
  const response = await apiCall(`campuses/${slug}/`);
  return response.json();
};
```

#### Join Campus
```javascript
// POST /campuses/{slug}/join/
const joinCampus = async (slug) => {
  const response = await apiCall(`campuses/${slug}/join/`, {
    method: 'POST'
  });
  return response.json();
};
```

#### Leave Campus
```javascript
// POST /campuses/{slug}/leave/
const leaveCampus = async (slug) => {
  const response = await apiCall(`campuses/${slug}/leave/`, {
    method: 'POST'
  });
  return response.json();
};
```

### 2. Room Management

#### List Rooms in Campus
```javascript
// GET /rooms/?campus={slug}
const getCampusRooms = async (campusSlug) => {
  const response = await apiCall(`rooms/?campus=${campusSlug}`);
  return response.json();
};
```

**Response Example:**
```json
[
  {
    "id": 1,
    "name": "General Discussion",
    "name_somali": "Doodka Guud",
    "description": "General discussions about the subject",
    "description_somali": "Doodyo guud oo ku saabsan mawduuca",
    "room_type": "general",
    "room_type_display": "General",
    "room_type_display_somali": "Guud",
    "member_count": 145,
    "post_count": 89,
    "is_private": false,
    "campus": {
      "slug": "physics-campus",
      "name": "Physics"
    }
  }
]
```

#### Get Room Posts
```javascript
// GET /rooms/{id}/posts/
const getRoomPosts = async (roomId) => {
  const response = await apiCall(`rooms/${roomId}/posts/`);
  return response.json();
};
```

### 3. Post Management

#### List Posts
```javascript
// GET /posts/
const getPosts = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await apiCall(`posts/?${params}`);
  return response.json();
};

// Filtering examples
const roomPosts = await getPosts({ room: roomId });
const campusPosts = await getPosts({ campus: 'physics-campus' });
const questionPosts = await getPosts({ post_type: 'question' });
const searchPosts = await getPosts({ search: 'quantum mechanics' });
```

**Response Example:**
```json
{
  "count": 25,
  "next": "http://api.garaad.org/api/community/posts/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid-here",
      "title": "Quantum Mechanics Question",
      "content": "Can someone explain the double-slit experiment?",
      "user": {
        "id": 1,
        "username": "physics_student",
        "first_name": "Ahmed",
        "last_name": "Hassan",
        "profile_picture": "https://api.garaad.org/api/media/profile_pics/ahmed.jpg"
      },
      "room": {
        "id": 1,
        "name": "General Discussion",
        "name_somali": "Doodka Guud"
      },
      "language": "en",
      "language_display": "English",
      "post_type": "question",
      "post_type_display": "Question",
      "image": null,
      "video_url": null,
      "is_pinned": false,
      "is_featured": false,
      "likes_count": 5,
      "comments_count": 3,
      "views_count": 45,
      "user_has_liked": false,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Create Post
```javascript
// POST /posts/
const createPost = async (postData) => {
  const response = await apiCall('posts/', {
    method: 'POST',
    body: JSON.stringify(postData)
  });
  return response.json();
};

// Usage example
const newPost = await createPost({
  title: "My Physics Question",
  content: "I need help understanding quantum mechanics...",
  room_id: 1,
  language: "en",
  post_type: "question"
});
```

#### Get Post Details
```javascript
// GET /posts/{id}/
const getPostDetails = async (postId) => {
  const response = await apiCall(`posts/${postId}/`);
  return response.json();
};
```

#### Like/Unlike Post
```javascript
// POST /posts/{id}/like/
const togglePostLike = async (postId) => {
  const response = await apiCall(`posts/${postId}/like/`, {
    method: 'POST'
  });
  return response.json();
};
```

### 4. Comment Management

#### List Comments
```javascript
// GET /comments/?post={post_id}
const getComments = async (postId) => {
  const response = await apiCall(`comments/?post=${postId}`);
  return response.json();
};
```

**Response Example:**
```json
[
  {
    "id": "uuid-here",
    "content": "Great explanation! This really helped me understand.",
    "user": {
      "id": 2,
      "username": "helpful_user",
      "first_name": "Fatima",
      "last_name": "Ali"
    },
    "post": "post-uuid",
    "parent_comment": null,
    "language": "en",
    "language_display": "English",
    "likes_count": 2,
    "user_has_liked": false,
    "created_at": "2024-01-15T11:00:00Z",
    "replies": [
      {
        "id": "reply-uuid",
        "content": "I agree with this explanation!",
        "user": {
          "id": 3,
          "username": "another_user",
          "first_name": "Omar",
          "last_name": "Mohamed"
        },
        "parent_comment": "uuid-here",
        "likes_count": 1,
        "user_has_liked": false,
        "created_at": "2024-01-15T11:30:00Z"
      }
    ]
  }
]
```

#### Create Comment
```javascript
// POST /comments/
const createComment = async (commentData) => {
  const response = await apiCall('comments/', {
    method: 'POST',
    body: JSON.stringify(commentData)
  });
  return response.json();
};

// Usage examples
const newComment = await createComment({
  content: "This is a great question!",
  post_id: "post-uuid",
  language: "en"
});

const reply = await createComment({
  content: "I agree with the above comment",
  post_id: "post-uuid",
  parent_comment_id: "parent-comment-uuid",
  language: "en"
});
```

#### Like/Unlike Comment
```javascript
// POST /comments/{id}/like/
const toggleCommentLike = async (commentId) => {
  const response = await apiCall(`comments/${commentId}/like/`, {
    method: 'POST'
  });
  return response.json();
};
```

### 5. User Profile & Gamification

#### Get User Profile
```javascript
// GET /profiles/me/
const getUserProfile = async () => {
  const response = await apiCall('profiles/me/');
  return response.json();
};
```

**Response Example:**
```json
{
  "user": {
    "id": 1,
    "username": "physics_student",
    "first_name": "Ahmed",
    "last_name": "Hassan",
    "email": "ahmed@example.com",
    "profile_picture": "https://api.garaad.org/api/media/profile_pics/ahmed.jpg"
  },
  "community_points": 1250,
  "badge_level": "expert",
  "badge_level_display": "Expert",
  "badge_level_display_somali": "Khabiir",
  "total_posts": 15,
  "total_comments": 45,
  "preferred_language": "en",
  "email_notifications": true,
  "mention_notifications": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Get Leaderboard
```javascript
// GET /profiles/leaderboard/
const getLeaderboard = async (campusSlug = null) => {
  const params = campusSlug ? `?campus=${campusSlug}` : '';
  const response = await apiCall(`profiles/leaderboard/${params}`);
  return response.json();
};

// Usage examples
const globalLeaderboard = await getLeaderboard();
const campusLeaderboard = await getLeaderboard('physics-campus');
```

### 6. Notifications

#### List Notifications
```javascript
// GET /notifications/
const getNotifications = async () => {
  const response = await apiCall('notifications/');
  return response.json();
};
```

**Response Example:**
```json
[
  {
    "id": "uuid-here",
    "notification_type": "like",
    "notification_type_display": "Like",
    "notification_type_display_somali": "Jecel",
    "title": "Someone liked your post",
    "title_somali": "Qof baa jecel qoraalkaaga",
    "message": "Fatima Ali liked your post 'Quantum Mechanics Question'",
    "message_somali": "Fatima Ali waxay jecel qoraalkaaga 'Su'aal Fiisikis'",
    "is_read": false,
    "created_at": "2024-01-15T10:30:00Z",
    "related_post": {
      "id": "post-uuid",
      "title": "Quantum Mechanics Question"
    }
  }
]
```

#### Mark Notification as Read
```javascript
// POST /notifications/{id}/mark_read/
const markNotificationRead = async (notificationId) => {
  const response = await apiCall(`notifications/${notificationId}/mark_read/`, {
    method: 'POST'
  });
  return response.json();
};
```

#### Mark All Notifications as Read
```javascript
// POST /notifications/mark_all_read/
const markAllNotificationsRead = async () => {
  const response = await apiCall('notifications/mark_all_read/', {
    method: 'POST'
  });
  return response.json();
};
```

---

## 🎨 UI/UX Guidelines

### Language Support
- **Primary UI Language**: Somali (use `*_somali` fields)
- **Content Languages**: Somali, English, Arabic
- **Display Language**: Use `language_display` fields for proper labels

### Error Handling
```javascript
const handleApiError = (error) => {
  if (error.status === 401) {
    // Redirect to login
    router.push('/login');
  } else if (error.status === 403) {
    // Show permission error
    showError('Waxaad u baahan tahay inaad ka mid tahay campus-ka');
  } else if (error.status === 404) {
    // Show not found error
    showError('Wax la ma helin');
  } else {
    // Show generic error
    showError('Khalad ayaa dhacay. Fadlan isku day mar kale.');
  }
};
```

### Loading States
```javascript
const [loading, setLoading] = useState(false);
const [data, setData] = useState(null);

const fetchData = async () => {
  setLoading(true);
  try {
    const result = await apiCall('endpoint/');
    setData(result);
  } catch (error) {
    handleApiError(error);
  } finally {
    setLoading(false);
  }
};
```

### Real-time Updates
For real-time features, consider implementing WebSocket connections or polling:
```javascript
// Poll for new notifications every 30 seconds
useEffect(() => {
  const interval = setInterval(() => {
    fetchNotifications();
  }, 30000);
  
  return () => clearInterval(interval);
}, []);
```

---

## 📱 React Component Examples

### Campus List Component
```jsx
import React, { useState, useEffect } from 'react';

const CampusList = () => {
  const [campuses, setCampuses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCampuses();
  }, []);

  const fetchCampuses = async () => {
    try {
      const data = await getCampuses();
      setCampuses(data.results);
    } catch (error) {
      console.error('Error fetching campuses:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleJoinCampus = async (slug) => {
    try {
      await joinCampus(slug);
      fetchCampuses(); // Refresh list
    } catch (error) {
      console.error('Error joining campus:', error);
    }
  };

  if (loading) return <div>Loading campuses...</div>;

  return (
    <div className="campus-list">
      {campuses.map(campus => (
        <div key={campus.slug} className="campus-card">
          <h3>{campus.name_somali}</h3>
          <p>{campus.description_somali}</p>
          <div className="campus-stats">
            <span>{campus.member_count} members</span>
            <span>{campus.post_count} posts</span>
          </div>
          {!campus.is_member ? (
            <button onClick={() => handleJoinCampus(campus.slug)}>
              Join Campus
            </button>
          ) : (
            <span className="member-badge">Member</span>
          )}
        </div>
      ))}
    </div>
  );
};
```

### Post Creation Component
```jsx
import React, { useState } from 'react';

const CreatePost = ({ roomId, onPostCreated }) => {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    post_type: 'text',
    language: 'so'
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const newPost = await createPost({
        ...formData,
        room_id: roomId
      });
      
      onPostCreated(newPost);
      setFormData({ title: '', content: '', post_type: 'text', language: 'so' });
    } catch (error) {
      console.error('Error creating post:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="create-post-form">
      <input
        type="text"
        placeholder="Cinwaan (Title)"
        value={formData.title}
        onChange={(e) => setFormData({...formData, title: e.target.value})}
        required
      />
      
      <textarea
        placeholder="Qoraal (Content)"
        value={formData.content}
        onChange={(e) => setFormData({...formData, content: e.target.value})}
        required
      />
      
      <select
        value={formData.post_type}
        onChange={(e) => setFormData({...formData, post_type: e.target.value})}
      >
        <option value="text">Qoraal</option>
        <option value="question">Su'aal</option>
        <option value="announcement">Ogeysiis</option>
        <option value="poll">Codbixin</option>
        <option value="media">Sawir/Muuqaal</option>
      </select>
      
      <button type="submit">Qor Qoraal</button>
    </form>
  );
};
```

---

## 🚀 Deployment Checklist

### Environment Variables
```bash
# Required for production
REACT_APP_API_BASE_URL=https://api.garaad.org/api/community/
REACT_APP_AUTH_TOKEN_KEY=access_token
```

### Build Configuration
```javascript
// vite.config.js or webpack.config.js
export default {
  define: {
    'process.env.REACT_APP_API_BASE_URL': JSON.stringify(process.env.REACT_APP_API_BASE_URL)
  }
};
```

### CORS Configuration
Ensure your frontend domain is allowed in Django CORS settings:
```python
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
    "http://localhost:3000",  # For development
]
```

---

## 📞 Support

For technical support or questions about the API:
- **Email**: dev@garaad.org
- **Documentation**: Check the API documentation for detailed endpoint information
- **Testing**: Use the provided examples to test endpoints before implementation

---

## 🔄 Updates

This guide will be updated as new features are added to the community system. Check the repository for the latest version.

**Last Updated**: January 2024  
**Version**: 1.0.0 