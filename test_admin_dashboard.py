#!/usr/bin/env python
"""
Test script for Admin Dashboard API
Run this to verify the admin dashboard endpoints are working correctly.
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.admin_dashboard import AdminDashboardService
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
import json

User = get_user_model()

def test_admin_dashboard():
    """Test the admin dashboard service"""
    print("🔍 Testing Admin Dashboard Service...")
    
    try:
        # Test the main dashboard data function
        dashboard_data = AdminDashboardService.get_dashboard_data()
        
        print("✅ Dashboard data generated successfully!")
        print(f"📊 Overview metrics:")
        print(f"   - Total Users: {dashboard_data['overview']['total_users']}")
        print(f"   - Total Courses: {dashboard_data['overview']['total_courses']}")
        print(f"   - Active Users: {dashboard_data['overview']['active_users']}")
        print(f"   - Completion Rate: {dashboard_data['overview']['completion_rate']}%")
        
        print(f"\n👥 User Analytics:")
        print(f"   - Premium Users: {dashboard_data['users']['premium_users']}")
        print(f"   - Free Users: {dashboard_data['users']['free_users']}")
        print(f"   - High Engagement: {dashboard_data['users']['engagement_levels']['high']}")
        
        print(f"\n💰 Revenue Metrics:")
        print(f"   - Total Premium: {dashboard_data['revenue']['subscription_breakdown']['total_premium']}")
        print(f"   - Estimated MRR: ${dashboard_data['revenue']['estimated_revenue']['mrr']}")
        print(f"   - Conversion Rate: {dashboard_data['revenue']['conversion_rate']}%")
        
        print(f"\n🎯 System Health:")
        print(f"   - Database Records: {sum(dashboard_data['system']['database_stats'].values())}")
        print(f"   - Active Alerts: {len(dashboard_data['alerts'])}")
        
        if dashboard_data['alerts']:
            print(f"\n⚠️  Active Alerts:")
            for alert in dashboard_data['alerts']:
                print(f"   - {alert['type'].upper()}: {alert['title']} ({alert['count']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_services():
    """Test individual service methods"""
    print("\n🧪 Testing Individual Services...")
    
    services = [
        ('Overview Stats', AdminDashboardService.get_overview_stats),
        ('User Stats', AdminDashboardService.get_user_stats),
        ('Course Stats', AdminDashboardService.get_course_stats),
        ('Learning Stats', AdminDashboardService.get_learning_stats),
        ('Engagement Stats', AdminDashboardService.get_engagement_stats),
        ('Revenue Stats', AdminDashboardService.get_revenue_stats),
        ('System Stats', AdminDashboardService.get_system_stats),
        ('Recent Activity', AdminDashboardService.get_recent_activity),
        ('Top Performers', AdminDashboardService.get_top_performers),
        ('System Alerts', AdminDashboardService.get_system_alerts),
    ]
    
    results = {}
    for name, service_func in services:
        try:
            result = service_func()
            results[name] = True
            print(f"   ✅ {name}: OK")
        except Exception as e:
            results[name] = False
            print(f"   ❌ {name}: ERROR - {str(e)}")
    
    return results

def create_test_superuser():
    """Create a test superuser if none exists"""
    print("\n👤 Checking for superuser...")
    
    superusers = User.objects.filter(is_superuser=True)
    if superusers.exists():
        print(f"   ✅ Found {superusers.count()} superuser(s)")
        return superusers.first()
    else:
        print("   ⚠️  No superuser found. Creating test superuser...")
        try:
            user = User.objects.create_superuser(
                username='admin_test',
                email='admin@test.com',
                password='testpass123'
            )
            print("   ✅ Test superuser created successfully!")
            print("   📧 Email: admin@test.com")
            print("   🔑 Password: testpass123")
            return user
        except Exception as e:
            print(f"   ❌ Failed to create superuser: {str(e)}")
            return None

def main():
    """Run all tests"""
    print("🚀 Admin Dashboard Test Suite")
    print("=" * 50)
    
    # Check for superuser
    superuser = create_test_superuser()
    
    # Test the dashboard service
    dashboard_success = test_admin_dashboard()
    
    # Test individual services
    individual_results = test_individual_services()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 50)
    
    if dashboard_success:
        print("✅ Main Dashboard Service: PASSED")
    else:
        print("❌ Main Dashboard Service: FAILED")
    
    passed_services = sum(1 for result in individual_results.values() if result)
    total_services = len(individual_results)
    print(f"✅ Individual Services: {passed_services}/{total_services} PASSED")
    
    if passed_services == total_services and dashboard_success:
        print("\n🎉 All tests PASSED! Admin Dashboard is ready to use.")
        print("\n📖 Next Steps:")
        print("1. Start your Django server: python manage.py runserver")
        print("2. Login as admin user")
        print("3. Access dashboard at: /api/admin/dashboard/")
        print("4. Check documentation: docs/ADMIN_DASHBOARD_API.md")
    else:
        print("\n⚠️  Some tests FAILED. Please check the errors above.")
    
    return dashboard_success and passed_services == total_services

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 