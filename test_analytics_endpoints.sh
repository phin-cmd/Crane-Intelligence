#!/bin/bash

echo "=========================================="
echo "Testing Analytics Endpoints"
echo "=========================================="
echo ""

# Test visitor tracking endpoint (public, no auth)
echo "1. Testing visitor tracking endpoint (public)..."
TRACK_RESPONSE=$(curl -s -X POST http://localhost:8004/api/v1/visitor-tracking/track \
  -H "Content-Type: application/json" \
  -d '{"page_url": "https://craneintelligence.tech/test", "page_title": "Test Page"}')

if echo "$TRACK_RESPONSE" | grep -q "visitor_id"; then
    echo "   ✅ Tracking endpoint is working!"
    echo "   Response: $TRACK_RESPONSE" | head -c 200
    echo ""
else
    echo "   ⚠️  Tracking endpoint response: $TRACK_RESPONSE" | head -c 200
    echo ""
fi

# Test if backend is accessible
echo ""
echo "2. Testing backend connectivity..."
if curl -s http://localhost:8004/api/v1/health > /dev/null 2>&1; then
    echo "   ✅ Backend is accessible"
else
    echo "   ❌ Backend is not accessible (502 errors expected if backend is down)"
fi

# Check if visitor_tracking table exists
echo ""
echo "3. Checking if visitor_tracking table exists..."
TABLE_CHECK=$(docker exec crane-backend-1 python3 -c "
from app.core.database import engine
from sqlalchemy import inspect
try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print('visitor_tracking' in tables)
except Exception as e:
    print('Error:', str(e))
" 2>&1)

if echo "$TABLE_CHECK" | grep -q "True"; then
    echo "   ✅ visitor_tracking table exists"
elif echo "$TABLE_CHECK" | grep -q "Error"; then
    echo "   ⚠️  Could not check table: $TABLE_CHECK"
else
    echo "   ❌ visitor_tracking table does not exist"
fi

echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="

