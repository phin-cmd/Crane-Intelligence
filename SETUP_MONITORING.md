# Server Monitoring Setup Guide

## Overview

This monitoring system automatically checks the health of dev, UAT, and production servers and websites, sending immediate notifications and emails to admins when issues are detected.

## Setup Steps

### 1. Install Dependencies

```bash
pip3 install requests
```

### 2. Configure Environment Variables

Create a systemd override file to set environment variables:

```bash
sudo mkdir -p /etc/systemd/system/server-monitor.service.d
sudo nano /etc/systemd/system/server-monitor.service.d/override.conf
```

Add the following (replace with your actual values):

```ini
[Service]
Environment="SMTP_HOST=smtp.gmail.com"
Environment="SMTP_PORT=587"
Environment="SMTP_USER=your-email@gmail.com"
Environment="SMTP_PASSWORD=your-app-password"
Environment="FROM_EMAIL=alerts@craneintelligence.tech"
Environment="ADMIN_EMAILS=admin1@example.com,admin2@example.com,admin3@example.com"
Environment="ALERT_API_URL=https://craneintelligence.tech/api/v1/admin/alerts"
```

**Note:** For Gmail, you'll need to use an App Password, not your regular password.

### 3. Make Script Executable

```bash
chmod +x /root/crane/server-monitor.py
```

### 4. Install Systemd Service

```bash
# Copy service file
sudo cp /root/crane/server-monitor.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (starts on boot)
sudo systemctl enable server-monitor

# Start service
sudo systemctl start server-monitor

# Check status
sudo systemctl status server-monitor

# View logs
sudo journalctl -u server-monitor -f
```

### 5. Implement Backend API Endpoints

You need to implement the following API endpoints in your backend:

1. **GET `/api/v1/admin/server-status`** - Returns current server status
2. **POST `/api/v1/admin/alerts`** - Receives alerts from monitoring script
3. **GET `/api/v1/health`** - Health check endpoint for each server

See `API_ENDPOINT_DOCUMENTATION.md` for detailed specifications.

### 6. Update Admin Dashboard

The admin dashboard JavaScript has been updated to:
- Display server status indicator in the header
- Show detailed server status in a modal
- Auto-refresh every 30 seconds

Make sure `server-status.js` is included in all admin pages.

### 7. Test the System

1. **Test monitoring script manually:**
   ```bash
   python3 /root/crane/server-monitor.py
   ```

2. **Test email notifications:**
   - Temporarily stop a server
   - Check that emails are sent to admin addresses

3. **Test dashboard display:**
   - Open admin dashboard
   - Check that server status indicator appears in header
   - Click on status indicator to see details

## Monitoring Script Behavior

- **Check Interval:** Every 60 seconds
- **Timeout:** 10 seconds per check
- **Alert Behavior:** Only sends alerts when status changes (avoids spam)
- **Recovery:** Logs recovery but doesn't send recovery emails (can be configured)

## Troubleshooting

### Monitoring script not running
```bash
sudo systemctl status server-monitor
sudo journalctl -u server-monitor -n 50
```

### Emails not being sent
- Check SMTP credentials in override.conf
- Verify Gmail App Password is correct
- Check logs for SMTP errors

### Dashboard not showing status
- Check browser console for API errors
- Verify `/api/v1/admin/server-status` endpoint is implemented
- Check that admin token is valid

### False positives
- Adjust timeout values in `server-monitor.py`
- Check network connectivity
- Verify health check endpoints are responding correctly

## Customization

### Change Check Interval

Edit `server-monitor.py`:
```python
time.sleep(60)  # Change 60 to desired seconds
```

### Add More Servers

Edit `SERVERS` dictionary in `server-monitor.py`:
```python
SERVERS = {
    'production': {...},
    'uat': {...},
    'dev': {...},
    'staging': {
        'api_url': 'https://staging.craneintelligence.tech/api/v1/health',
        'website_url': 'https://staging.craneintelligence.tech',
        'name': 'Staging Server'
    }
}
```

### Enable Recovery Notifications

Edit `should_send_alert()` function to send notifications when servers recover.

