#!/bin/bash

# Automated Backup Scheduling Script
# Sets up cron jobs for automated database backups

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_SCRIPT="$SCRIPT_DIR/backup-databases.sh"

echo "========================================="
echo "Automated Backup Scheduler Setup"
echo "========================================="
echo ""

# Check if backup script exists
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo "❌ ERROR: Backup script not found: $BACKUP_SCRIPT"
    exit 1
fi

# Make backup script executable
chmod +x "$BACKUP_SCRIPT"

# Create cron job entry
CRON_SCHEDULE=${1:-"0 2 * * *"}  # Default: 2 AM daily
CRON_COMMAND="$BACKUP_SCRIPT >> $PROJECT_ROOT/backups/backup.log 2>&1"
CRON_ENTRY="$CRON_SCHEDULE $CRON_COMMAND"

echo "Cron schedule: $CRON_SCHEDULE"
echo "Command: $CRON_COMMAND"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    echo "⚠️  WARNING: Backup cron job already exists!"
    echo ""
    echo "Current cron jobs:"
    crontab -l | grep "$BACKUP_SCRIPT"
    echo ""
    read -p "Do you want to replace it? (yes/no): " -r
    echo
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        # Remove existing entry
        crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT" | crontab -
        echo "Removed existing cron job"
    else
        echo "Keeping existing cron job. Exiting."
        exit 0
    fi
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job added successfully!"
    echo ""
    echo "Current cron jobs:"
    crontab -l | grep "$BACKUP_SCRIPT"
    echo ""
    echo "Backups will run automatically at: $CRON_SCHEDULE"
    echo "Logs will be written to: $PROJECT_ROOT/backups/backup.log"
else
    echo "❌ ERROR: Failed to add cron job"
    exit 1
fi

echo ""
echo "========================================="
echo "Setup complete!"
echo "========================================="
echo ""
echo "To view cron jobs: crontab -l"
echo "To remove cron job: crontab -e (then delete the line)"
echo "To test backup manually: $BACKUP_SCRIPT"

