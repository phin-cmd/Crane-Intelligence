# Monitoring and Backup Setup

## Automated Backups

### Setup Cron Job for Daily Backups

Add to crontab (`crontab -e`):

```bash
# Daily database backups at 2 AM
0 2 * * * /root/crane/backup-databases.sh >> /var/log/crane-backups.log 2>&1
```

### Manual Backup

Run backup script manually:
```bash
/root/crane/backup-databases.sh
```

Backups are stored in `/root/crane/backups/` and automatically cleaned up after 7 days.

### Restore from Backup

```bash
# List available backups
ls -lh /root/crane/backups/

# Restore a backup
/root/crane/restore-database.sh <environment> <backup_file>
# Example:
/root/crane/restore-database.sh prod /root/crane/backups/prod_db_20241218_120000.sql.gz
```

## Monitoring Recommendations

### 1. Application Monitoring

Set up error tracking:
- **Sentry** (recommended): https://sentry.io
  - Add Sentry SDK to your backend
  - Configure different projects for dev/uat/prod
  - Set up alerts for production errors

### 2. Uptime Monitoring

Use external monitoring services:
- **UptimeRobot**: https://uptimerobot.com (free tier available)
- **Pingdom**: https://www.pingdom.com
- **StatusCake**: https://www.statuscake.com

Monitor these URLs:
- https://craneintelligence.tech/ (Production)
- https://uat.craneintelligence.tech/ (UAT)
- https://dev.craneintelligence.tech/ (Dev - optional)

### 3. Log Aggregation

Consider setting up:
- **Loki + Grafana**: For log aggregation and visualization
- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Cloud logging**: AWS CloudWatch, Google Cloud Logging, etc.

### 4. Container Health Checks

Add health checks to docker-compose files:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 5. Disk Space Monitoring

Set up alerts for disk usage:
```bash
# Add to crontab
0 * * * * df -h | awk '$5 > 80 {print "WARNING: Disk usage > 80%"}'
```

### 6. Database Monitoring

Monitor database:
- Connection pool usage
- Query performance
- Disk space usage
- Replication lag (if applicable)

## Alerting

### Critical Alerts (Production Only)

- Application down (HTTP 5xx errors)
- Database connection failures
- Disk space > 90%
- Memory usage > 90%
- SSL certificate expiring soon

### Warning Alerts

- High error rate (> 1% of requests)
- Slow response times (> 2 seconds)
- Disk space > 80%
- Backup failures

## Log Retention

- **Application logs**: 30 days
- **Access logs**: 90 days
- **Error logs**: 1 year
- **Database backups**: 7 days (configurable in backup script)

## Health Check Endpoints

Ensure your application exposes health check endpoints:

- `/health` - Basic health check
- `/health/db` - Database connectivity check
- `/health/redis` - Redis connectivity check

These can be used by monitoring tools and load balancers.

