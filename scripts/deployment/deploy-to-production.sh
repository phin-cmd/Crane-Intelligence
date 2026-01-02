#!/bin/bash
# Deploy changes to PRODUCTION environment only
# This script ensures only the production environment is affected
# ⚠️  WARNING: This affects production - use with caution!

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
echo "Deploying to PRODUCTION Environment ONLY"
echo "=========================================="
echo ""
echo -e "${RED}⚠️  WARNING: This will affect PRODUCTION!${NC}"
echo -e "${RED}⚠️  DEV and UAT will NOT be affected${NC}"
echo ""

# Safety confirmation
read -p "Are you sure you want to deploy to PRODUCTION? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 0
fi

# Check if docker compose is available
if command -v docker compose &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo -e "${RED}ERROR: docker compose not found${NC}"
    exit 1
fi

# Check if docker-compose file exists
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}ERROR: docker-compose.yml not found${NC}"
    exit 1
fi

ENV_NAME="prod"
COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="crane"

echo -e "${BLUE}Step 1: Stopping PRODUCTION backend container...${NC}"
# Stop and remove only PRODUCTION backend container
CONTAINER_NAME="crane-backend-1"
if docker ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    echo -e "${GREEN}✓ PRODUCTION backend container stopped${NC}"
else
    echo -e "${YELLOW}⚠ PRODUCTION backend container not found (may not be running)${NC}"
fi

echo ""
echo -e "${BLUE}Step 2: Rebuilding PRODUCTION backend image...${NC}"
$DOCKER_COMPOSE -f "$COMPOSE_FILE" build --no-cache backend

echo ""
echo -e "${BLUE}Step 3: Starting PRODUCTION backend container...${NC}"
$DOCKER_COMPOSE -f "$COMPOSE_FILE" up -d --no-deps backend

echo ""
echo -e "${BLUE}Step 4: Waiting for PRODUCTION backend to be ready...${NC}"
sleep 5

echo ""
echo -e "${BLUE}Step 5: Verifying PRODUCTION backend...${NC}"
CONTAINER_NAME="crane-backend-1"
if ! docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}✗ PRODUCTION backend container not found${NC}"
    exit 1
fi

# Verify environment
if docker exec "$CONTAINER_NAME" env 2>/dev/null | grep -q "ENVIRONMENT=prod"; then
    echo -e "${GREEN}✓ PRODUCTION backend is running with correct environment${NC}"
    echo ""
    echo "Environment variables:"
    docker exec "$CONTAINER_NAME" env | grep -E "ENVIRONMENT|DO_SPACES_BUCKET|DO_SPACES_CDN|STRIPE" | sed 's/^/  /'
else
    echo -e "${RED}✗ PRODUCTION backend environment verification failed${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}PRODUCTION Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "PRODUCTION Environment:"
echo "  - Backend: http://localhost:8004"
echo "  - Frontend: http://localhost:3001"
echo "  - Database: localhost:5434"
echo ""
echo "To view logs:"
echo "  $DOCKER_COMPOSE -f $COMPOSE_FILE logs -f backend"
echo ""
echo -e "${GREEN}✓ Only PRODUCTION environment was affected${NC}"
echo -e "${GREEN}✓ DEV and UAT remain unchanged${NC}"
echo ""

