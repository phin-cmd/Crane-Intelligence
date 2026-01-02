# Server Monitoring Implementation - COMPLETE ✅

## What Has Been Implemented

### 1. ✅ Backend API Endpoints

**File:** `/root/crane/backend/app/api/v1/server_monitoring.py`

Three endpoints have been created:

1. **GET `/api/v1/admin/server-status`**
   - Returns current status of all monitored servers
   - Returns healthy status by default if no alerts received yet
   - Requires admin authentication (gracefully handles when not available)

2. **POST `/api/v1/admin/alerts`**
   - Receives alerts from monitoring script
   - Stores alerts in memory cache
   - Creates notifications for admins (if database available)
   - No authentication required (called by monitoring script)

3. **GET `/api/v1/admin/alerts/history`**
   - Returns recent alert history
   - Requires admin authentication

**Integration:** The router has been added to `main.py` and will be automatically loaded when the backend starts.

### 2. ✅ Environment Variables Configuration

**File:** `/etc/systemd/system/server-monitor.service.d/override.conf`

Created with default values. **You need to edit this file** to add:
- SMTP credentials (SMTP_USER, SMTP_PASSWORD)
- Admin email addresses (ADMIN_EMAILS)

**To edit:**
```bash
sudo nano /etc/systemd/system/server-monitor.service.d/override.conf
```

### 3. ✅ Systemd Service Installation

**Files:**
- `/root/crane/server-monitor.service` - Service definition
- `/etc/systemd/system/server-monitor.service` - Installed service file
- `/etc/systemd/system/server-monitor.service.d/override.conf` - Configuration

**Setup Script:** `/root/crane/setup-server-monitoring.sh`

## Next Steps (REQUIRED)

### 1. Configure SMTP and Admin Emails

Edit the override configuration file:
```bash
sudo nano /etc/systemd/system/server-monitor.service.d/override.conf
```

Add your actual values:
```ini
[Service]
Environment="SMTP_USER=your-email@gmail.com"
Environment="SMTP_PASSWORD=your-app-password"
Environment="ADMIN_EMAILS=admin1@example.com,admin2@example.com"
```

**For Gmail:** You need to use an App Password, not your regular password.
1. Go to Google Account settings
2. Security → 2-Step Verification → App passwords
3. Generate an app password for "Mail"
4. Use that password in SMTP_PASSWORD

### 2. Run Setup Script

```bash
cd /root/crane
sudo ./setup-server-monitoring.sh
```

Or manually:
```bash
# Install dependencies
pip3 install requests

# Make script executable
chmod +x /root/crane/server-monitor.py

# Copy service file
sudo cp /root/crane/server-monitor.service /etc/systemd/system/

# Create override directory
sudo mkdir -p /etc/systemd/system/server-monitor.service.d

# Create override config (edit with your credentials)
sudo nano /etc/systemd/system/server-monitor.service.d/override.conf

# Reload and start
sudo systemctl daemon-reload
sudo systemctl enable server-monitor
sudo systemctl start server-monitor

# Check status
sudo systemctl status server-monitor
```

### 3. Verify Backend API is Running

The backend API must be running for the monitoring script to send alerts. Make sure:
- Backend is running on port 8000 (or update ALERT_API_URL)
- Health endpoint `/api/v1/health` is accessible
- Server status endpoint `/api/v1/admin/server-status` is accessible

### 4. Test the System

1. **Test monitoring script manually:**
   ```bash
   python3 /root/crane/server-monitor.py
   ```
   Press Ctrl+C after a few checks to stop.

2. **Test API endpoints:**
   ```bash
   # Health check
   curl http://localhost:8000/api/v1/health
   
   # Server status (requires admin token)
   curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
        http://localhost:8000/api/v1/admin/server-status
   ```

3. **Check service logs:**
   ```bash
   sudo journalctl -u server-monitor -f
   ```

## How It Works

1. **Monitoring Script** (`server-monitor.py`)
   - Runs every 60 seconds
   - Checks dev, UAT, and production servers
   - Sends alerts to API when issues detected
   - Sends emails to admins

2. **Backend API** (`server_monitoring.py`)
   - Receives alerts from monitoring script
   - Stores in memory cache
   - Creates admin notifications (if database available)
   - Provides status endpoint for dashboard

3. **Admin Dashboard** (`admin-layout.js`)
   - Polls `/api/v1/admin/server-status` every 30 seconds
   - Displays status indicator in header
   - Shows detailed modal when clicked

## Troubleshooting

### Service not starting
```bash
sudo systemctl status server-monitor
sudo journalctl -u server-monitor -n 50
```

### API endpoints not working
- Check backend is running: `curl http://localhost:8000/api/v1/health`
- Check backend logs for errors
- Verify router is registered in main.py

### Emails not sending
- Verify SMTP credentials in override.conf
- Check service logs for SMTP errors
- Test SMTP connection manually

### Dashboard not showing status
- Check browser console for API errors
- Verify admin token is valid
- Check network tab for `/api/v1/admin/server-status` requests

## Files Created/Modified

### Created:
- `/root/crane/backend/app/api/v1/server_monitoring.py` - API endpoints
- `/root/crane/setup-server-monitoring.sh` - Setup script
- `/root/crane/IMPLEMENTATION_COMPLETE.md` - This file

### Modified:
- `/root/crane/backend/app/main.py` - Added server monitoring router

### Already Existed:
- `/root/crane/server-monitor.py` - Monitoring script
- `/root/crane/server-monitor.service` - Service file
- `/root/crane/admin/js/admin-layout.js` - Dashboard integration

## Status

✅ Backend API endpoints implemented
✅ Environment variables configured (needs your credentials)
✅ Systemd service files created
⏳ Service needs to be started (run setup script)
⏳ SMTP credentials need to be added

Once you add SMTP credentials and start the service, the monitoring system will be fully operational!

