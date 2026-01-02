#!/bin/bash
# Complete Payment Flow Verification Script
# Verifies webhook secrets, tests payment flow, and confirms end-to-end working

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRANE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$CRANE_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "=========================================="
echo "Complete Payment Flow Verification"
echo "=========================================="
echo ""

# Step 1: Verify webhook secrets in config files
echo -e "${BLUE}Step 1: Verifying Webhook Secrets in Config Files${NC}"
echo ""

ENVS=("dev" "uat" "prod")
ALL_SECRETS_OK=true

for env in "${ENVS[@]}"; do
    env_file="config/${env}.env"
    if [ -f "$env_file" ]; then
        webhook_secret=$(grep "^STRIPE_WEBHOOK_SECRET=" "$env_file" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
        if [[ "$webhook_secret" =~ ^whsec_ ]] && [[ ! "$webhook_secret" =~ replace ]]; then
            echo -e "${GREEN}✓ ${env^^}: Webhook secret configured (${webhook_secret:0:20}...)${NC}"
        else
            echo -e "${RED}✗ ${env^^}: Webhook secret not properly configured${NC}"
            ALL_SECRETS_OK=false
        fi
    else
        echo -e "${RED}✗ ${env^^}: Config file not found${NC}"
        ALL_SECRETS_OK=false
    fi
done
echo ""

# Step 2: Restart backends to load new secrets
if [ "$ALL_SECRETS_OK" = true ]; then
    echo -e "${BLUE}Step 2: Restarting Backend Services${NC}"
    echo ""
    
    # Restart DEV
    if docker ps --format "{{.Names}}" | grep -q "^crane-dev-backend-1$"; then
        echo "Restarting DEV backend..."
        docker restart crane-dev-backend-1 >/dev/null 2>&1
        sleep 3
        echo -e "${GREEN}✓ DEV backend restarted${NC}"
    fi
    
    # Restart UAT
    if docker ps --format "{{.Names}}" | grep -q "^crane-uat-backend-1$"; then
        echo "Restarting UAT backend..."
        docker restart crane-uat-backend-1 >/dev/null 2>&1
        sleep 3
        echo -e "${GREEN}✓ UAT backend restarted${NC}"
    fi
    
    # Restart PROD
    if docker ps --format "{{.Names}}" | grep -q "^crane-backend-1$"; then
        echo "Restarting PROD backend..."
        docker restart crane-backend-1 >/dev/null 2>&1
        sleep 3
        echo -e "${GREEN}✓ PROD backend restarted${NC}"
    fi
    echo ""
fi

# Step 3: Wait for backends to be ready
echo -e "${BLUE}Step 3: Waiting for Backends to be Ready${NC}"
sleep 5
echo ""

# Step 4: Test config endpoints
echo -e "${BLUE}Step 4: Testing Config Endpoints${NC}"
echo ""

declare -A ENDPOINTS
ENDPOINTS[dev]="http://localhost:8104"
ENDPOINTS[uat]="http://localhost:8204"
ENDPOINTS[prod]="http://localhost:8004"

ALL_CONFIG_OK=true
for env in "${ENVS[@]}"; do
    base_url="${ENDPOINTS[$env]}"
    response=$(curl -s "${base_url}/api/v1/config/public" 2>/dev/null || echo "")
    
    if [ -n "$response" ] && echo "$response" | grep -q "stripe_publishable_key"; then
        stripe_key=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('stripe_publishable_key', ''))" 2>/dev/null || echo "")
        stripe_mode=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('stripe_mode', ''))" 2>/dev/null || echo "")
        
        if [ -n "$stripe_key" ]; then
            if [ "$env" = "prod" ]; then
                if [[ "$stripe_key" =~ ^pk_live_ ]]; then
                    echo -e "${GREEN}✓ ${env^^}: Config endpoint working (Live mode)${NC}"
                else
                    echo -e "${RED}✗ ${env^^}: Config endpoint returns wrong key type${NC}"
                    ALL_CONFIG_OK=false
                fi
            else
                if [[ "$stripe_key" =~ ^pk_test_ ]]; then
                    echo -e "${GREEN}✓ ${env^^}: Config endpoint working (Test mode)${NC}"
                else
                    echo -e "${RED}✗ ${env^^}: Config endpoint returns wrong key type${NC}"
                    ALL_CONFIG_OK=false
                fi
            fi
        else
            echo -e "${RED}✗ ${env^^}: Config endpoint not returning valid data${NC}"
            ALL_CONFIG_OK=false
        fi
    else
        echo -e "${RED}✗ ${env^^}: Config endpoint not accessible${NC}"
        ALL_CONFIG_OK=false
    fi
done
echo ""

# Step 5: Test payment intent creation
echo -e "${BLUE}Step 5: Testing Payment Intent Creation${NC}"
echo ""

ALL_PAYMENT_OK=true
for env in "${ENVS[@]}"; do
    base_url="${ENDPOINTS[$env]}"
    response=$(curl -s -X POST "${base_url}/api/v1/fmv-reports/create-payment" \
        -H "Content-Type: application/json" \
        -d '{
            "report_type": "spot_check",
            "amount": 10000,
            "crane_data": {"manufacturer": "Test", "model": "Test Model"},
            "cardholder_name": "Test User",
            "receipt_email": "test@example.com"
        }' 2>/dev/null || echo "")
    
    if [ -n "$response" ] && echo "$response" | grep -q "success"; then
        success=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "False")
        pi_id=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('payment_intent_id', ''))" 2>/dev/null || echo "")
        
        if [ "$success" = "True" ] || [ "$success" = "true" ]; then
            echo -e "${GREEN}✓ ${env^^}: Payment intent created successfully${NC}"
            echo -e "  Payment Intent ID: ${CYAN}${pi_id:0:40}...${NC}"
        else
            echo -e "${RED}✗ ${env^^}: Payment intent creation failed${NC}"
            ALL_PAYMENT_OK=false
        fi
    else
        echo -e "${RED}✗ ${env^^}: Payment endpoint not accessible${NC}"
        ALL_PAYMENT_OK=false
    fi
done
echo ""

# Step 6: Check webhook secrets in running containers
echo -e "${BLUE}Step 6: Verifying Webhook Secrets in Running Containers${NC}"
echo ""

declare -A CONTAINERS
CONTAINERS[dev]="crane-dev-backend-1"
CONTAINERS[uat]="crane-uat-backend-1"
CONTAINERS[prod]="crane-backend-1"

ALL_CONTAINERS_OK=true
for env in "${ENVS[@]}"; do
    container="${CONTAINERS[$env]}"
    if docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
        env_vars=$(docker exec "$container" env 2>/dev/null || echo "")
        if echo "$env_vars" | grep -q "STRIPE_WEBHOOK_SECRET=whsec_"; then
            secret=$(echo "$env_vars" | grep "STRIPE_WEBHOOK_SECRET=" | cut -d'=' -f2-)
            if [[ ! "$secret" =~ replace ]]; then
                echo -e "${GREEN}✓ ${env^^}: Webhook secret loaded in container${NC}"
            else
                echo -e "${RED}✗ ${env^^}: Webhook secret not properly loaded${NC}"
                ALL_CONTAINERS_OK=false
            fi
        else
            echo -e "${RED}✗ ${env^^}: Webhook secret not found in container${NC}"
            ALL_CONTAINERS_OK=false
        fi
    else
        echo -e "${YELLOW}⚠ ${env^^}: Container not running${NC}"
    fi
done
echo ""

# Step 7: Check Stripe service logs
echo -e "${BLUE}Step 7: Checking Stripe Service Status${NC}"
echo ""

for env in "${ENVS[@]}"; do
    container="${CONTAINERS[$env]}"
    if docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
        logs=$(docker logs "$container" --tail 50 2>&1 | grep -i "stripe service" | tail -3)
        if echo "$logs" | grep -q "initialized"; then
            echo -e "${GREEN}✓ ${env^^}: Stripe service initialized${NC}"
        else
            echo -e "${YELLOW}⚠ ${env^^}: Could not verify Stripe service status${NC}"
        fi
    fi
done
echo ""

# Final Summary
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo ""

if [ "$ALL_SECRETS_OK" = true ] && [ "$ALL_CONFIG_OK" = true ] && [ "$ALL_PAYMENT_OK" = true ] && [ "$ALL_CONTAINERS_OK" = true ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo -e "${CYAN}Payment Flow Status:${NC}"
    echo "  ✓ Webhook secrets configured in all environments"
    echo "  ✓ Backend services restarted"
    echo "  ✓ Config endpoints working"
    echo "  ✓ Payment intent creation working"
    echo "  ✓ Webhook secrets loaded in containers"
    echo ""
    echo -e "${CYAN}Next Steps:${NC}"
    echo "  1. Test frontend payment flow:"
    echo "     - DEV: https://dev.craneintelligence.tech/report-generation.html"
    echo "     - UAT: https://uat.craneintelligence.tech/report-generation.html"
    echo "     - PROD: https://craneintelligence.tech/report-generation.html"
    echo ""
    echo "  2. Monitor webhook delivery:"
    echo "     docker logs crane-dev-backend-1 -f | grep -i webhook"
    echo ""
    echo "  3. Verify report status updates after payment"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some checks failed${NC}"
    echo ""
    echo "Please review the output above and fix any issues."
    exit 1
fi

