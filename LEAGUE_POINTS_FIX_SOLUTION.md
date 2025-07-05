# League Points Calculation Fix

## Problem Analysis

The league leaderboard was showing 0 points for all users because:

1. **Missing Method**: The `UserLeague` model in `leagues/models.py` was missing the `update_weekly_points()` method that was being called in the code.

2. **Incomplete XP Updates**: The `award_xp()` method in `api/models.py` was creating UserLeague records but not updating the `weekly_xp`, `monthly_xp`, and `total_xp` fields.

3. **Data Inconsistency**: Existing UserLeague records had 0 points because they were never properly updated when users earned XP.

## Root Cause

The issue was in the `award_xp()` method in `api/models.py`:

```python
def award_xp(self, amount, xp_type='problem'):
    # ... XP calculation ...
    
    user_league, _ = UserLeague.objects.get_or_create(
        user=self.user,
        defaults={
            'current_league': default_league,
            'total_xp': 0,
            'weekly_xp': 0,
            'monthly_xp': 0
        }
    )
    
    # Missing: user_league.update_weekly_points(amount)
    
    # ... rest of method ...
```

The method was creating UserLeague records but never updating the points fields.

## Solution Implemented

### 1. Added Missing Methods to UserLeague Model

**File**: `leagues/models.py`

Added the following methods to the `UserLeague` model:

```python
def update_weekly_points(self, amount):
    """Update weekly points for the user."""
    self.weekly_xp += amount
    self.total_xp += amount
    self.monthly_xp += amount
    self.save()

def update_monthly_points(self, amount):
    """Update monthly points for the user."""
    self.monthly_xp += amount
    self.total_xp += amount
    self.save()

def reset_weekly_points(self):
    """Reset weekly points to 0."""
    self.weekly_xp = 0
    self.save()

def reset_monthly_points(self):
    """Reset monthly points to 0."""
    self.monthly_xp = 0
    self.save()
```

### 2. Fixed XP Award Method

**File**: `api/models.py`

Updated the `award_xp()` method to properly update UserLeague points:

```python
def award_xp(self, amount, xp_type='problem'):
    # ... existing XP calculation ...
    
    user_league, _ = UserLeague.objects.get_or_create(
        user=self.user,
        defaults={
            'current_league': default_league,
            'total_xp': 0,
            'weekly_xp': 0,
            'monthly_xp': 0
        }
    )
    
    # NEW: Update UserLeague points
    user_league.update_weekly_points(amount)
    
    # ... rest of method ...
```

### 3. Created Data Fix Command

**File**: `leagues/management/commands/fix_league_points.py`

Created a Django management command to fix existing data:

```bash
python manage.py fix_league_points
```

This command:
- Calculates correct points from `UserReward` records
- Updates all existing `UserLeague` records
- Ensures league promotions are correct
- Updates `Streak` records for consistency

## How Points Are Calculated

### Weekly Points
- Sum of all `UserReward` records with `reward_type='points'` from the last 7 days
- Updated whenever a user earns XP

### Monthly Points  
- Sum of all `UserReward` records with `reward_type='points'` from the last 30 days
- Updated whenever a user earns XP

### Total Points
- Sum of all `UserReward` records with `reward_type='points'` (all time)
- Used for league promotions

## Points Sources

Points are awarded from:

1. **Problem Completion**: 5-20 XP per problem
2. **Streak Bonuses**: 20 XP for daily streaks
3. **Milestone Bonuses**: 50 XP for 7/30/100 day streaks
4. **Perfect Scores**: 50 XP bonus for 100% scores
5. **Achievements**: Various XP rewards

## League Leaderboard Logic

The leaderboard in `leagues/views.py`:

```python
@action(detail=False, methods=['get'])
def leaderboard(self, request):
    time_period = request.query_params.get('time_period', 'weekly')
    league_id = request.query_params.get('league')
    
    queryset = UserLeague.objects.all()
    
    if league_id:
        queryset = queryset.filter(current_league_id=league_id)
    
    if time_period == 'weekly':
        queryset = queryset.order_by('-weekly_xp')
    elif time_period == 'monthly':
        queryset = queryset.order_by('-monthly_xp')
    else:  # all_time
        queryset = queryset.order_by('-weekly_xp')
    
    # Returns standings with points from UserLeague.weekly_xp
```

## Deployment Steps

1. **Deploy Code Changes**:
   ```bash
   git add .
   git commit -m "Fix league points calculation"
   git push origin main
   ```

2. **Run Migration** (if needed):
   ```bash
   python manage.py makemigrations leagues
   python manage.py migrate
   ```

3. **Fix Existing Data**:
   ```bash
   python manage.py fix_league_points
   ```

4. **Verify Fix**:
   - Check league leaderboard endpoint
   - Verify points are no longer 0
   - Test with new user activity

## Testing the Fix

### Before Fix
```json
{
  "time_period": "weekly",
  "league": "1", 
  "standings": [
    {
      "rank": 1,
      "user": {"id": 41, "name": "abdishakuuralimohamed"},
      "points": 0,  // ❌ Always 0
      "streak": 1
    }
  ]
}
```

### After Fix
```json
{
  "time_period": "weekly",
  "league": "1",
  "standings": [
    {
      "rank": 1, 
      "user": {"id": 41, "name": "abdishakuuralimohamed"},
      "points": 150,  // ✅ Correct points
      "streak": 1
    }
  ]
}
```

## Future Maintenance

1. **Weekly Reset**: Consider implementing automatic weekly point resets
2. **Monthly Reset**: Consider implementing automatic monthly point resets  
3. **Monitoring**: Add logging to track point calculations
4. **Caching**: Consider caching leaderboard results for performance

## Files Modified

1. `leagues/models.py` - Added missing methods
2. `api/models.py` - Fixed award_xp method
3. `leagues/management/commands/fix_league_points.py` - Data fix command
4. `LEAGUE_POINTS_FIX_SOLUTION.md` - This documentation

## Impact

- ✅ League leaderboard will show correct points
- ✅ Users will see their actual progress
- ✅ League promotions will work correctly
- ✅ Gamification system will be functional
- ✅ User engagement will improve 