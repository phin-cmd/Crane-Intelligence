#!/bin/bash

# Script to fix ticker scrolling across all HTML pages
# This script will ensure consistent ticker scrolling behavior

echo "Fixing ticker scrolling across all pages..."

# List of pages to fix
PAGES=(
    "/var/www/craneintelligence.tech/about-us.html"
    "/var/www/craneintelligence.tech/contact.html"
    "/var/www/craneintelligence.tech/advanced-analytics.html"
    "/var/www/craneintelligence.tech/blog.html"
    "/var/www/craneintelligence.tech/account-settings.html"
    "/var/www/craneintelligence.tech/add-equipment.html"
    "/var/www/craneintelligence.tech/export-data.html"
)

for page in "${PAGES[@]}"; do
    if [ -f "$page" ]; then
        echo "Processing $page..."
        
        # Fix conflicting CSS rules
        sed -i 's/animation: none !important;//g' "$page"
        sed -i 's/transition: none !important;//g' "$page"
        sed -i 's/transform: none !important;//g' "$page"
        
        # Ensure proper ticker CSS
        if grep -q "ticker-content" "$page"; then
            # Add will-change property for better performance
            sed -i 's/\.ticker-content {/\.ticker-content {\n            will-change: transform;/g' "$page"
            
            # Ensure proper animation
            sed -i 's/animation: scrollHorizontal/animation: scroll/g' "$page"
            sed -i 's/@keyframes scrollHorizontal/@keyframes scroll/g' "$page"
        fi
        
        echo "Fixed $page"
    else
        echo "File not found: $page"
    fi
done

echo "Ticker fixes completed!"
