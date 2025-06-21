#!/usr/bin/env python
"""
Backup Management Script for Supabase Database
"""

import os
import sys
import glob
import json
from datetime import datetime

def list_backups():
    """List all available backups"""
    backup_dir = "database_backups"
    
    if not os.path.exists(backup_dir):
        print("❌ No backup directory found!")
        return
    
    summary_files = glob.glob(f"{backup_dir}/backup_summary_*.json")
    
    if not summary_files:
        print("❌ No backups found!")
        return
    
    print("📋 Available Backups:")
    print("-" * 50)
    
    for summary_file in sorted(summary_files, reverse=True):
        with open(summary_file, 'r') as f:
            summary = json.load(f)
        
        timestamp = summary['backup_timestamp']
        total_records = summary['total_records']
        backup_files = len(summary['backup_files'])
        
        # Get file size
        file_size = os.path.getsize(summary_file)
        
        print(f"🕒 {timestamp}")
        print(f"   📊 Records: {total_records}")
        print(f"   📁 Files: {backup_files}")
        print(f"   📏 Size: {file_size} bytes")
        print()

def create_backup():
    """Create a new backup"""
    print("🔄 Creating new backup...")
    os.system("python backup_django.py")

def cleanup_old_backups(keep_count=5):
    """Clean up old backups, keeping only the most recent ones"""
    backup_dir = "database_backups"
    
    if not os.path.exists(backup_dir):
        print("❌ No backup directory found!")
        return
    
    summary_files = glob.glob(f"{backup_dir}/backup_summary_*.json")
    
    if len(summary_files) <= keep_count:
        print(f"✅ No cleanup needed. Only {len(summary_files)} backups exist.")
        return
    
    # Sort by creation time (newest first)
    summary_files.sort(key=os.path.getctime, reverse=True)
    
    # Files to delete
    files_to_delete = summary_files[keep_count:]
    
    print(f"🧹 Cleaning up {len(files_to_delete)} old backups...")
    
    for summary_file in files_to_delete:
        try:
            # Read summary to get timestamp
            with open(summary_file, 'r') as f:
                summary = json.load(f)
            timestamp = summary['backup_timestamp']
            
            # Delete all files with this timestamp
            pattern = f"{backup_dir}/*_{timestamp}.json"
            files_to_remove = glob.glob(pattern)
            
            for file_to_remove in files_to_remove:
                os.remove(file_to_remove)
                print(f"🗑️  Deleted: {os.path.basename(file_to_remove)}")
                
        except Exception as e:
            print(f"❌ Error deleting {summary_file}: {str(e)}")
    
    print(f"✅ Cleanup completed! Kept {keep_count} most recent backups.")

def show_help():
    """Show help information"""
    print("""
🔧 Backup Management Script

Usage: python manage_backups.py [command]

Commands:
  list          - List all available backups
  create        - Create a new backup
  cleanup       - Clean up old backups (keep 5 most recent)
  cleanup N     - Clean up old backups (keep N most recent)
  help          - Show this help message

Examples:
  python manage_backups.py list
  python manage_backups.py create
  python manage_backups.py cleanup
  python manage_backups.py cleanup 10
""")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_backups()
    elif command == "create":
        create_backup()
    elif command == "cleanup":
        keep_count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        cleanup_old_backups(keep_count)
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()
        sys.exit(1) 