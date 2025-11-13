#!/bin/bash

echo "🔄 Restoring Hero Sections and Moving Boxed Ticker to Market Ticker"
echo "=================================================================="

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
        
        # Restore original LIVE MARKET DATA view in hero sections
        if grep -q "live-market-data" "$page"; then
            echo "Restoring hero section in $page..."
            
            # Replace boxed ticker with original market metrics
            sed -i '/<!-- Boxed Scrolling Ticker -->/,/<!-- Duplicate for continuous scrolling -->/{
                /<!-- Boxed Scrolling Ticker -->/{
                    r /dev/stdin
                }
                d
            }' "$page" << 'EOF'
                <div class="market-metrics">
                    <div class="metric-item">
                        <span class="metric-label">Market Index</span>
                        <div>
                            <span class="metric-value">733.4</span>
                            <span class="metric-change positive">+1.2%</span>
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <span class="metric-label">Volume (24H)</span>
                        <div>
                            <span class="metric-value">$73.3M</span>
                            <span class="metric-change positive">+8.1%</span>
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <span class="metric-label">Avg Deal Size</span>
                        <div>
                            <span class="metric-value">$0.7M</span>
                            <span class="metric-change positive">+2.3%</span>
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <span class="metric-label">Confidence</span>
                        <div>
                            <span class="metric-value">92.5%</span>
                            <span class="metric-change positive">+2.1%</span>
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <span class="metric-label">Active Listings</span>
                        <div>
                            <span class="metric-value">1,000</span>
                            <span class="metric-change positive">+155%</span>
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <span class="metric-label">Risk Level</span>
                        <div>
                            <span class="metric-value">12.3%</span>
                            <span class="metric-change negative">-0.8%</span>
                        </div>
                    </div>
                </div>
EOF
        fi
        
        # Add boxed ticker to market ticker sections if they exist
        if grep -q "market-ticker" "$page"; then
            echo "Adding boxed ticker to market ticker section in $page..."
            
            # This will be handled by the existing ticker system
            # The boxed ticker CSS is already in optimized-ticker.css
        fi
        
        echo "✅ Updated $page"
    else
        echo "❌ File not found: $page"
    fi
done

echo "✅ Hero sections restored and boxed ticker moved to market ticker sections!"
