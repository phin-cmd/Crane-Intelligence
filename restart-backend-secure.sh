#!/bin/bash

# Secure Backend Restart Script
# Restarts the backend with security measures active

# Don't exit on first error - we want to provide helpful messages
set +e

cd /root/crane

echo "=========================================="
echo "Restarting Backend with Security Enabled"
echo "=========================================="
echo ""

# Check if Docker is available
if ! command -v docker >/dev/null 2>&1; then
    echo "❌ Docker is not installed or not in PATH"
    echo "   Please install Docker or use alternative deployment method"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
    echo "❌ docker-compose is not available"
    echo "   Please install docker-compose"
    exit 1
fi

# Use docker compose (newer) or docker-compose (older)
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo "Step 1: Checking current status..."
$DOCKER_COMPOSE ps

echo ""
echo "Step 2: Verifying environment configuration..."
if grep -q "ENVIRONMENT=production" config/prod.env 2>/dev/null; then
    echo "✅ ENVIRONMENT=production is set"
else
    echo "⚠️  ENVIRONMENT=production not found in config/prod.env"
    echo "   Adding it now..."
    echo "ENVIRONMENT=production" >> config/prod.env
    echo "✅ Added ENVIRONMENT=production"
fi

echo ""
echo "Step 3: Restarting backend container..."
$DOCKER_COMPOSE restart backend

echo ""
echo "Step 4: Waiting for backend to start (10 seconds)..."
sleep 10

echo ""
echo "Step 5: Checking backend health..."
HEALTH_CHECK_PASSED=0
for i in {1..5}; do
    # Try both ports (8004 for Docker, 8003 for direct)
    if curl -s -f http://localhost:8004/api/v1/health >/dev/null 2>&1 || \
       curl -s -f http://localhost:8003/api/v1/health >/dev/null 2>&1; then
        echo "✅ Backend is healthy and responding"
        HEALTH_CHECK_PASSED=1
        break
    else
        if [ $i -eq 5 ]; then
            echo "⚠️  Backend not responding after 5 attempts"
            echo "   This might be normal if backend is still starting"
            echo "   Check logs: $DOCKER_COMPOSE logs backend"
            echo "   Or check if running directly: ps aux | grep uvicorn"
        else
            echo "   Attempt $i failed, retrying in 3 seconds..."
            sleep 3
        fi
    fi
done

echo ""
echo "Step 6: Verifying security measures..."

# Check API docs are disabled (try both ports)
DOCS_CHECKED=0
for port in 8004 8003; do
    if curl -s http://localhost:$port/docs >/dev/null 2>&1; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/docs 2>/dev/null)
        if [ "$HTTP_CODE" = "404" ]; then
            echo "✅ API docs are disabled (404) on port $port"
            DOCS_CHECKED=1
            break
        fi
    fi
done
if [ $DOCS_CHECKED -eq 0 ]; then
    echo "⚠️  Could not verify API docs status (backend may not be running)"
fi

# Check security headers (try both ports)
HEADERS_CHECKED=0
for port in 8004 8003; do
    if curl -sI http://localhost:$port 2>/dev/null | grep -q "X-Frame-Options"; then
        echo "✅ Security headers are present on port $port"
        HEADERS_CHECKED=1
        break
    fi
done
if [ $HEADERS_CHECKED -eq 0 ]; then
    echo "⚠️  Could not verify security headers (backend may not be running or behind proxy)"
fi

echo ""
echo "Step 7: Final status..."
$DOCKER_COMPOSE ps

echo ""
echo "=========================================="
echo "✅ Backend Restart Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run security tests: ./test_security.sh http://localhost:8004"
echo "2. Monitor logs: $DOCKER_COMPOSE logs -f backend"
echo "3. Check security: ./monitor_security.sh monitor"
echo ""

