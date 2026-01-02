#!/bin/bash
# Helper script to configure webhook secrets in environment files
# This script makes it easy to update webhook secrets once obtained from Stripe dashboard

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
echo "Stripe Webhook Secret Configuration"
echo "=========================================="
echo ""

# Function to update webhook secret in environment file
update_webhook_secret() {
    local env=$1
    local secret=$2
    local env_file="config/${env}.env"
    
    if [ ! -f "$env_file" ]; then
        echo -e "${RED}Error: Environment file not found: $env_file${NC}"
        return 1
    fi
    
    # Validate secret format
    if [[ ! "$secret" =~ ^whsec_ ]]; then
        echo -e "${RED}Error: Webhook secret must start with 'whsec_'${NC}"
        return 1
    fi
    
    # Backup original file
    cp "$env_file" "${env_file}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Update webhook secret
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|^STRIPE_WEBHOOK_SECRET=.*|STRIPE_WEBHOOK_SECRET=$secret|" "$env_file"
    else
        # Linux
        sed -i "s|^STRIPE_WEBHOOK_SECRET=.*|STRIPE_WEBHOOK_SECRET=$secret|" "$env_file"
    fi
    
    echo -e "${GREEN}✓ Updated $env.env with webhook secret${NC}"
    return 0
}

# Interactive mode
if [ "$1" = "--interactive" ] || [ -z "$1" ]; then
    echo -e "${CYAN}Interactive Mode${NC}"
    echo ""
    echo "This script will help you configure webhook secrets for each environment."
    echo "You need to get the webhook secrets from Stripe dashboard first."
    echo ""
    echo "Steps to get webhook secrets:"
    echo "1. Go to https://dashboard.stripe.com/webhooks"
    echo "2. For DEV/UAT: Toggle to 'Test mode'"
    echo "3. For PROD: Toggle to 'Live mode'"
    echo "4. Click on your webhook endpoint"
    echo "5. Click 'Reveal' next to 'Signing secret'"
    echo "6. Copy the secret (starts with whsec_)"
    echo ""
    
    # DEV
    echo -e "${BLUE}DEV Environment (Test Mode)${NC}"
    read -p "Enter webhook secret for DEV (or press Enter to skip): " dev_secret
    if [ -n "$dev_secret" ]; then
        update_webhook_secret "dev" "$dev_secret"
    else
        echo -e "${YELLOW}⚠ Skipped DEV environment${NC}"
    fi
    echo ""
    
    # UAT
    echo -e "${BLUE}UAT Environment (Test Mode)${NC}"
    read -p "Enter webhook secret for UAT (or press Enter to skip): " uat_secret
    if [ -n "$uat_secret" ]; then
        update_webhook_secret "uat" "$uat_secret"
    else
        echo -e "${YELLOW}⚠ Skipped UAT environment${NC}"
    fi
    echo ""
    
    # PROD
    echo -e "${BLUE}PRODUCTION Environment (Live Mode)${NC}"
    read -p "Enter webhook secret for PROD (or press Enter to skip): " prod_secret
    if [ -n "$prod_secret" ]; then
        update_webhook_secret "prod" "$prod_secret"
    else
        echo -e "${YELLOW}⚠ Skipped PROD environment${NC}"
    fi
    echo ""
    
    echo -e "${CYAN}Configuration complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Restart backend services:"
    echo "   ./scripts/restart-backends-with-env-config.sh"
    echo ""
    echo "2. Verify configuration:"
    echo "   ./scripts/validate-stripe-config.sh"
    echo ""
    echo "3. Test webhook delivery:"
    echo "   ./scripts/test-webhook-delivery.sh dev"
    
# Direct mode: update specific environment
elif [ "$1" = "dev" ] || [ "$1" = "uat" ] || [ "$1" = "prod" ]; then
    ENV=$1
    SECRET=$2
    
    if [ -z "$SECRET" ]; then
        echo -e "${RED}Error: Webhook secret required${NC}"
        echo "Usage: $0 [dev|uat|prod] <webhook_secret>"
        echo "   or: $0 --interactive"
        exit 1
    fi
    
    update_webhook_secret "$ENV" "$SECRET"
    
    echo ""
    echo "Restart backend service:"
    echo "  docker restart crane-${ENV}-backend-1"
    
else
    echo "Usage:"
    echo "  $0 --interactive              # Interactive mode"
    echo "  $0 [dev|uat|prod] <secret>   # Update specific environment"
    echo ""
    echo "Examples:"
    echo "  $0 --interactive"
    echo "  $0 dev whsec_1234567890abcdef"
    echo "  $0 uat whsec_0987654321fedcba"
    echo "  $0 prod whsec_abcdef1234567890"
    exit 1
fi

