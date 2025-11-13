#!/bin/bash

echo "🎨 APPLYING UNIFORM MARKET TICKER DESIGN ACROSS ALL PAGES"
echo "========================================================"

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
        
        # Replace market ticker section with homepage design
        if grep -q "market-ticker" "$page"; then
            echo "Updating market ticker design in $page..."
            
            # Replace the entire market ticker section
            sed -i '/<!-- Market Ticker -->/,/<!-- Main Content -->/{
                /<!-- Market Ticker -->/{
                    r /dev/stdin
                }
                d
            }' "$page" << 'EOF'
    <!-- Market Ticker -->
    <div class="market-ticker">
        <div class="ticker-container">
            <div class="ticker-content">
                <div class="ticker-item">
                    <span class="ticker-symbol">XCMG</span>
                    <span class="ticker-price">467.8</span>
                    <span class="ticker-change down">-0.4%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">MANITEX</span>
                    <span class="ticker-price">757.8</span>
                    <span class="ticker-change up">+1.3%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">SHUTTLELIFT</span>
                    <span class="ticker-price">683.4</span>
                    <span class="ticker-change up">+2.2%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">DEMAG</span>
                    <span class="ticker-price">667.8</span>
                    <span class="ticker-change down">-1.1%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">NA-CRANE</span>
                    <span class="ticker-price">762.1</span>
                    <span class="ticker-change up">+1.8%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">EU-CRANE</span>
                    <span class="ticker-price">639.8</span>
                    <span class="ticker-change up">+2.1%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">AS-CRANE</span>
                    <span class="ticker-price">749.2</span>
                    <span class="ticker-change down">-0.7%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">TEREX</span>
                    <span class="ticker-price">523.4</span>
                    <span class="ticker-change up">+0.8%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">LIEBHERR</span>
                    <span class="ticker-price">891.2</span>
                    <span class="ticker-change down">-0.3%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">GROVE</span>
                    <span class="ticker-price">645.7</span>
                    <span class="ticker-change up">+1.5%</span>
                </div>
                <!-- Duplicate content for continuous scrolling -->
                <div class="ticker-item">
                    <span class="ticker-symbol">XCMG</span>
                    <span class="ticker-price">467.8</span>
                    <span class="ticker-change down">-0.4%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">MANITEX</span>
                    <span class="ticker-price">757.8</span>
                    <span class="ticker-change up">+1.3%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">SHUTTLELIFT</span>
                    <span class="ticker-price">683.4</span>
                    <span class="ticker-change up">+2.2%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">DEMAG</span>
                    <span class="ticker-price">667.8</span>
                    <span class="ticker-change down">-1.1%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">NA-CRANE</span>
                    <span class="ticker-price">762.1</span>
                    <span class="ticker-change up">+1.8%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">EU-CRANE</span>
                    <span class="ticker-price">639.8</span>
                    <span class="ticker-change up">+2.1%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">AS-CRANE</span>
                    <span class="ticker-price">749.2</span>
                    <span class="ticker-change down">-0.7%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">TEREX</span>
                    <span class="ticker-price">523.4</span>
                    <span class="ticker-change up">+0.8%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">LIEBHERR</span>
                    <span class="ticker-price">891.2</span>
                    <span class="ticker-change down">-0.3%</span>
                </div>
                <div class="ticker-item">
                    <span class="ticker-symbol">GROVE</span>
                    <span class="ticker-price">645.7</span>
                    <span class="ticker-change up">+1.5%</span>
                </div>
            </div>
        </div>
    </div>
EOF
        fi
        
        # Add uniform CSS styling if not present
        if ! grep -q "\.market-ticker.*background.*#1A1A1A" "$page"; then
            echo "Adding uniform CSS styling to $page..."
            
            # Add the uniform CSS after the first style tag
            sed -i '/<style>/a\
        /* ===== UNIFORM MARKET TICKER DESIGN ===== */\
        .market-ticker {\
            background: #1A1A1A !important;\
            padding: 8px 0 !important;\
            border-bottom: 1px solid #404040 !important;\
            overflow: hidden !important;\
            white-space: nowrap !important;\
            display: block !important;\
            height: auto !important;\
        }\
\
        .ticker-container {\
            max-width: 1400px !important;\
            margin: 0 auto !important;\
            padding: 0 var(--space-xl) !important;\
            overflow: hidden !important;\
        }\
\
        .ticker-content {\
            display: flex !important;\
            align-items: center !important;\
            gap: 40px !important;\
            animation: scroll 30s linear infinite !important;\
            white-space: nowrap !important;\
        }\
\
        .ticker-item {\
            display: flex;\
            align-items: center;\
            gap: 8px;\
            padding: 8px 16px;\
            background: rgba(255, 255, 255, 0.05);\
            border-radius: 4px;\
            border: 1px solid rgba(255, 255, 255, 0.1);\
            flex-shrink: 0;\
        }\
\
        .ticker-symbol {\
            font-family: "Inter", sans-serif;\
            font-size: 14px;\
            font-weight: 700;\
            color: #FFD600;\
            text-transform: uppercase;\
        }\
\
        .ticker-price {\
            font-family: "Inter", sans-serif;\
            font-size: 14px;\
            font-weight: 600;\
            color: #FFFFFF;\
        }\
\
        .ticker-change {\
            font-family: "Inter", sans-serif;\
            font-size: 12px;\
            font-weight: 600;\
        }\
\
        .ticker-change.up {\
            color: #00FF85;\
        }\
\
        .ticker-change.down {\
            color: #FF4444;\
        }\
\
        @keyframes scroll {\
            0% { transform: translateX(100%); }\
            100% { transform: translateX(-100%); }\
        }' "$page"
        fi
        
        echo "✅ Updated $page with uniform design"
    else
        echo "❌ File not found: $page"
    fi
done

echo "✅ UNIFORM MARKET TICKER DESIGN APPLIED TO ALL PAGES!"
echo "All pages now have consistent homepage-style market ticker UI/UX."
