# Notification Email Troubleshooting Guide

## Overview
This guide helps diagnose and fix issues with notification emails in the Garaad LMS system.

## Common Issues and Solutions

### 1. **Emails Not Being Sent**

#### Check Environment Variables
Ensure these environment variables are properly set:
```bash
RESEND_API_KEY=your_resend_api_key
FROM_EMAIL=your_verified_email@domain.com
RESEND_TEST_MODE=False  # Set to True for testing
```

#### Test Email Configuration
```bash
python manage.py debug_notifications --test-email --user-id <USER_ID>
```

#### Check Resend API Status
- Verify your Resend API key is valid
- Check if your sending domain is verified in Resend
- Ensure you haven't exceeded your email sending limits

### 2. **Notifications Not Being Processed**

#### Check if Scheduled Tasks are Running
The notification system requires a scheduled task to process notifications:

```bash
# Run manually to test
python manage.py send_notifications

# Set up automated processing (see setup_notification_cron.sh)
```

#### Check for Past Scheduled Notifications
```bash
python manage.py debug_notifications --fix-scheduled
```

#### Verify Timezone Settings
The system uses UTC timezone. Check if notifications are being scheduled correctly:
```bash
python manage.py debug_notifications
```

### 3. **Date/Time Issues**

#### Timezone Handling
- The system uses UTC timezone (`TIME_ZONE = 'UTC'` in settings.py)
- User preferences are converted to UTC for scheduling
- Check if user timezone preferences are being handled correctly

#### Scheduling Logic Issues
The scheduling logic has been improved to handle edge cases:
- If reminder time has passed today, schedule for tomorrow
- Ensure notifications are never scheduled in the past
- Add 5-minute buffer for immediate notifications

### 4. **Email Template Issues**

#### Check Template Files
Ensure these template files exist:
- `templates/emails/daily_goal.html`
- `templates/emails/streak_reminder.html`
- `templates/emails/achievement_earned.html`
- `templates/emails/league_update.html`

#### Template Context Issues
Check if all required context variables are available:
- `user`
- `notification`
- `site_url`
- `study_badge`
- `goal_badge`
- `daily_goal_minutes`
- `preferred_study_time`

### 5. **Database Issues**

#### Check Notification Records
```bash
python manage.py shell
```
```python
from courses.models import UserNotification
from django.utils import timezone

# Check pending notifications
pending = UserNotification.objects.filter(is_sent=False)
print(f"Pending notifications: {pending.count()}")

# Check due notifications
due = UserNotification.objects.filter(
    is_sent=False, 
    scheduled_for__lte=timezone.now()
)
print(f"Due notifications: {due.count()}")

# Check recent notifications
recent = UserNotification.objects.order_by('-created_at')[:5]
for n in recent:
    print(f"{n.user.username}: {n.notification_type} - {'SENT' if n.is_sent else 'PENDING'}")
```

### 6. **User Profile Issues**

#### Check User Profile Data
Ensure users have proper profile data:
```python
from accounts.models import User

user = User.objects.get(id=<USER_ID>)
print(f"Has student_profile: {hasattr(user, 'student_profile')}")
print(f"Has useronboarding: {hasattr(user, 'useronboarding')}")

if hasattr(user, 'student_profile'):
    profile = user.student_profile
    print(f"Daily goal minutes: {profile.daily_goal_minutes}")
    print(f"Preferred study time: {profile.get_preferred_study_time_display()}")
```

## Debugging Commands

### 1. **Debug Notifications**
```bash
python manage.py debug_notifications
```

### 2. **Test Email Sending**
```bash
python manage.py debug_notifications --test-email --user-id <USER_ID>
```

### 3. **Fix Past Scheduled Notifications**
```bash
python manage.py debug_notifications --fix-scheduled
```

### 4. **Process Notifications Manually**
```bash
python manage.py send_notifications
```

## Setup Automated Processing

### 1. **Using Cron (Linux/Mac)**
```bash
# Run the setup script
./setup_notification_cron.sh

# Add to crontab (every 5 minutes)
*/5 * * * * /path/to/garaad_backend/process_notifications.sh

# Or every hour
0 * * * * /path/to/garaad_backend/process_notifications.sh
```

### 2. **Using Windows Task Scheduler**
- Create a batch file with the notification processing command
- Schedule it to run every 5 minutes or hourly

### 3. **Using Cloud Services**
- **Railway**: Add a worker dyno with the notification command
- **Heroku**: Use Heroku Scheduler add-on
- **AWS**: Use AWS Lambda with EventBridge

## Logging and Monitoring

### 1. **Check Application Logs**
```bash
# Check Django logs
tail -f logs/django.log

# Check notification processing logs
tail -f logs/notifications.log
```

### 2. **Monitor Email Sending**
- Check Resend dashboard for delivery status
- Monitor bounce rates and spam complaints
- Check email sending limits

### 3. **Database Monitoring**
```sql
-- Check notification statistics
SELECT 
    notification_type,
    COUNT(*) as total,
    SUM(CASE WHEN is_sent THEN 1 ELSE 0 END) as sent,
    SUM(CASE WHEN NOT is_sent THEN 1 ELSE 0 END) as pending
FROM courses_usernotification 
GROUP BY notification_type;
```

## Common Error Messages

### 1. **"RESEND_API_KEY is not configured"**
- Set the `RESEND_API_KEY` environment variable
- Restart your application after setting the variable

### 2. **"Failed to send email: 401 Unauthorized"**
- Check if your Resend API key is valid
- Verify the API key has proper permissions

### 3. **"No template found for notification type"**
- Check if the notification type exists in the templates dictionary
- Verify the template file exists in the templates directory

### 4. **"User has no student_profile"**
- Ensure users complete their profile setup
- Check if the profile creation process is working correctly

## Performance Optimization

### 1. **Batch Processing**
- Process notifications in batches to avoid memory issues
- Use database transactions for consistency

### 2. **Email Rate Limiting**
- Implement rate limiting to avoid hitting API limits
- Use email queues for high-volume sending

### 3. **Database Indexing**
- Ensure proper indexes on notification tables
- Monitor query performance for large datasets

## Testing

### 1. **Unit Tests**
```bash
python manage.py test courses.tests.test_notification_gamification
```

### 2. **Integration Tests**
```bash
python manage.py test courses.tests.test_integrated_gamification
```

### 3. **Manual Testing**
- Create test users with different notification preferences
- Test various notification types
- Verify email delivery and content

## Support

If you continue to experience issues:
1. Check the logs for specific error messages
2. Verify all environment variables are set correctly
3. Test email sending manually
4. Check Resend API status and limits
5. Review the notification scheduling logic 