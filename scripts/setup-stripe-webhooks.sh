#!/bin/bash
# Script to guide Stripe webhook setup for each environment
# Provides instructions and webhook endpoint URLs

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

echo "=========================================="
echo "Stripe Webhook Setup Guide"
echo "=========================================="
echo ""

echo "This script provides instructions for setting up Stripe webhooks"
echo "for each environment. Webhooks allow Stripe to notify your"
echo "application about payment events."
echo ""

# Webhook endpoints
DEV_WEBHOOK_URL="https://dev.craneintelligence.tech/api/v1/payment-webhooks/stripe"
UAT_WEBHOOK_URL="https://uat.craneintelligence.tech/api/v1/payment-webhooks/stripe"
PROD_WEBHOOK_URL="https://craneintelligence.tech/api/v1/payment-webhooks/stripe"

echo -e "${CYAN}Webhook Endpoints:${NC}"
echo ""
echo "  Dev:    $DEV_WEBHOOK_URL"
echo "  UAT:    $UAT_WEBHOOK_URL"
echo "  Prod:   $PROD_WEBHOOK_URL"
echo ""

echo -e "${CYAN}Setup Instructions:${NC}"
echo ""
echo "1. Go to Stripe Dashboard: https://dashboard.stripe.com/webhooks"
echo ""
echo "2. For each environment:"
echo ""
echo "   ${BLUE}For DEV/UAT (Test Mode):${NC}"
echo "   - Toggle to 'Test mode' (top right of Stripe dashboard)"
echo "   - Click 'Add endpoint'"
echo "   - Enter webhook URL:"
echo "     • Dev: $DEV_WEBHOOK_URL"
echo "     • UAT: $UAT_WEBHOOK_URL"
echo "   - Select events to listen to:"
echo "     • payment_intent.succeeded"
echo "     • payment_intent.payment_failed"
echo "     • payment_intent.canceled"
echo "   - Click 'Add endpoint'"
echo "   - Copy the 'Signing secret' (starts with whsec_)"
echo "   - Update config/dev.env or config/uat.env with:"
echo "     STRIPE_WEBHOOK_SECRET=whsec_..."
echo ""
echo "   ${BLUE}For PRODUCTION (Live Mode):${NC}"
echo "   - Toggle to 'Live mode' (top right of Stripe dashboard)"
echo "   - Click 'Add endpoint'"
echo "   - Enter webhook URL: $PROD_WEBHOOK_URL"
echo "   - Select events to listen to:"
echo "     • payment_intent.succeeded"
echo "     • payment_intent.payment_failed"
echo "     • payment_intent.canceled"
echo "   - Click 'Add endpoint'"
echo "   - Copy the 'Signing secret' (starts with whsec_)"
echo "   - Update config/prod.env with:"
echo "     STRIPE_WEBHOOK_SECRET=whsec_..."
echo ""
echo "3. After updating environment files, restart backend services:"
echo "   ./scripts/restart-backends-with-env-config.sh"
echo ""
echo "4. Test webhook delivery:"
echo "   - In Stripe dashboard, click on your webhook endpoint"
echo "   - Click 'Send test webhook'"
echo "   - Select 'payment_intent.succeeded'"
echo "   - Click 'Send test webhook'"
echo "   - Check backend logs to verify webhook was received"
echo ""

echo -e "${CYAN}Important Notes:${NC}"
echo ""
echo "  • Each environment needs a SEPARATE webhook endpoint"
echo "  • Test mode webhooks (dev/uat) use different secrets than live mode (prod)"
echo "  • Never share webhook secrets between environments"
echo "  • Webhook secrets are different from API keys"
echo "  • Keep webhook secrets secure - they're used to verify webhook authenticity"
echo ""

echo -e "${CYAN}Verification:${NC}"
echo ""
echo "After setup, verify webhook configuration:"
echo "  ./scripts/validate-stripe-config.sh"
echo ""

