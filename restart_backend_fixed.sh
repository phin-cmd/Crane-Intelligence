#!/bin/bash
# Script to restart the FastAPI/uvicorn backend server
# This script handles dependency installation and server restart

set -e

echo "🔄 Restarting FastAPI backend server..."

# Find and kill the existing uvicorn process
echo "📋 Finding existing uvicorn process..."
PID=$(pgrep -f "uvicorn app.main:app" || true)
if [ -n "$PID" ]; then
    echo "🛑 Stopping process $PID..."
    kill $PID 2>/dev/null || true
    sleep 2
    # Force kill if still running
    if kill -0 $PID 2>/dev/null; then
        echo "⚠️  Process still running, force killing..."
        kill -9 $PID 2>/dev/null || true
        sleep 1
    fi
    echo "✅ Process stopped"
else
    echo "ℹ️  No existing process found"
fi

# Wait a moment
sleep 1

# Navigate to backend directory
cd /root/crane/backend || { echo "❌ Cannot find /root/crane/backend"; exit 1; }

# Check if uvicorn is available
PYTHON_CMD="/usr/bin/python3"
if [ -f "/usr/local/bin/python3.11" ]; then
    PYTHON_CMD="/usr/local/bin/python3.11"
fi

echo "📝 Using Python: $PYTHON_CMD"

# Check if uvicorn is installed
if ! $PYTHON_CMD -m uvicorn --version >/dev/null 2>&1; then
    echo "⚠️  uvicorn not found. Installing dependencies..."
    echo "📦 Installing from requirements.txt (this may take a minute)..."
    $PYTHON_CMD -m pip install --upgrade pip --break-system-packages >/dev/null 2>&1
    $PYTHON_CMD -m pip install uvicorn[standard] fastapi --break-system-packages >/dev/null 2>&1
    echo "✅ Dependencies installed"
fi

# Start the server in the background
echo "🚀 Starting uvicorn server..."
nohup $PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8003 > /tmp/uvicorn.log 2>&1 &

# Wait a moment for it to start
sleep 3

# Check if it's running
NEW_PID=$(pgrep -f "uvicorn app.main:app" || true)
if [ -n "$NEW_PID" ]; then
    echo "✅ Server restarted successfully! PID: $NEW_PID"
    echo "📝 Logs are being written to: /tmp/uvicorn.log"
    echo "🔍 Check status with: ps aux | grep uvicorn"
    echo "📊 View logs with: tail -f /tmp/uvicorn.log"
else
    echo "❌ Failed to start server. Check logs:"
    tail -20 /tmp/uvicorn.log
    exit 1
fi


