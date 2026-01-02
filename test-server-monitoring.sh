#!/bin/bash
# Quick test script for server monitoring system

echo "Testing Server Monitoring System..."
echo ""

# Test 1: Check if monitoring script exists and is executable
echo "1. Checking monitoring script..."
if [ -f "/root/crane/server-monitor.py" ]; then
    echo "   ✅ Monitoring script exists"
    if [ -x "/root/crane/server-monitor.py" ]; then
        echo "   ✅ Script is executable"
    else
        echo "   ⚠️  Script is not executable (run: chmod +x /root/crane/server-monitor.py)"
    fi
else
    echo "   ❌ Monitoring script not found"
fi

# Test 2: Check if service file exists
echo ""
echo "2. Checking systemd service..."
if [ -f "/etc/systemd/system/server-monitor.service" ]; then
    echo "   ✅ Service file installed"
else
    echo "   ⚠️  Service file not installed (run setup script)"
fi

# Test 3: Check if service is enabled
echo ""
echo "3. Checking service status..."
if systemctl is-enabled server-monitor >/dev/null 2>&1; then
    echo "   ✅ Service is enabled"
    if systemctl is-active server-monitor >/dev/null 2>&1; then
        echo "   ✅ Service is running"
    else
        echo "   ⚠️  Service is not running (start with: sudo systemctl start server-monitor)"
    fi
else
    echo "   ⚠️  Service is not enabled (run: sudo systemctl enable server-monitor)"
fi

# Test 4: Check Python dependencies
echo ""
echo "4. Checking Python dependencies..."
if python3 -c "import requests" 2>/dev/null; then
    echo "   ✅ requests module available"
else
    echo "   ⚠️  requests module not found (install with: pip3 install requests)"
fi

# Test 5: Check backend API health endpoint
echo ""
echo "5. Testing backend API health endpoint..."
if curl -s -f http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    echo "   ✅ Backend API is responding"
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/v1/health)
    echo "   Response: $HEALTH_RESPONSE"
else
    echo "   ⚠️  Backend API not responding (make sure backend is running on port 8000)"
fi

# Test 6: Check server status endpoint (if admin token available)
echo ""
echo "6. Testing server status endpoint..."
if [ -n "$ADMIN_TOKEN" ]; then
    if curl -s -f -H "Authorization: Bearer $ADMIN_TOKEN" http://localhost:8000/api/v1/admin/server-status >/dev/null 2>&1; then
        echo "   ✅ Server status endpoint is accessible"
    else
        echo "   ⚠️  Server status endpoint not accessible (check admin token)"
    fi
else
    echo "   ⚠️  Skipping (set ADMIN_TOKEN environment variable to test)"
fi

# Test 7: Check configuration file
echo ""
echo "7. Checking configuration..."
if [ -f "/etc/systemd/system/server-monitor.service.d/override.conf" ]; then
    echo "   ✅ Configuration file exists"
    SMTP_USER=$(grep "SMTP_USER=" /etc/systemd/system/server-monitor.service.d/override.conf | cut -d'=' -f2 | tr -d '"')
    if [ -n "$SMTP_USER" ]; then
        echo "   ✅ SMTP_USER is configured"
    else
        echo "   ⚠️  SMTP_USER is empty (edit override.conf)"
    fi
else
    echo "   ⚠️  Configuration file not found"
fi

echo ""
echo "Test complete!"
echo ""
echo "To view service logs: sudo journalctl -u server-monitor -f"
echo "To restart service: sudo systemctl restart server-monitor"

