#!/usr/bin/env python
"""
Standalone script to apply the diagrams migration.
This can be run during deployment to ensure the diagrams field exists.
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line
from django.db import connection

def setup_django():
    """Set up Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
    django.setup()

def check_diagrams_column_exists():
    """Check if the diagrams column already exists"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='courses_problem' 
                AND column_name='diagrams';
            """)
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        print(f"Error checking column existence: {e}")
        return False

def apply_diagrams_migration():
    """Apply the diagrams migration"""
    print("🚀 Starting diagrams migration application...")
    
    try:
        # Setup Django
        setup_django()
        
        # Check if migration is needed
        if check_diagrams_column_exists():
            print("✅ Diagrams column already exists. No migration needed.")
            return True
            
        print("📊 Diagrams column not found. Applying migration...")
        
        # Apply all pending migrations
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Verify the column was created
        if check_diagrams_column_exists():
            print("✅ Successfully applied diagrams migration!")
            return True
        else:
            print("❌ Migration applied but diagrams column still not found.")
            return False
            
    except Exception as e:
        print(f"❌ Error applying diagrams migration: {e}")
        return False

if __name__ == "__main__":
    success = apply_diagrams_migration()
    sys.exit(0 if success else 1) 