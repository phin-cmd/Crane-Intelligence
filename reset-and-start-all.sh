#!/bin/bash
# Comprehensive reset and restart script for Crane Intelligence Platform
# This script ensures everything works end-to-end

set -e

cd /root/crane

echo "=========================================="
echo "CRANE INTELLIGENCE - COMPLETE RESET & START"
echo "=========================================="
echo ""

# Step 1: Stop all existing processes
echo "Step 1: Stopping all existing processes..."
echo "----------------------------------------"

# Kill all uvicorn processes
echo "  - Stopping uvicorn processes..."
pkill -f "uvicorn.*8003" 2>/dev/null || echo "    No uvicorn processes found"
sleep 2

# Stop Docker containers
echo "  - Stopping Docker containers..."
docker ps -q --filter "name=crane" | xargs -r docker stop 2>/dev/null || echo "    No Docker containers to stop"
sleep 2

# Remove Docker containers
echo "  - Removing Docker containers..."
docker ps -aq --filter "name=crane" | xargs -r docker rm -f 2>/dev/null || echo "    No Docker containers to remove"

# Stop system nginx if it conflicts
echo "  - Checking for conflicting nginx processes..."
NGINX_CONFLICTS=$(ps aux | grep "nginx.*master" | grep -v grep | grep -v "docker" | wc -l)
if [ "$NGINX_CONFLICTS" -gt 0 ]; then
    echo "    Warning: System nginx detected. Docker nginx will use different ports."
fi

echo "✓ Step 1 complete"
echo ""

# Step 2: Verify Docker is running
echo "Step 2: Verifying Docker..."
echo "----------------------------------------"
if ! systemctl is-active --quiet docker; then
    echo "  - Starting Docker service..."
    systemctl start docker
    sleep 3
fi
echo "✓ Docker is running"
echo ""

# Step 3: Check environment variables
echo "Step 3: Checking critical environment variables..."
echo "----------------------------------------"
if [ -z "$BREVO_API_KEY" ]; then
    echo "  ⚠️  BREVO_API_KEY not set in environment"
    echo "     Will use value from docker-compose.yml or default"
else
    echo "  ✓ BREVO_API_KEY is set"
fi
echo ""

# Step 4: Build and start Docker containers
echo "Step 4: Building and starting Docker containers..."
echo "----------------------------------------"

# Use docker compose (newer syntax) or docker-compose (older)
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    echo "  ✗ ERROR: Neither 'docker compose' nor 'docker-compose' found!"
    exit 1
fi

echo "  - Using: $DOCKER_COMPOSE_CMD"
echo "  - Building images..."
$DOCKER_COMPOSE_CMD build --no-cache 2>&1 | tail -10

echo "  - Starting services..."
$DOCKER_COMPOSE_CMD up -d

echo "  - Waiting for services to initialize (30 seconds)..."
sleep 30

echo "✓ Step 4 complete"
echo ""

# Step 5: Check container status
echo "Step 5: Checking container status..."
echo "----------------------------------------"
$DOCKER_COMPOSE_CMD ps
echo ""

# Step 6: Check logs for errors
echo "Step 6: Checking service logs for errors..."
echo "----------------------------------------"
echo "Backend logs (last 20 lines):"
$DOCKER_COMPOSE_CMD logs --tail=20 backend 2>&1 | tail -20
echo ""
echo "Frontend logs (last 10 lines):"
$DOCKER_COMPOSE_CMD logs --tail=10 frontend 2>&1 | tail -10
echo ""
echo "Database logs (last 10 lines):"
$DOCKER_COMPOSE_CMD logs --tail=10 db 2>&1 | tail -10
echo ""

# Step 7: Health checks
echo "Step 7: Running health checks..."
echo "----------------------------------------"

# Backend health check
echo "  - Testing backend (port 8004)..."
for i in {1..10}; do
    if curl -s -f http://localhost:8004/api/v1/health > /dev/null 2>&1; then
        echo "    ✓ Backend is healthy!"
        BACKEND_HEALTH=$(curl -s http://localhost:8004/api/v1/health)
        echo "    Response: $BACKEND_HEALTH"
        break
    else
        if [ $i -eq 10 ]; then
            echo "    ✗ Backend health check failed after 10 attempts"
            echo "    Checking backend logs..."
            $DOCKER_COMPOSE_CMD logs --tail=30 backend | tail -30
        else
            echo "    Attempt $i/10 failed, retrying in 3 seconds..."
            sleep 3
        fi
    fi
done
echo ""

# Frontend check
echo "  - Testing frontend (port 3001)..."
if curl -s -f http://localhost:3001/ > /dev/null 2>&1; then
    echo "    ✓ Frontend is accessible!"
else
    echo "    ✗ Frontend check failed"
    echo "    Checking frontend logs..."
    $DOCKER_COMPOSE_CMD logs --tail=20 frontend | tail -20
fi
echo ""

# Database check
echo "  - Testing database connection..."
if $DOCKER_COMPOSE_CMD exec -T db pg_isready -U crane_user -d crane_intelligence > /dev/null 2>&1; then
    echo "    ✓ Database is ready!"
    USER_COUNT=$($DOCKER_COMPOSE_CMD exec -T db psql -U crane_user -d crane_intelligence -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | tr -d ' ')
    echo "    Users in database: $USER_COUNT"
else
    echo "    ✗ Database connection failed"
fi
echo ""

# Step 8: Test critical API endpoints
echo "Step 8: Testing critical API endpoints..."
echo "----------------------------------------"

# Test API root
echo "  - Testing /api/v1/..."
if curl -s http://localhost:8004/api/v1/ > /dev/null 2>&1; then
    echo "    ✓ API root accessible"
else
    echo "    ✗ API root failed"
fi

# Test health endpoint
echo "  - Testing /api/v1/health..."
HEALTH_RESPONSE=$(curl -s http://localhost:8004/api/v1/health)
if [ -n "$HEALTH_RESPONSE" ]; then
    echo "    ✓ Health endpoint: $HEALTH_RESPONSE"
else
    echo "    ✗ Health endpoint failed"
fi

echo ""

# Step 9: Final status
echo "=========================================="
echo "FINAL STATUS"
echo "=========================================="
echo ""

echo "Container Status:"
$DOCKER_COMPOSE_CMD ps
echo ""

echo "Port Status:"
netstat -tlnp 2>/dev/null | grep -E ":(80|443|3001|8004|5434|8082)" || ss -tlnp 2>/dev/null | grep -E ":(80|443|3001|8004|5434|8082)"
echo ""

echo "Access URLs:"
echo "  - Frontend: http://localhost:3001"
echo "  - Backend API: http://localhost:8004"
echo "  - Adminer: http://localhost:8082"
echo "  - Database: localhost:5434"
echo ""

echo "Useful commands:"
echo "  - View logs: $DOCKER_COMPOSE_CMD logs -f [service]"
echo "  - Stop all: $DOCKER_COMPOSE_CMD down"
echo "  - Restart: $DOCKER_COMPOSE_CMD restart [service]"
echo ""

echo "=========================================="
echo "RESET & START COMPLETE"
echo "=========================================="

