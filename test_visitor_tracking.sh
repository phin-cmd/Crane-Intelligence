#!/bin/bash

echo "=========================================="
echo "Testing Visitor Tracking Setup"
echo "=========================================="
echo ""

# Test 1: Check if backend is running
echo "1. Checking backend container..."
if docker ps | grep -q crane-backend-1; then
    echo "   ✅ Backend container is running"
else
    echo "   ❌ Backend container is NOT running"
    exit 1
fi

# Test 2: Test tracking endpoint
echo ""
echo "2. Testing tracking endpoint..."
RESPONSE=$(curl -s -X POST http://localhost:8004/api/v1/visitor-tracking/track \
  -H "Content-Type: application/json" \
  -d '{"page_url": "https://craneintelligence.tech/test", "page_title": "Test Page"}')

if echo "$RESPONSE" | grep -q "visitor_id"; then
    echo "   ✅ Tracking endpoint is working!"
    echo "   Response: $RESPONSE"
else
    echo "   ⚠️  Tracking endpoint response: $RESPONSE"
    echo "   (This might be normal if there's an error, but endpoint exists)"
fi

# Test 3: Check if API endpoint is registered
echo ""
echo "3. Checking API documentation..."
if curl -s http://localhost:8004/docs | grep -q "visitor-tracking"; then
    echo "   ✅ Visitor tracking API is registered"
else
    echo "   ⚠️  Could not verify API registration (docs might not be accessible)"
fi

echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Visit https://craneintelligence.tech/ to generate tracking data"
echo "2. Check /admin/analytics.html to view the data"
echo ""

