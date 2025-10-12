#!/bin/bash

# Monitoring Setup Script for Crane Intelligence Platform
# This script sets up basic monitoring and logging

# Configuration
LOG_DIR="/root/Crane-Intelligence/logs"
MONITORING_DIR="/root/Crane-Intelligence/monitoring"
DATE=$(date +%Y%m%d_%H%M%S)

# Create directories
mkdir -p "$LOG_DIR"
mkdir -p "$MONITORING_DIR"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_DIR}/monitoring.log"
}

# Function to check service health
check_service_health() {
    local service_name="$1"
    local port="$2"
    local url="$3"
    
    log_message "Checking $service_name health..."
    
    if [ -n "$port" ]; then
        if nc -z localhost "$port" 2>/dev/null; then
            log_message "✅ $service_name (port $port) is running"
            return 0
        else
            log_message "❌ $service_name (port $port) is not responding"
            return 1
        fi
    fi
    
    if [ -n "$url" ]; then
        if curl -s -f "$url" > /dev/null 2>&1; then
            log_message "✅ $service_name ($url) is responding"
            return 0
        else
            log_message "❌ $service_name ($url) is not responding"
            return 1
        fi
    fi
}

# Function to check disk usage
check_disk_usage() {
    log_message "Checking disk usage..."
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$DISK_USAGE" -lt 80 ]; then
        log_message "✅ Disk usage: ${DISK_USAGE}% (Healthy)"
    elif [ "$DISK_USAGE" -lt 90 ]; then
        log_message "⚠️  Disk usage: ${DISK_USAGE}% (Warning)"
    else
        log_message "🚨 Disk usage: ${DISK_USAGE}% (Critical)"
    fi
}

# Function to check memory usage
check_memory_usage() {
    log_message "Checking memory usage..."
    MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    
    if [ "$MEMORY_USAGE" -lt 80 ]; then
        log_message "✅ Memory usage: ${MEMORY_USAGE}% (Healthy)"
    elif [ "$MEMORY_USAGE" -lt 90 ]; then
        log_message "⚠️  Memory usage: ${MEMORY_USAGE}% (Warning)"
    else
        log_message "🚨 Memory usage: ${MEMORY_USAGE}% (Critical)"
    fi
}

# Function to check Docker containers
check_docker_containers() {
    log_message "Checking Docker containers..."
    
    cd /root/Crane-Intelligence
    
    # Check if containers are running
    if docker-compose ps | grep -q "Up"; then
        log_message "✅ Docker containers are running"
        
        # Check individual services
        check_service_health "Frontend" "3001"
        check_service_health "Backend" "8004"
        check_service_health "Database" "5434"
        check_service_health "Redis" "6380"
        check_service_health "Adminer" "8082"
    else
        log_message "❌ Docker containers are not running"
        return 1
    fi
}

# Function to check API endpoints
check_api_endpoints() {
    log_message "Checking API endpoints..."
    
    # Health check
    if curl -s http://localhost:8004/api/v1/health | grep -q "healthy"; then
        log_message "✅ API health check passed"
    else
        log_message "❌ API health check failed"
    fi
    
    # Crane listings endpoint
    if curl -s http://localhost:8004/api/v1/enhanced-data/crane-listings?limit=1 > /dev/null 2>&1; then
        log_message "✅ Crane listings endpoint responding"
    else
        log_message "❌ Crane listings endpoint not responding"
    fi
    
    # Market analysis endpoint
    if curl -s http://localhost:8004/api/v1/analytics/market-analysis > /dev/null 2>&1; then
        log_message "✅ Market analysis endpoint responding"
    else
        log_message "❌ Market analysis endpoint not responding"
    fi
}

# Function to check database connectivity
check_database_connectivity() {
    log_message "Checking database connectivity..."
    
    cd /root/Crane-Intelligence
    
    if docker-compose exec -T db psql -U crane_user -d crane_db -c "SELECT 1;" > /dev/null 2>&1; then
        log_message "✅ Database connection successful"
        
        # Check table counts
        USER_COUNT=$(docker-compose exec -T db psql -U crane_user -d crane_db -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | tr -d ' ')
        LISTING_COUNT=$(docker-compose exec -T db psql -U crane_user -d crane_db -t -c "SELECT COUNT(*) FROM crane_listings;" 2>/dev/null | tr -d ' ')
        CONSULTATION_COUNT=$(docker-compose exec -T db psql -U crane_user -d crane_db -t -c "SELECT COUNT(*) FROM consultations;" 2>/dev/null | tr -d ' ')
        
        log_message "📊 Database statistics:"
        log_message "   - Users: $USER_COUNT"
        log_message "   - Crane Listings: $LISTING_COUNT"
        log_message "   - Consultations: $CONSULTATION_COUNT"
    else
        log_message "❌ Database connection failed"
        return 1
    fi
}

# Function to generate monitoring report
generate_report() {
    local report_file="${MONITORING_DIR}/health_report_${DATE}.txt"
    
    log_message "Generating monitoring report: $report_file"
    
    {
        echo "=== Crane Intelligence Platform Health Report ==="
        echo "Generated: $(date)"
        echo ""
        echo "=== System Resources ==="
        echo "Disk Usage:"
        df -h | grep -E "(Filesystem|/dev/)"
        echo ""
        echo "Memory Usage:"
        free -h
        echo ""
        echo "=== Docker Services ==="
        docker-compose ps
        echo ""
        echo "=== API Endpoints ==="
        echo "Health Check:"
        curl -s http://localhost:8004/api/v1/health || echo "Failed"
        echo ""
        echo "=== Database Status ==="
        docker-compose exec -T db psql -U crane_user -d crane_db -c "SELECT version();" 2>/dev/null || echo "Database connection failed"
        echo ""
        echo "=== Recent Logs ==="
        tail -20 "${LOG_DIR}/monitoring.log" 2>/dev/null || echo "No logs available"
    } > "$report_file"
    
    log_message "Monitoring report generated: $report_file"
}

# Main monitoring function
run_monitoring() {
    log_message "=== Starting Crane Intelligence Platform Monitoring ==="
    
    # System checks
    check_disk_usage
    check_memory_usage
    
    # Service checks
    check_docker_containers
    check_api_endpoints
    check_database_connectivity
    
    # Generate report
    generate_report
    
    log_message "=== Monitoring Check Completed ==="
}

# Function to setup cron job for automated monitoring
setup_cron_monitoring() {
    log_message "Setting up automated monitoring..."
    
    # Create monitoring script
    cat > "${MONITORING_DIR}/monitor.sh" << 'EOF'
#!/bin/bash
cd /root/Crane-Intelligence
./monitoring_setup.sh
EOF
    
    chmod +x "${MONITORING_DIR}/monitor.sh"
    
    # Add to crontab (run every 5 minutes)
    (crontab -l 2>/dev/null; echo "*/5 * * * * ${MONITORING_DIR}/monitor.sh") | crontab -
    
    log_message "✅ Automated monitoring setup completed (runs every 5 minutes)"
}

# Main execution
main() {
    case "${1:-monitor}" in
        "monitor")
            run_monitoring
            ;;
        "setup")
            setup_cron_monitoring
            ;;
        "report")
            generate_report
            ;;
        *)
            echo "Usage: $0 {monitor|setup|report}"
            echo "  monitor - Run health checks"
            echo "  setup   - Setup automated monitoring"
            echo "  report  - Generate health report"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
