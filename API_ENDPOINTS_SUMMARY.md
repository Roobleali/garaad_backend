# 📊 Admin Dashboard API Quick Reference

## 🔐 Authentication
All admin endpoints require:
- Valid JWT token
- User must be staff (`is_staff=True`) or superuser (`is_superuser=True`)

## 📡 Endpoints

### 1. Complete Dashboard
```http
GET /api/admin/dashboard/
```
**Returns:** All dashboard metrics in one response
- Overview stats (users, courses, completion rates)
- User analytics (premium/free, engagement levels)
- Course analytics (enrollments, popular courses)
- Learning metrics (XP, streaks, activity)
- Revenue data (MRR, ARR, conversion rates)
- System health & alerts

### 2. User Analytics
```http
GET /api/admin/users/
```
**Returns:** Detailed user statistics
- Total users (premium vs free)
- Active users (today/week/month)
- Engagement levels (high/medium/low)
- New registrations
- Recent active users

### 3. Course Analytics
```http
GET /api/admin/courses/
```
**Returns:** Course and learning data
- Course stats (total, popular, completion rates)
- Learning metrics (daily activity, XP, streaks)
- Problem type breakdown
- Top performers

### 4. Revenue Report
```http
GET /api/admin/revenue/
```
**Returns:** Subscription and revenue data
- Subscription breakdown (monthly/yearly/lifetime)
- Revenue estimates (MRR, ARR)
- Conversion rates
- Churn indicators

### 5. User Activity Monitor
```http
GET /api/admin/activity/?period=today&limit=50
```
**Parameters:**
- `period`: `today`, `week`, `month`
- `limit`: Number of users to return

**Returns:** Real-time activity data
- Active users in time period
- Recent learning activities
- User engagement details

## 📊 Key Metrics

### User Metrics
- **Total Users**: Complete user count
- **Premium Users**: Active subscribers
- **Active Users**: Daily/weekly/monthly activity
- **Last Active**: Recent user activity tracking

### Course Metrics  
- **Total Courses**: All courses available
- **Enrollments**: Course enrollment analytics
- **Completion Rate**: Overall success percentage
- **Popular Content**: Most engaged courses

### Revenue Metrics
- **MRR/ARR**: Monthly/Annual recurring revenue
- **Conversion Rate**: Free to premium conversion
- **Churn Analysis**: Subscription health

### Learning Analytics
- **Daily Activity**: Problems solved, sessions completed
- **XP & Streaks**: Gamification metrics
- **Engagement**: User activity classification

## 🚨 System Alerts
Automatic monitoring for:
- Expired subscriptions
- Inactive premium users  
- Low course completion rates
- High user churn

## 🔧 Example Usage

```bash
# Get complete dashboard
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/admin/dashboard/

# Get user analytics
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/admin/users/

# Get real-time activity 
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/admin/activity/?period=week&limit=100"
```

## 📱 Frontend Integration

Perfect for building admin dashboards with:
- Overview cards showing key metrics
- Charts for trends and distributions
- Real-time activity feeds  
- Alert notifications
- Export capabilities

**All endpoints return JSON data ready for visualization!** 📈 