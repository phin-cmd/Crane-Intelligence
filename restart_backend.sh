#!/bin/bash
# Script to fix Docker issues and restart the backend service

set -e

echo "=== Fixing Docker Issues and Restarting Backend ==="

# Step 1: Check and start Docker daemon
echo "Step 1: Checking Docker daemon status..."
if ! sudo systemctl is-active --quiet docker; then
    echo "Docker daemon is not running. Starting it..."
    sudo systemctl start docker
    sleep 2
else
    echo "Docker daemon is running."
fi

# Step 2: Fix Docker socket permissions
echo "Step 2: Fixing Docker socket permissions..."
sudo chmod 666 /var/run/docker.sock 2>/dev/null || echo "Note: Could not modify socket permissions (may need different approach)"

# Step 3: Check Docker connection
echo "Step 3: Testing Docker connection..."
if docker ps > /dev/null 2>&1; then
    echo "✓ Docker connection successful"
    DOCKER_CMD="docker"
    COMPOSE_CMD="docker compose"
else
    echo "⚠ Docker connection failed, trying with sudo..."
    if sudo docker ps > /dev/null 2>&1; then
        echo "✓ Docker connection successful with sudo"
        DOCKER_CMD="sudo docker"
        COMPOSE_CMD="sudo docker compose"
    else
        echo "✗ Docker connection failed. Please check Docker installation."
        exit 1
    fi
fi

# Step 4: Navigate to project directory
cd /root/crane || { echo "Error: Could not navigate to /root/crane"; exit 1; }

# Step 5: Try Docker Compose v2 first, then fallback to v1
echo "Step 4: Attempting to restart backend with Docker Compose..."
if $COMPOSE_CMD restart backend 2>/dev/null; then
    echo "✓ Backend restarted successfully using docker compose"
elif docker-compose restart backend 2>/dev/null; then
    echo "✓ Backend restarted successfully using docker-compose"
else
    echo "⚠ Docker Compose failed, trying direct Docker restart..."
    # Find backend container
    CONTAINER_ID=$($DOCKER_CMD ps -q -f "name=backend" -f "name=crane.*backend" | head -1)
    if [ -z "$CONTAINER_ID" ]; then
        CONTAINER_ID=$($DOCKER_CMD ps -a | grep backend | awk '{print $1}' | head -1)
    fi
    
    if [ -n "$CONTAINER_ID" ]; then
        echo "Found container: $CONTAINER_ID"
        $DOCKER_CMD restart $CONTAINER_ID
        echo "✓ Backend container restarted directly"
    else
        echo "✗ Could not find backend container. Listing all containers:"
        $DOCKER_CMD ps -a
        exit 1
    fi
fi

# Step 6: Wait for service to start
echo "Step 5: Waiting for backend to start..."
sleep 5

# Step 7: Check logs for consultation router
echo "Step 6: Checking consultation router status..."
if $COMPOSE_CMD logs --tail=100 backend 2>/dev/null | grep -i "consultation router" | head -5; then
    echo ""
    echo "✓ Consultation router found in logs"
elif docker-compose logs --tail=100 backend 2>/dev/null | grep -i "consultation router" | head -5; then
    echo ""
    echo "✓ Consultation router found in logs"
else
    echo "⚠ Consultation router message not found in recent logs"
    echo "Showing last 20 lines of backend logs:"
    $DOCKER_CMD logs --tail=20 $(docker ps -q -f "name=backend" | head -1) 2>/dev/null || echo "Could not retrieve logs"
fi

echo ""
echo "=== Restart Complete ==="
echo "Backend service has been restarted."
echo "Check the logs above to verify the consultation router is loaded."
