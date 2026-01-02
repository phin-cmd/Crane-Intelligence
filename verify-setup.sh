#!/bin/bash
# Verification script for server monitoring setup

echo "=========================================="
echo "Server Monitoring Setup Verification"
echo "=========================================="
echo ""

# Check configuration file
echo "1. Checking configuration file..."
if [ -f "/etc/systemd/system/server-monitor.service.d/override.conf" ]; then
    echo "   ✅ Configuration file exists"
    SMTP_USER=$(grep "SMTP_USER=" /etc/systemd/system/server-monitor.service.d/override.conf | cut -d'=' -f2 | tr -d '"')
    ADMIN_EMAILS=$(grep "ADMIN_EMAILS=" /etc/systemd/system/server-monitor.service.d/override.conf | cut -d'=' -f2 | tr -d '"')
    if [ -n "$SMTP_USER" ]; then
        echo "   ✅ SMTP User: $SMTP_USER"
    else
        echo "   ⚠️  SMTP User not configured"
    fi
    if [ -n "$ADMIN_EMAILS" ]; then
        echo "   ✅ Admin Emails: $ADMIN_EMAILS"
    else
        echo "   ⚠️  Admin Emails not configured"
    fi
else
    echo "   ❌ Configuration file not found"
fi

echo ""

# Check service file
echo "2. Checking service file..."
if [ -f "/etc/systemd/system/server-monitor.service" ]; then
    echo "   ✅ Service file exists"
else
    echo "   ❌ Service file not found"
fi

echo ""

# Check service status
echo "3. Checking service status..."
if systemctl is-enabled server-monitor >/dev/null 2>&1; then
    echo "   ✅ Service is enabled"
else
    echo "   ⚠️  Service is not enabled"
fi

if systemctl is-active server-monitor >/dev/null 2>&1; then
    echo "   ✅ Service is running"
    echo ""
    echo "   Recent logs:"
    journalctl -u server-monitor -n 5 --no-pager | tail -5 | sed 's/^/      /'
else
    echo "   ⚠️  Service is not running"
    echo "   Start with: sudo systemctl start server-monitor"
fi

echo ""

# Check monitoring script
echo "4. Checking monitoring script..."
if [ -f "/root/crane/server-monitor.py" ]; then
    echo "   ✅ Monitoring script exists"
    if [ -x "/root/crane/server-monitor.py" ]; then
        echo "   ✅ Script is executable"
    else
        echo "   ⚠️  Script is not executable"
    fi
else
    echo "   ❌ Monitoring script not found"
fi

echo ""

# Check Python dependencies
echo "5. Checking Python dependencies..."
if python3 -c "import requests" 2>/dev/null; then
    echo "   ✅ requests module available"
else
    echo "   ⚠️  requests module not found"
fi

echo ""

# Check backend API
echo "6. Checking backend API..."
if curl -s -f http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    echo "   ✅ Backend API is responding"
    HEALTH=$(curl -s http://localhost:8000/api/v1/health)
    echo "   Response: $HEALTH"
else
    echo "   ⚠️  Backend API not responding"
    echo "   Make sure backend is running on port 8000"
fi

echo ""
echo "=========================================="
echo "Verification Complete"
echo "=========================================="
echo ""
echo "To view live logs: sudo journalctl -u server-monitor -f"
echo "To restart service: sudo systemctl restart server-monitor"
echo "To check status: sudo systemctl status server-monitor"

