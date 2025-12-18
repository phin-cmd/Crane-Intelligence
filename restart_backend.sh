#!/bin/bash
# Script to restart the FastAPI/uvicorn backend server

echo "🔄 Restarting FastAPI backend server..."

# Find and kill the existing uvicorn process
echo "📋 Finding existing uvicorn process..."
PID=$(pgrep -f "uvicorn app.main:app")
if [ -n "$PID" ]; then
    echo "🛑 Stopping process $PID..."
    kill $PID
    sleep 2
    # Force kill if still running
    if kill -0 $PID 2>/dev/null; then
        echo "⚠️  Process still running, force killing..."
        kill -9 $PID
        sleep 1
    fi
    echo "✅ Process stopped"
else
    echo "ℹ️  No existing process found"
fi

# Wait a moment
sleep 1

# Navigate to backend directory
cd /root/crane/backend || exit 1

# Start the server in the background
echo "🚀 Starting uvicorn server..."

# Try to find the correct Python
if [ -f "/usr/local/bin/python3.11" ]; then
    PYTHON_CMD="/usr/local/bin/python3.11"
elif [ -f "/usr/bin/python3" ]; then
    PYTHON_CMD="/usr/bin/python3"
else
    PYTHON_CMD=$(which python3)
fi

echo "📝 Using Python: $PYTHON_CMD"

# Try uvicorn as module (most reliable method)
if $PYTHON_CMD -m uvicorn --version >/dev/null 2>&1; then
    echo "✅ Using: $PYTHON_CMD -m uvicorn"
    cd /root/crane/backend
    nohup $PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8003 > /tmp/uvicorn.log 2>&1 &
elif command -v uvicorn >/dev/null 2>&1; then
    echo "✅ Using: uvicorn command"
    cd /root/crane/backend
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8003 > /tmp/uvicorn.log 2>&1 &
else
    echo "❌ uvicorn not found. Please install dependencies first:"
    echo "   cd /root/crane/backend && $PYTHON_CMD -m pip install -r requirements.txt --break-system-packages"
    exit 1
fi

# Wait a moment for it to start
sleep 2

# Check if it's running
NEW_PID=$(pgrep -f "uvicorn app.main:app")
if [ -n "$NEW_PID" ]; then
    echo "✅ Server restarted successfully! PID: $NEW_PID"
    echo "📝 Logs are being written to: /tmp/uvicorn.log"
    echo "🔍 Check status with: ps aux | grep uvicorn"
else
    echo "❌ Failed to start server. Check logs: /tmp/uvicorn.log"
    exit 1
fi

