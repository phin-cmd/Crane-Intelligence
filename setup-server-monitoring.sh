#!/bin/bash
# Setup script for server monitoring system

set -e

echo "Setting up Server Monitoring System..."

# 1. Install Python dependencies
echo "Installing Python dependencies..."
pip3 install requests --quiet

# 2. Make script executable
echo "Making monitoring script executable..."
chmod +x /root/crane/server-monitor.py

# 3. Create systemd override directory
echo "Creating systemd override directory..."
mkdir -p /etc/systemd/system/server-monitor.service.d

# 4. Create override config (user should edit this with their SMTP credentials)
echo "Creating systemd override configuration..."
cat > /etc/systemd/system/server-monitor.service.d/override.conf << 'EOF'
[Service]
# SMTP Configuration (edit with your actual credentials)
Environment="SMTP_HOST=smtp.gmail.com"
Environment="SMTP_PORT=587"
Environment="SMTP_USER="
Environment="SMTP_PASSWORD="
Environment="FROM_EMAIL=alerts@craneintelligence.tech"

# Admin email addresses (comma-separated)
Environment="ADMIN_EMAILS=admin@craneintelligence.tech"

# API endpoint for alerts
Environment="ALERT_API_URL=http://localhost:8000/api/v1/admin/alerts"
EOF

echo "⚠️  IMPORTANT: Edit /etc/systemd/system/server-monitor.service.d/override.conf"
echo "   and add your SMTP credentials and admin email addresses!"

# 5. Copy service file
echo "Copying systemd service file..."
cp /root/crane/server-monitor.service /etc/systemd/system/server-monitor.service

# 6. Reload systemd
echo "Reloading systemd..."
systemctl daemon-reload

# 7. Enable service
echo "Enabling server-monitor service..."
systemctl enable server-monitor

# 8. Start service
echo "Starting server-monitor service..."
systemctl start server-monitor

# 9. Check status
echo ""
echo "Checking service status..."
sleep 2
systemctl status server-monitor --no-pager | head -15

echo ""
echo "✅ Server monitoring setup complete!"
echo ""
echo "To view logs: sudo journalctl -u server-monitor -f"
echo "To edit configuration: sudo nano /etc/systemd/system/server-monitor.service.d/override.conf"
echo "To restart service: sudo systemctl restart server-monitor"

