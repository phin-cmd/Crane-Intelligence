#!/bin/bash

echo "🔧 PERMANENT TICKER FIX - Ensuring scrolling works on all pages"
echo "=============================================================="

# List of all pages to fix
PAGES=(
    "/var/www/craneintelligence.tech/homepage.html"
    "/var/www/craneintelligence.tech/dashboard.html"
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
        echo "Fixing $page..."
        
        # Remove conflicting CSS rules that block animations
        sed -i 's/animation: none !important;//g' "$page"
        sed -i 's/transform: none !important;//g' "$page"
        
        # Ensure ticker-content has proper animation
        if ! grep -q "\.ticker-content.*animation.*scroll.*!important" "$page"; then
            # Add proper ticker CSS if not present
            sed -i '/\.ticker-content {/a\
            animation: scroll 30s linear infinite !important;\
            will-change: transform !important;' "$page"
        fi
        
        # Fix JavaScript animation names
        sed -i 's/scrollHorizontal/scroll/g' "$page"
        
        # Remove JavaScript that sets animation to none
        sed -i 's/tickerContent.style.animation = '\''none'\'';//g' "$page"
        sed -i 's/tickerContent.style.transform = '\''none'\'';//g' "$page"
        
        # Ensure proper keyframes exist
        if ! grep -q "@keyframes scroll" "$page"; then
            sed -i '/\.ticker-content {/a\
        @keyframes scroll {\
            0% { transform: translateX(100%); }\
            100% { transform: translateX(-100%); }\
        }' "$page"
        fi
        
        echo "✅ Fixed $page"
    else
        echo "❌ File not found: $page"
    fi
done

echo "✅ PERMANENT TICKER FIX COMPLETED!"
echo "All pages now have proper ticker scrolling animations."
