#!/bin/bash
# Script to properly restart the backend

echo "=== Restarting Backend ==="
echo ""

# Step 1: Find and kill existing processes
echo "1. Stopping existing backend processes..."
pkill -f "uvicorn.*main:app" 2>/dev/null
sleep 2

# Check if port is still in use
if lsof -ti:8004 >/dev/null 2>&1; then
    echo "   Port 8004 still in use, force killing..."
    lsof -ti:8004 | xargs kill -9 2>/dev/null
    sleep 2
fi

# Verify port is free
if lsof -ti:8004 >/dev/null 2>&1; then
    echo "   ❌ Port 8004 is still in use"
    exit 1
else
    echo "   ✅ Port 8004 is now free"
fi

# Step 2: Load environment variables
echo ""
echo "2. Loading environment variables..."
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "   ✅ Loaded from .env"
else
    echo "   ⚠️  .env file not found, using defaults"
fi

# Ensure DigitalOcean Spaces credentials are set (from environment or .env)
# NOTE: DO_SPACES_KEY and DO_SPACES_SECRET should be set in .env file (not committed to git)
if [ -z "$DO_SPACES_KEY" ] || [ -z "$DO_SPACES_SECRET" ]; then
    echo "   ⚠️  WARNING: DO_SPACES_KEY or DO_SPACES_SECRET not set!"
    echo "   Please set these in .env file or environment variables."
fi

export DO_SPACES_REGION=${DO_SPACES_REGION:-"atl1"}
export DO_SPACES_BUCKET=${DO_SPACES_BUCKET:-"crane-intelligence-storage"}
export ENVIRONMENT=${ENVIRONMENT:-"prod"}

if [ -n "$DO_SPACES_KEY" ]; then
    echo "   DO_SPACES_KEY: ${DO_SPACES_KEY:0:10}..."
else
    echo "   DO_SPACES_KEY: NOT SET"
fi
echo "   DO_SPACES_REGION: $DO_SPACES_REGION"
echo "   DO_SPACES_BUCKET: $DO_SPACES_BUCKET"
echo "   ENVIRONMENT: $ENVIRONMENT"

# Step 3: Start backend
echo ""
echo "3. Starting backend on port 8004..."
cd /root/crane/backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

echo "   Backend started with PID: $BACKEND_PID"

# Step 4: Wait and check status
echo ""
echo "4. Waiting for backend to initialize..."
sleep 5

if ps -p $BACKEND_PID > /dev/null; then
    echo "   ✅ Backend process is running"
else
    echo "   ❌ Backend process died, check logs:"
    tail -50 /tmp/backend.log
    exit 1
fi

# Step 5: Check for initialization messages
echo ""
echo "5. Checking initialization logs..."
if grep -q "DigitalOcean Spaces client initialized" /tmp/backend.log 2>/dev/null; then
    echo "   ✅ Storage service initialized"
    grep "DigitalOcean Spaces client initialized" /tmp/backend.log | tail -1
else
    echo "   ⚠️  Storage service initialization not found in logs yet"
fi

# Step 6: Test health endpoint
echo ""
echo "6. Testing backend health..."
sleep 2
if curl -s http://localhost:8004/health > /dev/null 2>&1; then
    echo "   ✅ Backend is responding"
else
    echo "   ⚠️  Backend not responding yet (may need more time)"
fi

echo ""
echo "=== Backend Restart Complete ==="
echo ""
echo "Backend logs: /tmp/backend.log"
echo "To view logs: tail -f /tmp/backend.log"
echo "To check storage service: grep -i 'storage\|spaces' /tmp/backend.log"
