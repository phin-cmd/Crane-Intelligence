#!/bin/bash
# Script to run draft reminder scheduler
# This should be run via cron every hour to check for 8-hour intervals

cd /root/crane/backend
/usr/bin/python3 -c "
from app.services.draft_reminder_scheduler import send_draft_reminders
result = send_draft_reminders()
print(f'Reminder emails: {result.get(\"sent\", 0)} sent, {result.get(\"skipped\", 0)} skipped, {result.get(\"errors\", 0)} errors')
"

