#!/bin/bash
# Setup automatic SSL certificate renewal and monitoring

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRANE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$CRANE_DIR"

echo "=========================================="
echo "SSL Certificate Auto-Renewal Setup"
echo "=========================================="
echo ""

# Check if certbot renewal is already configured
if systemctl list-timers | grep -q certbot; then
    echo "✓ Certbot timer already configured"
    systemctl list-timers | grep certbot
else
    echo "Setting up certbot renewal timer..."
    systemctl enable certbot.timer
    systemctl start certbot.timer
    echo "✓ Certbot timer configured"
fi

# Add pre-renewal hook to test nginx config
if [ ! -f /etc/letsencrypt/renewal-hooks/pre/nginx-test.sh ]; then
    cat > /etc/letsencrypt/renewal-hooks/pre/nginx-test.sh << 'EOF'
#!/bin/bash
# Test nginx configuration before renewal
nginx -t || exit 1
EOF
    chmod +x /etc/letsencrypt/renewal-hooks/pre/nginx-test.sh
    echo "✓ Pre-renewal hook configured"
fi

# Add post-renewal hook to reload nginx
if [ ! -f /etc/letsencrypt/renewal-hooks/deploy/nginx-reload.sh ]; then
    cat > /etc/letsencrypt/renewal-hooks/deploy/nginx-reload.sh << 'EOF'
#!/bin/bash
# Reload nginx after certificate renewal
systemctl reload nginx
EOF
    chmod +x /etc/letsencrypt/renewal-hooks/deploy/nginx-reload.sh
    echo "✓ Post-renewal hook configured"
fi

# Setup daily monitoring cron job
CRON_JOB="0 2 * * * $CRANE_DIR/scripts/ssl-certificate-monitor.sh >> /var/log/ssl-monitor.log 2>&1"

if ! crontab -l 2>/dev/null | grep -q "ssl-certificate-monitor.sh"; then
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✓ Daily monitoring cron job configured"
else
    echo "✓ Daily monitoring cron job already exists"
fi

echo ""
echo "=========================================="
echo "Setup Complete"
echo "=========================================="
echo ""
echo "Certificate renewal is now automated:"
echo "  - Certbot will automatically renew certificates"
echo "  - Nginx will be reloaded after renewal"
echo "  - Daily monitoring will check certificate status"
echo ""
echo "To manually renew certificates:"
echo "  certbot renew"
echo ""
echo "To check certificate status:"
echo "  ./scripts/ssl-certificate-monitor.sh"
echo ""

