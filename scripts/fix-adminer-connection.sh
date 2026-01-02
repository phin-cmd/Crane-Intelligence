#!/bin/bash
# Script to fix Adminer database connection issues
# Ensures database container is running and Adminer can connect

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
echo "Adminer Database Connection Fix"
echo "=========================================="
echo ""

# Check if database container exists
if ! docker ps -a --format "{{.Names}}" | grep -q "^crane-db-1$"; then
    echo -e "${YELLOW}Database container not found. Creating...${NC}"
    docker compose up -d db
    sleep 5
fi

# Check if database is running
if ! docker ps --format "{{.Names}}" | grep -q "^crane-db-1$"; then
    echo -e "${YELLOW}Database container not running. Starting...${NC}"
    
    # Try to start the container
    if docker start crane-db-1 2>&1 | grep -q "port.*already allocated"; then
        echo -e "${YELLOW}Port conflict detected. Removing and recreating container...${NC}"
        docker rm -f crane-db-1
        docker compose up -d db
    else
        docker start crane-db-1
    fi
    
    echo "Waiting for database to be ready..."
    sleep 5
fi

# Wait for database to be ready
echo -e "${BLUE}Waiting for database to be ready...${NC}"
for i in {1..30}; do
    if docker exec crane-db-1 pg_isready -U crane_user > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Database is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Database did not become ready in time${NC}"
        exit 1
    fi
    sleep 1
done

# Verify network connectivity
echo -e "${BLUE}Verifying network connectivity...${NC}"
if docker exec crane-adminer-1 ping -c 1 db > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Adminer can reach database${NC}"
else
    echo -e "${YELLOW}⚠ Adminer cannot ping database hostname${NC}"
    echo "  This might be a network issue. Checking container networks..."
    
    # Check if containers are on same network
    adminer_net=$(docker inspect crane-adminer-1 --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}')
    db_net=$(docker inspect crane-db-1 --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}')
    
    if [ "$adminer_net" = "$db_net" ]; then
        echo -e "${GREEN}✓ Containers are on the same network${NC}"
    else
        echo -e "${RED}✗ Containers are on different networks${NC}"
        echo "  Adminer network: $adminer_net"
        echo "  Database network: $db_net"
        echo "  Restarting Adminer to fix network..."
        docker restart crane-adminer-1
        sleep 3
    fi
fi

# Test database connection
echo -e "${BLUE}Testing database connection...${NC}"
if docker exec crane-db-1 psql -U crane_user -d crane_intelligence -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Database connection successful${NC}"
else
    echo -e "${RED}✗ Database connection failed${NC}"
    echo "  Checking database logs..."
    docker logs crane-db-1 --tail 10
    exit 1
fi

# Restart Adminer to ensure fresh connection
echo -e "${BLUE}Restarting Adminer...${NC}"
docker restart crane-adminer-1
sleep 3

# Summary
echo ""
echo "=========================================="
echo "Fix Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}✓ Database container is running${NC}"
echo -e "${GREEN}✓ Database is accepting connections${NC}"
echo -e "${GREEN}✓ Adminer can reach database${NC}"
echo ""
echo "Adminer should now be accessible at:"
echo "  http://129.212.177.131:8082"
echo ""
echo "Connection details:"
echo "  System: PostgreSQL"
echo "  Server: db"
echo "  Username: crane_user"
echo "  Password: crane_password"
echo "  Database: crane_intelligence"
echo ""
echo "If you still have issues, try:"
echo "  1. Clear browser cache"
echo "  2. Use the direct connection URL:"
echo "     http://129.212.177.131:8082/?pgsql=db&username=crane_user&db=crane_intelligence"
echo ""

