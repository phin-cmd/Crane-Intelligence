#!/bin/bash
# Comprehensive Integration Test for Crane Intelligence Platform

echo "=========================================="
echo "   Crane Intelligence Integration Test"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter for tests
PASSED=0
FAILED=0

# Test function
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected="$3"
    
    echo -n "Testing $name... "
    response=$(curl -s "$url")
    
    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "  Expected: $expected"
        echo "  Got: $response"
        ((FAILED++))
        return 1
    fi
}

echo "1. Testing Backend Health"
echo "-------------------------"
test_endpoint "Backend Health" "http://localhost:8004/api/v1/health" "healthy"
echo ""

echo "2. Testing Frontend Proxy"
echo "-------------------------"
test_endpoint "Frontend Proxy Health" "http://localhost:3001/api/v1/health" "healthy"
echo ""

echo "3. Testing Database Integration"
echo "-------------------------------"
test_endpoint "Crane Listings Count" "http://localhost:3001/api/v1/crane-listings?limit=1" "success"
test_endpoint "Crane Listings Data" "http://localhost:3001/api/v1/crane-listings?limit=1" "manufacturer"
test_endpoint "Market Data" "http://localhost:3001/api/v1/market-data?limit=1" "market_data"
test_endpoint "Dashboard Stats" "http://localhost:3001/api/v1/dashboard/stats" "total_listings"
echo ""

echo "4. Testing Database Content"
echo "---------------------------"
echo -n "Checking crane_listings table... "
count=$(docker exec crane-intelligence-db-1 psql -U crane_user -d crane_intelligence -t -c "SELECT COUNT(*) FROM crane_listings;" 2>/dev/null | xargs)
if [ "$count" -gt 0 ]; then
    echo -e "${GREEN}✓ PASS${NC} ($count records)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo -n "Checking market_data table... "
count=$(docker exec crane-intelligence-db-1 psql -U crane_user -d crane_intelligence -t -c "SELECT COUNT(*) FROM market_data;" 2>/dev/null | xargs)
if [ "$count" -gt 0 ]; then
    echo -e "${GREEN}✓ PASS${NC} ($count records)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo -n "Checking users table... "
count=$(docker exec crane-intelligence-db-1 psql -U crane_user -d crane_intelligence -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | xargs)
if [ "$count" -gt 0 ]; then
    echo -e "${GREEN}✓ PASS${NC} ($count records)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi
echo ""

echo "5. Testing Container Status"
echo "---------------------------"
echo -n "Backend container... "
if docker ps | grep -q "crane-intelligence-backend-1"; then
    echo -e "${GREEN}✓ RUNNING${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ NOT RUNNING${NC}"
    ((FAILED++))
fi

echo -n "Frontend container... "
if docker ps | grep -q "crane-intelligence-frontend-1"; then
    echo -e "${GREEN}✓ RUNNING${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ NOT RUNNING${NC}"
    ((FAILED++))
fi

echo -n "Database container... "
if docker ps | grep -q "crane-intelligence-db-1"; then
    echo -e "${GREEN}✓ RUNNING${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ NOT RUNNING${NC}"
    ((FAILED++))
fi
echo ""

echo "6. Testing API Response Structure"
echo "---------------------------------"
echo -n "Crane listing structure... "
response=$(curl -s "http://localhost:3001/api/v1/crane-listings?limit=1")
if echo "$response" | jq -e '.listings[0].manufacturer' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo -n "Market data structure... "
response=$(curl -s "http://localhost:3001/api/v1/market-data?limit=1")
if echo "$response" | jq -e '.market_data[0].crane_type' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo -n "Dashboard stats structure... "
response=$(curl -s "http://localhost:3001/api/v1/dashboard/stats")
if echo "$response" | jq -e '.stats.total_listings' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi
echo ""

echo "7. Sample Data Verification"
echo "---------------------------"
echo "Sample crane listings:"
docker exec crane-intelligence-db-1 psql -U crane_user -d crane_intelligence -c "SELECT manufacturer, model, price FROM crane_listings LIMIT 3;" 2>/dev/null

echo ""
echo "Sample market data:"
docker exec crane-intelligence-db-1 psql -U crane_user -d crane_intelligence -c "SELECT crane_type, make, average_price FROM market_data LIMIT 3;" 2>/dev/null

echo ""
echo "=========================================="
echo "             TEST RESULTS"
echo "=========================================="
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo ""
    echo "🚀 Your Crane Intelligence platform is fully operational!"
    echo ""
    echo "Access URLs:"
    echo "  Frontend: http://localhost:3001"
    echo "  API Docs: http://localhost:8004/docs"
    echo "  Database: http://localhost:8082 (Adminer)"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please check the logs:"
    echo "  docker logs crane-intelligence-backend-1"
    echo "  docker logs crane-intelligence-frontend-1"
    exit 1
fi

