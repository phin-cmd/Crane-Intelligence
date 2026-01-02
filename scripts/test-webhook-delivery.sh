#!/bin/bash
# Script to test webhook delivery for Stripe webhooks
# This script helps verify that webhooks are configured correctly

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
echo "Testing Webhook Delivery - $ENVIRONMENT"
echo "=========================================="
echo ""

# Determine webhook URL and container name
case $ENVIRONMENT in
    dev)
        WEBHOOK_URL="https://dev.craneintelligence.tech/api/v1/payment-webhooks/stripe"
        CONTAINER_NAME="crane-dev-backend-1"
        PORT=8104
        ;;
    uat)
        WEBHOOK_URL="https://uat.craneintelligence.tech/api/v1/payment-webhooks/stripe"
        CONTAINER_NAME="crane-uat-backend-1"
        PORT=8204
        ;;
    prod)
        WEBHOOK_URL="https://craneintelligence.tech/api/v1/payment-webhooks/stripe"
        CONTAINER_NAME="crane-backend-1"
        PORT=8004
        ;;
esac

echo -e "${CYAN}Environment:${NC} $ENVIRONMENT"
echo -e "${CYAN}Webhook URL:${NC} $WEBHOOK_URL"
echo -e "${CYAN}Container:${NC} $CONTAINER_NAME"
echo ""

# Check if container is running
if ! docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}✗ Container $CONTAINER_NAME is not running${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Container $CONTAINER_NAME is running${NC}"
echo ""

# Check webhook endpoint accessibility
echo -e "${BLUE}Testing webhook endpoint accessibility...${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -H "stripe-signature: test" \
    -d '{}' 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "000" ]; then
    echo -e "${YELLOW}⚠ Could not reach webhook endpoint (network error)${NC}"
    echo "   This might be normal if the endpoint requires valid Stripe signature"
elif [ "$HTTP_CODE" = "400" ]; then
    echo -e "${GREEN}✓ Webhook endpoint is accessible (returned 400 - expected for invalid signature)${NC}"
elif [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    echo -e "${YELLOW}⚠ Webhook endpoint returned $HTTP_CODE (authentication/authorization issue)${NC}"
else
    echo -e "${YELLOW}⚠ Webhook endpoint returned HTTP $HTTP_CODE${NC}"
fi
echo ""

# Check webhook secret configuration
echo -e "${BLUE}Checking webhook secret configuration...${NC}"
ENV_FILE="config/${ENVIRONMENT}.env"

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}✗ Environment file not found: $ENV_FILE${NC}"
    exit 1
fi

WEBHOOK_SECRET=$(grep "^STRIPE_WEBHOOK_SECRET=" "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'")

if [ -z "$WEBHOOK_SECRET" ] || [ "$WEBHOOK_SECRET" = "whsec_replace_with"* ] || [[ "$WEBHOOK_SECRET" == *"replace"* ]]; then
    echo -e "${RED}✗ Webhook secret not configured in $ENV_FILE${NC}"
    echo "   Please update STRIPE_WEBHOOK_SECRET with the actual secret from Stripe dashboard"
    exit 1
elif [[ "$WEBHOOK_SECRET" =~ ^whsec_ ]]; then
    echo -e "${GREEN}✓ Webhook secret is configured (format looks correct)${NC}"
else
    echo -e "${YELLOW}⚠ Webhook secret format may be incorrect (expected: whsec_...)${NC}"
fi
echo ""

# Check backend logs for webhook-related messages
echo -e "${BLUE}Checking recent webhook activity in backend logs...${NC}"
RECENT_WEBHOOKS=$(docker logs "$CONTAINER_NAME" --tail 100 2>&1 | grep -i "webhook" | tail -5)

if [ -z "$RECENT_WEBHOOKS" ]; then
    echo -e "${YELLOW}⚠ No recent webhook activity found in logs${NC}"
    echo "   This is normal if no webhooks have been received recently"
else
    echo -e "${GREEN}Recent webhook activity:${NC}"
    echo "$RECENT_WEBHOOKS" | sed 's/^/  /'
fi
echo ""

# Check for webhook-related errors
echo -e "${BLUE}Checking for webhook-related errors...${NC}"
WEBHOOK_ERRORS=$(docker logs "$CONTAINER_NAME" --tail 200 2>&1 | grep -iE "(webhook.*error|invalid.*webhook|webhook.*fail)" | tail -5)

if [ -z "$WEBHOOK_ERRORS" ]; then
    echo -e "${GREEN}✓ No webhook errors found in recent logs${NC}"
else
    echo -e "${RED}⚠ Found webhook-related errors:${NC}"
    echo "$WEBHOOK_ERRORS" | sed 's/^/  /'
fi
echo ""

# Instructions for manual testing
echo -e "${CYAN}Manual Testing Instructions:${NC}"
echo ""
echo "1. Go to Stripe Dashboard: https://dashboard.stripe.com/webhooks"
echo ""
if [ "$ENVIRONMENT" = "prod" ]; then
    echo "2. Toggle to ${RED}LIVE MODE${NC} (top right)"
else
    echo "2. Toggle to ${YELLOW}TEST MODE${NC} (top right)"
fi
echo ""
echo "3. Find your webhook endpoint for: $WEBHOOK_URL"
echo ""
echo "4. Click on the webhook endpoint"
echo ""
echo "5. Click 'Send test webhook' button"
echo ""
echo "6. Select event: 'payment_intent.succeeded'"
echo ""
echo "7. Click 'Send test webhook'"
echo ""
echo "8. Check 'Recent deliveries' section for delivery status"
echo ""
echo "9. Monitor backend logs:"
echo "   docker logs $CONTAINER_NAME --tail 50 -f"
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo "1. Configure webhook secret in Stripe dashboard (if not done)"
echo "2. Update $ENV_FILE with the webhook secret"
echo "3. Restart backend: docker restart $CONTAINER_NAME"
echo "4. Test webhook delivery using Stripe dashboard"
echo "5. Monitor logs: docker logs $CONTAINER_NAME -f | grep -i webhook"
echo ""

