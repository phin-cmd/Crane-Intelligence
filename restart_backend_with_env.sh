#!/bin/bash
# Restart backend with BREVO_API_KEY and Stripe environment variables
# This ensures verification emails and Stripe integration work correctly

BREVO_API_KEY="${BREVO_API_KEY:-your-brevo-api-key-here}"
STRIPE_PUBLISHABLE_KEY="${STRIPE_PUBLISHABLE_KEY:-your-stripe-publishable-key-here}"
STRIPE_SECRET_KEY="${STRIPE_SECRET_KEY:-your-stripe-secret-key-here}"

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
