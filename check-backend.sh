#!/bin/bash

# Quick script to check if backend is running and accessible

echo "=========================================="
echo "Backend Status Check"
echo "=========================================="
echo ""

# Check common ports
PORTS=(8004 8003 8000 8080)
BACKEND_FOUND=0

for port in "${PORTS[@]}"; do
    echo -n "Checking port $port... "
    response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port/api/v1/health" 2>/dev/null)
    
    if [ "$response" = "200" ] || [ "$response" = "404" ]; then
        echo "✅ Backend responding (HTTP $response)"
        echo "   URL: http://localhost:$port"
        BACKEND_FOUND=1
        
        # Test health endpoint
        health=$(curl -s "http://localhost:$port/api/v1/health" 2>/dev/null)
        if [ -n "$health" ]; then
            echo "   Health check: OK"
        fi
        break
    elif [ "$response" = "000" ]; then
        echo "❌ Connection refused"
    else
        echo "⚠️  Got HTTP $response"
    fi
done

echo ""

# Check Docker
echo "Checking Docker containers..."
if command -v docker >/dev/null 2>&1; then
    if docker compose ps 2>/dev/null | grep -q "backend\|Up"; then
        echo "✅ Docker containers running"
        docker compose ps 2>/dev/null | grep -E "NAME|backend"
    elif docker-compose ps 2>/dev/null | grep -q "backend\|Up"; then
        echo "✅ Docker containers running"
        docker-compose ps 2>/dev/null | grep -E "NAME|backend"
    else
        echo "⚠️  No Docker containers found"
    fi
else
    echo "⚠️  Docker not available"
fi

echo ""

# Check processes
echo "Checking running processes..."
if pgrep -f "uvicorn.*main:app" >/dev/null; then
    echo "✅ Backend process found:"
    ps aux | grep -E "uvicorn|gunicorn" | grep -v grep | head -2
else
    echo "⚠️  No backend process found"
fi

echo ""

if [ $BACKEND_FOUND -eq 0 ]; then
    echo "=========================================="
    echo "❌ Backend is not accessible"
    echo "=========================================="
    echo ""
    echo "To start the backend:"
    echo ""
    echo "Option 1: Docker Compose"
    echo "  cd /root/crane"
    echo "  docker compose up -d"
    echo ""
    echo "Option 2: Direct Python"
    echo "  cd /root/crane/backend"
    echo "  uvicorn app.main:app --host 0.0.0.0 --port 8003"
    echo ""
    echo "Option 3: Use restart script"
    echo "  cd /root/crane"
    echo "  ./restart-backend-secure.sh"
    echo ""
    exit 1
else
    echo "=========================================="
    echo "✅ Backend is accessible"
    echo "=========================================="
    echo ""
    echo "You can now run security tests:"
    echo "  ./test_security.sh http://localhost:$port"
    echo ""
    exit 0
fi


