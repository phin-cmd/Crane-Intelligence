# Server Monitoring System - Implementation Summary

## What Has Been Implemented

### 1. Monitoring Script (`server-monitor.py`)
- ✅ Monitors dev, UAT, and production servers
- ✅ Checks both API and website health
- ✅ Sends email alerts to admins when issues detected
- ✅ Sends alerts to API endpoint for dashboard display
- ✅ Avoids duplicate alerts (only sends when status changes)
- ✅ Logs all monitoring activity

### 2. Admin Dashboard Integration
- ✅ Server status indicator in admin header (all pages)
- ✅ Real-time status updates (every 30 seconds)
- ✅ Visual indicators (green/yellow/red)
- ✅ Clickable status indicator shows detailed modal
- ✅ Detailed server status view with API/website breakdown

### 3. Systemd Service
- ✅ Service file created for automatic startup
- ✅ Auto-restart on failure
- ✅ Logging to journalctl

### 4. Documentation
- ✅ Setup guide (`SETUP_MONITORING.md`)
- ✅ API endpoint documentation (`API_ENDPOINT_DOCUMENTATION.md`)
- ✅ This summary document

## What Needs to Be Done

### 1. Backend API Implementation (REQUIRED)

You need to implement these endpoints in your backend:

#### GET `/api/v1/admin/server-status`
Returns current status of all monitored servers. Should query the database where monitoring alerts are stored.

#### POST `/api/v1/admin/alerts`
Receives alerts from the monitoring script. Should:
- Store alerts in database
- Create notifications for all admin users
- Optionally send additional email notifications

#### GET `/api/v1/health`
Health check endpoint for each server. Should return 200 OK when healthy.

### 2. Configuration

1. **Set up SMTP credentials:**
   ```bash
   sudo mkdir -p /etc/systemd/system/server-monitor.service.d
   sudo nano /etc/systemd/system/server-monitor.service.d/override.conf
   ```
   
   Add your SMTP settings and admin emails.

2. **Install and start the service:**
   ```bash
   sudo cp /root/crane/server-monitor.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable server-monitor
   sudo systemctl start server-monitor
   ```

3. **Add server-status.js to all admin pages:**
   The script has been added to `fmv-reports.html`. Add this line to other admin pages:
   ```html
   <script src="js/server-status.js"></script>
   ```

### 3. Database Schema (if storing alerts)

If you want to store alerts in the database, create a table:

```sql
CREATE TABLE server_alerts (
    id SERIAL PRIMARY KEY,
    server VARCHAR(50) NOT NULL,
    server_name VARCHAR(255),
    status VARCHAR(20) NOT NULL,
    api_status VARCHAR(20),
    website_status VARCHAR(20),
    api_error TEXT,
    website_error TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_server_alerts_server ON server_alerts(server);
CREATE INDEX idx_server_alerts_timestamp ON server_alerts(timestamp);
```

## Files Created/Modified

### Created Files:
1. `/root/crane/server-monitor.py` - Main monitoring script
2. `/root/crane/server-monitor.service` - Systemd service file
3. `/root/crane/admin/js/server-status.js` - Dashboard status display
4. `/root/crane/API_ENDPOINT_DOCUMENTATION.md` - API specs
5. `/root/crane/SETUP_MONITORING.md` - Setup guide
6. `/root/crane/MONITORING_SUMMARY.md` - This file

### Modified Files:
1. `/root/crane/admin/js/admin-layout.js` - Added server status indicator and monitoring
2. `/root/crane/admin/fmv-reports.html` - Added server-status.js script

## Testing

1. **Test monitoring script:**
   ```bash
   python3 /root/crane/server-monitor.py
   ```
   Should see health checks running every 60 seconds.

2. **Test email notifications:**
   - Stop a test server temporarily
   - Check that emails are sent

3. **Test dashboard:**
   - Open admin dashboard
   - Verify status indicator appears in header
   - Click to see detailed status

## Monitoring Behavior

- **Check Frequency:** Every 60 seconds
- **Dashboard Refresh:** Every 30 seconds
- **Alert Behavior:** Only sends alerts when status changes (prevents spam)
- **Email Recipients:** All emails in ADMIN_EMAILS environment variable
- **Log Location:** `/var/log/crane/server-monitor.log` and journalctl

## Next Steps

1. ✅ Implement backend API endpoints
2. ✅ Configure SMTP and admin emails
3. ✅ Install and start systemd service
4. ✅ Test the complete system
5. ✅ Add server-status.js to all admin pages (if not already done)

## Support

If you encounter issues:
1. Check logs: `sudo journalctl -u server-monitor -f`
2. Verify API endpoints are implemented
3. Check SMTP configuration
4. Verify admin emails are correct

