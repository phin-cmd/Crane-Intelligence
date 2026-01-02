# Server Monitoring - Setup Complete ✅

## Configuration Summary

### SMTP Configuration
- **SMTP Host:** smtp.gmail.com
- **SMTP Port:** 587
- **SMTP User:** pgenerelly@craneintelligence.tech
- **From Email:** pgenerelly@craneintelligence.tech

### Admin Email Recipients
1. pgenerelly@craneintelligence.tech
2. rema@thecranehotlist.com
3. treprltd@gmail.com

### Service Status
- **Service Name:** server-monitor
- **Status:** Enabled and Running
- **Check Interval:** Every 60 seconds
- **Monitored Servers:**
  - Production: https://craneintelligence.tech
  - UAT: https://uat.craneintelligence.tech
  - Dev: https://dev.craneintelligence.tech

## What's Happening Now

1. **Monitoring Script** is running and checking servers every 60 seconds
2. **Email Alerts** will be sent to all 3 admin emails when issues are detected
3. **API Alerts** are being sent to `/api/v1/admin/alerts` endpoint
4. **Admin Dashboard** will show server status in the header

## Verification Commands

### Check Service Status
```bash
sudo systemctl status server-monitor
```

### View Live Logs
```bash
sudo journalctl -u server-monitor -f
```

### View Recent Logs
```bash
sudo journalctl -u server-monitor -n 50
```

### Restart Service (if needed)
```bash
sudo systemctl restart server-monitor
```

### Test Backend API
```bash
curl http://localhost:8000/api/v1/health
```

## Admin Dashboard

The admin dashboard will now:
- Show server status indicator in the header (green/yellow/red)
- Auto-refresh every 30 seconds
- Display detailed status when clicked
- Show alerts for any server issues

## Email Notifications

When a server issue is detected, all 3 admin emails will receive:
- Subject: "🚨 ALERT: [Server Name] Server Issues Detected"
- Details about which server, what issue, and when it occurred

## Files Configured

- `/etc/systemd/system/server-monitor.service` - Service definition
- `/etc/systemd/system/server-monitor.service.d/override.conf` - Configuration with SMTP and admin emails
- `/root/crane/server-monitor.py` - Monitoring script (running)
- `/root/crane/backend/app/api/v1/server_monitoring.py` - API endpoints

## Next Steps

The system is now fully operational! 

- ✅ Monitoring is active
- ✅ Email notifications configured
- ✅ Admin dashboard integration complete
- ✅ API endpoints ready

You can now:
1. Check the admin dashboard to see server status
2. Wait for email alerts if any server issues occur
3. View logs to see monitoring activity

## Troubleshooting

If emails are not being sent:
1. Check service logs: `sudo journalctl -u server-monitor -f`
2. Verify Gmail App Password is correct (not regular password)
3. Check if Gmail account has 2FA enabled (required for App Passwords)
4. Verify SMTP credentials in override.conf

If dashboard not showing status:
1. Check browser console for API errors
2. Verify backend is running: `curl http://localhost:8000/api/v1/health`
3. Check admin token is valid
4. Verify `/api/v1/admin/server-status` endpoint is accessible

---

**Setup completed on:** $(date)
**Configuration file:** /etc/systemd/system/server-monitor.service.d/override.conf
