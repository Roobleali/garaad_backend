# Frontend Activity Tracking Integration Guide

## Overview

This guide explains how to integrate your frontend application with the new robust activity tracking system. The system now tracks user activity comprehensively, similar to platforms like Duolingo and Brilliant.org.

## Key Features

- **Automatic tracking**: User activity is tracked on every authenticated request
- **Debounced updates**: Prevents excessive database writes (updates every 5 minutes)
- **Token refresh tracking**: Activity is updated when tokens are refreshed
- **Manual updates**: Frontend can trigger activity updates for better UX

## Integration Methods

### 1. Automatic Tracking (Recommended)

The backend automatically tracks activity on every authenticated request. No frontend changes needed for basic tracking.

### 2. Periodic Activity Updates

Call the activity update endpoint periodically while the user is active:

```javascript
// Update activity every 5 minutes while user is active
const ACTIVITY_UPDATE_INTERVAL = 5 * 60 * 1000; // 5 minutes

let activityUpdateTimer = null;

function startActivityTracking() {
  // Clear existing timer
  if (activityUpdateTimer) {
    clearInterval(activityUpdateTimer);
  }
  
  // Start periodic updates
  activityUpdateTimer = setInterval(async () => {
    try {
      const response = await fetch('/api/activity/update/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Activity updated:', data);
        
        // Update UI with new streak/activity info
        updateActivityUI(data);
      }
    } catch (error) {
      console.error('Failed to update activity:', error);
    }
  }, ACTIVITY_UPDATE_INTERVAL);
}

function stopActivityTracking() {
  if (activityUpdateTimer) {
    clearInterval(activityUpdateTimer);
    activityUpdateTimer = null;
  }
}

// Start tracking when user logs in
function onUserLogin() {
  startActivityTracking();
}

// Stop tracking when user logs out
function onUserLogout() {
  stopActivityTracking();
}
```

### 3. User Interaction Tracking

Update activity on user interactions for better UX:

```javascript
// Track user interactions
function setupActivityTracking() {
  let lastActivityUpdate = 0;
  const MIN_UPDATE_INTERVAL = 60000; // 1 minute
  
  function updateActivityOnInteraction() {
    const now = Date.now();
    if (now - lastActivityUpdate > MIN_UPDATE_INTERVAL) {
      updateActivity();
      lastActivityUpdate = now;
    }
  }
  
  // Track various user interactions
  document.addEventListener('click', updateActivityOnInteraction);
  document.addEventListener('scroll', updateActivityOnInteraction);
  document.addEventListener('keypress', updateActivityOnInteraction);
  
  // Track page visibility changes
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
      updateActivityOnInteraction();
    }
  });
  
  // Track focus/blur events
  window.addEventListener('focus', updateActivityOnInteraction);
  window.addEventListener('blur', updateActivityOnInteraction);
}

async function updateActivity() {
  try {
    const response = await fetch('/api/activity/update/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getAccessToken()}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      updateActivityUI(data);
    }
  } catch (error) {
    console.error('Failed to update activity:', error);
  }
}
```

### 4. Token Refresh Integration

Update activity when tokens are refreshed:

```javascript
// In your token refresh logic
async function refreshToken() {
  try {
    const response = await fetch('/api/auth/refresh/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getRefreshToken()}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      
      // Update tokens
      setAccessToken(data.tokens.access);
      setRefreshToken(data.tokens.refresh);
      
      // Activity is automatically updated by backend middleware
      // But you can also manually update for immediate UI feedback
      updateActivity();
      
      return true;
    }
  } catch (error) {
    console.error('Token refresh failed:', error);
    return false;
  }
}
```

## API Response Format

The `/api/activity/update/` endpoint returns:

```json
{
  "success": true,
  "message": "Activity updated successfully",
  "user": {
    "last_active": "2025-01-29T10:30:00Z",
    "last_login": "2025-01-29T09:00:00Z"
  },
  "streak": {
    "current_streak": 5,
    "max_streak": 10,
    "last_activity_date": "2025-01-29"
  },
  "activity": {
    "date": "2025-01-29",
    "status": "partial",
    "problems_solved": 2,
    "lesson_ids": ["lesson1", "lesson2"]
  },
  "activity_date": "2025-01-29"
}
```

## UI Integration Examples

### React Component Example

```jsx
import React, { useState, useEffect } from 'react';

function ActivityTracker({ user }) {
  const [activityData, setActivityData] = useState(null);
  const [isTracking, setIsTracking] = useState(false);
  
  useEffect(() => {
    if (user) {
      startActivityTracking();
      return () => stopActivityTracking();
    }
  }, [user]);
  
  const startActivityTracking = () => {
    setIsTracking(true);
    
    // Initial activity update
    updateActivity();
    
    // Periodic updates
    const interval = setInterval(updateActivity, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  };
  
  const updateActivity = async () => {
    try {
      const response = await fetch('/api/activity/update/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getAccessToken()}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setActivityData(data);
      }
    } catch (error) {
      console.error('Activity update failed:', error);
    }
  };
  
  if (!activityData) {
    return <div>Loading activity...</div>;
  }
  
  return (
    <div className="activity-tracker">
      <div className="streak-info">
        <h3>Current Streak: {activityData.streak.current_streak} days</h3>
        <p>Max Streak: {activityData.streak.max_streak} days</p>
      </div>
      
      <div className="activity-status">
        <p>Today's Activity: {activityData.activity.status}</p>
        <p>Problems Solved: {activityData.activity.problems_solved}</p>
      </div>
      
      <div className="last-active">
        <p>Last Active: {new Date(activityData.user.last_active).toLocaleString()}</p>
      </div>
    </div>
  );
}

export default ActivityTracker;
```

### Vue.js Component Example

```vue
<template>
  <div class="activity-tracker">
    <div v-if="activityData" class="activity-info">
      <h3>Current Streak: {{ activityData.streak.current_streak }} days</h3>
      <p>Today's Activity: {{ activityData.activity.status }}</p>
      <p>Last Active: {{ formatDate(activityData.user.last_active) }}</p>
    </div>
    
    <div v-else>
      Loading activity...
    </div>
  </div>
</template>

<script>
export default {
  name: 'ActivityTracker',
  data() {
    return {
      activityData: null,
      updateInterval: null
    }
  },
  
  mounted() {
    this.startActivityTracking();
  },
  
  beforeDestroy() {
    this.stopActivityTracking();
  },
  
  methods: {
    startActivityTracking() {
      // Initial update
      this.updateActivity();
      
      // Periodic updates
      this.updateInterval = setInterval(() => {
        this.updateActivity();
      }, 5 * 60 * 1000); // 5 minutes
    },
    
    stopActivityTracking() {
      if (this.updateInterval) {
        clearInterval(this.updateInterval);
        this.updateInterval = null;
      }
    },
    
    async updateActivity() {
      try {
        const response = await fetch('/api/activity/update/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.getAccessToken()}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          this.activityData = data;
        }
      } catch (error) {
        console.error('Activity update failed:', error);
      }
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleString();
    },
    
    getAccessToken() {
      // Get access token from your auth system
      return localStorage.getItem('access_token');
    }
  }
}
</script>
```

## Best Practices

### 1. Performance Optimization

- **Debounce updates**: Don't call the API on every user interaction
- **Use intervals**: Update every 5 minutes instead of continuously
- **Handle errors gracefully**: Don't break the app if activity updates fail

### 2. User Experience

- **Show activity status**: Display current streak and activity status
- **Provide feedback**: Show when activity is being updated
- **Handle offline state**: Don't try to update activity when offline

### 3. Security

- **Use HTTPS**: Always use secure connections
- **Validate tokens**: Ensure tokens are valid before making requests
- **Handle auth errors**: Redirect to login if authentication fails

### 4. Error Handling

```javascript
async function updateActivity() {
  try {
    const response = await fetch('/api/activity/update/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getAccessToken()}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.status === 401) {
      // Token expired, redirect to login
      redirectToLogin();
      return;
    }
    
    if (response.ok) {
      const data = await response.json();
      updateActivityUI(data);
    } else {
      console.error('Activity update failed:', response.status);
    }
  } catch (error) {
    console.error('Activity update error:', error);
    // Don't break the app, just log the error
  }
}
```

## Testing

### Manual Testing

```javascript
// Test activity update
async function testActivityUpdate() {
  const response = await fetch('/api/activity/update/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getAccessToken()}`,
      'Content-Type': 'application/json'
    }
  });
  
  console.log('Response:', await response.json());
}
```

### Automated Testing

```javascript
// Jest test example
describe('Activity Tracking', () => {
  test('should update activity successfully', async () => {
    const mockResponse = {
      success: true,
      streak: { current_streak: 5, max_streak: 10 },
      activity: { status: 'partial', problems_solved: 2 }
    };
    
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    });
    
    const result = await updateActivity();
    expect(result).toEqual(mockResponse);
  });
});
```

## Migration Guide

### From Old System

If you were previously using a different activity tracking system:

1. **Remove old activity calls**: Remove any existing activity update logic
2. **Update UI components**: Use the new response format
3. **Test thoroughly**: Verify that activity tracking works correctly
4. **Monitor performance**: Ensure the new system doesn't impact performance

### Backward Compatibility

The new system is backward compatible:
- Old activity data is preserved
- Existing API endpoints continue to work
- Gradual migration is supported

## Troubleshooting

### Common Issues

1. **Activity not updating**: Check if user is authenticated and tokens are valid
2. **Streak not incrementing**: Verify that activity is being tracked on consecutive days
3. **Performance issues**: Ensure you're not calling the API too frequently
4. **CORS errors**: Make sure your frontend domain is allowed in CORS settings

### Debug Commands

```javascript
// Check current activity status
async function debugActivity() {
  const response = await fetch('/api/activity/update/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getAccessToken()}`,
      'Content-Type': 'application/json'
    }
  });
  
  const data = await response.json();
  console.log('Current activity:', data);
  return data;
}
```

## Conclusion

This new activity tracking system provides robust, accurate user activity tracking similar to top learning platforms. By following this integration guide, you can ensure your frontend properly integrates with the backend activity tracking system. 