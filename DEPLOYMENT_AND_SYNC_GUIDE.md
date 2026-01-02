# Deployment and Database Sync Guide

## Overview

This guide explains how to deploy code and sync database from Production to UAT and DEV environments.

## Quick Start

### Complete Deployment and Sync (Recommended)

This script does everything: syncs database AND deploys code to both UAT and DEV:

```bash
cd /root/crane
./scripts/deployment/sync-prod-to-all-environments.sh
```

**What it does:**
1. ✅ Backs up UAT and DEV databases
2. ✅ Dumps production database
3. ✅ Syncs production database to UAT
4. ✅ Syncs production database to DEV
5. ✅ Deploys production code to UAT
6. ✅ Deploys production code to DEV
7. ✅ Restarts all backend services

## Step-by-Step Process

### Option 1: Complete Sync (Database + Code)

```bash
cd /root/crane
./scripts/deployment/sync-prod-to-all-environments.sh
```

This is the **recommended** approach as it ensures both code and database are in sync.

### Option 2: Database Sync Only

If you only need to sync the database:

#### Sync Production → DEV

```bash
cd /root/crane
./scripts/database/sync-prod-to-dev.sh
```

#### Sync Production → UAT

Currently, there's no UAT-specific sync script. You can:
1. Use the complete sync script above, or
2. Manually modify the DEV sync script for UAT

#### Sync Schema Only (No Data)

If you only want to sync the database structure:

```bash
cd /root/crane
./scripts/database/sync-schema-only-prod-to-dev.sh
```

### Option 3: Code Deployment Only

If you only need to deploy code (without database sync):

#### Deploy to DEV

```bash
cd /root/crane
./scripts/deployment/deploy-to-dev.sh
```

#### Deploy to UAT

```bash
cd /root/crane
./scripts/deployment/deploy-to-uat.sh
```

## What Gets Synced

### Database Sync Includes:
- ✅ All tables and data
- ✅ Database schema
- ✅ Sequences (updated to prevent ID conflicts)
- ✅ Indexes and constraints

### Code Deployment Includes:
- ✅ Backend application code
- ✅ Environment configuration
- ✅ Docker images rebuilt
- ✅ Services restarted

## Safety Features

### Automatic Backups

Before any sync operation:
- ✅ Current database is backed up
- ✅ Backups saved to `/root/crane/backups/`
- ✅ Backup files include timestamp
- ✅ Can be restored if needed

### Safety Checks

The scripts include:
- ✅ Verification that you're not on production server
- ✅ Confirmation prompt before destructive operations
- ✅ Container status checks
- ✅ Error handling and rollback instructions

## Restore from Backup

If something goes wrong, you can restore from backup:

```bash
# Find your backup file
ls -lh /root/crane/backups/

# Restore DEV database
gunzip -c /root/crane/backups/dev_db_before_sync_YYYYMMDD_HHMMSS.sql.gz | \
  docker compose -f docker-compose.dev.yml -p crane-dev exec -T db \
    psql -U crane_dev_user -d crane_intelligence_dev

# Restore UAT database
gunzip -c /root/crane/backups/uat_db_before_sync_YYYYMMDD_HHMMSS.sql.gz | \
  docker compose -f docker-compose.uat.yml -p crane-uat exec -T db \
    psql -U crane_uat_user -d crane_intelligence_uat
```

## Verification After Sync

### 1. Check Backend Services

```bash
docker ps | grep backend
```

Should show:
- `crane-dev-backend-1` - Up
- `crane-uat-backend-1` - Up
- `crane-backend-1` - Up (production)

### 2. Test API Endpoints

```bash
# DEV
curl http://localhost:8104/api/v1/config/public | jq

# UAT
curl http://localhost:8204/api/v1/config/public | jq
```

### 3. Test Payment Flow

```bash
# DEV
./scripts/test-complete-payment-flow.sh dev

# UAT
./scripts/test-complete-payment-flow.sh uat
```

### 4. Check Database

```bash
# DEV - Check table count
docker compose -f docker-compose.dev.yml -p crane-dev exec db \
  psql -U crane_dev_user -d crane_intelligence_dev -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"

# UAT - Check table count
docker compose -f docker-compose.uat.yml -p crane-uat exec db \
  psql -U crane_uat_user -d crane_intelligence_uat -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
```

## Important Notes

### ⚠️ Warnings

1. **Data Loss**: Syncing will OVERWRITE UAT and DEV databases with production data
2. **Environment-Specific Config**: After sync, verify environment-specific settings:
   - Stripe keys (should remain test keys for dev/uat)
   - Webhook secrets (should remain environment-specific)
   - Database URLs (should remain environment-specific)
   - DO Spaces buckets (should remain environment-specific)

3. **User Data**: Production user data will be copied to UAT/DEV
   - Consider if this is desired
   - May need to clean up test data after sync

### ✅ Best Practices

1. **Always Backup First**: Scripts do this automatically, but verify backups exist
2. **Test After Sync**: Run verification scripts to ensure everything works
3. **Monitor Logs**: Check backend logs after deployment
4. **Verify Environment Config**: Ensure environment-specific settings are correct

## Troubleshooting

### Database Sync Fails

1. **Check Container Status**
   ```bash
   docker ps | grep db
   ```

2. **Check Disk Space**
   ```bash
   df -h
   ```

3. **Check Logs**
   ```bash
   docker logs <container-name>
   ```

### Code Deployment Fails

1. **Check Docker Compose**
   ```bash
   docker compose version
   ```

2. **Check Build Logs**
   ```bash
   docker compose -f docker-compose.dev.yml -p crane-dev build backend
   ```

3. **Check Container Logs**
   ```bash
   docker logs crane-dev-backend-1
   ```

### Services Not Starting

1. **Check Environment Files**
   ```bash
   ls -lh config/*.env
   ```

2. **Check Port Conflicts**
   ```bash
   netstat -tulpn | grep -E "8104|8204|8004"
   ```

3. **Restart Services**
   ```bash
   ./scripts/restart-backends-with-env-config.sh
   ```

## Quick Reference

| Task | Command |
|------|---------|
| Complete sync (DB + Code) | `./scripts/deployment/sync-prod-to-all-environments.sh` |
| Sync DB only (DEV) | `./scripts/database/sync-prod-to-dev.sh` |
| Sync schema only (DEV) | `./scripts/database/sync-schema-only-prod-to-dev.sh` |
| Deploy code (DEV) | `./scripts/deployment/deploy-to-dev.sh` |
| Deploy code (UAT) | `./scripts/deployment/deploy-to-uat.sh` |
| Verify deployment | `./scripts/test-complete-payment-flow.sh dev` |
| Check backups | `ls -lh backups/` |

## Summary

The **recommended approach** is to use the complete sync script:

```bash
cd /root/crane
./scripts/deployment/sync-prod-to-all-environments.sh
```

This ensures both code and database are synchronized from production to both UAT and DEV environments, with automatic backups and safety checks.

