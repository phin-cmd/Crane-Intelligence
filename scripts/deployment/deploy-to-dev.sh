#!/bin/bash
# Deploy changes to DEV environment only
# This script ensures only the dev environment is affected

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRANE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$CRANE_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Deploying to DEV Environment ONLY"
echo "=========================================="
echo ""
echo -e "${YELLOW}⚠️  WARNING: This will only affect the DEV environment${NC}"
echo -e "${YELLOW}⚠️  UAT and Production will NOT be affected${NC}"
echo ""

# Check if docker compose is available
if command -v docker compose &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo -e "${RED}ERROR: docker compose not found${NC}"
    exit 1
fi

# Check if environment file exists
if [ ! -f "config/dev.env" ]; then
    echo -e "${RED}ERROR: config/dev.env not found${NC}"
    exit 1
fi

# Check if docker-compose file exists
if [ ! -f "docker-compose.dev.yml" ]; then
    echo -e "${RED}ERROR: docker-compose.dev.yml not found${NC}"
    exit 1
fi

ENV_NAME="dev"
COMPOSE_FILE="docker-compose.dev.yml"
PROJECT_NAME="crane-dev"
ENV_FILE="config/dev.env"

echo -e "${BLUE}Step 1: Stopping DEV backend container...${NC}"
# Stop and remove only DEV backend container
CONTAINER_NAME=$(docker ps -a --format "{{.Names}}" | grep -E "^${PROJECT_NAME}-backend-1$" | head -1)
if [ -n "$CONTAINER_NAME" ]; then
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    echo -e "${GREEN}✓ DEV backend container stopped${NC}"
else
    echo -e "${YELLOW}⚠ DEV backend container not found (may not be running)${NC}"
fi

echo ""
echo -e "${BLUE}Step 2: Rebuilding DEV backend image...${NC}"
$DOCKER_COMPOSE -f "$COMPOSE_FILE" -p "$PROJECT_NAME" build --no-cache backend

echo ""
echo -e "${BLUE}Step 3: Starting DEV backend container...${NC}"
$DOCKER_COMPOSE -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d --no-deps backend

echo ""
echo -e "${BLUE}Step 4: Waiting for DEV backend to be ready...${NC}"
sleep 5

echo ""
echo -e "${BLUE}Step 5: Verifying DEV backend...${NC}"
CONTAINER_NAME=$(docker ps --filter "name=${PROJECT_NAME}-backend" --format "{{.Names}}" | head -1)
if [ -z "$CONTAINER_NAME" ]; then
    echo -e "${RED}✗ DEV backend container not found${NC}"
    exit 1
fi

# Verify environment
if docker exec "$CONTAINER_NAME" env 2>/dev/null | grep -q "ENVIRONMENT=dev"; then
    echo -e "${GREEN}✓ DEV backend is running with correct environment${NC}"
    echo ""
    echo "Environment variables:"
    docker exec "$CONTAINER_NAME" env | grep -E "ENVIRONMENT|DO_SPACES_BUCKET|DO_SPACES_CDN|STRIPE" | sed 's/^/  /'
else
    echo -e "${RED}✗ DEV backend environment verification failed${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}DEV Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "DEV Environment:"
echo "  - Backend: http://localhost:8104"
echo "  - Frontend: http://localhost:3101"
echo "  - Database: localhost:5534"
echo ""
echo "To view logs:"
echo "  $DOCKER_COMPOSE -f $COMPOSE_FILE -p $PROJECT_NAME logs -f backend"
echo ""
echo -e "${GREEN}✓ Only DEV environment was affected${NC}"
echo -e "${GREEN}✓ UAT and Production remain unchanged${NC}"
echo ""

