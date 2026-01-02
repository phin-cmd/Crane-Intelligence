# Server Monitoring - Quick Start Guide

## ✅ Implementation Complete!

All backend API endpoints, configuration, and service setup have been completed.

## 🚀 Quick Start (3 Steps)

### Step 1: Configure SMTP and Admin Emails

Edit the configuration file:
```bash
sudo nano /etc/systemd/system/server-monitor.service.d/override.conf
```

Add your SMTP credentials and admin emails:
```ini
[Service]
Environment="SMTP_USER=your-email@gmail.com"
Environment="SMTP_PASSWORD=your-app-password"
Environment="ADMIN_EMAILS=admin1@example.com,admin2@example.com"
```

**For Gmail:** Use an App Password (not your regular password)
- Go to Google Account → Security → 2-Step Verification → App passwords
- Generate password for "Mail"
- Use that in SMTP_PASSWORD

### Step 2: Run Setup Script

```bash
cd /root/crane
sudo ./setup-server-monitoring.sh
```

This will:
- Install Python dependencies
- Make script executable
- Install systemd service
- Enable and start the service

### Step 3: Verify It's Working

```bash
# Check service status
sudo systemctl status server-monitor

# View logs
sudo journalctl -u server-monitor -f

# Run test script
./test-server-monitoring.sh
```

## 📋 What Was Implemented

### Backend API Endpoints ✅
- `GET /api/v1/admin/server-status` - Get server status (for dashboard)
- `POST /api/v1/admin/alerts` - Receive alerts from monitoring script
- `GET /api/v1/admin/alerts/history` - Get alert history
- `GET /api/v1/health` - Health check (for monitoring script)

**Location:** `/root/crane/backend/app/api/v1/server_monitoring.py`
**Integration:** Added to `main.py` - will load automatically when backend starts

### Configuration ✅
- Systemd service file: `/etc/systemd/system/server-monitor.service`
- Environment override: `/etc/systemd/system/server-monitor.service.d/override.conf`
- Setup script: `/root/crane/setup-server-monitoring.sh`
- Test script: `/root/crane/test-server-monitoring.sh`

### Admin Dashboard ✅
- Server status indicator in header (already integrated)
- Auto-refreshes every 30 seconds
- Shows detailed status modal

## 🔍 Verification

### Test Backend API
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Server status (requires admin token)
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
     http://localhost:8000/api/v1/admin/server-status
```

### Test Monitoring Script
```bash
# Run manually (will check servers every 60 seconds)
python3 /root/crane/server-monitor.py
```

### Check Service
```bash
# Status
sudo systemctl status server-monitor

# Logs
sudo journalctl -u server-monitor -n 50

# Restart if needed
sudo systemctl restart server-monitor
```

## 📊 How It Works

1. **Monitoring Script** runs every 60 seconds
   - Checks dev, UAT, and production servers
   - Sends alerts to `/api/v1/admin/alerts` when issues detected
   - Sends emails to admins

2. **Backend API** receives and stores alerts
   - Stores in memory cache
   - Creates admin notifications
   - Provides status via `/api/v1/admin/server-status`

3. **Admin Dashboard** displays status
   - Polls status endpoint every 30 seconds
   - Shows indicator in header (green/yellow/red)
   - Click to see detailed breakdown

## 🐛 Troubleshooting

### Service not starting
```bash
sudo journalctl -u server-monitor -n 50
# Check for Python errors or missing dependencies
```

### API not responding
- Verify backend is running: `curl http://localhost:8000/api/v1/health`
- Check backend logs
- Verify router is registered (check main.py)

### Emails not sending
- Verify SMTP credentials in override.conf
- Check service logs for SMTP errors
- Test SMTP connection manually

### Dashboard not showing status
- Open browser console (F12)
- Check for API errors
- Verify admin token is valid
- Check Network tab for `/api/v1/admin/server-status` requests

## 📝 Files Created

- `/root/crane/backend/app/api/v1/server_monitoring.py` - API endpoints
- `/root/crane/setup-server-monitoring.sh` - Setup script
- `/root/crane/test-server-monitoring.sh` - Test script
- `/root/crane/IMPLEMENTATION_COMPLETE.md` - Full documentation
- `/root/crane/QUICK_START.md` - This file

## ✅ Status

- ✅ Backend API endpoints implemented
- ✅ Environment variables configured (needs your credentials)
- ✅ Systemd service files created
- ✅ Setup scripts created
- ⏳ **Action Required:** Add SMTP credentials and run setup script

Once you complete Step 1 and Step 2 above, the monitoring system will be fully operational!

