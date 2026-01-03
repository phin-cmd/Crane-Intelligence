#!/bin/bash

# Security Monitoring Script
# Monitors security logs and alerts on critical events

# Don't exit on error for monitoring script - we want to continue even if some checks fail
set +e

LOG_FILE="${1:-/var/log/app/security.log}"
APP_LOG="${2:-/var/log/app/app.log}"
ALERT_EMAIL="${3:-security@craneintelligence.tech}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "Security Event Monitor"
echo "=========================================="
echo "Monitoring: $LOG_FILE"
echo ""

# Function to send alert
send_alert() {
    local severity=$1
    local message=$2
    
    if [ "$severity" == "critical" ] || [ "$severity" == "high" ]; then
        echo -e "${RED}ALERT [$severity]: $message${NC}"
        # TODO: Send email/Slack notification
        # mail -s "Security Alert: $message" "$ALERT_EMAIL" <<< "$message"
    else
        echo -e "${YELLOW}WARNING [$severity]: $message${NC}"
    fi
}

# Monitor for security events
monitor_security_events() {
    echo "Monitoring security events..."
    echo ""
    
    # Check if log file exists
    if [ ! -f "$APP_LOG" ]; then
        echo "⚠️  Log file not found: $APP_LOG"
        echo "   Using default log locations..."
        # Try common log locations
        APP_LOG="/var/log/app/app.log"
        if [ ! -f "$APP_LOG" ]; then
            APP_LOG="/var/log/nginx/access.log"
        fi
        if [ ! -f "$APP_LOG" ]; then
            echo "   No log file found. Monitoring disabled."
            return 0
        fi
    fi
    
    # Check for payment manipulation attempts
    PAYMENT_ATTEMPTS=$(grep -i "payment.*manipulation" "$APP_LOG" 2>/dev/null | wc -l | tr -d ' ')
    if [ "${PAYMENT_ATTEMPTS:-0}" -gt 0 ]; then
        send_alert "high" "Payment manipulation attempts detected: $PAYMENT_ATTEMPTS"
    fi
    
    # Check for SQL injection attempts
    SQL_INJECTION=$(grep -i "sql.*injection" "$APP_LOG" 2>/dev/null | wc -l | tr -d ' ')
    if [ "${SQL_INJECTION:-0}" -gt 0 ]; then
        send_alert "critical" "SQL injection attempts detected: $SQL_INJECTION"
    fi
    
    # Check for bot detection
    BOT_DETECTIONS=$(grep -i "bot.*detected" "$APP_LOG" 2>/dev/null | wc -l | tr -d ' ')
    if [ "${BOT_DETECTIONS:-0}" -gt 100 ]; then
        send_alert "medium" "High number of bot detections: $BOT_DETECTIONS"
    fi
    
    # Check for rate limit violations
    RATE_LIMITS=$(grep -i "rate.*limit" "$APP_LOG" 2>/dev/null | wc -l | tr -d ' ')
    if [ "${RATE_LIMITS:-0}" -gt 50 ]; then
        send_alert "medium" "Rate limit violations: $RATE_LIMITS"
    fi
    
    # Check for authentication failures
    AUTH_FAILURES=$(grep -i "authentication.*failed\|invalid.*token\|unauthorized" "$APP_LOG" 2>/dev/null | wc -l | tr -d ' ')
    if [ "${AUTH_FAILURES:-0}" -gt 100 ]; then
        send_alert "high" "High number of authentication failures: $AUTH_FAILURES"
    fi
}

# Show recent security events
show_recent_events() {
    echo "Recent Security Events (last 50):"
    echo "----------------------------------"
    
    if [ -f "$APP_LOG" ]; then
        grep -i "security\|injection\|manipulation\|bot.*detected" "$APP_LOG" 2>/dev/null | tail -50
    else
        echo "Log file not found: $APP_LOG"
    fi
}

# Show security statistics
show_statistics() {
    echo ""
    echo "Security Statistics (last 24 hours):"
    echo "------------------------------------"
    
    if [ -f "$APP_LOG" ]; then
        echo "Payment Manipulation Attempts: $(grep -i "payment.*manipulation" "$APP_LOG" 2>/dev/null | wc -l | tr -d ' ')"
        echo "SQL Injection Attempts: $(grep -i "sql.*injection" "$APP_LOG" 2>/dev/null | wc -l | tr -d ' ')"
        echo "Bot Detections: $(grep -i "bot.*detected" "$APP_LOG" 2>/dev/null | wc -l | tr -d ' ')"
        echo "Rate Limit Violations: $(grep -i "rate.*limit" "$APP_LOG" 2>/dev/null | wc -l | tr -d ' ')"
        echo "Authentication Failures: $(grep -i "authentication.*failed\|invalid.*token" "$APP_LOG" 2>/dev/null | wc -l | tr -d ' ')"
    else
        echo "Log file not found: $APP_LOG"
        echo "Trying to find log files..."
        if [ -f "/var/log/app/app.log" ]; then
            echo "Found: /var/log/app/app.log"
            APP_LOG="/var/log/app/app.log"
        elif [ -f "/var/log/nginx/access.log" ]; then
            echo "Found: /var/log/nginx/access.log"
            APP_LOG="/var/log/nginx/access.log"
        else
            echo "No log files found. Please specify log file path."
        fi
    fi
}

# Main menu
case "${1:-monitor}" in
    monitor)
        monitor_security_events
        ;;
    recent)
        show_recent_events
        ;;
    stats)
        show_statistics
        ;;
    watch)
        if [ ! -f "$APP_LOG" ]; then
            echo "Log file not found: $APP_LOG"
            echo "Trying default locations..."
            if [ -f "/var/log/app/app.log" ]; then
                APP_LOG="/var/log/app/app.log"
            elif [ -f "/var/log/nginx/access.log" ]; then
                APP_LOG="/var/log/nginx/access.log"
            else
                echo "No log file found. Please specify log file path."
                exit 1
            fi
        fi
        echo "Watching security logs: $APP_LOG"
        echo "Press Ctrl+C to stop..."
        tail -f "$APP_LOG" 2>/dev/null | grep --line-buffered -i "security\|injection\|manipulation\|bot.*detected" || {
            echo "No matching log entries found or log file not accessible"
            echo "Trying to read from Docker logs..."
            if command -v docker >/dev/null 2>&1; then
                docker compose logs -f backend 2>/dev/null | grep --line-buffered -i "security\|injection\|manipulation\|bot.*detected" || \
                docker-compose logs -f backend 2>/dev/null | grep --line-buffered -i "security\|injection\|manipulation\|bot.*detected" || \
                echo "Could not access logs"
            fi
        }
        ;;
    *)
        echo "Usage: $0 [monitor|recent|stats|watch] [log_file] [app_log] [alert_email]"
        echo ""
        echo "Commands:"
        echo "  monitor  - Check for security events and send alerts"
        echo "  recent   - Show recent security events"
        echo "  stats    - Show security statistics"
        echo "  watch    - Watch security logs in real-time"
        exit 1
        ;;
esac

