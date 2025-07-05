#!/usr/bin/env python
"""
Script to apply the referral system migration to production database.
This script should be run on the production server to add the missing referral_code column.
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.contrib.auth import get_user_model

User = get_user_model()

def check_database_schema():
    """Check if the referral_code column exists in the database"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'accounts_user' 
            AND column_name = 'referral_code'
        """)
        result = cursor.fetchone()
        return result is not None

def apply_migration_manually():
    """Apply the referral system migration manually if needed"""
    print("Checking database schema...")
    
    if check_database_schema():
        print("✅ referral_code column already exists")
        return True
    
    print("❌ referral_code column does not exist. Applying migration...")
    
    try:
        # Run the migration
        execute_from_command_line(['manage.py', 'migrate', 'accounts'])
        print("✅ Migration applied successfully")
        return True
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        return False

def populate_referral_codes():
    """Populate referral codes for existing users"""
    print("Populating referral codes for existing users...")
    
    import random
    import string
    
    def generate_referral_code():
        """Generate a unique 8-character alphanumeric referral code"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    users_without_codes = User.objects.filter(referral_code='')
    print(f"Found {users_without_codes.count()} users without referral codes")
    
    for user in users_without_codes:
        # Generate unique referral code
        while True:
            code = generate_referral_code()
            if not User.objects.filter(referral_code=code).exists():
                break
        
        user.referral_code = code
        user.save()
        print(f"✅ Added referral code {code} to user {user.username}")
    
    print("✅ All users now have referral codes")

def main():
    """Main function to apply the migration"""
    print("=== Applying Referral System Migration ===")
    
    # Check if we're in production
    if os.getenv('DEBUG') == 'True':
        print("⚠️  Running in development mode")
    else:
        print("✅ Running in production mode")
    
    # Apply migration
    if apply_migration_manually():
        # Populate referral codes
        populate_referral_codes()
        print("✅ Migration and population completed successfully!")
    else:
        print("❌ Failed to apply migration")
        sys.exit(1)

if __name__ == '__main__':
    main() 