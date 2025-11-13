#!/bin/bash

echo "🔄 Updating all pages with optimized ticker system..."

PAGES=(
    "/var/www/craneintelligence.tech/about-us.html"
    "/var/www/craneintelligence.tech/contact.html"
    "/var/www/craneintelligence.tech/advanced-analytics.html"
    "/var/www/craneintelligence.tech/blog.html"
    "/var/www/craneintelligence.tech/account-settings.html"
    "/var/www/craneintelligence.tech/add-equipment.html"
    "/var/www/craneintelligence.tech/export-data.html"
    "/var/www/craneintelligence.tech/security.html"
    "/var/www/craneintelligence.tech/terms-of-service.html"
    "/var/www/craneintelligence.tech/generate-report.html"
    "/var/www/craneintelligence.tech/signup.html"
    "/var/www/craneintelligence.tech/reset-password.html"
    "/var/www/craneintelligence.tech/report-generation.html"
    "/var/www/craneintelligence.tech/admin-login.html"
    "/var/www/craneintelligence.tech/market-analysis.html"
)

for page in "${PAGES[@]}"; do
    if [ -f "$page" ]; then
        echo "Updating $page..."
        
        # Add optimized ticker files if not already present
        if ! grep -q "optimized-ticker.css" "$page"; then
            sed -i '/js\/anti-flickering.js/a\
    <link rel="stylesheet" href="css/optimized-ticker.css">\
    <script src="js/optimized-ticker.js"></script>' "$page"
        fi
        
        echo "✅ Updated $page"
    else
        echo "❌ File not found: $page"
    fi
done

echo "✅ All pages updated with optimized ticker system!"
