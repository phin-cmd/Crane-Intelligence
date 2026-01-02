#!/bin/bash
# Script to restart all backend services with environment-specific DigitalOcean Spaces configuration
# This ensures containers are recreated with the correct environment variables

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRANE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$CRANE_DIR"

echo "=========================================="
echo "Restarting Backend Services with Env Config"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to restart a single environment
restart_environment() {
    local env=$1
    local compose_file=$2
    local env_file=$3
    local project_name="crane-${env}"
    
    echo -e "${YELLOW}Processing $env environment...${NC}"
    
    # Check if env file exists
    if [ ! -f "$env_file" ]; then
        echo -e "${RED}ERROR: Environment file not found: $env_file${NC}"
        return 1
    fi
    
    # Find the actual container name (check multiple possible names)
    local container_name=$(docker ps -a --format "{{.Names}}" | grep -E "(^${project_name}-backend-1$|^crane-backend-1$)" | head -1)
    
    # Also check by port if container name not found
    if [ -z "$container_name" ]; then
        if [ "$env" = "dev" ]; then
            container_name=$(docker ps -a --filter "publish=8104" --format "{{.Names}}" | head -1)
        elif [ "$env" = "uat" ]; then
            container_name=$(docker ps -a --filter "publish=8204" --format "{{.Names}}" | head -1)
        fi
    fi
    
    # Stop and remove backend container only (not dependencies)
    if [ -n "$container_name" ]; then
        echo "  Stopping $env backend container: $container_name..."
        docker stop "$container_name" 2>/dev/null || true
        docker rm "$container_name" 2>/dev/null || true
        sleep 1
    fi
    
    # Recreate backend container with new environment variables using project name
    echo "  Recreating $env backend container..."
    docker compose -f "$compose_file" -p "$project_name" up -d --no-deps --force-recreate backend
    
    # Wait for container to start
    sleep 3
    
    # Find the new container name
    container_name=$(docker ps --filter "name=${project_name}-backend" --format "{{.Names}}" | head -1)
    
    if [ -z "$container_name" ]; then
        echo -e "  ${RED}✗ $env backend container not found after creation${NC}"
        return 1
    fi
    
    # Verify environment variables
    echo "  Verifying configuration for: $container_name..."
    if docker exec "$container_name" env 2>/dev/null | grep -q "ENVIRONMENT=$env"; then
        echo -e "  ${GREEN}✓ $env backend configured correctly${NC}"
        
        # Show key environment variables
        echo "  Environment variables:"
        docker exec "$container_name" env | grep -E "ENVIRONMENT|DO_SPACES_BUCKET|DO_SPACES_CDN" | sed 's/^/    /'
    else
        echo -e "  ${RED}✗ $env backend configuration verification failed${NC}"
        return 1
    fi
    
    echo ""
}

# Function to restart production environment
restart_production() {
    echo -e "${YELLOW}Processing production environment...${NC}"
    
    # Stop and remove backend container
    echo "  Stopping production backend container..."
    docker stop crane-backend-1 2>/dev/null || true
    docker rm crane-backend-1 2>/dev/null || true
    
    # Recreate backend container
    echo "  Recreating production backend container..."
    docker compose up -d --no-deps --force-recreate backend
    
    # Wait for container to start
    sleep 3
    
    # Verify environment variables
    echo "  Verifying configuration..."
    if docker exec crane-backend-1 env | grep -q "ENVIRONMENT=prod"; then
        echo -e "  ${GREEN}✓ Production backend configured correctly${NC}"
        
        # Show key environment variables
        echo "  Environment variables:"
        docker exec crane-backend-1 env | grep -E "ENVIRONMENT|DO_SPACES_BUCKET|DO_SPACES_CDN" | sed 's/^/    /'
    else
        echo -e "  ${RED}✗ Production backend configuration verification failed${NC}"
        return 1
    fi
    
    echo ""
}

# Main execution
echo "Starting backend service restarts..."
echo ""

# Restart Dev environment
if [ -f "docker-compose.dev.yml" ] && [ -f "config/dev.env" ]; then
    restart_environment "dev" "docker-compose.dev.yml" "config/dev.env"
else
    echo -e "${YELLOW}Warning: Dev environment files not found, skipping...${NC}"
fi

# Restart UAT environment
if [ -f "docker-compose.uat.yml" ] && [ -f "config/uat.env" ]; then
    restart_environment "uat" "docker-compose.uat.yml" "config/uat.env"
else
    echo -e "${YELLOW}Warning: UAT environment files not found, skipping...${NC}"
fi

# Restart Production environment
if [ -f "docker-compose.yml" ]; then
    restart_production
else
    echo -e "${YELLOW}Warning: Production docker-compose.yml not found, skipping...${NC}"
fi

# Final status check
echo "=========================================="
echo "Final Status Check"
echo "=========================================="
echo ""

docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "backend" || echo "No backend containers found"

echo ""
echo -e "${GREEN}Backend service restart complete!${NC}"
echo ""
echo "To verify environment variables in each container, find container names with:"
echo "  docker ps | grep backend"
echo ""
echo "Then check each container:"
echo "  docker exec <container-name> env | grep -E 'ENVIRONMENT|DO_SPACES'"
echo ""

