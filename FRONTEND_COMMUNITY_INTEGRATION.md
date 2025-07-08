# Garaad Community System - Frontend Integration Guide

## 🚀 Quick Start

The Garaad Community System provides a complete social learning platform with campuses, posts, comments, and gamification. All API endpoints require JWT authentication and return data optimized for frontend consumption.

**Base URL**: `https://api.garaad.org/api/community/api/`  
**Authentication**: JWT Bearer token required for all endpoints

## 📱 Core Features for Frontend

### 🏫 Campus System
- Browse and search subject-based campuses
- Join/leave campuses with real-time member count updates
- Display campus-specific themes and icons
- Show user membership status

### 📝 Content Management  
- Create and display rich posts with media support
- Threaded comment system with replies
- Real-time like counts and user interaction states
- Content search and filtering

### 🎯 Gamification
- Real-time point tracking and badge progression
- Leaderboards (global and campus-specific)
- Achievement notifications and celebrations

### 🔔 Notifications
- Real-time notification feed
- Mark as read functionality
- Different notification types with appropriate icons

## 🔐 Authentication Setup

All API calls must include the JWT token in the Authorization header:

```javascript
const apiCall = async (endpoint, options = {}) => {
  const token = localStorage.getItem('access_token'); // or from your auth state
  
  return fetch(`https://api.garaad.org/api/community/api/${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
};
```

## 📊 API Endpoints & Usage

### 1. Campus Management

#### List All Campuses
```javascript
// GET /campuses/
const getCampuses = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await apiCall(`campuses/?${params}`);
  return response.json();
};

// Example response
{
  "results": [
    {
      "id": 1,
      "name": "Physics Campus",
      "name_somali": "Campus Fiisigis",
      "description": "Explore the fundamental laws of nature...",
      "description_somali": "Baadh sharciyada asaasiga ah...",
      "subject_tag": "physics",
      "subject_display_somali": "Fiisigis",
      "icon": "⚛️",
      "slug": "physics-campus",
      "color_code": "#3B82F6",
      "member_count": 245,
      "post_count": 123,
      "user_is_member": false
    }
  ]
}

// Usage with filters
const physicsCampuses = await getCampuses({ subject_tag: 'physics' });
const searchResults = await getCampuses({ search: 'math' });
```

#### Get Campus Details
```javascript
// GET /campuses/{slug}/
const getCampusDetails = async (slug) => {
  const response = await apiCall(`campuses/${slug}/`);
  return response.json();
};

// Example response includes recent_posts array and user_membership object
{
  "id": 1,
  "name_somali": "Campus Fiisigis",
  "user_membership": {
    "is_member": true,
    "is_moderator": false,
    "joined_at": "2025-07-08T10:30:00Z",
    "posts_count": 5,
    "reputation_score": 85
  },
  "recent_posts": [
    {
      "id": "uuid-here",
      "title": "Quantum Mechanics Basics",
      "user": "ahmed_student",
      "room": "Doodka Guud",
      "created_at": "2025-07-08T09:15:00Z",
      "likes_count": 12,
      "comments_count": 8
    }
  ]
}
```

#### Join/Leave Campus
```javascript
// POST /campuses/{slug}/join/
const joinCampus = async (slug) => {
  const response = await apiCall(`campuses/${slug}/join/`, {
    method: 'POST'
  });
  return response.json();
};

// POST /campuses/{slug}/leave/
const leaveCampus = async (slug) => {
  const response = await apiCall(`campuses/${slug}/leave/`, {
    method: 'POST'
  });
  return response.json();
};

// Success response (join)
{
  "message": "Si guul leh ayaad ugu biirtay Campus Fiisigis!"
}
```

#### Get Campus Rooms
```javascript
// GET /campuses/{slug}/rooms/
const getCampusRooms = async (slug) => {
  const response = await apiCall(`campuses/${slug}/rooms/`);
  return response.json();
};

// Example response
[
  {
    "id": 1,
    "name": "General Discussion",
    "name_somali": "Doodka Guud",
    "description_somali": "Doodyo guud oo ku saabsan mawduuca",
    "room_type": "general",
    "room_type_display": "Guud",
    "member_count": 145,
    "post_count": 89,
    "is_private": false
  }
]
```

### 2. Post Management

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
const searchPosts = await getPosts({ search: 'quantum' });

// Example response
{
  "count": 150,
  "next": "https://api.garaad.org/api/community/api/posts/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid-here",
      "title": "How does quantum entanglement work?",
      "content": "I'm trying to understand the concept...",
      "user": {
        "id": 1,
        "username": "ahmed_student",
        "profile_picture": "/media/profiles/ahmed.jpg"
      },
      "room": {
        "id": 1,
        "name_somali": "Su'aalaha iyo Jawaabaha",
        "campus": {
          "name_somali": "Campus Fiisigis",
          "color_code": "#3B82F6"
        }
      },
      "language": "en",
      "language_display": "English",
      "post_type": "question",
      "post_type_display": "Su'aal",
      "image": null,
      "video_url": null,
      "is_pinned": false,
      "is_featured": false,
      "likes_count": 15,
      "comments_count": 8,
      "views_count": 142,
      "created_at": "2025-07-08T08:30:00Z",
      "updated_at": "2025-07-08T08:30:00Z",
      "user_has_liked": false
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

// Example usage
const newPost = await createPost({
  title: "Quantum Physics Questions",
  content: "I have some questions about quantum mechanics...",
  room_id: 1,
  language: "so", // Somali
  post_type: "question",
  image: null, // or File object for image uploads
  video_url: "https://youtube.com/watch?v=..."
});

// Error handling for validation
try {
  const post = await createPost(postData);
} catch (error) {
  if (error.status === 400) {
    // Handle validation errors
    const errors = await error.json();
    console.log(errors); // { "room_id": ["Waa inaad ka mid tahay campus-ka..."] }
  }
}
```

#### Get Post Details
```javascript
// GET /posts/{id}/
const getPostDetails = async (postId) => {
  const response = await apiCall(`posts/${postId}/`);
  return response.json();
};

// Response includes comments array with nested replies
{
  "id": "uuid-here",
  "title": "Post title",
  // ... other post fields
  "comments": [
    {
      "id": "comment-uuid",
      "content": "Great question!",
      "user": { "username": "teacher_said" },
      "language_display": "Somali",
      "likes_count": 3,
      "created_at": "2025-07-08T09:00:00Z",
      "user_has_liked": false,
      "replies_count": 2,
      "replies": [
        {
          "id": "reply-uuid",
          "content": "I agree with this explanation",
          "user": { "username": "student_fatima" },
          "likes_count": 1,
          "created_at": "2025-07-08T09:15:00Z"
        }
      ]
    }
  ]
}
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

// Response
{
  "message": "Qoraalka waa la jeclaystay.", // or "Qoraalka waa laga qaaday jecelka."
  "liked": true, // or false if unliked
  "likes_count": 16
}
```

### 3. Comment Management

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

// Create top-level comment
const newComment = await createComment({
  content: "Waa su'aal fiican!",
  post_id: "post-uuid-here",
  language: "so"
});

// Create reply to comment
const reply = await createComment({
  content: "Waan ku raacsanahay!",
  post_id: "post-uuid-here", 
  parent_comment_id: "comment-uuid-here",
  language: "so"
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

### 4. User Profile & Gamification

#### Get User Profile
```javascript
// GET /profiles/me/
const getUserProfile = async () => {
  const response = await apiCall('profiles/me/');
  return response.json();
};

// Example response
{
  "user": {
    "id": 1,
    "username": "ahmed_student",
    "profile_picture": "/media/profiles/ahmed.jpg"
  },
  "community_points": 2450,
  "badge_level": "sare",
  "badge_level_display": "Garaad Sare",
  "total_posts": 25,
  "total_comments": 67,
  "total_likes_received": 189,
  "total_likes_given": 234,
  "preferred_language": "so",
  "email_notifications": true,
  "mention_notifications": true
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

// Example response
[
  {
    "user": {
      "id": 1,
      "username": "top_student",
      "profile_picture": "/media/profiles/student.jpg"
    },
    "community_points": 5240,
    "badge_level": "hogaamiye",
    "badge_level_display": "Garaad Hogaamiye",
    "total_posts": 89,
    "total_comments": 245
  }
]
```

### 5. Notifications

#### List Notifications
```javascript
// GET /notifications/
const getNotifications = async () => {
  const response = await apiCall('notifications/');
  return response.json();
};

// Example response
{
  "results": [
    {
      "id": 1,
      "sender": {
        "username": "fatima_teacher"
      },
      "notification_type": "post_like",
      "notification_type_display": "Qofka Soo Jeclaystay Qoraalkaaga",
      "title": "Qof ayaa jeclaystay qoraalkaaga",
      "message": "fatima_teacher ayaa jeclaystay qoraalkaaga \"Quantum Physics Basics\"",
      "is_read": false,
      "created_at": "2025-07-08T10:15:00Z",
      "post_title": "Quantum Physics Basics",
      "campus_name": "Campus Fiisigis"
    }
  ]
}
```

#### Mark Notifications as Read
```javascript
// POST /notifications/{id}/mark_read/
const markNotificationRead = async (notificationId) => {
  const response = await apiCall(`notifications/${notificationId}/mark_read/`, {
    method: 'POST'
  });
  return response.json();
};

// POST /notifications/mark_all_read/
const markAllNotificationsRead = async () => {
  const response = await apiCall('notifications/mark_all_read/', {
    method: 'POST'
  });
  return response.json();
};
```

## 🎨 UI Implementation Guidelines

### Campus Display
```jsx
// Campus Card Component
const CampusCard = ({ campus }) => (
  <div 
    className="campus-card"
    style={{ borderColor: campus.color_code }}
  >
    <div className="campus-header">
      <span className="campus-icon">{campus.icon}</span>
      <h3>{campus.name_somali}</h3>
    </div>
    <p>{campus.description_somali}</p>
    <div className="campus-stats">
      <span>{campus.member_count} xubnood</span>
      <span>{campus.post_count} qoraal</span>
    </div>
    {campus.user_is_member ? (
      <button onClick={() => viewCampus(campus.slug)}>
        Arag Campus-ka
      </button>
    ) : (
      <button onClick={() => joinCampus(campus.slug)}>
        Ku biir
      </button>
    )}
  </div>
);
```

### Post Display
```jsx
// Post Component
const PostItem = ({ post }) => (
  <div className="post-item">
    <div className="post-header">
      <img src={post.user.profile_picture} alt={post.user.username} />
      <div>
        <h4>{post.user.username}</h4>
        <span>{post.room.name_somali} • {formatDate(post.created_at)}</span>
      </div>
    </div>
    
    <h3>{post.title}</h3>
    <p>{post.content}</p>
    
    {post.image && <img src={post.image} alt="Post image" />}
    {post.video_url && <VideoEmbed url={post.video_url} />}
    
    <div className="post-actions">
      <button 
        className={post.user_has_liked ? 'liked' : ''}
        onClick={() => toggleLike(post.id)}
      >
        👍 {post.likes_count}
      </button>
      <button onClick={() => showComments(post.id)}>
        💬 {post.comments_count}
      </button>
      <button>👁️ {post.views_count}</button>
    </div>
  </div>
);
```

### Badge Display
```jsx
// Badge Component
const BadgeDisplay = ({ badgeLevel, points }) => {
  const badges = {
    'dhalinyaro': { emoji: '🌱', color: '#22C55E' },
    'dhexe': { emoji: '⭐', color: '#3B82F6' },
    'sare': { emoji: '🏆', color: '#F59E0B' },
    'weyne': { emoji: '💎', color: '#8B5CF6' },
    'hogaamiye': { emoji: '👑', color: '#EF4444' }
  };
  
  const badge = badges[badgeLevel];
  
  return (
    <div className="badge-display" style={{ borderColor: badge.color }}>
      <span className="badge-emoji">{badge.emoji}</span>
      <div>
        <div className="badge-level">{getBadgeDisplayName(badgeLevel)}</div>
        <div className="badge-points">{points} dhibco</div>
      </div>
    </div>
  );
};
```

### Notification Component
```jsx
// Notification Item
const NotificationItem = ({ notification }) => {
  const icons = {
    'post_like': '👍',
    'comment_like': '💬',
    'post_comment': '💭',
    'comment_reply': '↩️',
    'mention': '@',
    'new_campus_member': '👋'
  };
  
  return (
    <div 
      className={`notification ${!notification.is_read ? 'unread' : ''}`}
      onClick={() => markAsRead(notification.id)}
    >
      <span className="notification-icon">
        {icons[notification.notification_type]}
      </span>
      <div>
        <h4>{notification.title}</h4>
        <p>{notification.message}</p>
        <span className="notification-time">
          {formatTimeAgo(notification.created_at)}
        </span>
      </div>
    </div>
  );
};
```

## 📱 State Management Recommendations

### Redux Toolkit Example
```javascript
// communitySlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const fetchCampuses = createAsyncThunk(
  'community/fetchCampuses',
  async (filters = {}) => {
    const response = await getCampuses(filters);
    return response;
  }
);

const communitySlice = createSlice({
  name: 'community',
  initialState: {
    campuses: [],
    posts: [],
    userProfile: null,
    notifications: [],
    loading: false,
    error: null
  },
  reducers: {
    updatePostLike: (state, action) => {
      const { postId, liked, likesCount } = action.payload;
      const post = state.posts.find(p => p.id === postId);
      if (post) {
        post.user_has_liked = liked;
        post.likes_count = likesCount;
      }
    },
    markNotificationRead: (state, action) => {
      const notification = state.notifications.find(n => n.id === action.payload);
      if (notification) {
        notification.is_read = true;
      }
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCampuses.fulfilled, (state, action) => {
        state.campuses = action.payload.results;
        state.loading = false;
      })
      .addCase(fetchCampuses.pending, (state) => {
        state.loading = true;
      });
  }
});
```

### React Query Example
```javascript
// hooks/useCommunity.js
import { useQuery, useMutation, useQueryClient } from 'react-query';

export const useCampuses = (filters = {}) => {
  return useQuery(['campuses', filters], () => getCampuses(filters));
};

export const usePosts = (filters = {}) => {
  return useQuery(['posts', filters], () => getPosts(filters));
};

export const useJoinCampus = () => {
  const queryClient = useQueryClient();
  
  return useMutation(joinCampus, {
    onSuccess: () => {
      queryClient.invalidateQueries(['campuses']);
      queryClient.invalidateQueries(['user-profile']);
    }
  });
};

export const useTogglePostLike = () => {
  const queryClient = useQueryClient();
  
  return useMutation(togglePostLike, {
    onSuccess: (data, postId) => {
      queryClient.setQueryData(['posts'], (oldData) => {
        return oldData.map(post => 
          post.id === postId 
            ? { ...post, user_has_liked: data.liked, likes_count: data.likes_count }
            : post
        );
      });
    }
  });
};
```

## 🌍 Internationalization

### Language Support
All API responses include Somali translations. Use these patterns:

```javascript
// Display names with fallback
const getDisplayName = (item) => {
  return item.name_somali || item.name;
};

// Language-specific content
const getLocalizedContent = (item, userLanguage = 'so') => {
  if (userLanguage === 'so') {
    return {
      title: item.title,
      description: item.description_somali || item.description
    };
  }
  return {
    title: item.title,
    description: item.description
  };
};
```

### Common Somali UI Text
```javascript
const somaliText = {
  // Navigation
  campuses: 'Campusyada',
  posts: 'Qoraallada',
  notifications: 'Ogeysiisyada',
  profile: 'Waybaha',
  
  // Actions
  join: 'Ku biir',
  leave: 'Ka bax',
  like: 'Jeclaasho',
  comment: 'Ka faallee',
  share: 'La wadaag',
  
  // Status
  member: 'Xubin',
  moderator: 'Maamule',
  online: 'Online',
  offline: 'Offline',
  
  // Time
  now: 'hadda',
  minute: 'daqiiqad',
  hour: 'saacad',
  day: 'maalin',
  week: 'usbuuc',
  
  // Content types
  question: 'Su\'aal',
  announcement: 'Ogeysiis',
  discussion: 'Dood',
  poll: 'Codbixin'
};
```

## 🚦 Error Handling

### API Error Responses
```javascript
// Standard error handling
const handleApiError = async (response) => {
  if (!response.ok) {
    const error = await response.json();
    
    switch (response.status) {
      case 400:
        // Validation errors
        return { type: 'validation', errors: error };
      case 401:
        // Authentication required
        return { type: 'auth', message: 'Waa inaad galato si aad u isticmaasho' };
      case 403:
        // Permission denied
        return { type: 'permission', message: 'Ma lehe ogolaansho' };
      case 404:
        // Not found
        return { type: 'notFound', message: 'Lama helin' };
      default:
        return { type: 'unknown', message: 'Cillad ayaa dhacday' };
    }
  }
  return null;
};

// Usage in components
const handleSubmit = async (formData) => {
  try {
    const response = await createPost(formData);
    // Success handling
  } catch (error) {
    const apiError = await handleApiError(error);
    if (apiError?.type === 'validation') {
      setErrors(apiError.errors);
    } else {
      showToast(apiError?.message || 'Cillad ayaa dhacday');
    }
  }
};
```

## 🔄 Real-time Updates

### WebSocket Integration (Future)
```javascript
// WebSocket setup for real-time features
const useRealtimeUpdates = () => {
  useEffect(() => {
    const ws = new WebSocket('wss://api.garaad.org/ws/community/');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'new_post':
          // Update posts list
          break;
        case 'new_comment':
          // Update comments
          break;
        case 'like_update':
          // Update like counts
          break;
        case 'notification':
          // Show new notification
          break;
      }
    };
    
    return () => ws.close();
  }, []);
};
```

### Polling for Updates
```javascript
// Polling for notifications
const useNotificationPolling = () => {
  const { data: notifications } = useQuery(
    'notifications',
    getNotifications,
    {
      refetchInterval: 30000, // 30 seconds
      refetchIntervalInBackground: false
    }
  );
  
  return notifications;
};
```

## 📊 Performance Optimization

### Pagination Implementation
```javascript
// Infinite scroll for posts
const useInfinitePosts = (filters) => {
  const [posts, setPosts] = useState([]);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  
  const loadMore = async () => {
    if (loading || !hasMore) return;
    
    setLoading(true);
    try {
      const response = await getPosts({ ...filters, page: currentPage + 1 });
      setPosts(prev => [...prev, ...response.results]);
      setHasMore(!!response.next);
      setCurrentPage(prev => prev + 1);
    } finally {
      setLoading(false);
    }
  };
  
  return { posts, loadMore, hasMore, loading };
};
```

### Image Optimization
```javascript
// Lazy loading images
const LazyImage = ({ src, alt, className }) => {
  const [loaded, setLoaded] = useState(false);
  const imgRef = useRef();
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setLoaded(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );
    
    if (imgRef.current) {
      observer.observe(imgRef.current);
    }
    
    return () => observer.disconnect();
  }, []);
  
  return (
    <div ref={imgRef} className={className}>
      {loaded && <img src={src} alt={alt} />}
    </div>
  );
};
```

## 🧪 Testing

### API Testing Examples
```javascript
// Jest + React Testing Library
import { renderHook, waitFor } from '@testing-library/react';
import { useCampuses } from '../hooks/useCommunity';

test('should fetch campuses', async () => {
  const { result } = renderHook(() => useCampuses());
  
  await waitFor(() => {
    expect(result.current.data).toBeDefined();
    expect(result.current.data.results).toHaveLength(10);
  });
});

// Component testing
test('should display campus in Somali', () => {
  const campus = {
    name_somali: 'Campus Fiisigis',
    description_somali: 'Baadh sharciyada asaasiga ah'
  };
  
  render(<CampusCard campus={campus} />);
  
  expect(screen.getByText('Campus Fiisigis')).toBeInTheDocument();
  expect(screen.getByText('Baadh sharciyada asaasiga ah')).toBeInTheDocument();
});
```

## 📋 Implementation Checklist

### Phase 1: Basic Features
- [ ] Authentication integration
- [ ] Campus listing and joining
- [ ] Post creation and display
- [ ] Comment system
- [ ] Like functionality
- [ ] User profile display

### Phase 2: Enhanced Features  
- [ ] Search and filtering
- [ ] Image upload handling
- [ ] Notification system
- [ ] Leaderboards
- [ ] Badge display
- [ ] Responsive design

### Phase 3: Advanced Features
- [ ] Real-time updates
- [ ] Advanced moderation UI
- [ ] Analytics dashboard
- [ ] Mobile app integration
- [ ] Offline support
- [ ] Push notifications

## 🆘 Support & Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure JWT token is included in all requests
   - Check token expiration and refresh logic

2. **Permission Errors**
   - Verify user is member of campus before posting
   - Check if user has required permissions for actions

3. **Image Upload Issues**
   - Use FormData for file uploads
   - Check file size and format restrictions

4. **Somali Text Display**
   - Ensure proper UTF-8 encoding
   - Test with various Somali characters

### Debug Tools
```javascript
// Debug API calls
const debugApiCall = (endpoint, options) => {
  console.log(`API Call: ${endpoint}`, options);
  return apiCall(endpoint, options).then(response => {
    console.log(`API Response: ${endpoint}`, response);
    return response;
  });
};
```

---

**Happy coding! 🚀 Ready to build an amazing community experience for Somali learners!** 