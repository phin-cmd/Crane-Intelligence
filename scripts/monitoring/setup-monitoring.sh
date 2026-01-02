#!/bin/bash

# Monitoring Setup Script
# Sets up automated health checks and monitoring

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HEALTH_CHECK_SCRIPT="$SCRIPT_DIR/health-check.sh"

echo "========================================="
echo "Monitoring Setup"
echo "========================================="
echo ""

# Make health check script executable
chmod +x "$HEALTH_CHECK_SCRIPT"

# Setup cron jobs for health checks
ENVIRONMENTS=("dev" "uat" "production")

for env in "${ENVIRONMENTS[@]}"; do
    CRON_SCHEDULE="*/5 * * * *"  # Every 5 minutes
    CRON_COMMAND="$HEALTH_CHECK_SCRIPT $env >> $PROJECT_ROOT/logs/health-check-$env.log 2>&1"
    CRON_ENTRY="$CRON_SCHEDULE $CRON_COMMAND"
    
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "health-check.sh $env"; then
        echo "⚠️  Health check cron job for $env already exists"
    else
        (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
        echo "✅ Added health check cron job for $env (every 5 minutes)"
    fi
done

echo ""
echo "========================================="
echo "Monitoring setup complete!"
echo "========================================="
echo ""
echo "Health checks will run every 5 minutes for:"
echo "  - Dev environment"
echo "  - UAT environment"
echo "  - Production environment"
echo ""
echo "Logs location: $PROJECT_ROOT/logs/"
echo ""
echo "To view cron jobs: crontab -l"
echo "To test health check: $HEALTH_CHECK_SCRIPT <environment>"

