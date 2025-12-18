#!/bin/bash
# Restart backend with BREVO_API_KEY and Stripe environment variables
# This ensures verification emails and Stripe integration work correctly

BREVO_API_KEY="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"
STRIPE_PUBLISHABLE_KEY="pk_test_51SJKv7BME5ZRi6spdiFi7Vjl0OYR0JxIppswByoC6v4zpBDcGa8hZxsiiAzXgVLRK3tFJ8UlZDvImAfYv5o0accj00IZw9Rl4R"
STRIPE_SECRET_KEY="sk_test_51SJKv7BME5ZRi6spDsiedaGw4VWwCxgokO4ahK0ad6ORGqWdIao6t8gW9MXy3TGuZSnOjdXx0kwOPg51GvFd3Zri000q3mJFhQ"

# Kill existing uvicorn process
echo "Stopping existing server..."
pkill -f "uvicorn.*8003"
sleep 2

# Start new process with environment variables
cd /root/crane/backend
echo "Starting server with BREVO_API_KEY and Stripe keys..."
export BREVO_API_KEY="$BREVO_API_KEY"
export STRIPE_PUBLISHABLE_KEY="$STRIPE_PUBLISHABLE_KEY"
export STRIPE_SECRET_KEY="$STRIPE_SECRET_KEY"
nohup /usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8003 > /tmp/uvicorn.log 2>&1 &

sleep 3
echo "✅ Backend restarted with BREVO_API_KEY and Stripe keys"
ps aux | grep uvicorn | grep -v grep | head -1

# Verify the API keys are set
echo ""
echo "Verifying environment variables in process..."
PID=$(pgrep -f "uvicorn.*8003" | head -1)
if [ -n "$PID" ]; then
    if cat /proc/$PID/environ 2>/dev/null | tr '\0' '\n' | grep -q "BREVO_API_KEY"; then
        echo "✅ BREVO_API_KEY is set in server process"
    else
        echo "⚠️  BREVO_API_KEY not found in server process environment"
    fi
    if cat /proc/$PID/environ 2>/dev/null | tr '\0' '\n' | grep -q "STRIPE_PUBLISHABLE_KEY"; then
        echo "✅ STRIPE_PUBLISHABLE_KEY is set in server process"
    else
        echo "⚠️  STRIPE_PUBLISHABLE_KEY not found in server process environment"
    fi
    if cat /proc/$PID/environ 2>/dev/null | tr '\0' '\n' | grep -q "STRIPE_SECRET_KEY"; then
        echo "✅ STRIPE_SECRET_KEY is set in server process"
    else
        echo "⚠️  STRIPE_SECRET_KEY not found in server process environment"
    fi
fi
