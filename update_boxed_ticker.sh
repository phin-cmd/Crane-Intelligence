#!/bin/bash

echo "🔄 Implementing Boxed Scrolling Ticker Across All Pages"
echo "====================================================="

# List of all pages to update
PAGES=(
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
        echo "Processing $page..."
        
        # Remove AMERICAN and GALION from ticker symbols
        sed -i "s/'XCMG', 'MANITEX', 'AMERICAN', 'SHUTTLELIFT', 'GALION', 'DEMAG', 'TEREX', 'LIEBHERR'/'XCMG', 'MANITEX', 'SHUTTLELIFT', 'DEMAG', 'TEREX', 'LIEBHERR', 'GROVE', 'MANITOWOC'/g" "$page"
        
        # Update any other references to AMERICAN or GALION
        sed -i 's/AMERICAN//g' "$page"
        sed -i 's/GALION//g' "$page"
        
        # Add boxed ticker CSS if live-market-data exists
        if grep -q "live-market-data" "$page"; then
            echo "Adding boxed ticker to $page..."
            
            # Replace static market metrics with scrolling ticker
            sed -i '/<div class="market-metrics">/,/<\/div>/{
                /<div class="market-metrics">/{
                    r /dev/stdin
                }
                d
            }' "$page" << 'EOF'
                <!-- Boxed Scrolling Ticker -->
                <div class="ticker-content">
                    <div class="ticker-item">
                        <span class="ticker-symbol">Market Index</span>
                        <span class="ticker-price">733.4</span>
                        <span class="ticker-change positive">+1.2%</span>
                    </div>
                    <div class="ticker-item">
                        <span class="ticker-symbol">Volume (24H)</span>
                        <span class="ticker-price">$73.3M</span>
                        <span class="ticker-change positive">+8.1%</span>
                    </div>
                    <div class="ticker-item">
                        <span class="ticker-symbol">Avg Deal Size</span>
                        <span class="ticker-price">$0.7M</span>
                        <span class="ticker-change positive">+2.3%</span>
                    </div>
                    <div class="ticker-item">
                        <span class="ticker-symbol">Confidence</span>
                        <span class="ticker-price">92.5%</span>
                        <span class="ticker-change positive">+2.1%</span>
                    </div>
                    <div class="ticker-item">
                        <span class="ticker-symbol">Active Listings</span>
                        <span class="ticker-price">1,000</span>
                        <span class="ticker-change positive">+155%</span>
                    </div>
                    <div class="ticker-item">
                        <span class="ticker-symbol">Risk Level</span>
                        <span class="ticker-price">12.3%</span>
                        <span class="ticker-change negative">-0.8%</span>
                    </div>
                    <!-- Duplicate for continuous scrolling -->
                    <div class="ticker-item">
                        <span class="ticker-symbol">Market Index</span>
                        <span class="ticker-price">733.4</span>
                        <span class="ticker-change positive">+1.2%</span>
                    </div>
                    <div class="ticker-item">
                        <span class="ticker-symbol">Volume (24H)</span>
                        <span class="ticker-price">$73.3M</span>
                        <span class="ticker-change positive">+8.1%</span>
                    </div>
                    <div class="ticker-item">
                        <span class="ticker-symbol">Avg Deal Size</span>
                        <span class="ticker-price">$0.7M</span>
                        <span class="ticker-change positive">+2.3%</span>
                    </div>
                    <div class="ticker-item">
                        <span class="ticker-symbol">Confidence</span>
                        <span class="ticker-price">92.5%</span>
                        <span class="ticker-change positive">+2.1%</span>
                    </div>
                    <div class="ticker-item">
                        <span class="ticker-symbol">Active Listings</span>
                        <span class="ticker-price">1,000</span>
                        <span class="ticker-change positive">+155%</span>
                    </div>
                    <div class="ticker-item">
                        <span class="ticker-symbol">Risk Level</span>
                        <span class="ticker-price">12.3%</span>
                        <span class="ticker-change negative">-0.8%</span>
                    </div>
                </div>
EOF
        fi
        
        echo "✅ Updated $page"
    else
        echo "❌ File not found: $page"
    fi
done

echo "✅ Boxed ticker implementation completed across all pages!"
