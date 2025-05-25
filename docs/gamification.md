# Garaad Gamification System Documentation

## Overview
The Garaad gamification system is inspired by Brilliant.org's approach, combining XP-based progression, daily streaks, and competitive leagues. The system is designed to motivate users through a combination of immediate rewards (XP for problems), daily engagement (streaks), and long-term progression (leagues).

## Core Components

### 1. Problem XP System
- Each problem has an `xp` value (default: 10 XP)
- XP is awarded immediately upon solving a problem
- XP values can be customized per problem
- XP contributes to:
  - Daily XP total
  - Weekly XP total
  - Monthly XP total
  - Total XP (all-time)

### 2. Streak System
- Streaks are earned by solving 2-3 problems per day
- Streak tracking:
  - `current_streak`: Current consecutive days of activity
  - `max_streak`: Highest streak achieved
  - `problems_to_next_streak`: Problems needed to maintain streak
- Energy system:
  - Users have limited energy (default: 3)
  - Energy regenerates over time (1 energy every 4 hours)
  - Energy can be used to maintain streaks

### 3. League System
- 10 league levels with Somali cultural names:
  1. Biyo (Water)
  2. Geesi (Hero)
  3. Ogow (Knowledge)
  4. Iftiin (Light)
  5. Bir Adag (Iron)
  6. Ugaas (Chief)
  7. Abwaan (Poet)
  8. Ilbax (Star)
  9. Guuleyste (Champion)
  10. Farsamo-yahan (Master)

- League progression:
  - Based on total XP
  - Each league has minimum XP requirements
  - Promotions occur when XP thresholds are met
  - Weekly rankings within leagues

## Data Models

### Problem Model
```python
class Problem(models.Model):
    xp = models.PositiveIntegerField(default=10)
    # ... other fields
```

### UserProblem Model
```python
class UserProblem(models.Model):
    user = models.ForeignKey(User)
    problem = models.ForeignKey(Problem)
    solved = models.BooleanField(default=False)
    solved_at = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
```

### Streak Model
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

### UserProgress Model
```python
class UserProgress(models.Model):
    user = models.ForeignKey(User)
    lesson = models.ForeignKey(Lesson)
    problems_solved = models.PositiveIntegerField(default=0)
    total_xp_earned = models.PositiveIntegerField(default=0)
    streak_updated = models.BooleanField(default=False)
```

## XP Flow

1. **Problem Solving**:
   ```python
   # When a problem is solved
   user_problem = UserProblem.objects.get(user=user, problem=problem)
   user_problem.mark_as_solved()  # Awards XP and updates progress
   ```

2. **Streak Updates**:
   ```python
   # After solving 2-3 problems
   if progress.problems_solved in [2, 3] and not progress.streak_updated:
       streak.update_streak(1, [lesson.id])
       progress.streak_updated = True
   ```

3. **Lesson Completion**:
   ```python
   # When a lesson is completed
   progress.mark_as_completed()
   # Calculates total XP from all solved problems
   # Updates user's streak and XP
   # Updates course progress
   ```

## API Endpoints

### 1. Gamification Status
```
GET /api/gamification/status/
```
Returns:
```json
{
    "xp": {
        "total": 1000,
        "daily": 50,
        "weekly": 300,
        "monthly": 1200
    },
    "streak": {
        "current": 5,
        "max": 10,
        "energy": 3,
        "problems_to_next": 2
    },
    "league": {
        "current": {
            "id": 1,
            "name": "Biyo",
            "somali_name": "Biyo",
            "min_xp": 0
        },
        "next": {
            "id": 2,
            "name": "Geesi",
            "somali_name": "Geesi",
            "min_xp": 1000,
            "points_needed": 500
        }
    },
    "rank": {
        "weekly": 15
    }
}
```

### 2. Leaderboard
```
GET /api/gamification/leaderboard/
Query Parameters:
- time_period: weekly/monthly/all_time
- league: league_id (optional)
```
Returns:
```json
{
    "time_period": "weekly",
    "league": 1,
    "standings": [
        {
            "rank": 1,
            "user": {
                "id": 1,
                "name": "username"
            },
            "points": 1000,
            "streak": 5,
            "league": {
                "id": 1,
                "name": "Biyo"
            }
        }
    ],
    "my_standing": {
        "rank": 15,
        "points": 500,
        "streak": 3,
        "league": {
            "id": 1,
            "name": "Biyo"
        }
    }
}
```

### 3. Use Energy
```
POST /api/gamification/use_energy/
```
Returns:
```json
{
    "success": true,
    "remaining_energy": 2,
    "message": "Waad ku mahadsantahay ilaalinta xariggaaga"
}
```

## Best Practices

1. **XP Awarding**:
   - Award XP immediately upon problem completion
   - Include XP in problem creation/editing interface
   - Consider difficulty when setting XP values

2. **Streak Management**:
   - Update streaks after 2-3 problems
   - Use energy system to prevent streak abuse
   - Send notifications for streak maintenance

3. **League Progression**:
   - Update leagues based on total XP
   - Consider weekly performance for promotions
   - Provide clear feedback on league status

4. **Performance**:
   - Use database indexes for frequent queries
   - Cache leaderboard data
   - Batch XP updates when possible

## Error Handling

1. **Insufficient Energy**:
```json
{
    "success": false,
    "message": "Ma haysato tamar"
}
```

2. **Invalid Time Period**:
```json
{
    "error": "Invalid time period. Must be weekly, monthly, or all_time"
}
```

## Notifications

The system sends notifications for:
- Streak reminders
- League promotions
- Achievement unlocks
- Daily goals
- Challenge availability

## Future Enhancements

1. **Social Features**:
   - Friend leaderboards
   - Study groups
   - XP sharing

2. **Advanced Streaks**:
   - Streak multipliers
   - Streak challenges
   - Streak rewards

3. **League Features**:
   - League-specific challenges
   - League tournaments
   - League achievements
