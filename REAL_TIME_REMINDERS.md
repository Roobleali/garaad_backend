# Real-Time Email Reminders System

## Overview
The real-time reminder system sends email notifications to users based on their behavior, activity patterns, and specific events rather than just scheduled times.

## When Emails Are Sent

### 1. **Inactivity Reminders** 📅
**Triggered when:** User hasn't completed any lessons for a certain number of days

**Email Schedule:**
- **1 day inactive:** "Maanta waa maalin wanaagsan oo aad ku baran karto! 🌟"
- **3 days inactive:** "Waxaad horey u qaadatay 3 maalmood! 🔥"
- **7 days inactive:** "Toddobaad cusub! 🎯"
- **14+ days inactive:** "Soo noqo waxbarashada! 📚"

**Code Logic:**
```python
# Check user's last activity date
if last_activity_date:
    days_inactive = (today - last_activity_date).days
    
    if days_inactive == 1:
        send_inactivity_reminder(user, 1)
    elif days_inactive == 3:
        send_inactivity_reminder(user, 3)
    elif days_inactive == 7:
        send_inactivity_reminder(user, 7)
    elif days_inactive >= 14:
        send_inactivity_reminder(user, days_inactive)
```

### 2. **Streak Break Reminders** 🔥
**Triggered when:** User breaks their learning streak

**Email Content:** "Xariggaaga waa la jebiyay 😔"

**Code Logic:**
```python
# Check if user broke their streak
if last_activity_date and (today - last_activity_date).days > 1:
    if current_streak > 0:
        send_streak_break_reminder(user, current_streak)
```

### 3. **Goal Reminders** 🎯
**Triggered when:** Based on user's daily, weekly, or monthly goals

**Types:**
- **Daily:** "Waqtiga Waxbarashada! (30 Daqiiqo) 🎯"
- **Weekly:** "Hadafka Usbuuca! 📅"
- **Monthly:** "Hadafka Bilka! 🌟"

### 4. **Motivational Reminders** 💪
**Triggered when:** User reaches specific milestones

**Types:**
- **First Lesson:** "Hambalyo! Casharka ugu horeysa! 🎉"
- **Streak Milestones:** "Xariggaaga waa la socdaa! 🔥" (at 5, 10, 30, 100 days)
- **Level Up:** "Heerkaaga waa la kor dhigay! ⬆️"
- **General:** "Waxbarasho waa guul! 💪"

### 5. **Immediate Reminders** ⚡
**Triggered when:** Manual or urgent notifications needed

**Types:**
- **Custom:** User-defined message
- **Urgent:** "Waxbarasho Degdeg ah! ⚡"
- **General:** "Waxbarasho! 📖"

## How to Trigger Real-Time Reminders

### 1. **Automatic Triggers**
The system automatically checks and sends reminders when:
- User completes a lesson (triggers streak and goal checks)
- User logs in after a period of inactivity
- Daily/weekly/monthly goal periods end
- Streak milestones are reached

### 2. **Manual Triggers**
You can manually trigger reminders using the management command:

```bash
# Test all reminder types
python manage.py test_real_time_reminders --user-id 41

# Test specific reminder types
python manage.py test_real_time_reminders --user-id 41 --reminder-type inactivity --days-inactive 3
python manage.py test_real_time_reminders --user-id 41 --reminder-type streak_break --streak-days 5
python manage.py test_real_time_reminders --user-id 41 --reminder-type goal --goal-type daily
python manage.py test_real_time_reminders --user-id 41 --reminder-type motivational --motivation-type first_lesson
python manage.py test_real_time_reminders --user-id 41 --reminder-type immediate --custom-message "Your custom message here"
```

### 3. **Programmatic Triggers**
You can trigger reminders from your code:

```python
from courses.services import NotificationService

# Send inactivity reminder
NotificationService.send_inactivity_reminder(user, days_inactive=3)

# Send streak break reminder
NotificationService.send_streak_break_reminder(user, broken_streak_days=5)

# Send goal reminder
NotificationService.send_goal_reminder(user, goal_type='daily')

# Send motivational reminder
NotificationService.send_motivational_reminder(user, motivation_type='first_lesson')

# Send immediate reminder
NotificationService.send_immediate_reminder(user, 'custom', 'Your message here')

# Check and send all appropriate reminders
NotificationService.check_and_send_real_time_reminders(user)
```

## Integration Points

### 1. **Lesson Completion**
When a user completes a lesson, automatically check for reminders:

```python
# In your lesson completion view
def complete_lesson(request, lesson_id):
    # ... existing lesson completion logic ...
    
    # Check for real-time reminders
    NotificationService.check_and_send_real_time_reminders(user)
    
    return response
```

### 2. **User Login**
When a user logs in, check if they need reminders:

```python
# In your login view
def user_login(request):
    # ... existing login logic ...
    
    # Check for reminders if user was inactive
    NotificationService.check_and_send_real_time_reminders(user)
    
    return response
```

### 3. **Daily Cron Job**
Set up a daily cron job to check all users:

```bash
# Add to crontab
0 9 * * * /path/to/garaad_backend/check_all_users_reminders.sh
```

Create the script:
```bash
#!/bin/bash
cd /path/to/garaad_backend
python manage.py shell -c "
from accounts.models import User
from courses.services import NotificationService

for user in User.objects.all():
    NotificationService.check_and_send_real_time_reminders(user)
"
```

## Email Templates

Each reminder type uses specific email templates:

- **Inactivity:** `templates/emails/inactivity_reminder.html`
- **Streak Break:** `templates/emails/streak_break.html`
- **Goal:** `templates/emails/goal_reminder.html`
- **Motivational:** `templates/emails/motivational.html`
- **Immediate:** `templates/emails/immediate_reminder.html`

## Configuration

### User Preferences
Users can set their preferences in their UserOnboarding:
- **Minutes per day:** How many minutes they want to study daily (`minutes_per_day`)
- **Preferred study time:** When they prefer to study (`preferred_study_time` - morning, afternoon, evening, flexible)
- **Learning approach:** Their preferred learning method
- **Math level:** Their current math proficiency level
- **Topic:** Their preferred learning topic

### System Settings
Configure reminder thresholds in `courses/services.py`:
```python
# Inactivity thresholds
INACTIVITY_THRESHOLDS = [1, 3, 7, 14]

# Streak milestone thresholds
STREAK_MILESTONES = [5, 10, 30, 100]

# Goal reminder types
GOAL_TYPES = ['daily', 'weekly', 'monthly']

# Time display mapping
TIME_DISPLAY_MAP = {
    'morning': 'Subax',
    'afternoon': 'Galab', 
    'evening': 'Fiid',
    'flexible': 'Waqti kasta'
}
```

## Testing

### 1. **Test Individual Reminders**
```bash
python manage.py test_real_time_reminders --user-id 41 --reminder-type inactivity
```

### 2. **Test All Reminders**
```bash
python manage.py test_real_time_reminders --user-id 41
```

### 3. **Test with Custom Messages**
```bash
python manage.py test_real_time_reminders --user-id 41 --reminder-type immediate --custom-message "Test message"
```

## Monitoring

### 1. **Check Reminder Statistics**
```bash
python manage.py debug_notifications
```

### 2. **Monitor Email Delivery**
Check Resend dashboard for delivery status and bounce rates.

### 3. **Log Analysis**
Monitor logs for reminder-related activities:
```bash
tail -f logs/notifications.log | grep "reminder"
```

## Best Practices

1. **Don't Spam Users:** Limit reminder frequency to avoid overwhelming users
2. **Personalize Content:** Use user's name and specific goals in messages
3. **A/B Test Messages:** Test different message styles to see what works best
4. **Monitor Engagement:** Track which reminders lead to user activity
5. **Respect User Preferences:** Allow users to opt out of certain reminder types

## Troubleshooting

### Common Issues:
1. **Emails going to spam:** Improve sender reputation and email content
2. **Too many reminders:** Adjust frequency thresholds
3. **Wrong timing:** Check user timezone settings
4. **Template errors:** Verify email templates exist and are valid

### Debug Commands:
```bash
# Check user's activity status
python manage.py shell -c "
from accounts.models import User
from courses.models import UserProgress
from api.models import Streak

user = User.objects.get(id=41)
last_progress = UserProgress.objects.filter(user=user, status='completed').order_by('-completed_at').first()
streak = Streak.objects.get(user=user)

print(f'Last activity: {last_progress.completed_at if last_progress else None}')
print(f'Current streak: {streak.current_streak}')
print(f'Last activity date: {streak.last_activity_date}')
"
``` 