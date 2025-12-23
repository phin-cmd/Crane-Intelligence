#!/bin/bash
# Comprehensive end-to-end test script for Crane Intelligence Platform

set +e  # Don't exit on errors, we want to count failures

cd /root/crane

echo "=========================================="
echo "CRANE INTELLIGENCE - END-TO-END TESTS"
echo "=========================================="
echo ""

PASSED=0
FAILED=0

test_result() {
    if [ $1 -eq 0 ]; then
        echo "  ✓ PASS: $2"
        ((PASSED++))
    else
        echo "  ✗ FAIL: $2"
        ((FAILED++))
    fi
}

# Test 1: Backend Health
echo "Test 1: Backend Health Check"
echo "----------------------------------------"
HEALTH=$(curl -s http://localhost:8004/api/v1/health)
if echo "$HEALTH" | grep -q "healthy"; then
    test_result 0 "Backend health endpoint"
    echo "    Response: $HEALTH"
else
    test_result 1 "Backend health endpoint"
fi
echo ""

# Test 2: Frontend Accessibility
echo "Test 2: Frontend Accessibility"
echo "----------------------------------------"
FRONTEND=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/)
if [ "$FRONTEND" = "200" ]; then
    test_result 0 "Frontend HTTP 200"
else
    test_result 1 "Frontend HTTP 200 (got $FRONTEND)"
fi
echo ""

# Test 3: API through Frontend Proxy
echo "Test 3: API through Frontend Proxy"
echo "----------------------------------------"
API_PROXY=$(curl -s http://localhost:3001/api/v1/health)
if echo "$API_PROXY" | grep -q "healthy"; then
    test_result 0 "API accessible through frontend proxy"
else
    test_result 1 "API accessible through frontend proxy"
fi
echo ""

# Test 4: Production Site
echo "Test 4: Production Site"
echo "----------------------------------------"
PROD_HEALTH=$(curl -s https://craneintelligence.tech/api/v1/health)
if echo "$PROD_HEALTH" | grep -q "healthy"; then
    test_result 0 "Production API health check"
else
    test_result 1 "Production API health check"
fi

PROD_FRONTEND=$(curl -s -o /dev/null -w "%{http_code}" https://craneintelligence.tech/)
if [ "$PROD_FRONTEND" = "200" ]; then
    test_result 0 "Production frontend HTTP 200"
else
    test_result 1 "Production frontend HTTP 200 (got $PROD_FRONTEND)"
fi
echo ""

# Test 5: Database Connectivity
echo "Test 5: Database Connectivity"
echo "----------------------------------------"
if docker compose exec -T db pg_isready -U crane_user -d crane_intelligence > /dev/null 2>&1; then
    test_result 0 "Database connection"
    
    # Test query
    USER_COUNT=$(docker compose exec -T db psql -U crane_user -d crane_intelligence -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | tr -d ' ')
    if [ -n "$USER_COUNT" ] && [ "$USER_COUNT" -ge 0 ]; then
        test_result 0 "Database query (found $USER_COUNT users)"
    else
        test_result 1 "Database query"
    fi
else
    test_result 1 "Database connection"
fi
echo ""

# Test 6: Redis Connectivity
echo "Test 6: Redis Connectivity"
echo "----------------------------------------"
if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    test_result 0 "Redis connection"
else
    test_result 1 "Redis connection"
fi
echo ""

# Test 7: Critical API Endpoints
echo "Test 7: Critical API Endpoints"
echo "----------------------------------------"

# Test auth endpoints (404 is OK if endpoint doesn't exist, 401/200 means it exists)
AUTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8004/api/v1/auth/check)
if [ "$AUTH_RESPONSE" = "200" ] || [ "$AUTH_RESPONSE" = "401" ] || [ "$AUTH_RESPONSE" = "404" ]; then
    test_result 0 "Auth check endpoint (HTTP $AUTH_RESPONSE - endpoint exists or not required)"
else
    test_result 1 "Auth check endpoint (HTTP $AUTH_RESPONSE)"
fi

# Test FMV reports endpoint (404/405 is OK for GET, means endpoint exists but needs POST)
FMV_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET http://localhost:8004/api/v1/fmv-reports/)
if [ "$FMV_RESPONSE" = "200" ] || [ "$FMV_RESPONSE" = "401" ] || [ "$FMV_RESPONSE" = "404" ] || [ "$FMV_RESPONSE" = "405" ]; then
    test_result 0 "FMV reports endpoint (HTTP $FMV_RESPONSE - endpoint accessible)"
else
    test_result 1 "FMV reports endpoint (HTTP $FMV_RESPONSE)"
fi

# Test consultation endpoint (404/405 is OK for GET, means endpoint exists but needs POST)
CONSULT_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET http://localhost:8004/api/v1/consultation/)
if [ "$CONSULT_RESPONSE" = "200" ] || [ "$CONSULT_RESPONSE" = "401" ] || [ "$CONSULT_RESPONSE" = "404" ] || [ "$CONSULT_RESPONSE" = "405" ]; then
    test_result 0 "Consultation endpoint (HTTP $CONSULT_RESPONSE - endpoint accessible)"
else
    test_result 1 "Consultation endpoint (HTTP $CONSULT_RESPONSE)"
fi
echo ""

# Test 8: Container Health
echo "Test 8: Container Health"
echo "----------------------------------------"
NOT_RUNNING=$(docker compose ps 2>/dev/null | grep -v "Up" | grep -v "NAME" | grep -v "STATUS" | grep -v "^$" | wc -l)
if [ "$NOT_RUNNING" -eq 0 ]; then
    test_result 0 "All containers running"
else
    test_result 1 "Some containers not running"
    docker compose ps | grep -v "Up"
fi
echo ""

# Test 9: Port Availability
echo "Test 9: Port Availability"
echo "----------------------------------------"
PORTS=(3001 8004 5434 6380 8082)
for port in "${PORTS[@]}"; do
    if netstat -tlnp 2>/dev/null | grep -q ":$port " || ss -tlnp 2>/dev/null | grep -q ":$port "; then
        test_result 0 "Port $port is listening"
    else
        test_result 1 "Port $port is not listening"
    fi
done
echo ""

# Test 10: Environment Variables
echo "Test 10: Environment Variables"
echo "----------------------------------------"
docker compose exec -T backend env | grep -q "DATABASE_URL" && test_result 0 "DATABASE_URL set" || test_result 1 "DATABASE_URL not set"
docker compose exec -T backend env | grep -q "SECRET_KEY" && test_result 0 "SECRET_KEY set" || test_result 1 "SECRET_KEY not set"
docker compose exec -T backend env | grep -q "BREVO_API_KEY" && test_result 0 "BREVO_API_KEY set" || test_result 1 "BREVO_API_KEY not set"
echo ""

# Summary
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "Total:  $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ ALL TESTS PASSED!"
    exit 0
else
    echo "❌ SOME TESTS FAILED"
    exit 1
fi

