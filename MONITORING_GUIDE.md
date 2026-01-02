# Monitoring and Health Checks Guide

This guide explains the monitoring and health check system for the Crane Intelligence platform.

## Overview

The monitoring system provides:
- Health check endpoints
- Automated health monitoring
- System metrics collection
- Alerting capabilities

## Health Check Endpoints

### Basic Health Check

```bash
GET /api/v1/health
```

Returns simple OK status for load balancers.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-12-27T12:00:00Z",
  "service": "crane-intelligence-api"
}
```

### Detailed Health Check

```bash
GET /api/v1/health/detailed
```

Returns comprehensive health status for all system components.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-27T12:00:00Z",
  "service": "crane-intelligence-api",
  "version": "1.0.0",
  "environment": "production",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "system": {
      "status": "healthy",
      "cpu_percent": 45.2,
      "memory_percent": 62.1,
      "disk_percent": 38.5,
      "message": "System resources within acceptable limits"
    },
    "api": {
      "status": "healthy",
      "message": "API endpoints accessible"
    }
  }
}
```

### Database Health Check

```bash
GET /api/v1/health/database
```

Returns database-specific health information.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-27T12:00:00Z",
  "database": {
    "connected": true,
    "pool_size": 10,
    "size": "2.5 GB"
  }
}
```

### Readiness Check

```bash
GET /api/v1/health/readiness
```

Indicates if service is ready to accept traffic (used by Kubernetes, Docker, etc.).

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2024-12-27T12:00:00Z"
}
```

### Liveness Check

```bash
GET /api/v1/health/liveness
```

Indicates if service is alive (used by orchestrators for restart decisions).

**Response:**
```json
{
  "status": "alive",
  "timestamp": "2024-12-27T12:00:00Z"
}
```

### Metrics Endpoint

```bash
GET /api/v1/health/metrics
```

Returns system metrics for monitoring dashboards.

**Response:**
```json
{
  "timestamp": "2024-12-27T12:00:00Z",
  "system": {
    "cpu_percent": 45.2,
    "memory_percent": 62.1,
    "memory_available_mb": 4096,
    "disk_percent": 38.5,
    "disk_free_gb": 120.5
  },
  "database": {
    "pool_size": 10,
    "checked_in": 8,
    "checked_out": 2,
    "overflow": 0,
    "invalid": 0,
    "size": "2.5 GB"
  },
  "application": {
    "environment": "production",
    "version": "1.0.0"
  }
}
```

## Automated Monitoring

### Setup Automated Health Checks

```bash
./scripts/monitoring/setup-monitoring.sh
```

This sets up cron jobs to check health every 5 minutes for all environments.

### Manual Health Check

```bash
# Check dev environment
./scripts/monitoring/health-check.sh dev

# Check UAT environment
./scripts/monitoring/health-check.sh uat

# Check production environment
./scripts/monitoring/health-check.sh production
```

### View Health Check Logs

```bash
# View recent logs
tail -f logs/health-check.log

# View logs for specific environment
tail -f logs/health-check-dev.log
tail -f logs/health-check-uat.log
tail -f logs/health-check-production.log
```

## Health Status Values

- **healthy**: All systems operational
- **degraded**: Some systems have issues but service is functional
- **unhealthy**: Critical systems are down
- **unknown**: Unable to determine status

## Alerting

### Email Alerts

Set `ALERT_EMAIL` environment variable:

```bash
export ALERT_EMAIL="admin@craneintelligence.tech"
./scripts/monitoring/health-check.sh production
```

### Custom Alerting

You can integrate with:
- PagerDuty
- Slack
- Discord
- Custom webhooks

Modify `health-check.sh` to add custom alerting logic.

## Monitoring Best Practices

### 1. Regular Health Checks

- Run health checks every 5 minutes (default)
- Increase frequency for critical systems
- Check all environments

### 2. Alert Thresholds

- **Critical**: Service completely down
- **Warning**: Service degraded but functional
- **Info**: Normal operation

### 3. Metrics Collection

- Collect metrics every minute
- Store metrics for historical analysis
- Set up dashboards (Grafana, etc.)

### 4. Logging

- Log all health check results
- Retain logs for at least 30 days
- Monitor log file sizes

## Integration with Load Balancers

### Nginx Health Check

```nginx
location /health {
    proxy_pass http://backend:8003/api/v1/health;
    access_log off;
}
```

### Docker Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8003/api/v1/health || exit 1
```

### Kubernetes Liveness/Readiness

```yaml
livenessProbe:
  httpGet:
    path: /api/v1/health/liveness
    port: 8003
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /api/v1/health/readiness
    port: 8003
  initialDelaySeconds: 10
  periodSeconds: 5
```

## Troubleshooting

### Health Check Fails

1. Check if service is running
2. Check database connection
3. Check system resources
4. Review application logs

### High CPU/Memory Usage

1. Check detailed health endpoint
2. Review system metrics
3. Check for memory leaks
4. Scale resources if needed

### Database Connection Issues

1. Check database container status
2. Verify connection string
3. Check connection pool settings
4. Review database logs

## CI/CD Integration

Health checks are automatically run:
- After deployment to dev
- After deployment to UAT
- After deployment to production
- In GitHub Actions workflows

See `.github/workflows/*.yml` for details.

