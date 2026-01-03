#!/bin/bash

# Start backend for security testing
# This script helps start the backend if it's not running

cd /root/crane || exit 1

echo "=========================================="
echo "Starting Backend for Security Tests"
echo "=========================================="
echo ""

# Check if already running
if curl -s http://localhost:8003/api/v1/health >/dev/null 2>&1 || \
   curl -s http://localhost:8004/api/v1/health >/dev/null 2>&1; then
    echo "✅ Backend is already running"
    exit 0
fi

echo "Backend is not running. Starting..."

# Try Docker Compose first
if command -v docker >/dev/null 2>&1; then
    echo "Attempting to start with Docker Compose..."
    
    if docker compose version >/dev/null 2>&1; then
        docker compose up -d backend 2>&1 | head -5
        sleep 5
        if curl -s http://localhost:8004/api/v1/health >/dev/null 2>&1; then
            echo "✅ Backend started on port 8004"
            exit 0
        fi
    elif command -v docker-compose >/dev/null 2>&1; then
        docker-compose up -d backend 2>&1 | head -5
        sleep 5
        if curl -s http://localhost:8004/api/v1/health >/dev/null 2>&1; then
            echo "✅ Backend started on port 8004"
            exit 0
        fi
    fi
fi

# Try direct Python execution
echo "Attempting to start directly with Python..."
cd backend || exit 1

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# Start in background
nohup uvicorn app.main:app --host 0.0.0.0 --port 8003 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

echo "Backend starting (PID: $BACKEND_PID)..."
sleep 5

# Check if it started
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    if curl -s http://localhost:8003/api/v1/health >/dev/null 2>&1; then
        echo "✅ Backend started on port 8003 (PID: $BACKEND_PID)"
        echo "   Logs: /tmp/backend.log"
        exit 0
    else
        echo "⚠️  Backend process started but not responding"
        echo "   Check logs: tail -f /tmp/backend.log"
        exit 1
    fi
else
    echo "❌ Failed to start backend"
    echo "   Check logs: cat /tmp/backend.log"
    exit 1
fi


