#!/bin/bash
set -e

echo "========================================="
echo "Setting up SSL certificates for dev and UAT subdomains"
echo "========================================="
echo ""
echo "IMPORTANT: Before running this script, ensure DNS records are configured:"
echo "  - dev.craneintelligence.tech  -> A record pointing to this server's IP"
echo "  - uat.craneintelligence.tech  -> A record pointing to this server's IP"
echo ""
read -p "Have you configured DNS records? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please configure DNS first, then run this script again."
    exit 1
fi

echo ""
echo "Step 1: Obtaining SSL certificate for dev.craneintelligence.tech..."
certbot certonly --nginx \
    -d dev.craneintelligence.tech \
    --non-interactive --agree-tos \
    --email pgenerelly@craneintelligence.tech \
    --redirect

echo ""
echo "Step 2: Obtaining SSL certificate for uat.craneintelligence.tech..."
certbot certonly --nginx \
    -d uat.craneintelligence.tech \
    --non-interactive --agree-tos \
    --email pgenerelly@craneintelligence.tech \
    --redirect

echo ""
echo "Step 3: Updating Nginx configs to use new certificates..."

# Update dev config
sed -i 's|ssl_certificate /etc/letsencrypt/live/craneintelligence.tech/fullchain.pem;|ssl_certificate /etc/letsencrypt/live/dev.craneintelligence.tech/fullchain.pem;|' /etc/nginx/sites-available/dev.craneintelligence.tech
sed -i 's|ssl_certificate_key /etc/letsencrypt/live/craneintelligence.tech/privkey.pem;|ssl_certificate_key /etc/letsencrypt/live/dev.craneintelligence.tech/privkey.pem;|' /etc/nginx/sites-available/dev.craneintelligence.tech

# Update UAT config
sed -i 's|ssl_certificate /etc/letsencrypt/live/craneintelligence.tech/fullchain.pem;|ssl_certificate /etc/letsencrypt/live/uat.craneintelligence.tech/fullchain.pem;|' /etc/nginx/sites-available/uat.craneintelligence.tech
sed -i 's|ssl_certificate_key /etc/letsencrypt/live/craneintelligence.tech/privkey.pem;|ssl_certificate_key /etc/letsencrypt/live/uat.craneintelligence.tech/privkey.pem;|' /etc/nginx/sites-available/uat.craneintelligence.tech

# Re-enable HTTPS redirects
sed -i 's|# return 301 https://$host$request_uri;|return 301 https://$host$request_uri;|' /etc/nginx/sites-available/dev.craneintelligence.tech
sed -i 's|# return 301 https://$host$request_uri;|return 301 https://$host$request_uri;|' /etc/nginx/sites-available/uat.craneintelligence.tech

# Remove temporary HTTP location blocks (they're now in HTTPS block)
sed -i '/# Temporary: serve HTTP directly for testing/,/}$/d' /etc/nginx/sites-available/dev.craneintelligence.tech
sed -i '/# Temporary: serve HTTP directly for testing/,/}$/d' /etc/nginx/sites-available/uat.craneintelligence.tech

echo ""
echo "Step 4: Testing Nginx configuration..."
nginx -t

echo ""
echo "Step 5: Reloading Nginx..."
systemctl reload nginx

echo ""
echo "========================================="
echo "SSL setup complete!"
echo "========================================="
echo ""
echo "Your environments are now available at:"
echo "  - https://dev.craneintelligence.tech/"
echo "  - https://uat.craneintelligence.tech/"
echo ""

