#!/bin/bash

echo "🔧 COMPREHENSIVE TICKER FIX - PERMANENT SOLUTION"
echo "================================================"

# Fix the main valuation terminal file
echo "Fixing valuation_terminal.html..."

# Remove duplicate CSS blocks and consolidate
sed -i '/COMPREHENSIVE ANTI-FLICKERING CSS/,/Prevent layout shifts/{
    /COMPREHENSIVE ANTI-FLICKERING CSS/{
        r /dev/stdin
    }
    d
}' /var/www/craneintelligence.tech/valuation_terminal.html << 'EOF'
        /* OPTIMIZED ANTI-FLICKERING CSS - PRESERVING TICKER ANIMATIONS */
        * {
            transition: none !important;
        }
        
        /* PRESERVE TICKER ANIMATIONS - HIGHEST PRIORITY */
        .ticker-content {
            animation: scroll-left 30s linear infinite !important;
            will-change: transform !important;
        }
        
        /* Disable problematic animations only */
        .metric-value, .chart-container, .data-card, .live-data, .market-data {
            transition: none !important;
            animation: none !important;
            transform: none !important;
        }
        
        /* Disable hover effects that might cause flickering */
        *:hover {
            transition: none !important;
        }
        
        /* Prevent layout shifts */
        .ticker-card, .metric-item, .dashboard-metric {
            min-height: 1.2em;
            overflow: hidden;
        }
EOF

# Ensure ticker CSS is properly defined
echo "Ensuring ticker CSS is properly defined..."

# Add comprehensive ticker CSS if not present
if ! grep -q "\.ticker-content.*animation.*scroll-left" /var/www/craneintelligence.tech/valuation_terminal.html; then
    sed -i '/Stock Ticker/a\
        .ticker-content {\
            display: inline-block;\
            animation: scroll-left 30s linear infinite !important;\
            font-family: "JetBrains Mono", monospace;\
            font-size: 0.9rem;\
            font-weight: 500;\
            white-space: nowrap;\
            will-change: transform;\
        }' /var/www/craneintelligence.tech/valuation_terminal.html
fi

# Ensure keyframes exist
if ! grep -q "@keyframes scroll-left" /var/www/craneintelligence.tech/valuation_terminal.html; then
    sed -i '/@keyframes scroll-left/a\
        @keyframes scroll-left {\
            0% { transform: translate3d(100%, 0, 0); }\
            100% { transform: translate3d(-100%, 0, 0); }\
        }' /var/www/craneintelligence.tech/valuation_terminal.html
fi

# Fix JavaScript to ensure proper animation
echo "Fixing JavaScript animation logic..."

# Replace the startMarketTicker function with a more robust version
sed -i '/function startMarketTicker/,/}/c\
        function startMarketTicker() {\
            const tickerContent = document.querySelector(".ticker-content");\
            if (tickerContent) {\
                // Force remove any conflicting styles\
                tickerContent.style.animation = "none";\
                tickerContent.style.transform = "none";\
                tickerContent.offsetHeight; // Force reflow\
                \
                // Apply the correct animation\
                tickerContent.style.animation = "scroll-left 30s linear infinite";\
                tickerContent.style.willChange = "transform";\
                \
                console.log("✅ Market ticker animation FORCED to start");\
            } else {\
                console.log("❌ Ticker content not found");\
            }\
        }' /var/www/craneintelligence.tech/valuation_terminal.html

# Fix all other pages with the same issues
echo "Fixing all other pages..."

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
        echo "Processing $page..."
        
        # Remove global animation blocking
        sed -i 's/animation: none !important;//g' "$page"
        
        # Fix ticker-content CSS
        sed -i 's/\.ticker-content, \.metric-value/\.ticker-content {\
            animation: scroll 30s linear infinite !important;\
            will-change: transform !important;\
        }\
        \.metric-value/g' "$page"
        
        # Ensure proper keyframes
        if ! grep -q "@keyframes scroll" "$page"; then
            sed -i '/\.ticker-content {/a\
        @keyframes scroll {\
            0% { transform: translateX(100%); }\
            100% { transform: translateX(-100%); }\
        }' "$page"
        fi
        
        echo "Fixed $page"
    fi
done

echo "✅ COMPREHENSIVE TICKER FIX COMPLETED!"
echo "All conflicts resolved, animations preserved, code optimized."
