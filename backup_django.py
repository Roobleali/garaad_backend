#!/usr/bin/env python
"""
Django-based database backup script for Supabase
This script exports data to JSON format, which is safe and doesn't require pg_dump version compatibility
"""

import os
import sys
import django
from datetime import datetime
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')
django.setup()

from django.core import serializers
from django.apps import apps
from django.db import connection

def backup_database():
    """Backup all data from the database to JSON files"""
    
    # Create backup directory
    backup_dir = "database_backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"Starting Django database backup at {timestamp}")
    
    # Get all models
    models = apps.get_models()
    
    total_records = 0
    backup_files = []
    
    for model in models:
        try:
            # Get all records for this model
            records = model.objects.all()
            count = records.count()
            
            if count > 0:
                # Serialize to JSON
                serialized_data = serializers.serialize('json', records)
                
                # Create filename
                app_name = model._meta.app_label
                model_name = model._meta.model_name
                filename = f"{app_name}_{model_name}_{timestamp}.json"
                filepath = os.path.join(backup_dir, filename)
                
                # Save to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(serialized_data)
                
                backup_files.append(filepath)
                total_records += count
                
                print(f"✅ Backed up {app_name}.{model_name}: {count} records")
            
        except Exception as e:
            print(f"❌ Error backing up {model._meta.app_label}.{model._meta.model_name}: {str(e)}")
    
    # Create backup summary
    summary = {
        "backup_timestamp": timestamp,
        "total_records": total_records,
        "backup_files": backup_files,
        "database_info": {
            "engine": connection.settings_dict['ENGINE'],
            "name": connection.settings_dict['NAME'],
            "host": connection.settings_dict.get('HOST', 'localhost'),
        }
    }
    
    summary_file = os.path.join(backup_dir, f"backup_summary_{timestamp}.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\n🎉 Backup completed successfully!")
    print(f"📊 Total records backed up: {total_records}")
    print(f"📁 Backup files created: {len(backup_files)}")
    print(f"📋 Summary file: {summary_file}")
    print(f"📂 Backup directory: {backup_dir}")
    
    return summary

if __name__ == "__main__":
    backup_database() 