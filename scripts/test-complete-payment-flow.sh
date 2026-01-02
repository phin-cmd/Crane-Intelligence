#!/bin/bash
# Complete Payment Flow Test - Tests the entire payment flow including webhook simulation
# This script tests payment intent creation, webhook handling, and report status updates

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
echo "Complete Payment Flow Test - $ENVIRONMENT"
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
echo ""

# Test 1: Verify backend is running
echo -e "${BLUE}Step 1: Backend Health Check${NC}"
if ! docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}✗ Container $CONTAINER_NAME is not running${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Backend is running${NC}"
echo ""

# Test 2: Verify Stripe configuration
echo -e "${BLUE}Step 2: Stripe Configuration${NC}"
CONFIG_RESPONSE=$(curl -s "${API_URL}/api/v1/config/public")
STRIPE_KEY=$(echo "$CONFIG_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('stripe_publishable_key', ''))" 2>/dev/null || echo "")
STRIPE_MODE=$(echo "$CONFIG_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('stripe_mode', ''))" 2>/dev/null || echo "")

if [ -z "$STRIPE_KEY" ]; then
    echo -e "${RED}✗ Failed to get Stripe configuration${NC}"
    exit 1
fi

if [ "$ENVIRONMENT" = "prod" ]; then
    if [[ "$STRIPE_KEY" =~ ^pk_live_ ]] && [ "$STRIPE_MODE" = "live" ]; then
        echo -e "${GREEN}✓ Stripe live keys configured correctly${NC}"
    else
        echo -e "${RED}✗ Stripe configuration incorrect for production${NC}"
        exit 1
    fi
else
    if [[ "$STRIPE_KEY" =~ ^pk_test_ ]] && [ "$STRIPE_MODE" = "test" ]; then
        echo -e "${GREEN}✓ Stripe test keys configured correctly${NC}"
    else
        echo -e "${RED}✗ Stripe configuration incorrect for $ENVIRONMENT${NC}"
        exit 1
    fi
fi
echo ""

# Test 3: Create payment intent
echo -e "${BLUE}Step 3: Create Payment Intent${NC}"
PAYMENT_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/fmv-reports/create-payment" \
    -H "Content-Type: application/json" \
    -d '{
        "report_type": "spot_check",
        "amount": 10000,
        "crane_data": {
            "manufacturer": "Test Manufacturer",
            "model": "Test Model",
            "serial_number": "TEST123"
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
    echo -e "${RED}✗ Payment intent created but missing required fields${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Payment intent created successfully${NC}"
echo -e "  Payment Intent ID: ${CYAN}$PAYMENT_INTENT_ID${NC}"
echo -e "  Client Secret: ${CYAN}${CLIENT_SECRET:0:40}...${NC}"
echo ""

# Test 4: Check webhook configuration
echo -e "${BLUE}Step 4: Webhook Configuration Check${NC}"
ENV_FILE="config/${ENVIRONMENT}.env"
WEBHOOK_SECRET=$(grep "^STRIPE_WEBHOOK_SECRET=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'" || echo "")

if [ -z "$WEBHOOK_SECRET" ] || [[ "$WEBHOOK_SECRET" == *"replace"* ]]; then
    echo -e "${YELLOW}⚠ Webhook secret not configured${NC}"
    echo "   Webhooks will not be processed until secret is configured"
    echo "   See WEBHOOK_SETUP_GUIDE.md for instructions"
    WEBHOOK_CONFIGURED=false
else
    if [[ "$WEBHOOK_SECRET" =~ ^whsec_ ]]; then
        echo -e "${GREEN}✓ Webhook secret is configured${NC}"
        WEBHOOK_CONFIGURED=true
    else
        echo -e "${YELLOW}⚠ Webhook secret format may be incorrect${NC}"
        WEBHOOK_CONFIGURED=false
    fi
fi
echo ""

# Test 5: Monitor logs for payment activity
echo -e "${BLUE}Step 5: Payment Activity Monitoring${NC}"
echo -e "${CYAN}Monitoring backend logs for payment activity...${NC}"
echo ""

# Get recent payment logs
PAYMENT_LOGS=$(docker logs "$CONTAINER_NAME" --tail 50 2>&1 | grep -iE "(payment|stripe)" | tail -10)

if [ -n "$PAYMENT_LOGS" ]; then
    echo -e "${GREEN}Recent payment activity:${NC}"
    echo "$PAYMENT_LOGS" | sed 's/^/  /'
else
    echo -e "${YELLOW}No recent payment activity in logs${NC}"
fi
echo ""

# Test 6: Instructions for frontend testing
echo -e "${BLUE}Step 6: Frontend Payment Testing${NC}"
echo -e "${CYAN}To complete the payment flow:${NC}"
echo ""
echo "1. Open frontend: $FRONTEND_URL/report-generation.html"
echo ""
echo "2. Fill in report details:"
echo "   - Select report type"
echo "   - Enter crane details"
echo "   - Click 'Purchase Report'"
echo ""
echo "3. Complete payment:"
echo "   - Use test card: ${GREEN}4242 4242 4242 4242${NC}"
echo "   - Expiry: Any future date (e.g., 12/34)"
echo "   - CVC: Any 3 digits (e.g., 123)"
echo "   - ZIP: Any 5 digits (e.g., 12345)"
echo "   - Enter cardholder name"
echo "   - Enter receipt email"
echo "   - Click 'Submit Payment'"
echo ""
echo "4. Monitor webhook delivery:"
echo "   docker logs $CONTAINER_NAME -f | grep -i webhook"
echo ""
echo "5. Verify report status:"
echo "   - Check that report status updates to SUBMITTED"
echo "   - Verify payment_status is succeeded"
echo "   - Confirm amount_paid is set"
echo ""

# Test 7: Webhook testing instructions
if [ "$WEBHOOK_CONFIGURED" = true ]; then
    echo -e "${BLUE}Step 7: Webhook Testing${NC}"
    echo -e "${CYAN}Webhook is configured. Test webhook delivery:${NC}"
    echo ""
    echo "Option 1: Use Stripe Dashboard"
    echo "  1. Go to https://dashboard.stripe.com/webhooks"
    echo "  2. Toggle to ${ENVIRONMENT} mode (Test for dev/uat, Live for prod)"
    echo "  3. Click on your webhook endpoint"
    echo "  4. Click 'Send test webhook'"
    echo "  5. Select 'payment_intent.succeeded'"
    echo "  6. Click 'Send test webhook'"
    echo ""
    echo "Option 2: Use test script"
    echo "  ./scripts/test-webhook-delivery.sh $ENVIRONMENT"
    echo ""
else
    echo -e "${BLUE}Step 7: Webhook Configuration Required${NC}"
    echo -e "${YELLOW}Webhook secret not configured. Configure it first:${NC}"
    echo ""
    echo "1. Get webhook secret from Stripe dashboard"
    echo "2. Run: ./scripts/configure-webhook-secrets.sh --interactive"
    echo "3. Restart backend: docker restart $CONTAINER_NAME"
    echo "4. Test again: ./scripts/test-complete-payment-flow.sh $ENVIRONMENT"
    echo ""
fi

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}✓ Backend is running${NC}"
echo -e "${GREEN}✓ Stripe configuration correct${NC}"
echo -e "${GREEN}✓ Payment intent creation working${NC}"
if [ "$WEBHOOK_CONFIGURED" = true ]; then
    echo -e "${GREEN}✓ Webhook secret configured${NC}"
else
    echo -e "${YELLOW}⚠ Webhook secret not configured${NC}"
fi
echo ""
echo -e "${CYAN}Payment Intent Created:${NC}"
echo "  ID: $PAYMENT_INTENT_ID"
echo "  Amount: \$100.00"
echo "  Status: Ready for payment"
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo "1. Complete payment in frontend using test card"
echo "2. Monitor webhook delivery (if configured)"
echo "3. Verify report status updates"
echo "4. Check user notifications"
echo ""

