# Gamification System Documentation

## Overview

The gamification system is designed to increase user engagement and motivation through various game-like elements. It includes points, levels, achievements, challenges, leaderboards, and culturally relevant features.

## API Endpoints

### 1. User Rewards
```http
GET /api/courses/rewards/
```
- Lists all rewards earned by the authenticated user
- Filterable by lesson, course, or reward type
- Response includes points, badges, streaks, and achievements

### 2. Leaderboard
```http
GET /api/courses/leaderboard/
```
- Shows user rankings based on points
- Supports time periods: weekly, monthly, all-time
- Includes user stats and achievements
- Custom endpoint for user's rank: `/api/courses/leaderboard/my_rank/`

### 3. Daily Challenges
```http
GET /api/courses/challenges/
POST /api/courses/challenges/{id}/submit_attempt/
```
- Lists available challenges
- Allows submitting challenge attempts
- Tracks completion status and rewards

### 4. User Levels
```http
GET /api/courses/levels/
GET /api/courses/levels/leaderboard/
```
- Shows user's current level and experience
- Displays progress to next level
- Includes level leaderboard

### 5. Achievements
```http
GET /api/courses/achievements/
GET /api/courses/achievements/user_achievements/
```
- Lists all possible achievements
- Shows user's earned achievements
- Includes achievement details and rewards

### 6. Cultural Events
```http
GET /api/courses/cultural-events/
POST /api/courses/cultural-events/{id}/participate/
```
- Lists cultural events
- Allows event participation
- Tracks participation and rewards

### 7. Community Contributions
```http
GET /api/courses/contributions/
POST /api/courses/contributions/
```
- Lists user's contributions
- Allows submitting new contributions
- Tracks verification and rewards

## Data Structures

### User Level
```json
{
  "id": 1,
  "level": 3,
  "experience_points": 250,
  "experience_to_next_level": 500,
  "progress_to_next_level": 50,
  "last_level_up": "2024-03-20T10:00:00Z"
}
```

### Achievement
```json
{
  "id": 1,
  "name": "Dhalasho Cusub",
  "description": "Complete your first challenge",
  "icon": "first_challenge.png",
  "points_reward": 100,
  "level_required": 1,
  "achievement_type": "challenge"
}
```

### Leaderboard Entry
```json
{
  "id": 1,
  "user": {
    "username": "user123",
    "email": "user@example.com",
    "stats": {
      "total_points": 1000,
      "completed_lessons": 15,
      "enrolled_courses": 3,
      "current_streak": 5,
      "badges_count": 8
    }
  },
  "points": 1000,
  "time_period": "all_time",
  "rank": 1
}
```

### Cultural Event
```json
{
  "id": 1,
  "name": "Eid al-Fitr Celebration",
  "description": "Join our Eid celebration and learn about Somali traditions",
  "event_date": "2024-04-10",
  "event_type": "celebration",
  "points_reward": 100,
  "is_active": true
}
```

## UI Components to Implement

### 1. Progress Bar
- Show progress to next level
- Display current level and experience points
- Animate level-up transitions

### 2. Achievement Showcase
- Grid or list of achievements
- Visual indicators for locked/unlocked status
- Achievement details modal
- Notification system for new achievements

### 3. Leaderboard
- Tabbed view for different time periods
- User rank highlight
- Top 10 users display
- User stats summary

### 4. Daily Challenge Card
- Challenge description
- Points reward
- Completion status
- Submit attempt button
- Progress tracking

### 5. Cultural Event Card
- Event details
- Participation status
- Points reward
- Join/participate button
- Event countdown (if applicable)

### 6. Community Contribution Form
- Contribution type selection
- Description input
- Points reward display
- Verification status
- Contribution history

## Best Practices

1. **Immediate Feedback**
   - Show animations for points earned
   - Display achievement unlock notifications
   - Animate level-up transitions

2. **Progress Visualization**
   - Use progress bars for level progress
   - Show streaks with flame icons
   - Display points earned in real-time

3. **Cultural Relevance**
   - Use Somali language for achievement names
   - Include culturally relevant icons
   - Celebrate Somali holidays and events

4. **Mobile Responsiveness**
   - Ensure all components work well on mobile
   - Use appropriate touch targets
   - Optimize animations for mobile

5. **Accessibility**
   - Include alt text for achievement icons
   - Ensure color contrast meets WCAG standards
   - Provide keyboard navigation

## Example Implementation

```javascript
// Example React component for Achievement Card
const AchievementCard = ({ achievement }) => {
  return (
    <div className="achievement-card">
      <img 
        src={achievement.icon} 
        alt={achievement.name}
        className={`achievement-icon ${achievement.unlocked ? 'unlocked' : 'locked'}`}
      />
      <h3>{achievement.name}</h3>
      <p>{achievement.description}</p>
      <div className="achievement-reward">
        <span className="points">+{achievement.points_reward} points</span>
      </div>
      {achievement.unlocked && (
        <div className="achievement-date">
          Unlocked: {formatDate(achievement.earned_at)}
        </div>
      )}
    </div>
  );
};
```

## Error Handling

- Handle API errors gracefully
- Show appropriate error messages
- Provide retry options for failed requests
- Maintain state consistency

## Testing

- Test all API endpoints
- Verify reward calculations
- Check achievement triggers
- Validate leaderboard updates
- Test cultural event participation
- Verify contribution system

## Future Enhancements

1. **Social Features**
   - Friend leaderboards
   - Achievement sharing
   - Collaborative challenges

2. **Advanced Analytics**
   - User progress tracking
   - Engagement metrics
   - Performance analytics

3. **Personalization**
   - Custom achievement paths
   - Personalized challenges
   - Adaptive difficulty

4. **Cultural Integration**
   - More cultural events
   - Community challenges
   - Cultural content rewards 