#!/bin/bash

# Setup script for notification processing
# This script helps set up automated notification processing

echo "Setting up notification processing..."

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create a log directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/logs"

# Create the notification processing script
cat > "$SCRIPT_DIR/process_notifications.sh" << 'EOF'
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

# Process notifications and log the output
python manage.py send_notifications >> logs/notifications.log 2>&1

# Clean up old log files (keep last 30 days)
find logs/ -name "*.log" -mtime +30 -delete
EOF

# Make the script executable
chmod +x "$SCRIPT_DIR/process_notifications.sh"

echo "Created notification processing script: $SCRIPT_DIR/process_notifications.sh"

# Show cron setup instructions
echo ""
echo "=== CRON SETUP INSTRUCTIONS ==="
echo "To set up automated notification processing, add the following to your crontab:"
echo ""
echo "# Run notification processing every 5 minutes"
echo "*/5 * * * * $SCRIPT_DIR/process_notifications.sh"
echo ""
echo "# Or run it every hour"
echo "0 * * * * $SCRIPT_DIR/process_notifications.sh"
echo ""
echo "To edit your crontab, run:"
echo "crontab -e"
echo ""
echo "To view your current crontab:"
echo "crontab -l"
echo ""
echo "=== TESTING ==="
echo "To test the notification system manually, run:"
echo "python manage.py debug_notifications"
echo ""
echo "To test email sending:"
echo "python manage.py debug_notifications --test-email --user-id <USER_ID>"
echo ""
echo "To fix notifications scheduled in the past:"
echo "python manage.py debug_notifications --fix-scheduled"
echo ""
echo "=== LOGS ==="
echo "Notification processing logs will be saved to: $SCRIPT_DIR/logs/notifications.log"
echo ""
echo "Setup complete!" 