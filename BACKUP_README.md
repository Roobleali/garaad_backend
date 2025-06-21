# Supabase Database Backup Guide

This guide explains how to backup and restore your Supabase PostgreSQL database safely.

## 🎯 Overview

Your database backup system includes:
- **Django-based backup** (recommended) - Exports data to JSON format
- **pg_dump backup** (alternative) - Exports to SQL format (requires version compatibility)
- **Backup management tools** - List, create, and manage backups

## 📁 Backup Files Created

When you run a backup, the following files are created in the `database_backups/` directory:

```
database_backups/
├── accounts_user_20250621_062130.json
├── accounts_useronboarding_20250621_062130.json
├── courses_lesson_20250621_062130.json
├── courses_problem_20250621_062130.json
├── ... (one file per model)
└── backup_summary_20250621_062130.json
```

## 🚀 Quick Start

### 1. Create a Backup
```bash
# Using the management script (recommended)
python manage_backups.py create

# Or directly
python backup_django.py
```

### 2. List Available Backups
```bash
python manage_backups.py list
```

### 3. Clean Up Old Backups
```bash
# Keep 5 most recent backups
python manage_backups.py cleanup

# Keep 10 most recent backups
python manage_backups.py cleanup 10
```

## 🔧 Available Scripts

### `backup_django.py`
- **Purpose**: Create a complete backup of all database tables
- **Format**: JSON files (one per model)
- **Safe**: No data loss, creates new files only
- **Compatible**: Works with any PostgreSQL version

### `restore_django.py`
- **Purpose**: Restore data from backup files
- **Usage**: `python restore_django.py [timestamp]`
- **Safe**: Uses database transactions (rollback on error)

### `manage_backups.py`
- **Purpose**: Manage backup operations
- **Commands**: `list`, `create`, `cleanup`, `help`

## 📊 Backup Statistics

Your current backup contains:
- **1,211 total records**
- **20 model files**
- **All user data, courses, lessons, problems, etc.**

## 🔒 Safety Features

1. **No Data Loss**: Backups only create new files, never modify existing data
2. **Transaction Safety**: Restore operations use database transactions
3. **Version Independent**: Django backup works with any PostgreSQL version
4. **Automatic Cleanup**: Can automatically keep only recent backups

## 🚨 Important Notes

### For Supabase Free Plan:
- **Daily backups**: Supabase provides automatic daily backups (7-day retention)
- **Manual backups**: Use these scripts for additional safety
- **No data loss**: These scripts are read-only to your production database

### Before Making Database Changes:
1. **Always create a backup first**
2. **Test changes on a copy if possible**
3. **Keep multiple backup versions**

## 🔄 Restore Process

If you need to restore data:

1. **List available backups**:
   ```bash
   python manage_backups.py list
   ```

2. **Restore from specific backup**:
   ```bash
   python restore_django.py 20250621_062130
   ```

3. **Or restore from latest backup**:
   ```bash
   python restore_django.py
   ```

## 📋 Backup Schedule Recommendations

- **Before major changes**: Always backup
- **Weekly**: Create a backup for safety
- **Monthly**: Clean up old backups (keep 5-10 most recent)

## 🛠️ Troubleshooting

### Backup Fails
- Check your `DATABASE_URL` environment variable
- Ensure you have read access to the database
- Check disk space in the backup directory

### Restore Fails
- Ensure the backup files are complete
- Check database write permissions
- Verify the backup timestamp is correct

### pg_dump Version Mismatch
- Use the Django backup instead (`backup_django.py`)
- Or update your local PostgreSQL client

## 📞 Support

If you encounter issues:
1. Check the error messages in the terminal
2. Verify your database connection
3. Ensure all required files are present

---

**Remember**: Your data is safe! These backup tools are designed to be non-destructive and only create additional copies of your data. 