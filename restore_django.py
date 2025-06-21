#!/usr/bin/env python
"""
Django-based database restore script for Supabase
This script restores data from JSON backup files
"""

import os
import sys
import django
import json
import glob

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

from django.core import serializers
from django.apps import apps
from django.db import transaction

def restore_database(backup_timestamp=None):
    """Restore data from JSON backup files"""
    
    backup_dir = "database_backups"
    
    if not os.path.exists(backup_dir):
        print("❌ Backup directory not found!")
        return
    
    # Find backup files
    if backup_timestamp:
        pattern = f"{backup_dir}/*_{backup_timestamp}.json"
    else:
        # Get the most recent backup
        summary_files = glob.glob(f"{backup_dir}/backup_summary_*.json")
        if not summary_files:
            print("❌ No backup summary files found!")
            return
        
        # Get the most recent summary file
        latest_summary = max(summary_files, key=os.path.getctime)
        with open(latest_summary, 'r') as f:
            summary = json.load(f)
            backup_timestamp = summary['backup_timestamp']
        
        pattern = f"{backup_dir}/*_{backup_timestamp}.json"
    
    backup_files = glob.glob(pattern)
    backup_files = [f for f in backup_files if not f.endswith('backup_summary.json')]
    
    if not backup_files:
        print(f"❌ No backup files found for timestamp: {backup_timestamp}")
        return
    
    print(f"🔄 Starting restore from backup timestamp: {backup_timestamp}")
    print(f"📁 Found {len(backup_files)} backup files")
    
    total_restored = 0
    
    with transaction.atomic():
        for backup_file in backup_files:
            try:
                # Extract model info from filename
                filename = os.path.basename(backup_file)
                parts = filename.replace('.json', '').split('_')
                app_name = parts[0]
                model_name = parts[1]
                
                # Get the model
                model = apps.get_model(app_name, model_name)
                
                # Read backup data
                with open(backup_file, 'r', encoding='utf-8') as f:
                    serialized_data = f.read()
                
                # Deserialize and save
                objects = serializers.deserialize('json', serialized_data)
                restored_count = 0
                
                for obj in objects:
                    obj.save()
                    restored_count += 1
                
                total_restored += restored_count
                print(f"✅ Restored {app_name}.{model_name}: {restored_count} records")
                
            except Exception as e:
                print(f"❌ Error restoring {backup_file}: {str(e)}")
                raise  # This will rollback the transaction
    
    print(f"\n🎉 Restore completed successfully!")
    print(f"📊 Total records restored: {total_restored}")

if __name__ == "__main__":
    # You can specify a timestamp or use the latest
    timestamp = sys.argv[1] if len(sys.argv) > 1 else None
    restore_database(timestamp) 