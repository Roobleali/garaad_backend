#!/usr/bin/env python
"""
Data Verification Script
This script helps verify your database connection and data status
"""

import os
import sys
import django
from decouple import config

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line
from accounts.models import User, StudentProfile
from courses.models import Course, Lesson, UserNotification
from api.models import Streak, DailyActivity

def verify_database_connection():
    """Verify database connection"""
    print("🔍 Verifying Database Connection...")
    
    try:
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Database connected successfully!")
            print(f"📊 PostgreSQL version: {version[0]}")
            
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def check_data_counts():
    """Check data counts in all tables"""
    print("\n📊 Checking Data Counts...")
    
    models_to_check = [
        ('Users', User),
        ('Student Profiles', StudentProfile),
        ('Courses', Course),
        ('Lessons', Lesson),
        ('User Notifications', UserNotification),
        ('Streaks', Streak),
        ('Daily Activities', DailyActivity),
    ]
    
    total_records = 0
    
    for name, model in models_to_check:
        try:
            count = model.objects.count()
            print(f"📋 {name}: {count} records")
            total_records += count
        except Exception as e:
            print(f"❌ Error checking {name}: {str(e)}")
    
    print(f"\n🎯 Total records across all tables: {total_records}")
    return total_records

def check_environment_variables():
    """Check if required environment variables are set"""
    print("\n🔧 Checking Environment Variables...")
    
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'RESEND_API_KEY',
        'FROM_EMAIL'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = config(var, default=None)
        if value:
            # Show first few characters for security
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("\n✅ All required environment variables are set!")
        return True

def check_specific_data():
    """Check specific data that should exist"""
    print("\n🔍 Checking Specific Data...")
    
    # Check if there are any users
    user_count = User.objects.count()
    print(f"👥 Users: {user_count}")
    
    if user_count > 0:
        # Show first user
        first_user = User.objects.first()
        print(f"   First user: {first_user.email} (created: {first_user.date_joined})")
    
    # Check if there are any courses
    course_count = Course.objects.count()
    print(f"📚 Courses: {course_count}")
    
    if course_count > 0:
        # Show first course
        first_course = Course.objects.first()
        print(f"   First course: {first_course.title}")
    
    # Check if there are any lessons
    lesson_count = Lesson.objects.count()
    print(f"📖 Lessons: {lesson_count}")
    
    # Check if there are any notifications
    notification_count = UserNotification.objects.count()
    print(f"🔔 Notifications: {notification_count}")

def main():
    """Main verification function"""
    print("🚀 Garaad Backend Data Verification")
    print("=" * 50)
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    if not env_ok:
        print("\n❌ Environment variables are missing. Please check your configuration.")
        return
    
    # Check database connection
    if not verify_database_connection():
        print("\n❌ Cannot connect to database. Please check your DATABASE_URL.")
        return
    
    # Check data counts
    total_records = check_data_counts()
    
    # Check specific data
    check_specific_data()
    
    print("\n" + "=" * 50)
    if total_records > 0:
        print("✅ Data verification completed successfully!")
        print(f"📊 Your database contains {total_records} records")
    else:
        print("⚠️  No data found in database")
        print("💡 This might be normal for a new deployment")
    
    print("\n🔧 Next steps:")
    print("1. Check your Render deployment logs")
    print("2. Verify environment variables in Render dashboard")
    print("3. If data is missing, check your Supabase dashboard directly")
    print("4. Use your backup files if needed: python restore_django.py")

if __name__ == "__main__":
    main() 