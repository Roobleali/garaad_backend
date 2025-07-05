#!/bin/bash

# Notification processing script
# This script should be run by cron to process scheduled notifications

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the Django project directory
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set environment variables if .env file exists
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Process scheduled notifications
echo "$(date): Processing scheduled notifications..." >> logs/notifications.log
python manage.py send_notifications >> logs/notifications.log 2>&1

# Check for real-time notifications
echo "$(date): Checking real-time notifications..." >> logs/notifications.log
python manage.py check_real_time_notifications >> logs/notifications.log 2>&1

# Clean up old log files (keep last 30 days)
find logs/ -name "*.log" -mtime +30 -delete
