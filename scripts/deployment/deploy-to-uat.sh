#!/bin/bash
# Deploy changes to UAT environment only
# This script ensures only the UAT environment is affected

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
echo "Deploying to UAT Environment ONLY"
echo "=========================================="
echo ""
echo -e "${YELLOW}⚠️  WARNING: This will only affect the UAT environment${NC}"
echo -e "${YELLOW}⚠️  DEV and Production will NOT be affected${NC}"
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
if [ ! -f "config/uat.env" ]; then
    echo -e "${RED}ERROR: config/uat.env not found${NC}"
    exit 1
fi

# Check if docker-compose file exists
if [ ! -f "docker-compose.uat.yml" ]; then
    echo -e "${RED}ERROR: docker-compose.uat.yml not found${NC}"
    exit 1
fi

ENV_NAME="uat"
COMPOSE_FILE="docker-compose.uat.yml"
PROJECT_NAME="crane-uat"
ENV_FILE="config/uat.env"

echo -e "${BLUE}Step 1: Stopping UAT backend container...${NC}"
# Stop and remove only UAT backend container
CONTAINER_NAME=$(docker ps -a --format "{{.Names}}" | grep -E "^${PROJECT_NAME}-backend-1$" | head -1)
if [ -n "$CONTAINER_NAME" ]; then
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    echo -e "${GREEN}✓ UAT backend container stopped${NC}"
else
    echo -e "${YELLOW}⚠ UAT backend container not found (may not be running)${NC}"
fi

echo ""
echo -e "${BLUE}Step 2: Rebuilding UAT backend image...${NC}"
$DOCKER_COMPOSE -f "$COMPOSE_FILE" -p "$PROJECT_NAME" build --no-cache backend

echo ""
echo -e "${BLUE}Step 3: Starting UAT backend container...${NC}"
$DOCKER_COMPOSE -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d --no-deps backend

echo ""
echo -e "${BLUE}Step 4: Waiting for UAT backend to be ready...${NC}"
sleep 5

echo ""
echo -e "${BLUE}Step 5: Verifying UAT backend...${NC}"
CONTAINER_NAME=$(docker ps --filter "name=${PROJECT_NAME}-backend" --format "{{.Names}}" | head -1)
if [ -z "$CONTAINER_NAME" ]; then
    echo -e "${RED}✗ UAT backend container not found${NC}"
    exit 1
fi

# Verify environment
if docker exec "$CONTAINER_NAME" env 2>/dev/null | grep -q "ENVIRONMENT=uat"; then
    echo -e "${GREEN}✓ UAT backend is running with correct environment${NC}"
    echo ""
    echo "Environment variables:"
    docker exec "$CONTAINER_NAME" env | grep -E "ENVIRONMENT|DO_SPACES_BUCKET|DO_SPACES_CDN|STRIPE" | sed 's/^/  /'
else
    echo -e "${RED}✗ UAT backend environment verification failed${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}UAT Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "UAT Environment:"
echo "  - Backend: http://localhost:8204"
echo "  - Frontend: http://localhost:3201"
echo "  - Database: localhost:5634"
echo ""
echo "To view logs:"
echo "  $DOCKER_COMPOSE -f $COMPOSE_FILE -p $PROJECT_NAME logs -f backend"
echo ""
echo -e "${GREEN}✓ Only UAT environment was affected${NC}"
echo -e "${GREEN}✓ DEV and Production remain unchanged${NC}"
echo ""

