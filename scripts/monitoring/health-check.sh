#!/bin/bash
set -e

# Health Check Script
# Monitors application health and sends alerts if issues detected

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_FILE="$PROJECT_ROOT/logs/health-check.log"
ALERT_EMAIL=${ALERT_EMAIL:-"admin@craneintelligence.tech"}

ENVIRONMENT=${1:-dev}

# Set base URL based on environment
if [ "$ENVIRONMENT" == "dev" ]; then
    BASE_URL="https://dev.craneintelligence.tech"
elif [ "$ENVIRONMENT" == "uat" ]; then
    BASE_URL="https://uat.craneintelligence.tech"
else
    BASE_URL="https://craneintelligence.tech"
fi

mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check health endpoint
check_health() {
    local endpoint="$1"
    local name="$2"
    
    log "Checking $name: $endpoint"
    
    response=$(curl -s -w "\n%{http_code}" "$endpoint" --max-time 10 || echo -e "\n000")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" == "200" ] || [ "$http_code" == "200" ]; then
        log "✅ $name is healthy (HTTP $http_code)"
        return 0
    else
        log "❌ $name is unhealthy (HTTP $http_code)"
        log "   Response: $body"
        return 1
    fi
}

# Send alert
send_alert() {
    local message="$1"
    log "ALERT: $message"
    
    # Send email alert (if configured)
    if [ -n "$ALERT_EMAIL" ] && command -v mail &> /dev/null; then
        echo "$message" | mail -s "Health Check Alert - $ENVIRONMENT" "$ALERT_EMAIL" || true
    fi
    
    # Log to file
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ALERT: $message" >> "$LOG_FILE"
}

log "========================================="
log "Health Check - $ENVIRONMENT"
log "========================================="
log ""

# Check basic health
if ! check_health "$BASE_URL/api/v1/health" "Basic Health"; then
    send_alert "Basic health check failed for $ENVIRONMENT"
    exit 1
fi

# Check detailed health
if ! check_health "$BASE_URL/api/v1/health/detailed" "Detailed Health"; then
    send_alert "Detailed health check failed for $ENVIRONMENT"
    exit 1
fi

# Check database health
if ! check_health "$BASE_URL/api/v1/health/database" "Database Health"; then
    send_alert "Database health check failed for $ENVIRONMENT"
    exit 1
fi

# Check readiness
if ! check_health "$BASE_URL/api/v1/health/readiness" "Readiness"; then
    send_alert "Readiness check failed for $ENVIRONMENT"
    exit 1
fi

# Check liveness
if ! check_health "$BASE_URL/api/v1/health/liveness" "Liveness"; then
    send_alert "Liveness check failed for $ENVIRONMENT"
    exit 1
fi

log ""
log "========================================="
log "✅ All health checks passed!"
log "========================================="

exit 0

