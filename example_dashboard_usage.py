#!/usr/bin/env python
"""
Example: How to Use the Admin Dashboard API

This script demonstrates how to fetch and display admin dashboard data
for the Garaad LMS platform.
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000/api"  # Change to your server URL
ADMIN_EMAIL = "admin@test.com"
ADMIN_PASSWORD = "testpass123"

class AdminDashboardClient:
    def __init__(self, base_url, email, password):
        self.base_url = base_url
        self.token = None
        self.login(email, password)
    
    def login(self, email, password):
        """Login and get JWT token"""
        login_url = f"{self.base_url}/auth/signin/"
        response = requests.post(login_url, json={
            "email": email,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get('access') or data.get('tokens', {}).get('access')
            print("✅ Successfully logged in as admin")
        else:
            print(f"❌ Login failed: {response.text}")
            self.token = None
    
    def get_headers(self):
        """Get request headers with authorization"""
        if not self.token:
            raise ValueError("Not authenticated. Please login first.")
        
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def get_dashboard_data(self):
        """Fetch complete dashboard data"""
        url = f"{self.base_url}/admin/dashboard/"
        response = requests.get(url, headers=self.get_headers())
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            print("❌ Access denied. Make sure you have admin privileges.")
            return None
        else:
            print(f"❌ Error fetching dashboard: {response.text}")
            return None
    
    def get_user_analytics(self):
        """Fetch user analytics"""
        url = f"{self.base_url}/admin/users/"
        response = requests.get(url, headers=self.get_headers())
        return response.json() if response.status_code == 200 else None
    
    def get_course_analytics(self):
        """Fetch course analytics"""
        url = f"{self.base_url}/admin/courses/"
        response = requests.get(url, headers=self.get_headers())
        return response.json() if response.status_code == 200 else None
    
    def get_revenue_report(self):
        """Fetch revenue report"""
        url = f"{self.base_url}/admin/revenue/"
        response = requests.get(url, headers=self.get_headers())
        return response.json() if response.status_code == 200 else None
    
    def get_user_activity(self, period="today", limit=50):
        """Fetch user activity"""
        url = f"{self.base_url}/admin/activity/"
        params = {"period": period, "limit": limit}
        response = requests.get(url, headers=self.get_headers(), params=params)
        return response.json() if response.status_code == 200 else None

def display_dashboard_summary(dashboard_data):
    """Display a summary of dashboard data"""
    if not dashboard_data or not dashboard_data.get('success'):
        print("❌ No dashboard data available")
        return
    
    data = dashboard_data['data']
    
    print("\n" + "="*60)
    print("📊 GARAAD LMS ADMIN DASHBOARD SUMMARY")
    print("="*60)
    
    # Overview
    overview = data['overview']
    print(f"\n🎯 OVERVIEW")
    print(f"   Total Users: {overview['total_users']:,}")
    print(f"   Total Courses: {overview['total_courses']}")
    print(f"   Active Users (7 days): {overview['active_users']:,}")
    print(f"   Course Completion Rate: {overview['completion_rate']}%")
    
    # Users
    users = data['users']
    print(f"\n👥 USER ANALYTICS")
    print(f"   Premium Users: {users['premium_users']:,}")
    print(f"   Free Users: {users['free_users']:,}")
    print(f"   Active Today: {users['active_users']['today']}")
    print(f"   Active This Week: {users['active_users']['week']}")
    print(f"   New This Week: {users['new_registrations']['week']}")
    
    # Engagement
    engagement = users['engagement_levels']
    print(f"\n🎯 ENGAGEMENT LEVELS")
    print(f"   High Engagement (7+ day streaks): {engagement['high']}")
    print(f"   Medium Engagement (3-6 day streaks): {engagement['medium']}")
    print(f"   Low Engagement (1-2 day streaks): {engagement['low']}")
    
    # Revenue
    revenue = data['revenue']
    print(f"\n💰 REVENUE ANALYTICS")
    print(f"   Monthly Subscriptions: {revenue['subscription_breakdown']['monthly']}")
    print(f"   Yearly Subscriptions: {revenue['subscription_breakdown']['yearly']}")
    print(f"   Lifetime Subscriptions: {revenue['subscription_breakdown']['lifetime']}")
    print(f"   Estimated MRR: ${revenue['estimated_revenue']['mrr']:,.2f}")
    print(f"   Estimated ARR: ${revenue['estimated_revenue']['arr']:,.2f}")
    print(f"   Conversion Rate: {revenue['conversion_rate']}%")
    
    # Learning
    learning = data['learning']
    print(f"\n📚 LEARNING METRICS")
    print(f"   Problems Solved Today: {learning['today_activity']['total_problems']}")
    print(f"   Users Active Today: {learning['today_activity']['total_users']}")
    print(f"   Complete Sessions Today: {learning['today_activity']['complete_sessions']}")
    print(f"   Total XP Earned: {learning['xp_stats']['total_xp']:,}")
    print(f"   Average User XP: {learning['xp_stats']['avg_xp']}")
    
    # Alerts
    alerts = data['alerts']
    if alerts:
        print(f"\n⚠️  SYSTEM ALERTS ({len(alerts)})")
        for alert in alerts:
            print(f"   {alert['type'].upper()}: {alert['title']} - {alert['message']}")
    else:
        print(f"\n✅ SYSTEM STATUS: All systems normal")
    
    print(f"\n📅 Generated at: {dashboard_data['generated_at']}")
    print("="*60)

def main():
    """Main function to demonstrate dashboard usage"""
    print("🚀 Garaad LMS Admin Dashboard Example")
    print("="*50)
    
    # Initialize client
    client = AdminDashboardClient(API_BASE_URL, ADMIN_EMAIL, ADMIN_PASSWORD)
    
    if not client.token:
        print("❌ Authentication failed. Please check credentials.")
        return
    
    # Fetch and display complete dashboard
    print("\n📊 Fetching complete dashboard data...")
    dashboard_data = client.get_dashboard_data()
    
    if dashboard_data:
        display_dashboard_summary(dashboard_data)
    else:
        print("❌ Failed to fetch dashboard data")
        return
    
    # Example: Fetch specific analytics
    print("\n🔍 Fetching specific analytics...")
    
    # User analytics
    user_data = client.get_user_analytics()
    if user_data:
        recent_users = user_data['data']['recent_active_users']
        print(f"\n👤 Recent Active Users ({len(recent_users)}):")
        for user in recent_users[:5]:  # Show top 5
            print(f"   - {user['username']} ({'Premium' if user['is_premium'] else 'Free'})")
    
    # Real-time activity
    activity_data = client.get_user_activity(period="today", limit=10)
    if activity_data:
        activities = activity_data['data']['recent_activities']
        print(f"\n📈 Recent Activity ({len(activities)}):")
        for activity in activities[:5]:  # Show top 5
            print(f"   - {activity['username']}: {activity['problems_solved']} problems solved")
    
    print("\n✅ Dashboard example completed successfully!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard example interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc() 