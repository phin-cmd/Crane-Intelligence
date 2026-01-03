#!/bin/bash

# Security Testing Script
# Tests all implemented security measures

# Don't exit on first error - we want to run all tests
set +e

echo "=========================================="
echo "Crane Intelligence - Security Tests"
echo "=========================================="
echo ""

# Default to port 8003, but allow override
DEFAULT_PORT="${2:-8003}"
BASE_URL="${1:-http://localhost:${DEFAULT_PORT}}"
API_URL="${BASE_URL}/api/v1"

# Check if backend is accessible
check_backend() {
    local url=$1
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$url/api/v1/health" 2>/dev/null)
    if [ "$response" = "000" ] || [ -z "$response" ]; then
        return 1
    fi
    return 0
}

# Try to find the correct port
if ! check_backend "$BASE_URL"; then
    echo -e "${YELLOW}⚠️  Backend not accessible at $BASE_URL${NC}"
    echo "Trying alternative ports..."
    
    # Try common ports
    for port in 8004 8003 8000 8080; do
        test_url="http://localhost:$port"
        if check_backend "$test_url"; then
            echo -e "${GREEN}✓ Found backend at $test_url${NC}"
            BASE_URL="$test_url"
            API_URL="${BASE_URL}/api/v1"
            break
        fi
    done
    
    # Final check
    if ! check_backend "$BASE_URL"; then
        echo -e "${RED}❌ Backend is not accessible${NC}"
        echo ""
        echo "Please ensure the backend is running:"
        echo "  - Docker: cd /root/crane && docker compose up -d"
        echo "  - Direct: cd /root/crane/backend && uvicorn app.main:app --host 0.0.0.0 --port 8003"
        echo ""
        echo "Or specify the correct URL:"
        echo "  ./test_security.sh http://your-backend-url:port"
        echo ""
        exit 1
    fi
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC}: $2"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}: $2"
        ((FAILED++))
    fi
}

echo "1. Testing Payment Security (Amount Validation)"
echo "-----------------------------------------------"
# Test payment manipulation attempt
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}/fmv-reports/create-payment-intent" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "professional",
    "amount": 100,
    "crane_data": {}
  }' 2>/dev/null)

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" -eq 400 ] && echo "$BODY" | grep -q "amount mismatch\|Payment amount"; then
    test_result 0 "Payment manipulation blocked (expected 400 error)"
else
    test_result 1 "Payment manipulation not blocked (got $HTTP_CODE)"
fi

echo ""
echo "2. Testing SQL Injection Prevention"
echo "------------------------------------"
# Test SQL injection attempt
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${API_URL}/users?email=test@example.com' OR '1'='1" 2>/dev/null)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" -eq 400 ] || [ "$HTTP_CODE" -eq 403 ] || [ "$HTTP_CODE" -eq 500 ]; then
    test_result 0 "SQL injection attempt blocked (got $HTTP_CODE)"
else
    test_result 1 "SQL injection not blocked (got $HTTP_CODE)"
fi

echo ""
echo "3. Testing Bot Detection"
echo "------------------------"
# Test with bot user agent
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${API_URL}/health" \
  -H "User-Agent: python-requests/2.28.0" 2>/dev/null)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" -eq 403 ]; then
    test_result 0 "Bot detected and blocked (got 403)"
else
    test_result 1 "Bot not detected (got $HTTP_CODE)"
fi

echo ""
echo "4. Testing API Documentation (Production)"
echo "-----------------------------------------"
# Test if API docs are disabled
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}/docs" 2>/dev/null)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" -eq 404 ]; then
    test_result 0 "API docs disabled (got 404)"
else
    test_result 1 "API docs still accessible (got $HTTP_CODE)"
fi

echo ""
echo "5. Testing Rate Limiting"
echo "------------------------"
# Test rate limiting (make 25 rapid requests)
RATE_LIMIT_HIT=0
for i in {1..25}; do
    RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${API_URL}/health" 2>/dev/null)
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    if [ "$HTTP_CODE" -eq 429 ]; then
        RATE_LIMIT_HIT=1
        break
    fi
    sleep 0.1
done

if [ "$RATE_LIMIT_HIT" -eq 1 ]; then
    test_result 0 "Rate limiting active (got 429)"
else
    test_result 1 "Rate limiting not working"
fi

echo ""
echo "6. Testing Security Headers"
echo "---------------------------"
RESPONSE=$(curl -s -I -X GET "${BASE_URL}/" 2>/dev/null)

if echo "$RESPONSE" | grep -q "X-Frame-Options"; then
    test_result 0 "Security headers present"
else
    test_result 1 "Security headers missing"
fi

echo ""
echo "7. Testing Price Calculation Endpoint"
echo "-------------------------------------"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}/fmv-reports/calculate-price" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "professional",
    "crane_data": {}
  }' 2>/dev/null)

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" -eq 200 ] && echo "$BODY" | grep -q "amount"; then
    test_result 0 "Price calculation endpoint working"
    AMOUNT=$(echo "$BODY" | grep -o '"amount":[0-9]*' | cut -d: -f2)
    echo "   Calculated amount: $AMOUNT cents"
else
    test_result 1 "Price calculation endpoint failed (got $HTTP_CODE)"
fi

echo ""
echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

# Set exit code based on test results
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All security tests passed!${NC}"
    EXIT_CODE=0
else
    echo -e "${RED}Some security tests failed. Please review.${NC}"
    EXIT_CODE=1
fi

# Always exit with proper code
exit $EXIT_CODE

