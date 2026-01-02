#!/bin/bash
# Comprehensive Payment Flow Test Script
# Tests the complete payment flow including payment intent creation and webhook handling

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRANE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$CRANE_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

ENVIRONMENT=${1:-dev}

if [ "$ENVIRONMENT" != "dev" ] && [ "$ENVIRONMENT" != "uat" ] && [ "$ENVIRONMENT" != "prod" ]; then
    echo -e "${RED}Error: Invalid environment. Use: dev, uat, or prod${NC}"
    exit 1
fi

echo "=========================================="
echo "Payment Flow Test - $ENVIRONMENT"
echo "=========================================="
echo ""

# Determine API URL and container name
case $ENVIRONMENT in
    dev)
        API_URL="http://localhost:8104"
        CONTAINER_NAME="crane-dev-backend-1"
        FRONTEND_URL="https://dev.craneintelligence.tech"
        ;;
    uat)
        API_URL="http://localhost:8204"
        CONTAINER_NAME="crane-uat-backend-1"
        FRONTEND_URL="https://uat.craneintelligence.tech"
        ;;
    prod)
        API_URL="http://localhost:8004"
        CONTAINER_NAME="crane-backend-1"
        FRONTEND_URL="https://craneintelligence.tech"
        ;;
esac

echo -e "${CYAN}Environment:${NC} $ENVIRONMENT"
echo -e "${CYAN}API URL:${NC} $API_URL"
echo -e "${CYAN}Frontend URL:${NC} $FRONTEND_URL"
echo -e "${CYAN}Container:${NC} $CONTAINER_NAME"
echo ""

# Test 1: Check if backend is running
echo -e "${BLUE}Test 1: Backend Health Check${NC}"
if ! docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}✗ Container $CONTAINER_NAME is not running${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Container is running${NC}"
echo ""

# Test 2: Check config endpoint
echo -e "${BLUE}Test 2: Config Endpoint${NC}"
CONFIG_RESPONSE=$(curl -s "${API_URL}/api/v1/config/public")
STRIPE_KEY=$(echo "$CONFIG_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('stripe_publishable_key', ''))" 2>/dev/null || echo "")

if [ -z "$STRIPE_KEY" ]; then
    echo -e "${RED}✗ Failed to get Stripe key from config endpoint${NC}"
    exit 1
fi

if [ "$ENVIRONMENT" = "prod" ]; then
    if [[ "$STRIPE_KEY" =~ ^pk_live_ ]]; then
        echo -e "${GREEN}✓ Config endpoint returns live Stripe key (correct for production)${NC}"
    else
        echo -e "${RED}✗ Config endpoint returns test key (should be live for production)${NC}"
        exit 1
    fi
else
    if [[ "$STRIPE_KEY" =~ ^pk_test_ ]]; then
        echo -e "${GREEN}✓ Config endpoint returns test Stripe key (correct for $ENVIRONMENT)${NC}"
    else
        echo -e "${RED}✗ Config endpoint returns live key (should be test for $ENVIRONMENT)${NC}"
        exit 1
    fi
fi
echo ""

# Test 3: Create payment intent
echo -e "${BLUE}Test 3: Create Payment Intent${NC}"
PAYMENT_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/fmv-reports/create-payment" \
    -H "Content-Type: application/json" \
    -d '{
        "report_type": "spot_check",
        "amount": 10000,
        "crane_data": {
            "manufacturer": "Test Manufacturer",
            "model": "Test Model"
        },
        "cardholder_name": "Test User",
        "receipt_email": "test@example.com"
    }')

PAYMENT_INTENT_ID=$(echo "$PAYMENT_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('payment_intent_id', ''))" 2>/dev/null || echo "")
CLIENT_SECRET=$(echo "$PAYMENT_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('client_secret', ''))" 2>/dev/null || echo "")
SUCCESS=$(echo "$PAYMENT_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "False")

if [ "$SUCCESS" != "True" ] && [ "$SUCCESS" != "true" ]; then
    echo -e "${RED}✗ Failed to create payment intent${NC}"
    echo "Response: $PAYMENT_RESPONSE"
    exit 1
fi

if [ -z "$PAYMENT_INTENT_ID" ] || [ -z "$CLIENT_SECRET" ]; then
    echo -e "${RED}✗ Payment intent created but missing payment_intent_id or client_secret${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Payment intent created successfully${NC}"
echo -e "  Payment Intent ID: ${CYAN}$PAYMENT_INTENT_ID${NC}"
echo -e "  Client Secret: ${CYAN}${CLIENT_SECRET:0:30}...${NC}"
echo ""

# Test 4: Check Stripe service logs
echo -e "${BLUE}Test 4: Stripe Service Logs${NC}"
STRIPE_LOGS=$(docker logs "$CONTAINER_NAME" --tail 50 2>&1 | grep -i "stripe" | tail -10)

if [ -z "$STRIPE_LOGS" ]; then
    echo -e "${YELLOW}⚠ No recent Stripe-related logs found${NC}"
else
    echo -e "${GREEN}Recent Stripe logs:${NC}"
    echo "$STRIPE_LOGS" | sed 's/^/  /'
fi
echo ""

# Test 5: Check for Stripe errors/warnings
echo -e "${BLUE}Test 5: Stripe Errors/Warnings Check${NC}"
STRIPE_ERRORS=$(docker logs "$CONTAINER_NAME" --tail 200 2>&1 | grep -iE "(stripe.*error|stripe.*warn|stripe.*fail|invalid.*stripe)" | tail -10)

if [ -z "$STRIPE_ERRORS" ]; then
    echo -e "${GREEN}✓ No Stripe errors or warnings found${NC}"
else
    echo -e "${YELLOW}⚠ Found Stripe-related issues:${NC}"
    echo "$STRIPE_ERRORS" | sed 's/^/  /'
fi
echo ""

# Test 6: Verify webhook configuration
echo -e "${BLUE}Test 6: Webhook Configuration${NC}"
ENV_FILE="config/${ENVIRONMENT}.env"
WEBHOOK_SECRET=$(grep "^STRIPE_WEBHOOK_SECRET=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'" || echo "")

if [ -z "$WEBHOOK_SECRET" ] || [[ "$WEBHOOK_SECRET" == *"replace"* ]]; then
    echo -e "${YELLOW}⚠ Webhook secret not configured (this is expected if not set up yet)${NC}"
    echo "   See WEBHOOK_SETUP_GUIDE.md for instructions"
else
    if [[ "$WEBHOOK_SECRET" =~ ^whsec_ ]]; then
        echo -e "${GREEN}✓ Webhook secret is configured${NC}"
    else
        echo -e "${YELLOW}⚠ Webhook secret format may be incorrect${NC}"
    fi
fi
echo ""

# Test 7: Check payment intent status (if possible)
echo -e "${BLUE}Test 7: Payment Intent Verification${NC}"
echo -e "${CYAN}Note:${NC} To complete the full payment flow:"
echo "  1. Use the client_secret in the frontend"
echo "  2. Complete payment using Stripe test card: 4242 4242 4242 4242"
echo "  3. Webhook will be triggered automatically by Stripe"
echo "  4. Check backend logs for webhook processing"
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}✓ Backend is running${NC}"
echo -e "${GREEN}✓ Config endpoint working${NC}"
echo -e "${GREEN}✓ Payment intent creation working${NC}"
echo ""
echo -e "${CYAN}Payment Intent Details:${NC}"
echo "  ID: $PAYMENT_INTENT_ID"
echo "  Amount: \$100.00"
echo "  Report Type: spot_check"
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo "1. Test payment completion in frontend:"
echo "   - Go to: $FRONTEND_URL/report-generation.html"
echo "   - Fill in report details"
echo "   - Use test card: 4242 4242 4242 4242"
echo "   - Complete payment"
echo ""
echo "2. Monitor webhook delivery:"
echo "   docker logs $CONTAINER_NAME -f | grep -i webhook"
echo ""
echo "3. Check Stripe dashboard for payment status"
echo ""
echo "4. Verify report status updated after payment"
echo ""

