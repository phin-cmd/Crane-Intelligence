#!/bin/bash
# Script to validate Stripe key configuration per environment
# Checks that keys match environment (test keys for dev/uat, live keys for prod)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRANE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$CRANE_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Stripe Configuration Validation"
echo "=========================================="
echo ""

# Function to validate environment file
validate_environment() {
    local env_file=$1
    local env_name=$2
    
    echo -e "${BLUE}Validating $env_name environment: $env_file${NC}"
    
    if [ ! -f "$env_file" ]; then
        echo -e "  ${RED}✗ Environment file not found: $env_file${NC}"
        return 1
    fi
    
    # Source the environment file
    source <(grep -v '^#' "$env_file" | grep -E "^(ENVIRONMENT|STRIPE_|WEBHOOK)" | sed 's/^/export /')
    
    # Check environment variable
    if [ -z "$ENVIRONMENT" ]; then
        echo -e "  ${YELLOW}⚠ ENVIRONMENT variable not set${NC}"
    else
        echo -e "  ${GREEN}✓ ENVIRONMENT: $ENVIRONMENT${NC}"
    fi
    
    # Check Stripe keys
    local has_publishable=false
    local has_secret=false
    local has_webhook=false
    
    if [ -n "$STRIPE_PUBLISHABLE_KEY" ]; then
        has_publishable=true
        if [[ "$STRIPE_PUBLISHABLE_KEY" =~ ^pk_test_ ]]; then
            echo -e "  ${GREEN}✓ STRIPE_PUBLISHABLE_KEY: Test key detected${NC}"
            detected_mode="test"
        elif [[ "$STRIPE_PUBLISHABLE_KEY" =~ ^pk_live_ ]]; then
            echo -e "  ${GREEN}✓ STRIPE_PUBLISHABLE_KEY: Live key detected${NC}"
            detected_mode="live"
        elif [[ "$STRIPE_PUBLISHABLE_KEY" =~ replace-with ]]; then
            echo -e "  ${YELLOW}⚠ STRIPE_PUBLISHABLE_KEY: Placeholder value${NC}"
            detected_mode="unknown"
        else
            echo -e "  ${RED}✗ STRIPE_PUBLISHABLE_KEY: Invalid format${NC}"
            detected_mode="unknown"
        fi
    else
        echo -e "  ${RED}✗ STRIPE_PUBLISHABLE_KEY: Not configured${NC}"
    fi
    
    if [ -n "$STRIPE_SECRET_KEY" ]; then
        has_secret=true
        if [[ "$STRIPE_SECRET_KEY" =~ ^sk_test_ ]]; then
            echo -e "  ${GREEN}✓ STRIPE_SECRET_KEY: Test key detected${NC}"
            secret_mode="test"
        elif [[ "$STRIPE_SECRET_KEY" =~ ^sk_live_ ]]; then
            echo -e "  ${GREEN}✓ STRIPE_SECRET_KEY: Live key detected${NC}"
            secret_mode="live"
        elif [[ "$STRIPE_SECRET_KEY" =~ replace-with ]]; then
            echo -e "  ${YELLOW}⚠ STRIPE_SECRET_KEY: Placeholder value${NC}"
            secret_mode="unknown"
        else
            echo -e "  ${RED}✗ STRIPE_SECRET_KEY: Invalid format${NC}"
            secret_mode="unknown"
        fi
    else
        echo -e "  ${RED}✗ STRIPE_SECRET_KEY: Not configured${NC}"
    fi
    
    # Check for key type mismatch
    if [ "$detected_mode" != "$secret_mode" ] && [ "$detected_mode" != "unknown" ] && [ "$secret_mode" != "unknown" ]; then
        echo -e "  ${RED}✗ CRITICAL: Key type mismatch! Publishable key is $detected_mode but secret key is $secret_mode${NC}"
        return 1
    fi
    
    # Validate environment-key matching
    if [ "$ENVIRONMENT" = "prod" ]; then
        if [ "$detected_mode" = "test" ]; then
            echo -e "  ${RED}✗ CRITICAL: Production environment is using TEST keys!${NC}"
            echo -e "     Production MUST use live keys (pk_live_... and sk_live_...)${NC}"
            return 1
        elif [ "$detected_mode" = "live" ]; then
            echo -e "  ${GREEN}✓ Production environment using live keys (correct)${NC}"
        fi
    elif [ "$ENVIRONMENT" = "dev" ] || [ "$ENVIRONMENT" = "uat" ]; then
        if [ "$detected_mode" = "live" ]; then
            echo -e "  ${RED}✗ CRITICAL: $ENVIRONMENT environment is using LIVE keys!${NC}"
            echo -e "     $ENVIRONMENT environment should use test keys (pk_test_... and sk_test_...)${NC}"
            return 1
        elif [ "$detected_mode" = "test" ]; then
            echo -e "  ${GREEN}✓ $ENVIRONMENT environment using test keys (correct)${NC}"
        fi
    fi
    
    # Check webhook secret
    if [ -n "$STRIPE_WEBHOOK_SECRET" ]; then
        has_webhook=true
        if [[ "$STRIPE_WEBHOOK_SECRET" =~ ^whsec_ ]]; then
            echo -e "  ${GREEN}✓ STRIPE_WEBHOOK_SECRET: Configured${NC}"
        elif [[ "$STRIPE_WEBHOOK_SECRET" =~ replace-with ]]; then
            echo -e "  ${YELLOW}⚠ STRIPE_WEBHOOK_SECRET: Placeholder value${NC}"
        else
            echo -e "  ${YELLOW}⚠ STRIPE_WEBHOOK_SECRET: Format may be incorrect (expected: whsec_...)${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠ STRIPE_WEBHOOK_SECRET: Not configured${NC}"
    fi
    
    echo ""
    return 0
}

# Validate all environments
ISSUES_FOUND=0

if [ -f "config/dev.env" ]; then
    validate_environment "config/dev.env" "DEV"
    if [ $? -ne 0 ]; then
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
fi

if [ -f "config/uat.env" ]; then
    validate_environment "config/uat.env" "UAT"
    if [ $? -ne 0 ]; then
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
fi

if [ -f "config/prod.env.template" ]; then
    validate_environment "config/prod.env.template" "PROD (template)"
    if [ $? -ne 0 ]; then
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
fi

# Check for actual prod.env file
if [ -f "config/prod.env" ]; then
    validate_environment "config/prod.env" "PROD"
    if [ $? -ne 0 ]; then
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
else
    echo -e "${YELLOW}Note: config/prod.env not found (using template)${NC}"
    echo ""
fi

# Summary
echo "=========================================="
echo "Validation Summary"
echo "=========================================="
echo ""

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ All Stripe configurations are valid${NC}"
    exit 0
else
    echo -e "${RED}✗ $ISSUES_FOUND issue(s) found${NC}"
    echo ""
    echo "Please fix the issues above before deploying."
    exit 1
fi

