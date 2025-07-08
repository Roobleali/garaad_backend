# Garaad Community System Documentation

## Overview

The Garaad Community System is a comprehensive social learning platform that organizes users into subject-based "Campuses" where they can interact, share knowledge, and build a tribal feel around learning. The system is designed with Somali language as the primary interface language to serve the target audience.

## Features

### 🏫 Campus System
- **Subject-based Communities**: Users join campuses based on their interests (Physics, Math, Crypto, etc.)
- **Somali Language Support**: All campuses have both English and Somali names/descriptions
- **Color-coded Themes**: Each campus has its own visual identity
- **Member Management**: Track membership counts and moderate access

### 🏠 Room System
- **Organized Discussions**: Each campus has multiple rooms for different types of conversations
- **Room Types**: General, Study, Q&A Help, Announcements, Social Chat
- **Private Rooms**: Option for invitation-only discussions
- **Member Limits**: Control room capacity

### 📝 Content System
- **Multi-format Posts**: Text, questions, announcements, polls, media
- **Threaded Comments**: Support for replies and nested conversations
- **Rich Media**: Support for images and video links
- **Content Moderation**: Approval workflow for posts and comments

### 👍 Engagement System
- **Like System**: Users can like posts and comments
- **View Tracking**: Monitor post popularity
- **Content Discovery**: Search and filter functionality

### 🎯 Gamification
- **Point System**: 
  - +10 points for creating a post
  - +5 points for creating a comment
  - +1 point for receiving a like
  - Bonus points for first post/comment in a campus
  - Special bonuses for helpful content
- **Badge Levels** (in Somali):
  - Garaad Dhalinyaro (Young Garaad) - 0+ points
  - Garaad Dhexe (Middle Garaad) - 500+ points
  - Garaad Sare (Senior Garaad) - 1000+ points
  - Garaad Weyne (Great Garaad) - 2000+ points
  - Garaad Hogaamiye (Leader Garaad) - 5000+ points

### 🔔 Notification System
- **Real-time Notifications**: Likes, comments, replies, mentions
- **Campus Updates**: New member notifications for moderators
- **Achievement Notifications**: Badge level ups and point awards
- **Approval Notifications**: Content moderation updates

### 🛡️ Moderation System
- **Campus Moderators**: Designated users with moderation powers
- **Content Approval**: Posts and comments can require approval
- **Admin Controls**: Full moderation capabilities for staff
- **Permission System**: Granular control over user actions

## Database Models

### Campus
- `name` / `name_somali`: Campus names in English and Somali
- `description` / `description_somali`: Descriptions in both languages
- `subject_tag`: Unique identifier for the subject area
- `icon`: Emoji or icon for visual representation
- `color_code`: Hex color for theming
- `member_count` / `post_count`: Statistics
- `is_active` / `requires_approval`: Settings

### Room
- `name` / `name_somali`: Room names in English and Somali
- `description` / `description_somali`: Room descriptions
- `campus`: Foreign key to parent campus
- `room_type`: Type of room (general, study, help, etc.)
- `is_private` / `max_members`: Privacy and capacity settings

### Post
- `title` / `content`: Post content
- `user` / `room`: Author and location
- `language`: Content language (default: Somali)
- `post_type`: Type of post (text, question, announcement, etc.)
- `image` / `video_url`: Optional media
- `is_pinned` / `is_featured` / `is_approved`: Moderation flags
- `likes_count` / `comments_count` / `views_count`: Engagement metrics

### Comment
- `content`: Comment text
- `user` / `post`: Author and target post
- `parent_comment`: For threaded replies
- `language`: Content language
- `is_approved`: Moderation status

### Like
- `user`: User who liked
- `post` / `comment`: Target content
- `content_type`: What was liked

### UserCommunityProfile
- `user`: Associated user account
- `community_points`: Total points earned
- `badge_level`: Current badge level
- `total_posts` / `total_comments`: Activity statistics
- `preferred_language`: User's language preference
- `email_notifications` / `mention_notifications`: Notification settings

## API Endpoints

All endpoints require authentication. Base URL: `/api/community/api/`

### Campus Endpoints

#### List Campuses
```
GET /campuses/
```
Returns list of all active campuses with membership status for authenticated user.

Query Parameters:
- `subject_tag`: Filter by subject
- `search`: Search in names and descriptions

#### Get Campus Details
```
GET /campuses/{slug}/
```
Returns detailed campus information including recent posts and user membership status.

#### Join Campus
```
POST /campuses/{slug}/join/
```
Join a campus. Creates membership record and updates member count.

#### Leave Campus
```
POST /campuses/{slug}/leave/
```
Leave a campus. Deactivates membership.

#### Get Campus Rooms
```
GET /campuses/{slug}/rooms/
```
List all rooms in a specific campus.

#### Get Campus Members
```
GET /campuses/{slug}/members/
```
List all active members of a campus.

### Room Endpoints

#### List Rooms
```
GET /rooms/
```
List all accessible rooms.

Query Parameters:
- `campus`: Filter by campus slug
- `room_type`: Filter by room type

#### Get Room Posts
```
GET /rooms/{id}/posts/
```
Get all posts in a specific room with pagination.

### Post Endpoints

#### List Posts
```
GET /posts/
```
List posts with filtering and search capabilities.

Query Parameters:
- `room`: Filter by room ID
- `campus`: Filter by campus slug
- `post_type`: Filter by post type
- `search`: Search in title and content

#### Create Post
```
POST /posts/
```
Create a new post in a room. Requires campus membership.

Request Body:
```json
{
  "title": "Post title",
  "content": "Post content",
  "room_id": 1,
  "language": "so",
  "post_type": "text",
  "image": null,
  "video_url": null
}
```

#### Get Post Details
```
GET /posts/{id}/
```
Get detailed post information including comments.

#### Like/Unlike Post
```
POST /posts/{id}/like/
```
Toggle like status for a post. Awards points to post owner.

#### Approve/Disapprove Post (Moderators)
```
POST /posts/{id}/approve/
POST /posts/{id}/disapprove/
```
Moderate post approval status.

### Comment Endpoints

#### List Comments
```
GET /comments/
```
List comments with filtering.

Query Parameters:
- `post`: Filter by post ID

#### Create Comment
```
POST /comments/
```
Create a new comment or reply.

Request Body:
```json
{
  "content": "Comment content",
  "post_id": "uuid-here",
  "parent_comment_id": "uuid-here", // Optional for replies
  "language": "so"
}
```

#### Like/Unlike Comment
```
POST /comments/{id}/like/
```
Toggle like status for a comment.

### Profile Endpoints

#### Get User Profile
```
GET /profiles/me/
```
Get current user's community profile with stats and preferences.

#### Get Leaderboard
```
GET /profiles/leaderboard/
```
Get top users by community points.

Query Parameters:
- `campus`: Campus-specific leaderboard

### Notification Endpoints

#### List Notifications
```
GET /notifications/
```
Get user's community notifications.

#### Mark Notification as Read
```
POST /notifications/{id}/mark_read/
```
Mark a specific notification as read.

#### Mark All Notifications as Read
```
POST /notifications/mark_all_read/
```
Mark all notifications as read.

## Permission System

### User Permissions
- **Authenticated Users**: Can view public content, join campuses
- **Campus Members**: Can create posts/comments, like content in their campuses
- **Content Owners**: Can edit/delete their own content
- **Campus Moderators**: Can moderate content in their campuses
- **Staff/Superusers**: Full moderation capabilities

### Content Visibility
- **Approved Content**: Visible to all campus members
- **Unapproved Content**: Visible only to author, moderators, and staff
- **Private Rooms**: Visible only to room members

## Gamification Integration

### Point Awarding
Points are automatically awarded for various actions:
- Creating posts: 10 points (+ 20 bonus for first post in campus)
- Creating comments: 5 points (+ 10 bonus for first comment)
- Receiving likes: 1 point per like
- Helpful comments (5+ likes): 15 bonus points

### Badge Progression
Badge levels are automatically updated based on total points:
- Progression is seamless and automatic
- Users receive notifications when they level up
- Badge names reflect Somali cultural context

### Leaderboards
- Global leaderboard across all campuses
- Campus-specific leaderboards
- Real-time updates as users earn points

## Installation & Setup

1. **Add to Django Settings**:
   ```python
   INSTALLED_APPS = [
       # ... other apps
       'community',
   ]
   ```

2. **Apply Migrations**:
   ```bash
   python manage.py migrate community
   ```

3. **Setup Initial Data**:
   ```bash
   python manage.py setup_community
   ```

4. **Include URLs**:
   ```python
   path('api/community/', include('community.urls')),
   ```

## Management Commands

### Setup Community
```bash
python manage.py setup_community [--reset]
```
Creates initial campus and room data. Use `--reset` to clear existing data.

## Language Support

### Primary Language: Somali
- All UI text and labels are in Somali
- Campus and room names have Somali translations
- Notification messages are in Somali
- Error messages are localized

### Content Languages
Users can post content in:
- Somali (default)
- English
- Arabic

## Moderation Features

### Content Approval
- Posts and comments can require approval before being visible
- Moderators can approve/disapprove content
- Authors are notified of moderation decisions

### Campus Moderation
- Campus moderators have elevated permissions within their campuses
- Can moderate posts, comments, and manage members
- Receive notifications about new members and activities

### Admin Controls
- Full administrative control through Django admin interface
- Bulk moderation actions
- Comprehensive reporting and statistics

## Technical Implementation

### Architecture
- Built on Django REST Framework
- PostgreSQL database with optimized indexes
- Signal-based automatic point awarding
- Real-time notification system

### Performance
- Database indexes on frequently queried fields
- Optimized querysets with select_related and prefetch_related
- Pagination for large datasets
- Efficient permission checking

### Security
- Authentication required for all actions
- Permission-based access control
- Input validation and sanitization
- CSRF protection

## Frontend Integration

### Authentication
All API calls must include authentication headers:
```javascript
headers: {
  'Authorization': 'Bearer <access_token>',
  'Content-Type': 'application/json'
}
```

### Example Usage
```javascript
// Join a campus
const joinCampus = async (campusSlug) => {
  const response = await fetch(`/api/community/api/campuses/${campusSlug}/join/`, {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + accessToken,
      'Content-Type': 'application/json'
    }
  });
  return response.json();
};

// Create a post
const createPost = async (postData) => {
  const response = await fetch('/api/community/api/posts/', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + accessToken,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(postData)
  });
  return response.json();
};
```

## Cultural Considerations

### Somali Language Integration
- Proper Somali translations for all UI elements
- Cultural context in badge names and terminology
- Support for Somali date/time formatting
- Right-to-left text support where needed

### Community Building
- Emphasis on collaborative learning
- Respect for traditional educational values
- Integration with Islamic educational principles
- Support for clan and regional identity through user profiles

## Future Enhancements

### Planned Features
- Real-time chat functionality
- Voice/video discussion rooms
- Advanced search with filtering
- Mobile app integration
- Offline content caching
- Advanced analytics dashboard

### Scalability
- Redis caching for improved performance
- WebSocket support for real-time features
- CDN integration for media files
- Horizontal scaling capabilities

## Support & Maintenance

### Monitoring
- Application logs for debugging
- Performance metrics tracking
- User activity analytics
- Error reporting and alerting

### Backup & Recovery
- Regular database backups
- Media file backup strategy
- Disaster recovery procedures
- Data migration tools

## Troubleshooting

### Common Issues
1. **Migration Conflicts**: Use the provided migration fix script
2. **Permission Errors**: Check user campus membership
3. **Point Calculation**: Verify signal handlers are working
4. **Notification Delivery**: Check notification preferences

### Debug Commands
```bash
# Check community data
python manage.py shell -c "from community.models import *; print(f'Campuses: {Campus.objects.count()}')"

# Reset community data
python manage.py setup_community --reset

# Check user permissions
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.first(); print(user.community_profile)"
```

---

**Built with ❤️ for the Somali learning community** 