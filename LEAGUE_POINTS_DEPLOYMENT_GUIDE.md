# League Points Fix - Deployment Guide

## Overview

This guide will help you deploy and test the league points calculation fix to production.

## Step 1: Deploy Code Changes

The code changes have already been pushed to GitHub. Railway should automatically deploy them.

### Verify Deployment

1. **Check Railway Dashboard**:
   - Go to your Railway project dashboard
   - Verify the latest deployment is successful
   - Check the deployment logs for any errors

2. **Test API Health**:
   ```bash
   curl https://api.garaad.org/api/health/
   ```

## Step 2: Run Data Fix Command

Since Railway doesn't provide direct shell access on the free plan, you have two options:

### Option A: Use Railway Console (Recommended)

1. **Access Railway Console**:
   - Go to your Railway project dashboard
   - Click on your service
   - Go to the "Deployments" tab
   - Click on the latest deployment
   - Click "View Logs" or "Console"

2. **Run the Fix Command**:
   ```bash
   python manage.py fix_league_points
   ```

### Option B: Add to Deployment Script

The `railway-setup.sh` script has been updated to include the fix command. Railway will run this automatically on the next deployment.

## Step 3: Verify the Fix

### Test 1: Check API Endpoints

Run the test script:
```bash
python test_league_leaderboard.py
```

### Test 2: Manual API Testing

1. **Get a JWT Token**:
   ```bash
   curl -X POST https://api.garaad.org/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username":"your_username","password":"your_password"}'
   ```

2. **Test League Leaderboard**:
   ```bash
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     https://api.garaad.org/api/leagues/leaderboard/
   ```

3. **Test League Status**:
   ```bash
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     https://api.garaad.org/api/leagues/status/
   ```

### Expected Results

**Before Fix**:
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

**After Fix**:
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

## Step 4: Monitor and Verify

### Check Points Sources

Verify that points are being calculated from:
- Problem completions (5-20 XP each)
- Streak bonuses (20 XP daily)
- Milestone bonuses (50 XP for 7/30/100 day streaks)
- Perfect scores (50 XP bonus)
- Achievements (various XP)

### Test User Activity

1. **Complete a lesson** and verify points increase
2. **Maintain a streak** and verify streak bonuses
3. **Achieve milestones** and verify milestone bonuses

## Step 5: Troubleshooting

### If Points Are Still 0

1. **Check UserReward Records**:
   ```bash
   # In Railway console
   python manage.py shell
   ```
   ```python
   from courses.models import UserReward
   from leagues.models import UserLeague
   
   # Check if users have reward records
   UserReward.objects.filter(reward_type='points').count()
   
   # Check UserLeague records
   UserLeague.objects.all().values('user__username', 'weekly_xp', 'total_xp')
   ```

2. **Re-run Fix Command**:
   ```bash
   python manage.py fix_league_points
   ```

3. **Check for Errors**:
   - Review Railway deployment logs
   - Check for database connection issues
   - Verify all migrations are applied

### If API Returns Errors

1. **Check Railway Logs**:
   - Go to Railway dashboard
   - Check service logs for errors
   - Look for Django error messages

2. **Test Database Connection**:
   ```bash
   python manage.py dbshell
   ```

3. **Verify Environment Variables**:
   - Check Railway environment variables
   - Ensure database URL is correct

## Step 6: Performance Monitoring

### Monitor Points Calculation

1. **Check Query Performance**:
   - Monitor database query times
   - Look for slow queries in logs

2. **Consider Caching**:
   - League leaderboards can be cached
   - Implement Redis caching if needed

### Future Improvements

1. **Automatic Resets**:
   - Implement weekly point resets
   - Implement monthly point resets

2. **Real-time Updates**:
   - Consider WebSocket updates for live leaderboards
   - Implement real-time point notifications

## Success Criteria

✅ **League leaderboard shows correct points (not 0)**
✅ **Users can see their actual progress**
✅ **League promotions work correctly**
✅ **Gamification system is functional**
✅ **User engagement improves**

## Rollback Plan

If issues occur:

1. **Revert Code Changes**:
   ```bash
   git revert 8d6cde6  # Revert the league points fix commit
   git push origin main
   ```

2. **Restore Database**:
   - Use Railway database backups
   - Restore from previous state

3. **Monitor and Debug**:
   - Check logs for specific errors
   - Test in development environment first

## Support

If you encounter issues:

1. Check the comprehensive solution document: `LEAGUE_POINTS_FIX_SOLUTION.md`
2. Review Railway deployment logs
3. Test endpoints manually with curl
4. Verify database state in Railway console

## Files Modified

- `leagues/models.py` - Added missing methods
- `api/models.py` - Fixed award_xp method  
- `leagues/management/commands/fix_league_points.py` - Data fix command
- `railway-setup.sh` - Updated deployment script
- `test_league_leaderboard.py` - Test script
- `LEAGUE_POINTS_DEPLOYMENT_GUIDE.md` - This guide 