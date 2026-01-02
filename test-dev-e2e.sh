#!/bin/bash

# End-to-End Testing Script for Dev Environment
# Tests key functionality without requiring full Playwright setup

# Don't exit on error - we want to complete all tests
set +e

BASE_URL="http://localhost:3101"
API_URL="http://localhost:8104/api/v1"
TEST_RESULTS_DIR="test-results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$TEST_RESULTS_DIR/e2e-test-report-$TIMESTAMP.txt"

mkdir -p "$TEST_RESULTS_DIR"

echo "=========================================" > "$REPORT_FILE"
echo "End-to-End Test Report - Dev Environment" >> "$REPORT_FILE"
echo "Date: $(date)" >> "$REPORT_FILE"
echo "Base URL: $BASE_URL" >> "$REPORT_FILE"
echo "API URL: $API_URL" >> "$REPORT_FILE"
echo "=========================================" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Test counters
PASSED=0
FAILED=0
SKIPPED=0

test_result() {
    local test_name="$1"
    local status="$2"
    local message="$3"
    
    if [ "$status" == "PASS" ]; then
        echo "✅ PASS: $test_name" | tee -a "$REPORT_FILE"
        ((PASSED++))
    elif [ "$status" == "FAIL" ]; then
        echo "❌ FAIL: $test_name - $message" | tee -a "$REPORT_FILE"
        ((FAILED++))
    else
        echo "⏭️  SKIP: $test_name - $message" | tee -a "$REPORT_FILE"
        ((SKIPPED++))
    fi
}

# Test 1: Frontend Accessibility
echo "Testing Frontend Accessibility..."
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/" | grep -q "200"; then
    test_result "Frontend Homepage Accessible" "PASS"
else
    test_result "Frontend Homepage Accessible" "FAIL" "HTTP status not 200"
fi

# Test 2: API Health Check
echo "Testing API Health..."
HEALTH_RESPONSE=$(curl -s "$API_URL/health")
if echo "$HEALTH_RESPONSE" | grep -q "ok"; then
    test_result "API Health Check" "PASS"
else
    test_result "API Health Check" "FAIL" "Response: $HEALTH_RESPONSE"
fi

# Test 3: Backend Connectivity
echo "Testing Backend Connectivity..."
if curl -s -o /dev/null -w "%{http_code}" "$API_URL/health" | grep -q "200"; then
    test_result "Backend API Accessible" "PASS"
else
    test_result "Backend API Accessible" "FAIL" "HTTP status not 200"
fi

# Test 4: FMV Reports API (without auth - should return 401 or empty)
echo "Testing FMV Reports API..."
FMV_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/fmv-reports/user/64" 2>&1)
FMV_STATUS=$(echo "$FMV_RESPONSE" | tail -1)
if [ "$FMV_STATUS" == "200" ] || [ "$FMV_STATUS" == "401" ] || [ "$FMV_STATUS" == "403" ]; then
    test_result "FMV Reports API Endpoint" "PASS" "Status: $FMV_STATUS"
else
    test_result "FMV Reports API Endpoint" "FAIL" "Unexpected status: $FMV_STATUS"
fi

# Test 5: Admin FMV Reports API
echo "Testing Admin FMV Reports API..."
ADMIN_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/admin/fmv-reports" 2>&1)
ADMIN_STATUS=$(echo "$ADMIN_RESPONSE" | tail -1)
if [ "$ADMIN_STATUS" == "200" ] || [ "$ADMIN_STATUS" == "401" ] || [ "$ADMIN_STATUS" == "403" ]; then
    test_result "Admin FMV Reports API Endpoint" "PASS" "Status: $ADMIN_STATUS"
else
    test_result "Admin FMV Reports API Endpoint" "FAIL" "Unexpected status: $ADMIN_STATUS"
fi

# Test 6: Database Connectivity
echo "Testing Database Connectivity..."
DB_CHECK=$(docker exec crane-dev-db-1 psql -U crane_dev_user -d crane_intelligence_dev -c "SELECT 1;" 2>&1)
if echo "$DB_CHECK" | grep -q "1 row"; then
    test_result "Database Connectivity" "PASS"
else
    test_result "Database Connectivity" "FAIL" "Could not query database"
fi

# Test 7: Redis Connectivity
echo "Testing Redis Connectivity..."
REDIS_CHECK=$(docker exec crane-dev-redis-1 redis-cli ping 2>&1)
if echo "$REDIS_CHECK" | grep -q "PONG"; then
    test_result "Redis Connectivity" "PASS"
else
    test_result "Redis Connectivity" "FAIL" "Redis not responding"
fi

# Test 8: Check for FMV Reports in Database
echo "Testing FMV Reports Data..."
REPORT_COUNT=$(docker exec crane-dev-db-1 psql -U crane_dev_user -d crane_intelligence_dev -t -c "SELECT COUNT(*) FROM fmv_reports;" 2>&1 | tr -d ' ')
if [ "$REPORT_COUNT" -ge 0 ]; then
    test_result "FMV Reports Data Check" "PASS" "Found $REPORT_COUNT reports"
else
    test_result "FMV Reports Data Check" "FAIL" "Could not query reports"
fi

# Test 9: Check for Users in Database
echo "Testing Users Data..."
USER_COUNT=$(docker exec crane-dev-db-1 psql -U crane_dev_user -d crane_intelligence_dev -t -c "SELECT COUNT(*) FROM users;" 2>&1 | tr -d ' ')
if [ "$USER_COUNT" -ge 0 ]; then
    test_result "Users Data Check" "PASS" "Found $USER_COUNT users"
else
    test_result "Users Data Check" "FAIL" "Could not query users"
fi

# Test 10: Nginx Configuration
echo "Testing Nginx Configuration..."
NGINX_CHECK=$(docker exec crane-dev-frontend-1 nginx -t 2>&1)
if echo "$NGINX_CHECK" | grep -q "successful"; then
    test_result "Nginx Configuration" "PASS"
else
    test_result "Nginx Configuration" "FAIL" "$NGINX_CHECK"
fi

# Test 11: Container Health
echo "Testing Container Health..."
CONTAINERS=$(docker ps --filter "name=crane-dev" --format "{{.Names}}" | wc -l)
if [ "$CONTAINERS" -ge 4 ]; then
    test_result "Container Health" "PASS" "All $CONTAINERS dev containers running"
else
    test_result "Container Health" "FAIL" "Only $CONTAINERS containers running (expected 4+)"
fi

# Test 12: API Response Format
echo "Testing API Response Format..."
API_RESPONSE=$(curl -s "$API_URL/health")
if echo "$API_RESPONSE" | grep -q "status"; then
    test_result "API Response Format (JSON)" "PASS"
else
    test_result "API Response Format (JSON)" "FAIL" "Response not valid JSON"
fi

# Test 13: Frontend Pages Accessibility
echo "Testing Frontend Pages..."
PAGES=("homepage.html" "dashboard.html" "login.html" "signup.html" "fmv-reports.html")
for page in "${PAGES[@]}"; do
    PAGE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/$page")
    if [ "$PAGE_STATUS" == "200" ]; then
        test_result "Frontend Page: $page" "PASS"
    else
        test_result "Frontend Page: $page" "FAIL" "HTTP $PAGE_STATUS"
    fi
done

# Test 14: Admin Pages Accessibility
echo "Testing Admin Pages..."
ADMIN_PAGES=("admin/fmv-reports.html" "admin/login.html")
for page in "${ADMIN_PAGES[@]}"; do
    PAGE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/$page")
    if [ "$PAGE_STATUS" == "200" ]; then
        test_result "Admin Page: $page" "PASS"
    else
        test_result "Admin Page: $page" "FAIL" "HTTP $PAGE_STATUS"
    fi
done

# Summary
echo "" >> "$REPORT_FILE"
echo "=========================================" >> "$REPORT_FILE"
echo "Test Summary" >> "$REPORT_FILE"
echo "=========================================" >> "$REPORT_FILE"
echo "Total Tests: $((PASSED + FAILED + SKIPPED))" >> "$REPORT_FILE"
echo "Passed: $PASSED" >> "$REPORT_FILE"
echo "Failed: $FAILED" >> "$REPORT_FILE"
echo "Skipped: $SKIPPED" >> "$REPORT_FILE"
echo "Success Rate: $(awk "BEGIN {printf \"%.1f\", ($PASSED/($PASSED+$FAILED+$SKIPPED))*100}")%" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "Report saved to: $REPORT_FILE" >> "$REPORT_FILE"

echo ""
echo "========================================="
echo "Test Summary"
echo "========================================="
echo "Total Tests: $((PASSED + FAILED + SKIPPED))"
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
echo "⏭️  Skipped: $SKIPPED"
echo ""
echo "Full report: $REPORT_FILE"

exit $FAILED

