#!/bin/bash
# Restart backend for a SINGLE environment only
# Usage: ./scripts/restart-backend-single-env.sh [dev|uat|prod]

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

# Get environment from argument
ENV=${1:-}

if [ -z "$ENV" ]; then
    echo "Usage: $0 [dev|uat|prod]"
    echo ""
    echo "Restart backend for a single environment only."
    echo "This ensures only the specified environment is affected."
    exit 1
fi

ENV=$(echo "$ENV" | tr '[:upper:]' '[:lower:]')

case "$ENV" in
    dev)
        COMPOSE_FILE="docker-compose.dev.yml"
        PROJECT_NAME="crane-dev"
        ENV_FILE="config/dev.env"
        CONTAINER_PATTERN="crane-dev-backend"
        PORT="8104"
        ;;
    uat)
        COMPOSE_FILE="docker-compose.uat.yml"
        PROJECT_NAME="crane-uat"
        ENV_FILE="config/uat.env"
        CONTAINER_PATTERN="crane-uat-backend"
        PORT="8204"
        ;;
    prod|production)
        ENV="prod"
        COMPOSE_FILE="docker-compose.yml"
        PROJECT_NAME="crane"
        ENV_FILE="config/prod.env"
        CONTAINER_PATTERN="crane-backend-1"
        PORT="8004"
        ;;
    *)
        echo -e "${RED}ERROR: Invalid environment '$ENV'${NC}"
        echo "Valid environments: dev, uat, prod"
        exit 1
        ;;
esac

echo "=========================================="
echo "Restarting $ENV Backend ONLY"
echo "=========================================="
echo ""
echo -e "${YELLOW}⚠️  This will only affect the $ENV environment${NC}"
echo ""

# Check if files exist
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}ERROR: $COMPOSE_FILE not found${NC}"
    exit 1
fi

if [ "$ENV" != "prod" ] && [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}ERROR: $ENV_FILE not found${NC}"
    exit 1
fi

# Find container name
if [ "$ENV" = "prod" ]; then
    CONTAINER_NAME="crane-backend-1"
else
    CONTAINER_NAME=$(docker ps -a --format "{{.Names}}" | grep -E "^${PROJECT_NAME}-backend-1$" | head -1)
fi

# Stop and remove container
if [ -n "$CONTAINER_NAME" ] && docker ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${BLUE}Stopping $ENV backend container: $CONTAINER_NAME...${NC}"
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    sleep 1
else
    echo -e "${YELLOW}⚠ $ENV backend container not found (may not be running)${NC}"
fi

# Recreate container
echo -e "${BLUE}Recreating $ENV backend container...${NC}"
if [ "$ENV" = "prod" ]; then
    docker compose -f "$COMPOSE_FILE" up -d --no-deps --force-recreate backend
else
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d --no-deps --force-recreate backend
fi

# Wait for container to start
sleep 3

# Verify
if [ "$ENV" = "prod" ]; then
    CONTAINER_NAME="crane-backend-1"
else
    CONTAINER_NAME=$(docker ps --filter "name=${PROJECT_NAME}-backend" --format "{{.Names}}" | head -1)
fi

if [ -z "$CONTAINER_NAME" ] || ! docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}✗ $ENV backend container not found after creation${NC}"
    exit 1
fi

# Verify environment variables
echo -e "${BLUE}Verifying $ENV backend configuration...${NC}"
EXPECTED_ENV=$(echo "$ENV" | tr '[:lower:]' '[:upper:]')
if [ "$ENV" = "prod" ]; then
    EXPECTED_ENV="PROD"
fi

if docker exec "$CONTAINER_NAME" env 2>/dev/null | grep -q "ENVIRONMENT=$ENV"; then
    echo -e "${GREEN}✓ $ENV backend configured correctly${NC}"
    echo ""
    echo "Environment variables:"
    docker exec "$CONTAINER_NAME" env | grep -E "ENVIRONMENT|DO_SPACES_BUCKET|DO_SPACES_CDN" | sed 's/^/  /'
else
    echo -e "${RED}✗ $ENV backend configuration verification failed${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}$ENV Backend Restart Complete!${NC}"
echo "=========================================="
echo ""
echo -e "${GREEN}✓ Only $ENV environment was affected${NC}"
echo ""

