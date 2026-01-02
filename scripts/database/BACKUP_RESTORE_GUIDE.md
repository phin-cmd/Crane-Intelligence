# Database Backup and Restore Guide

This guide explains how to backup and restore databases for all environments.

## Overview

The backup system provides:
- Automated daily backups
- Manual backup capability
- Backup verification (checksums)
- Restore procedures
- Backup retention management

## Manual Backup

### Backup All Databases

```bash
./scripts/database/backup-databases.sh
```

This backs up:
- Dev database
- UAT database
- Production database

### Backup Specific Environment

The script automatically backs up all environments. To backup only one:

```bash
# For dev
docker compose -f docker-compose.dev.yml -p crane-dev exec -T db \
    pg_dump -U crane_dev_user crane_intelligence_dev | gzip > \
    backups/dev_db_$(date +%Y%m%d_%H%M%S).sql.gz
```

## Automated Backups

### Setup Automated Backups

```bash
# Setup daily backups at 2 AM (default)
./scripts/database/schedule-backups.sh

# Setup custom schedule (cron format)
./scripts/database/schedule-backups.sh "0 3 * * *"  # 3 AM daily
```

### Cron Schedule Examples

- `0 2 * * *` - Daily at 2 AM
- `0 */6 * * *` - Every 6 hours
- `0 2 * * 0` - Weekly on Sunday at 2 AM
- `0 2 1 * *` - Monthly on 1st at 2 AM

### View Scheduled Backups

```bash
crontab -l | grep backup
```

### Remove Scheduled Backups

```bash
crontab -e
# Delete the backup line
```

## Restore Database

### Restore from Backup

```bash
# List available backups
ls -lh backups/*.sql.gz

# Restore specific environment
./scripts/database/restore-database.sh <environment> <backup_file>

# Examples:
./scripts/database/restore-database.sh dev backups/dev_db_20241227_020000.sql.gz
./scripts/database/restore-database.sh uat backups/uat_db_20241227_020000.sql.gz
./scripts/database/restore-database.sh production backups/prod_db_20241227_020000.sql.gz
```

### Restore Process

1. **Safety Check**: Creates a backup before restore
2. **Verification**: Verifies backup checksum
3. **Connection Cleanup**: Drops existing connections
4. **Restore**: Restores database from backup
5. **Verification**: Confirms restore success

### Production Restore

Production restore requires explicit confirmation:

```bash
# You must type "RESTORE PRODUCTION" to proceed
./scripts/database/restore-database.sh production backups/prod_db_YYYYMMDD_HHMMSS.sql.gz
```

## Backup Management

### Backup Location

All backups are stored in: `/root/crane/backups/`

### Backup Naming

- Format: `<environment>_db_YYYYMMDD_HHMMSS.sql.gz`
- Examples:
  - `dev_db_20241227_020000.sql.gz`
  - `uat_db_20241227_020000.sql.gz`
  - `prod_db_20241227_020000.sql.gz`

### Backup Retention

- Default retention: 7 days
- Configured in: `backup-databases.sh`
- Old backups are automatically deleted

### Backup Verification

Each backup includes a checksum file:
- Format: `<backup_file>.sha256`
- Used to verify backup integrity before restore

### List Backups

```bash
# List all backups
ls -lh backups/*.sql.gz

# List backups by environment
ls -lh backups/dev_db_*.sql.gz
ls -lh backups/uat_db_*.sql.gz
ls -lh backups/prod_db_*.sql.gz

# List with details
ls -lht backups/*.sql.gz | head -10
```

## Backup Best Practices

### 1. Regular Backups

- **Production**: Daily at minimum
- **UAT**: Before major changes
- **Dev**: As needed

### 2. Before Major Changes

Always backup before:
- Database migrations
- Major deployments
- Schema changes
- Data migrations

### 3. Verify Backups

```bash
# Verify backup integrity
sha256sum -c backups/prod_db_20241227_020000.sql.gz.sha256
```

### 4. Test Restores

Periodically test restore procedures:
- Use dev environment
- Verify data integrity
- Document any issues

### 5. Offsite Backups

Consider copying backups to:
- Cloud storage (S3, DigitalOcean Spaces)
- Remote server
- Local backup drive

## Emergency Procedures

### Production Database Corruption

1. **Stop application**:
   ```bash
   docker compose stop backend
   ```

2. **Identify last good backup**:
   ```bash
   ls -lht backups/prod_db_*.sql.gz | head -5
   ```

3. **Restore from backup**:
   ```bash
   ./scripts/database/restore-database.sh production backups/prod_db_YYYYMMDD_HHMMSS.sql.gz
   ```

4. **Verify restore**:
   ```bash
   docker compose exec db psql -U crane_user -d crane_intelligence -c "SELECT COUNT(*) FROM users;"
   ```

5. **Restart application**:
   ```bash
   docker compose restart backend
   ```

### Partial Data Loss

1. Identify affected tables
2. Find backup before data loss
3. Extract specific tables from backup
4. Restore only affected tables

### Migration Rollback

If migration fails:

1. **Restore from pre-migration backup**:
   ```bash
   ./scripts/database/restore-database.sh production backups/prod_db_before_migration_YYYYMMDD_HHMMSS.sql.gz
   ```

2. **Or use migration rollback**:
   ```bash
   python backend/migrations/migration_manager.py rollback --name <migration_name> --env production
   ```

## Monitoring

### Backup Logs

Backup logs are written to: `backups/backup.log`

```bash
# View recent backup logs
tail -f backups/backup.log

# View backup history
grep "Backup complete" backups/backup.log
```

### Backup Status

Check backup status:

```bash
# Check last backup time
ls -lt backups/prod_db_*.sql.gz | head -1

# Check backup size
du -sh backups/

# Check backup count
ls -1 backups/*.sql.gz | wc -l
```

## Troubleshooting

### Backup Fails

1. Check database container is running
2. Check disk space: `df -h`
3. Check permissions: `ls -la backups/`
4. Check logs: `tail -f backups/backup.log`

### Restore Fails

1. Verify backup file exists and has content
2. Verify checksum: `sha256sum -c <backup>.sha256`
3. Check database container is running
4. Check disk space
5. Check database user permissions

### Backup Too Large

If backups are too large:
- Consider excluding large tables
- Use `pg_dump --exclude-table` option
- Compress more aggressively
- Archive old backups

## CI/CD Integration

Backups are automatically created during deployment:

- **Dev**: Before migrations (if any)
- **UAT**: Before migrations (required)
- **Production**: Before migrations (required, critical)

See `.github/workflows/*.yml` for details.

