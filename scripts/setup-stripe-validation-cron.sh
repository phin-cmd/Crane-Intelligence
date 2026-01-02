#!/bin/bash
# Setup daily cron job for Stripe configuration validation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRANE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$CRANE_DIR"

echo "=========================================="
echo "Setting up Stripe Validation Cron Job"
echo "=========================================="
echo ""

# Create log directory if it doesn't exist
LOG_DIR="/var/log/crane"
mkdir -p "$LOG_DIR"

# Cron job command - runs daily at 2 AM
CRON_JOB="0 2 * * * $CRANE_DIR/scripts/validate-stripe-config.sh >> $LOG_DIR/stripe-validation.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "validate-stripe-config.sh"; then
    echo "✓ Stripe validation cron job already exists"
    echo ""
    echo "Current cron jobs:"
    crontab -l | grep "validate-stripe-config"
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✓ Daily Stripe validation cron job configured"
    echo "  Runs daily at 2:00 AM"
    echo "  Logs to: $LOG_DIR/stripe-validation.log"
fi

echo ""
echo "To view cron jobs:"
echo "  crontab -l"
echo ""
echo "To view validation logs:"
echo "  tail -f $LOG_DIR/stripe-validation.log"
echo ""

