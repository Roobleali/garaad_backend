# Gamification System - Testing Guide

## Quick Overview

The gamification system has 5 main components that work together:

1. **XP System** - Points earned for activities
2. **Streak System** - Daily engagement tracking  
3. **League System** - Competitive rankings
4. **Achievement System** - Milestone rewards
5. **Notification System** - User feedback

## Test Scenarios & Expected Results

### Test 1: User Completes a Problem

**Steps**:
1. User logs in
2. User solves a problem
3. Check gamification status

**Expected Results**:
```json
{
  "xp": {
    "total": 15,        // Should increase by 5-20 XP
    "daily": 15,        // Should increase
    "weekly": 15,       // Should increase
    "monthly": 15       // Should increase
  },
  "streak": {
    "current": 1,       // Should be 1 if first problem today
    "energy": 2         // Should decrease by 1
  }
}
```

### Test 2: User Maintains Daily Streak

**Steps**:
1. User solves 2-3 problems today
2. User returns tomorrow and solves problems
3. Check streak count

**Expected Results**:
```json
{
  "streak": {
    "current": 2,       // Should increase from 1 to 2
    "max": 2,           // Should update if higher than before
    "energy": 3         // Should reset to max
  },
  "xp": {
    "total": 35,        // Should include streak bonus (+20 XP)
    "daily": 35         // Should include streak bonus
  }
}
```

### Test 3: User Reaches League Promotion

**Steps**:
1. User has 4,900 XP (in Ogow league, needs 5,000)
2. User completes lesson worth 150 XP
3. Check league status

**Expected Results**:
```json
{
  "league": {
    "current": {
      "name": "Iftiin",     // Should change from "Ogow"
      "min_xp": 10000       // Should be new league threshold
    },
    "next": {
      "name": "Bir Adag",   // Should show next league
      "points_needed": 24000 // Should calculate correctly
    }
  }
}
```

### Test 4: User Achieves Milestone

**Steps**:
1. User maintains 7-day streak
2. Check for milestone achievement
3. Check notifications

**Expected Results**:
```json
{
  "streak": {
    "current": 7,           // Should be exactly 7
    "max": 7               // Should update
  },
  "xp": {
    "total": 85,           // Should include milestone bonus (+50 XP)
    "daily": 85            // Should include milestone bonus
  }
}
```

### Test 5: Leaderboard Rankings

**Steps**:
1. Multiple users complete problems
2. Check league leaderboard
3. Verify rankings

**Expected Results**:
```json
{
  "time_period": "weekly",
  "league": "3",
  "standings": [
    {
      "rank": 1,
      "user": {"name": "user1"},
      "points": 500,       // Should NOT be 0
      "streak": 7
    },
    {
      "rank": 2,
      "user": {"name": "user2"},
      "points": 300,       // Should NOT be 0
      "streak": 5
    }
  ]
}
```

## Common Issues to Check

### ❌ Points Always Show 0
**Problem**: League leaderboard shows 0 points for all users
**Solution**: Run `python manage.py fix_league_points`

### ❌ Streak Not Counting
**Problem**: Streak doesn't increase after daily activity
**Solution**: Check energy availability and daily activity tracking

### ❌ League Promotion Not Working
**Problem**: User doesn't get promoted despite having enough XP
**Solution**: Check UserLeague.current_league field and XP thresholds

### ❌ Notifications Not Appearing
**Problem**: No notifications for achievements or promotions
**Solution**: Check notification creation logic and user preferences

## API Endpoints to Test

### 1. Get User Gamification Status
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://api.garaad.org/api/gamification/status/
```

### 2. Get League Leaderboard
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://api.garaad.org/api/leagues/leaderboard/?time_period=weekly
```

### 3. Get User Profile (with gamification)
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://api.garaad.org/api/accounts/profile/
```

## Test Data Setup

### Create Test Users
```python
# Create users with different XP levels
user1 = User.objects.create_user(username="testuser1", password="test123")
user2 = User.objects.create_user(username="testuser2", password="test123")

# Award different XP amounts
streak1 = Streak.objects.create(user=user1, xp=1500)
streak2 = Streak.objects.create(user=user2, xp=3000)
```

### Create Test Leagues
```python
# Create leagues with different XP thresholds
league1 = League.objects.create(name="Biyo", min_xp=0, order=1)
league2 = League.objects.create(name="Geesi", min_xp=1000, order=2)
league3 = League.objects.create(name="Ogow", min_xp=5000, order=3)
```

## Success Criteria

### ✅ Functional Requirements
- [ ] XP increases when problems are solved
- [ ] Streaks count correctly for daily activity
- [ ] League promotions happen at correct XP thresholds
- [ ] Achievements unlock when criteria are met
- [ ] Notifications appear for important events

### ✅ Performance Requirements
- [ ] API responses return within 2 seconds
- [ ] Leaderboard updates in real-time
- [ ] No database connection errors
- [ ] Caching works correctly

### ✅ User Experience Requirements
- [ ] Points are never 0 for active users
- [ ] Streak information is accurate
- [ ] League rankings are correct
- [ ] Notifications are timely and relevant

## Troubleshooting

### If Points Are Still 0
1. Check if UserReward records exist
2. Run the data fix command
3. Verify XP calculation logic

### If Streaks Don't Work
1. Check energy system
2. Verify daily activity tracking
3. Test streak reset logic

### If League Promotions Don't Work
1. Check XP thresholds
2. Verify UserLeague records
3. Test promotion logic

### If Notifications Don't Appear
1. Check notification preferences
2. Verify notification creation
3. Test email service

## Test Checklist

### Pre-Testing Setup
- [ ] Deploy latest code changes
- [ ] Run data fix command: `python manage.py fix_league_points`
- [ ] Create test users with different XP levels
- [ ] Verify API endpoints are accessible

### Core Functionality Tests
- [ ] Problem completion awards XP
- [ ] Daily streaks count correctly
- [ ] League promotions work
- [ ] Achievements unlock
- [ ] Notifications appear

### Integration Tests
- [ ] All components work together
- [ ] Data consistency across models
- [ ] API responses are correct
- [ ] Performance is acceptable

### Edge Cases
- [ ] Users with 0 XP
- [ ] Users with very high XP
- [ ] Streak resets
- [ ] League demotions
- [ ] Multiple achievements at once

## Reporting Issues

When reporting issues, include:
1. **Steps to reproduce**
2. **Expected vs actual results**
3. **User ID and XP level**
4. **API response data**
5. **Error messages or logs**

## Quick Commands

### Check User XP
```bash
curl -H "Authorization: Bearer TOKEN" \
  https://api.garaad.org/api/gamification/status/
```

### Check Leaderboard
```bash
curl -H "Authorization: Bearer TOKEN" \
  https://api.garaad.org/api/leagues/leaderboard/
```

### Fix Data Issues
```bash
python manage.py fix_league_points
```

### Check Database
```python
# In Django shell
from api.models import Streak
from leagues.models import UserLeague
from courses.models import UserReward

# Check user XP
user = User.objects.get(username="testuser")
streak = Streak.objects.get(user=user)
print(f"Total XP: {streak.xp}")

# Check league
user_league = UserLeague.objects.get(user=user)
print(f"League: {user_league.current_league.name}")
print(f"Weekly XP: {user_league.weekly_xp}")
``` 