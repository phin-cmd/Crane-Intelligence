#!/bin/bash

# Verification script for visitor tracking setup
echo "=========================================="
echo "Visitor Tracking Setup Verification"
echo "=========================================="
echo ""

# Check if visitor-tracker.js exists
echo "1. Checking visitor tracking script..."
if [ -f "/root/crane/js/visitor-tracker.js" ]; then
    echo "   ✅ visitor-tracker.js found"
else
    echo "   ❌ visitor-tracker.js NOT found"
fi

# Check if script is included in main pages
echo ""
echo "2. Checking if script is included in pages..."
if grep -q "visitor-tracker.js" /root/crane/homepage.html; then
    echo "   ✅ homepage.html includes tracking script"
else
    echo "   ❌ homepage.html missing tracking script"
fi

if grep -q "visitor-tracker.js" /root/crane/dashboard.html; then
    echo "   ✅ dashboard.html includes tracking script"
else
    echo "   ❌ dashboard.html missing tracking script"
fi

if grep -q "visitor-tracker.js" /root/crane/report-generation.html; then
    echo "   ✅ report-generation.html includes tracking script"
else
    echo "   ❌ report-generation.html missing tracking script"
fi

# Check backend files
echo ""
echo "3. Checking backend files..."
if [ -f "/root/crane/backend/app/models/visitor_tracking.py" ]; then
    echo "   ✅ visitor_tracking.py model found"
else
    echo "   ❌ visitor_tracking.py model NOT found"
fi

if [ -f "/root/crane/backend/app/api/v1/visitor_tracking.py" ]; then
    echo "   ✅ visitor_tracking.py API found"
else
    echo "   ❌ visitor_tracking.py API NOT found"
fi

# Check if model is imported in database.py
echo ""
echo "4. Checking database initialization..."
if grep -q "visitor_tracking" /root/crane/backend/app/core/database.py; then
    echo "   ✅ VisitorTracking model imported in database.py"
else
    echo "   ❌ VisitorTracking model NOT imported in database.py"
fi

# Check if router is registered in main.py
echo ""
echo "5. Checking API router registration..."
if grep -q "visitor_tracking" /root/crane/backend/app/main.py; then
    echo "   ✅ visitor_tracking router registered in main.py"
else
    echo "   ❌ visitor_tracking router NOT registered in main.py"
fi

# Check analytics page
echo ""
echo "6. Checking analytics dashboard..."
if [ -f "/root/crane/admin/analytics.html" ]; then
    if grep -q "visitorStatsSection\|visitorTimelineChart" /root/crane/admin/analytics.html; then
        echo "   ✅ analytics.html includes visitor tracking sections"
    else
        echo "   ⚠️  analytics.html exists but may need visitor tracking sections"
    fi
else
    echo "   ❌ analytics.html NOT found"
fi

echo ""
echo "=========================================="
echo "Verification Complete"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Restart the backend server to create the database table"
echo "2. Visit a page to test tracking"
echo "3. Check /admin/analytics.html to view the data"
echo ""

