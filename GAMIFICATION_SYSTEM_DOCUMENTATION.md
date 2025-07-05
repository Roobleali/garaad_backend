# Garaad Gamification System - Complete Documentation

## Overview

The Garaad gamification system is a comprehensive learning motivation platform that combines XP-based progression, daily streaks, competitive leagues, achievements, and notifications. The system is designed to keep users engaged through immediate rewards, daily challenges, and long-term progression goals.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Actions  │───▶│  XP Calculation │───▶│  League System  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Streak System  │    │ Achievement Sys │    │ Notification Sys│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. XP (Experience Points) System

**Purpose**: Primary currency for user progression and rewards.

**How it works**:
- Users earn XP for completing problems, lessons, and challenges
- XP is tracked in multiple time periods: daily, weekly, monthly, all-time
- XP determines league promotions and leaderboard rankings

**XP Sources**:
- **Problem Completion**: 5-20 XP per problem (based on difficulty)
- **Perfect Score Bonus**: +50 XP for 100% scores
- **Streak Bonuses**: +20 XP for daily streaks
- **Milestone Bonuses**: +50 XP for 7/30/100 day streaks
- **Achievement Rewards**: 50-200 XP per achievement
- **Challenge Completion**: 25-100 XP per daily challenge

### 2. Streak System

**Purpose**: Encourage daily engagement and consistent learning habits.

**Components**:
- **Current Streak**: Consecutive days of activity
- **Max Streak**: Highest streak achieved
- **Energy System**: Limited daily actions (3 energy, regenerates every 4 hours)
- **Problems to Next**: Problems needed to maintain streak (2-3 problems)

**Streak Rules**:
- ✅ **Maintain**: Solve 2-3 problems daily
- ✅ **Extend**: Continue daily activity
- ❌ **Reset**: Miss a day → streak resets to 1
- 🔋 **Energy**: Use energy to maintain streak when busy

### 3. League System

**Purpose**: Create competitive environment and long-term progression goals.

**League Levels** (Somali Cultural Names):
1. **Biyo** (Water) - 0 XP
2. **Geesi** (Hero) - 1,000 XP
3. **Ogow** (Knowledge) - 5,000 XP
4. **Iftiin** (Light) - 10,000 XP
5. **Bir Adag** (Iron) - 25,000 XP
6. **Ugaas** (Chief) - 50,000 XP
7. **Abwaan** (Poet) - 75,000 XP
8. **Ilbax** (Star) - 100,000 XP
9. **Guuleyste** (Champion) - 150,000 XP
10. **Farsamo-yahan** (Master) - 250,000 XP

**League Features**:
- **Weekly Rankings**: Top performers in each league
- **Promotions**: Automatic when XP thresholds are met
- **Demotions**: Can occur in higher leagues
- **Rewards**: Special rewards for league promotions

### 4. Achievement System

**Purpose**: Recognize milestones and encourage specific behaviors.

**Achievement Types**:
- **Course Completion**: Complete entire courses
- **Streak Milestone**: Reach 7, 30, 100 day streaks
- **Challenge Completion**: Complete daily challenges
- **Level Milestone**: Reach specific user levels
- **Perfect Score**: Get 100% on lessons
- **Early Adopter**: Join during early stages

**Achievement Rewards**:
- 50-200 XP per achievement
- Special badges and recognition
- Notification celebrations

### 5. Notification System

**Purpose**: Keep users informed and motivated.

**Notification Types**:
- **Streak Updates**: Daily streak reminders
- **League Promotions**: When promoted to higher league
- **Achievement Earned**: When unlocking achievements
- **Milestone Celebrations**: Special milestone notifications
- **Energy Updates**: When energy regenerates
- **Welcome Messages**: For new users

## Data Models & Relationships

### Core Models

#### 1. Streak Model (`api/models.py`)
```python
class Streak(models.Model):
    user = models.OneToOneField(User)
    current_streak = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)
    current_energy = models.IntegerField(default=3)
    max_energy = models.IntegerField(default=3)
    xp = models.IntegerField(default=0)
    daily_xp = models.IntegerField(default=0)
    weekly_xp = models.IntegerField(default=0)
    monthly_xp = models.IntegerField(default=0)
```

#### 2. UserLeague Model (`leagues/models.py`)
```python
class UserLeague(models.Model):
    user = models.OneToOneField(User)
    current_league = models.ForeignKey(League)
    total_xp = models.IntegerField(default=0)
    weekly_xp = models.IntegerField(default=0)
    monthly_xp = models.IntegerField(default=0)
```

#### 3. UserReward Model (`courses/models.py`)
```python
class UserReward(models.Model):
    user = models.ForeignKey(User)
    reward_type = models.CharField(choices=[
        ('points', 'Points'),
        ('badge', 'Badge'),
        ('streak', 'Streak'),
        ('achievement', 'Achievement'),
        ('challenge', 'Challenge'),
    ])
    reward_name = models.CharField(max_length=255)
    value = models.PositiveIntegerField(default=0)
```

#### 4. Notification Model (`api/models.py`)
```python
class Notification(models.Model):
    user = models.ForeignKey(User)
    type = models.CharField(choices=[
        ('streak', 'Streak Update'),
        ('league', 'League Promotion'),
        ('milestone', 'Milestone Achieved'),
        ('achievement', 'Achievement'),
        # ... more types
    ])
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=255)
```

### Model Relationships

```
User
├── Streak (1:1)
├── UserLeague (1:1)
├── UserReward (1:many)
├── UserProgress (1:many)
├── UserAchievement (1:many)
└── Notification (1:many)

League
└── UserLeague (1:many)

Achievement
└── UserAchievement (1:many)
```

## API Endpoints

### 1. Gamification Status
```
GET /api/gamification/status/
```
**Response**:
```json
{
  "xp": {
    "total": 1500,
    "daily": 50,
    "weekly": 300,
    "monthly": 1200
  },
  "streak": {
    "current": 7,
    "max": 15,
    "energy": 3,
    "problems_to_next": 2
  },
  "league": {
    "current": {
      "id": 3,
      "name": "Ogow",
      "somali_name": "Ogow",
      "min_xp": 5000
    },
    "next": {
      "id": 4,
      "name": "Iftiin",
      "somali_name": "Iftiin",
      "min_xp": 10000,
      "points_needed": 8500
    }
  },
  "rank": {
    "weekly": 5
  }
}
```

### 2. League Leaderboard
```
GET /api/leagues/leaderboard/?time_period=weekly&league=3
```
**Response**:
```json
{
  "time_period": "weekly",
  "league": "3",
  "standings": [
    {
      "rank": 1,
      "user": {
        "id": 41,
        "name": "abdishakuuralimohamed"
      },
      "points": 450,
      "streak": 7
    }
  ],
  "my_standing": {
    "rank": 5,
    "points": 300,
    "streak": 7
  }
}
```

### 3. User Profile (with gamification)
```
GET /api/accounts/profile/
```
**Response**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "xp": 1500,
  "streak": {
    "current": 7,
    "max": 15,
    "energy": 3
  },
  "league": {
    "id": 3,
    "name": "Ogow",
    "min_xp": 5000
  },
  "badges": [
    {
      "reward_name": "7 Day Streak",
      "awarded_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## Testing Scenarios

### Test Case 1: Complete Problem Flow
**Action**: User solves a problem
**Expected Results**:
1. ✅ XP awarded (5-20 points)
2. ✅ Streak updated if 2-3 problems solved
3. ✅ UserLeague points updated
4. ✅ Notification created (if milestone)
5. ✅ Leaderboard updated

### Test Case 2: Daily Streak Maintenance
**Action**: User completes daily learning goal
**Expected Results**:
1. ✅ Streak count increases
2. ✅ 20 XP bonus awarded
3. ✅ Energy consumed
4. ✅ Reminder notification scheduled
5. ✅ Milestone check (7, 30, 100 days)

### Test Case 3: League Promotion
**Action**: User reaches XP threshold for next league
**Expected Results**:
1. ✅ UserLeague.current_league updated
2. ✅ Promotion notification created
3. ✅ Competition notification created
4. ✅ Leaderboard rank recalculated

### Test Case 4: Achievement Unlock
**Action**: User meets achievement criteria
**Expected Results**:
1. ✅ UserAchievement record created
2. ✅ Achievement XP awarded (50-200 points)
3. ✅ Achievement notification created
4. ✅ Badge added to user profile

### Test Case 5: Perfect Score Bonus
**Action**: User gets 100% on lesson
**Expected Results**:
1. ✅ Base XP awarded
2. ✅ +50 XP perfect score bonus
3. ✅ Perfect score achievement check
4. ✅ Special notification created

## Integration Points

### 1. Lesson Completion
```python
# When lesson is completed
progress.mark_as_completed()
streak.award_xp(earned_xp, 'lesson_completion')
user_league.update_weekly_points(earned_xp)
```

### 2. Problem Solving
```python
# When problem is solved
user_problem.mark_as_solved()
streak.award_xp(problem.xp, 'problem')
user_league.update_weekly_points(problem.xp)
```

### 3. Daily Activity
```python
# When user completes daily goal
streak.update_streak(problems_solved, lesson_ids)
if streak.current_streak in [7, 30, 100]:
    streak.award_xp(50, 'milestone')
```

## Error Handling

### Common Issues & Solutions

1. **Points Not Updating**
   - Check UserLeague.update_weekly_points() method
   - Verify UserReward records exist
   - Run `python manage.py fix_league_points`

2. **Streak Not Counting**
   - Check energy availability
   - Verify daily activity tracking
   - Check streak reset logic

3. **League Promotion Not Working**
   - Verify XP thresholds
   - Check UserLeague.current_league field
   - Ensure League objects exist

4. **Notifications Not Sending**
   - Check notification preferences
   - Verify notification creation logic
   - Check email service configuration

## Performance Considerations

### Caching Strategy
- League leaderboards cached for 5 minutes
- User gamification status cached per user
- Achievement calculations cached

### Database Optimization
- Indexes on user, reward_type, awarded_at
- Composite indexes for leaderboard queries
- Regular cleanup of old notifications

## Monitoring & Analytics

### Key Metrics
- Daily Active Users (DAU)
- Streak retention rates
- League promotion rates
- Achievement unlock rates
- XP earning patterns

### Logging
- XP award events
- Streak updates
- League promotions
- Achievement unlocks
- Notification deliveries

## Future Enhancements

### Planned Features
1. **Seasonal Events**: Special XP multipliers during holidays
2. **Team Competitions**: Group-based challenges
3. **Advanced Achievements**: Multi-step achievement chains
4. **Social Features**: Friend challenges and comparisons
5. **Personalized Goals**: AI-driven learning targets

### Technical Improvements
1. **Real-time Updates**: WebSocket notifications
2. **Advanced Analytics**: Machine learning insights
3. **Mobile Optimization**: Push notifications
4. **Offline Support**: Local progress tracking

## Testing Checklist

### Functional Testing
- [ ] XP calculation accuracy
- [ ] Streak counting logic
- [ ] League promotion triggers
- [ ] Achievement unlock conditions
- [ ] Notification delivery
- [ ] Leaderboard rankings

### Integration Testing
- [ ] Lesson completion flow
- [ ] Problem solving flow
- [ ] Daily activity tracking
- [ ] Cross-component data consistency
- [ ] API endpoint responses

### Performance Testing
- [ ] Leaderboard query performance
- [ ] XP calculation speed
- [ ] Notification delivery time
- [ ] Database query optimization

### User Experience Testing
- [ ] Gamification feedback timing
- [ ] Notification relevance
- [ ] Progress visualization
- [ ] Achievement celebration flow 