#!/bin/bash

echo "Fixing ticker animations across all pages..."

# List of all HTML pages
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
        echo "Processing $page..."
        
        # Remove global animation disabling
        sed -i 's/animation: none !important;//g' "$page"
        
        # Fix ticker-content CSS to allow animation
        sed -i 's/\.ticker-content, \.metric-value/\.ticker-content {\n            animation: scroll 30s linear infinite !important;\n        }\n        \.metric-value/g' "$page"
        
        # Ensure proper animation keyframes exist
        if ! grep -q "@keyframes scroll" "$page"; then
            # Add scroll keyframes if they don't exist
            sed -i '/\.ticker-content {/a\        @keyframes scroll {\n            0% { transform: translateX(100%); }\n            100% { transform: translateX(-100%); }\n        }' "$page"
        fi
        
        echo "Fixed $page"
    else
        echo "File not found: $page"
    fi
done

echo "All ticker fixes completed!"
