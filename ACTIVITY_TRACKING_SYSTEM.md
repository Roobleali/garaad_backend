# Activity Tracking System

## Overview

The activity tracking system has been completely redesigned to properly track user activity like modern learning platforms (Duolingo, Brilliant.org). The system now tracks:

1. **General site activity** - Any authenticated user request
2. **Session activity** - Token refreshes and login sessions
3. **Learning activity** - Specific learning actions (problem solving, lesson completion)
4. **Daily activity records** - Comprehensive daily activity tracking

## Problem Solved

### Previous System Issues
- Only updated `last_activity_date` when users performed specific learning actions
- Users who logged in and browsed without solving problems would get incorrect streak breaks
- No tracking of general site activity or session activity
- Poor UX due to incorrect inactivity notifications

### New System Benefits
- **Comprehensive tracking**: All authenticated user activity is tracked
- **Session-aware**: Token refreshes and login sessions update activity
- **Learning-specific**: Special tracking for actual learning actions
- **Accurate streaks**: Streaks are maintained even for users who just browse
- **Better UX**: No false inactivity notifications

## System Components

### 1. Middleware Layer

#### UserActivityMiddleware
- **Purpose**: Tracks general user activity on every authenticated request
- **Updates**: `Streak.last_activity_date` and `DailyActivity` records
- **Logic**: 
  - Updates streak on consecutive days
  - Resets streak if more than 1 day gap
  - Creates daily activity records
  - Marks activity as 'partial' for general browsing

#### SessionActivityMiddleware
- **Purpose**: Tracks session-based activity and token refreshes
- **Updates**: `User.last_login` and streak records on token refresh
- **Logic**:
  - Updates `last_login` every hour
  - Handles token refresh activity tracking
  - Ensures session activity is recorded

#### LearningActivityMiddleware
- **Purpose**: Tracks specific learning activities
- **Updates**: Learning-specific activity records
- **Logic**:
  - Identifies learning endpoints
  - Updates activity status based on learning actions
  - Tracks lesson views, problem views, course views

### 2. API Endpoints

#### Manual Activity Update
```http
POST /api/activity/update/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "message": "Activity updated successfully",
  "streak": {
    "current_streak": 5,
    "max_streak": 10,
    "last_activity_date": "2025-01-29"
  },
  "activity_date": "2025-01-29"
}
```

### 3. Data Models

#### Streak Model Updates
```python
class Streak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    last_activity_date = models.DateField(null=True, blank=True)  # Key tracking field
    current_streak = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)
    # ... other fields
```

#### DailyActivity Model
```python
class DailyActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_activities')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=ACTIVITY_STATUS, default='none')
    problems_solved = models.IntegerField(default=0)
    lesson_ids = models.JSONField(default=list)
```

## Activity Tracking Logic

### 1. General Activity Tracking
```python
# Every authenticated request triggers this
def _update_user_activity(self, user):
    today = timezone.now().date()
    
    # Update streak record
    streak, created = Streak.objects.get_or_create(user=user)
    
    if not streak.last_activity_date or streak.last_activity_date != today:
        # Check consecutive days
        if streak.last_activity_date:
            days_diff = (today - streak.last_activity_date).days
            
            if days_diff == 1:
                # Consecutive day - increment streak
                streak.current_streak += 1
            elif days_diff > 1:
                # Streak broken - reset to 1
                streak.current_streak = 1
        
        streak.last_activity_date = today
        streak.save()
    
    # Create daily activity record
    activity, created = DailyActivity.objects.get_or_create(
        user=user, date=today,
        defaults={'status': 'partial', 'problems_solved': 0, 'lesson_ids': []}
    )
```

### 2. Session Activity Tracking
```python
# Token refresh triggers this
def _handle_token_refresh(self, user):
    today = timezone.now().date()
    
    streak = Streak.objects.get(user=user)
    if not streak.last_activity_date or streak.last_activity_date != today:
        # Update streak logic
        # Create daily activity record
```

### 3. Learning Activity Tracking
```python
# Learning endpoints trigger this
def _track_learning_activity(self, request):
    path = request.path
    
    learning_endpoints = {
        '/api/streak/': 'streak_update',
        '/api/lms/lessons/': 'lesson_view',
        '/api/lms/problems/': 'problem_view',
        '/api/lms/courses/': 'course_view',
    }
    
    for endpoint, activity_type in learning_endpoints.items():
        if path.startswith(endpoint):
            self._update_learning_activity(request.user, activity_type)
```

## Activity Status Levels

### DailyActivity Status
- **`none`**: No activity recorded
- **`partial`**: User was active but didn't complete learning goals
- **`complete`**: User completed learning goals (3+ problems solved)

### Streak Logic
- **Consecutive days**: Increment streak
- **Same day**: No change to streak
- **1 day gap**: Increment streak
- **2+ day gap**: Reset streak to 1

## Frontend Integration

### 1. Periodic Activity Updates
```javascript
// Call this every 5 minutes while user is active
setInterval(() => {
  fetch('/api/activity/update/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
}, 5 * 60 * 1000);
```

### 2. User Interaction Tracking
```javascript
// Track user interactions
document.addEventListener('click', () => {
  // Update activity on user interaction
  updateActivity();
});

document.addEventListener('scroll', () => {
  // Update activity on scroll
  updateActivity();
});
```

### 3. Token Refresh Handling
```javascript
// When token is refreshed, update activity
const refreshToken = async () => {
  const response = await fetch('/api/auth/refresh/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${refreshToken}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (response.ok) {
    // Activity is automatically updated by middleware
    const data = await response.json();
    // Update tokens
  }
};
```

## Testing

### Management Command
```bash
# Test activity tracking for all users
python manage.py test_activity_tracking

# Test specific user
python manage.py test_activity_tracking --user-id 123

# Simulate 14 days of activity
python manage.py test_activity_tracking --simulate-days 14
```

### Manual Testing
```bash
# Test activity update endpoint
curl -X POST http://localhost:8000/api/activity/update/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

## Configuration

### Middleware Order
The middleware is configured in `settings.py`:
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Custom activity tracking middleware
    'core.middleware.UserActivityMiddleware',
    'core.middleware.SessionActivityMiddleware',
    'core.middleware.LearningActivityMiddleware',
]
```

## Performance Considerations

### 1. Database Optimization
- Uses `get_or_create()` to avoid duplicate queries
- Updates only necessary fields with `update_fields`
- Indexes on frequently queried fields

### 2. Caching
- Activity updates are lightweight
- No heavy computations in middleware
- Efficient date comparisons

### 3. Rate Limiting
- Middleware only runs for authenticated users
- Excludes static files and admin paths
- Minimal database writes per request

## Monitoring and Analytics

### 1. Activity Metrics
- Daily active users
- User engagement levels
- Streak distribution
- Learning completion rates

### 2. Notification Triggers
- Streak breaks (after 2+ days of inactivity)
- Daily reminders (if no activity today)
- Milestone achievements (7, 30, 100 days)

### 3. Admin Dashboard
- Real-time user activity monitoring
- Engagement analytics
- Streak and notification reports

## Migration from Old System

### 1. Data Migration
- Existing streak records are preserved
- Daily activity records are created for existing users
- No data loss during migration

### 2. Backward Compatibility
- All existing API endpoints continue to work
- Old activity tracking still functions
- Gradual migration to new system

### 3. Testing Strategy
- Test with existing users
- Verify streak calculations
- Check notification accuracy

## Best Practices

### 1. Frontend Implementation
- Call activity update endpoint periodically
- Track user interactions
- Handle token refresh properly

### 2. Backend Monitoring
- Monitor middleware performance
- Track database query efficiency
- Alert on unusual activity patterns

### 3. User Experience
- Don't interrupt user flow
- Provide immediate feedback
- Show streak progress clearly

## Troubleshooting

### Common Issues

#### 1. Streaks Not Updating
- Check if middleware is enabled
- Verify user authentication
- Check database connections

#### 2. Incorrect Activity Dates
- Verify timezone settings
- Check date calculation logic
- Review middleware order

#### 3. Performance Issues
- Monitor database queries
- Check middleware efficiency
- Review caching strategy

### Debug Commands
```bash
# Check user activity
python manage.py test_activity_tracking --user-id USER_ID

# Check middleware
python manage.py shell
>>> from core.middleware import UserActivityMiddleware
>>> middleware = UserActivityMiddleware(lambda req: None)
>>> user = User.objects.get(id=USER_ID)
>>> middleware._update_user_activity(user)
```

## Future Enhancements

### 1. Advanced Analytics
- Learning pattern analysis
- Predictive engagement modeling
- Personalized notifications

### 2. Real-time Features
- Live streak updates
- Real-time notifications
- Activity feeds

### 3. Mobile Integration
- App lifecycle tracking
- Background activity monitoring
- Push notification optimization 