# Gamification System - Frontend Integration Guide

## 🎯 System Overview

The Garaad gamification system is fully functional and includes:

- **XP System**: Points awarded for activities (problem solving, lessons, streaks)
- **Streak System**: Daily engagement tracking with energy management
- **League System**: Competitive rankings with 5 league levels
- **Notification System**: Real-time user feedback
- **Progress Tracking**: Lesson completion and problem solving
- **Daily Activity**: Activity monitoring and status tracking
- **Leaderboard**: Competitive rankings
- **Rewards System**: Achievement and badge tracking

## 📊 Current System Status

Based on real-world testing, your user (`abdishakuuralimohamed`) has:

```
🔥 Streak: 2 days (max: 6)
⚡ Energy: 3/3
📈 Total XP: 930
🏆 League: Intermediate (ranked #1)
📊 Progress: 16 lessons completed, 11 problems solved
🏆 Rewards: 21 achievements earned
```

## 🔗 API Endpoints

### 1. Gamification Status
```
GET /api/gamification/status/
```

**Response:**
```json
{
  "xp": {
    "total": 930,
    "daily": 40,
    "weekly": 235,
    "monthly": 125
  },
  "streak": {
    "current": 2,
    "max": 6,
    "energy": 3,
    "max_energy": 3
  },
  "league": {
    "current": {
      "id": 2,
      "name": "Intermediate",
      "somali_name": "Dhexe",
      "min_xp": 1000
    },
    "next": {
      "id": 3,
      "name": "Advanced",
      "somali_name": "Sare",
      "min_xp": 2500,
      "points_needed": 1570
    }
  },
  "rank": {
    "weekly": 1,
    "monthly": 1,
    "all_time": 1
  }
}
```

### 2. Leaderboard
```
GET /api/gamification/leaderboard/?time_period=weekly&league=2
```

**Response:**
```json
{
  "time_period": "weekly",
  "league": "2",
  "standings": [
    {
      "rank": 1,
      "user": {
        "id": 41,
        "name": "abdishakuuralimohamed"
      },
      "points": 930,
      "streak": 2,
      "league": {
        "name": "Intermediate",
        "somali_name": "Dhexe"
      }
    }
  ],
  "my_standing": {
    "rank": 1,
    "points": 930,
    "streak": 2
  }
}
```

### 3. User Profile (with gamification)
```
GET /api/accounts/profile/
```

**Response:**
```json
{
  "username": "abdishakuuralimohamed",
  "email": "abdishakuuralimohamed@gmail.com",
  "xp": 930,
  "streak": {
    "current": 2,
    "max": 6,
    "energy": 3
  },
  "league": {
    "id": 2,
    "name": "Intermediate",
    "min_xp": 1000
  },
  "badges": [
    {
      "reward_name": "Course Completed: Xallinta isla'egyada",
      "awarded_at": "2025-01-15T10:30:00Z"
    }
  ],
  "notification_preferences": {
    "email_notifications": true,
    "streak_reminders": true,
    "achievement_notifications": true
  }
}
```

### 4. Activity Update
```
POST /api/activity/update/
```

**Response:**
```json
{
  "success": true,
  "message": "Activity updated successfully",
  "user": {
    "last_active": "2025-07-06T09:35:15.454955Z",
    "last_login": "2025-07-06T09:34:26.913782Z"
  },
  "streak": {
    "current_streak": 2,
    "max_streak": 6,
    "last_activity_date": "2025-07-06"
  },
  "activity": {
    "date": "2025-07-06",
    "status": "partial",
    "problems_solved": 2,
    "lesson_ids": [1]
  }
}
```

## 🎮 Gamification Flow

### 1. Problem Solving Flow
```javascript
// When user solves a problem
async function solveProblem(problemId) {
  const response = await fetch(`/api/lms/problems/${problemId}/solve/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getAccessToken()}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      answer: userAnswer,
      time_taken: 120
    })
  });
  
  const data = await response.json();
  
  // Update UI with new XP and streak
  updateGamificationUI(data);
  
  // Show notification
  showNotification('Problem Solved!', `You earned ${data.xp_earned} XP!`);
}
```

### 2. Lesson Completion Flow
```javascript
// When user completes a lesson
async function completeLesson(lessonId, completedProblems, score) {
  const response = await fetch(`/api/lms/lessons/${lessonId}/complete/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getAccessToken()}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      completed_problems: completedProblems,
      total_score: score
    })
  });
  
  const data = await response.json();
  
  // Update UI
  updateGamificationUI(data);
  
  // Check for achievements
  if (data.achievements) {
    data.achievements.forEach(achievement => {
      showAchievementNotification(achievement);
    });
  }
}
```

### 3. Daily Activity Tracking
```javascript
// Update activity periodically
setInterval(async () => {
  try {
    const response = await fetch('/api/activity/update/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getAccessToken()}`,
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response.json();
    updateActivityUI(data);
  } catch (error) {
    console.error('Activity update failed:', error);
  }
}, 5 * 60 * 1000); // Every 5 minutes
```

## 🎨 UI Components

### 1. XP Display
```jsx
function XPDisplay({ xp }) {
  return (
    <div className="xp-display">
      <div className="xp-icon">⭐</div>
      <div className="xp-amount">{xp.total}</div>
      <div className="xp-breakdown">
        <span>Daily: {xp.daily}</span>
        <span>Weekly: {xp.weekly}</span>
      </div>
    </div>
  );
}
```

### 2. Streak Counter
```jsx
function StreakCounter({ streak }) {
  return (
    <div className="streak-counter">
      <div className="streak-icon">🔥</div>
      <div className="streak-days">{streak.current} days</div>
      <div className="streak-energy">
        {Array(streak.energy).fill('⚡').join('')}
      </div>
      <div className="streak-max">Max: {streak.max} days</div>
    </div>
  );
}
```

### 3. League Display
```jsx
function LeagueDisplay({ league }) {
  return (
    <div className="league-display">
      <div className="league-name">{league.current.name}</div>
      <div className="league-progress">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{width: `${(league.current.xp / league.next.min_xp) * 100}%`}}
          />
        </div>
        <div className="progress-text">
          {league.current.xp} / {league.next.min_xp} XP
        </div>
      </div>
      <div className="next-league">
        Next: {league.next.name}
      </div>
    </div>
  );
}
```

### 4. Leaderboard
```jsx
function Leaderboard({ standings, myStanding }) {
  return (
    <div className="leaderboard">
      <h3>Leaderboard</h3>
      <div className="standings">
        {standings.map((standing, index) => (
          <div key={standing.user.id} className={`standing ${standing.user.id === myStanding.user.id ? 'my-standing' : ''}`}>
            <div className="rank">#{standing.rank}</div>
            <div className="user-name">{standing.user.name}</div>
            <div className="points">{standing.points} XP</div>
            <div className="streak">🔥 {standing.streak}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 5. Notification Center
```jsx
function NotificationCenter({ notifications }) {
  return (
    <div className="notification-center">
      <h3>Notifications</h3>
      {notifications.map(notification => (
        <div key={notification.id} className={`notification ${notification.type}`}>
          <div className="notification-icon">
            {getNotificationIcon(notification.type)}
          </div>
          <div className="notification-content">
            <div className="notification-title">{notification.title}</div>
            <div className="notification-message">{notification.message}</div>
            <div className="notification-time">
              {formatTime(notification.created_at)}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
```

## 🔄 Real-time Updates

### 1. WebSocket Integration (Optional)
```javascript
// Connect to WebSocket for real-time updates
const socket = new WebSocket('ws://your-api-url/ws/gamification/');

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'xp_update':
      updateXPDisplay(data.xp);
      break;
    case 'streak_update':
      updateStreakDisplay(data.streak);
      break;
    case 'league_promotion':
      showLeaguePromotionNotification(data.league);
      break;
    case 'achievement_earned':
      showAchievementNotification(data.achievement);
      break;
  }
};
```

### 2. Polling Updates
```javascript
// Poll for updates every 30 seconds
setInterval(async () => {
  try {
    const response = await fetch('/api/gamification/status/');
    const data = await response.json();
    updateGamificationUI(data);
  } catch (error) {
    console.error('Gamification update failed:', error);
  }
}, 30000);
```

## 🎯 Achievement System

### Achievement Types
- **Streak Achievements**: 7, 30, 100 day streaks
- **Problem Solving**: First problem, 10 problems, 100 problems
- **Lesson Completion**: First lesson, perfect score, course completion
- **League Achievements**: League promotions, top rankings

### Achievement Display
```jsx
function AchievementBadge({ achievement }) {
  return (
    <div className="achievement-badge">
      <div className="badge-icon">🏆</div>
      <div className="badge-name">{achievement.name}</div>
      <div className="badge-description">{achievement.description}</div>
      <div className="badge-xp">+{achievement.xp_reward} XP</div>
    </div>
  );
}
```

## 📱 Mobile Considerations

### 1. Responsive Design
```css
/* Mobile-first gamification UI */
.gamification-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
}

@media (min-width: 768px) {
  .gamification-panel {
    flex-direction: row;
    justify-content: space-between;
  }
}
```

### 2. Touch-friendly Interactions
```javascript
// Add touch gestures for mobile
let touchStartY = 0;
let touchEndY = 0;

element.addEventListener('touchstart', (e) => {
  touchStartY = e.touches[0].clientY;
});

element.addEventListener('touchend', (e) => {
  touchEndY = e.changedTouches[0].clientY;
  handleSwipe();
});
```

## 🚀 Performance Optimization

### 1. Caching
```javascript
// Cache gamification data
const gamificationCache = new Map();

async function getGamificationStatus() {
  const cacheKey = 'gamification_status';
  const cached = gamificationCache.get(cacheKey);
  
  if (cached && Date.now() - cached.timestamp < 30000) {
    return cached.data;
  }
  
  const response = await fetch('/api/gamification/status/');
  const data = await response.json();
  
  gamificationCache.set(cacheKey, {
    data,
    timestamp: Date.now()
  });
  
  return data;
}
```

### 2. Lazy Loading
```javascript
// Lazy load leaderboard data
const Leaderboard = lazy(() => import('./components/Leaderboard'));

function GamificationPanel() {
  const [showLeaderboard, setShowLeaderboard] = useState(false);
  
  return (
    <div>
      <button onClick={() => setShowLeaderboard(true)}>
        Show Leaderboard
      </button>
      
      {showLeaderboard && (
        <Suspense fallback={<div>Loading...</div>}>
          <Leaderboard />
        </Suspense>
      )}
    </div>
  );
}
```

## 🧪 Testing Scenarios

### 1. Problem Solving Test
```javascript
// Test problem solving flow
async function testProblemSolving() {
  // 1. User solves a problem
  const problemResponse = await solveProblem(1);
  
  // 2. Check XP increase
  expect(problemResponse.xp_earned).toBeGreaterThan(0);
  
  // 3. Check streak update
  expect(problemResponse.streak.current_streak).toBeGreaterThan(0);
  
  // 4. Check notification
  expect(problemResponse.notifications).toHaveLength(1);
}
```

### 2. League Promotion Test
```javascript
// Test league promotion
async function testLeaguePromotion() {
  // 1. Add enough XP to trigger promotion
  await addXP(1000);
  
  // 2. Check league change
  const status = await getGamificationStatus();
  expect(status.league.current.name).toBe('Intermediate');
  
  // 3. Check notification
  const notifications = await getNotifications();
  expect(notifications).toContainEqual(
    expect.objectContaining({
      type: 'league',
      title: 'League Promotion!'
    })
  );
}
```

## 📋 Implementation Checklist

- [ ] **XP Display**: Show total, daily, weekly XP
- [ ] **Streak Counter**: Display current streak and energy
- [ ] **League Display**: Show current league and progress
- [ ] **Leaderboard**: Display rankings and user position
- [ ] **Notifications**: Real-time achievement and milestone notifications
- [ ] **Activity Tracking**: Periodic activity updates
- [ ] **Achievement Badges**: Display earned achievements
- [ ] **Progress Bars**: Visual progress indicators
- [ ] **Mobile Responsive**: Touch-friendly interface
- [ ] **Performance Optimized**: Caching and lazy loading
- [ ] **Error Handling**: Graceful failure handling
- [ ] **Accessibility**: Screen reader support

## 🎉 Success Metrics

Track these metrics to measure gamification success:

- **Daily Active Users**: Users who earn XP daily
- **Streak Retention**: Users maintaining 7+ day streaks
- **League Progression**: Users advancing to higher leagues
- **Problem Completion**: Average problems solved per user
- **Achievement Unlocks**: Achievement unlock rates
- **Notification Engagement**: Notification open rates

## 🔧 Troubleshooting

### Common Issues

1. **XP not updating**: Check if user is authenticated and API calls are successful
2. **Streak not counting**: Verify energy availability and daily activity
3. **League not promoting**: Check XP thresholds and league configuration
4. **Notifications not showing**: Verify notification preferences and API responses

### Debug Commands
```javascript
// Debug gamification state
console.log('Current gamification state:', await getGamificationStatus());

// Debug API responses
fetch('/api/gamification/status/')
  .then(response => response.json())
  .then(data => console.log('API response:', data))
  .catch(error => console.error('API error:', error));
```

---

**The gamification system is fully functional and ready for frontend integration!** 🚀 