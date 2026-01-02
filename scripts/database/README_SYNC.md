# Database Sync Scripts

This directory contains scripts to sync database schema and data from production to dev environment.

## ⚠️ WARNING

These scripts will **OVERWRITE** the dev database. Always ensure:
- You have backups
- You're running in the correct environment
- Production and dev containers are running

## Available Scripts

### 1. `sync-prod-to-dev.sh`
Syncs **both schema and data** from production to dev.

**What it does:**
1. Backs up current dev database
2. Dumps production database (schema + data)
3. Drops and recreates dev database
4. Restores production data to dev
5. Updates sequences to prevent ID conflicts

**Usage:**
```bash
cd /root/crane
./scripts/database/sync-prod-to-dev.sh
```

**When to use:**
- When you need an exact copy of production in dev
- When testing with real production data
- When you need to debug issues that only occur with production data

### 2. `sync-schema-only-prod-to-dev.sh`
Syncs **only the schema (structure)** from production to dev, without data.

**What it does:**
1. Backs up current dev database
2. Dumps production schema only (no data)
3. Drops all tables in dev
4. Restores production schema to dev
5. Dev data is lost (tables are recreated empty)

**Usage:**
```bash
cd /root/crane
./scripts/database/sync-schema-only-prod-to-dev.sh
```

**When to use:**
- When you only need the table structure
- When production schema has been updated
- When you want to keep dev data separate but match structure

## Prerequisites

1. **Docker containers must be running:**
   ```bash
   # Production
   docker compose -f /root/crane/docker-compose.yml up -d db
   
   # Dev
   docker compose -f /root/crane/docker-compose.dev.yml -p crane-dev up -d db
   ```

2. **Backup directory exists:**
   ```bash
   mkdir -p /root/crane/backups
   ```

## Safety Features

Both scripts include:
- ✅ Safety checks to prevent running on production servers
- ✅ Automatic backup of dev database before sync
- ✅ Confirmation prompts before proceeding
- ✅ Container status checks
- ✅ Error handling with rollback instructions

## After Syncing

1. **Restart the dev backend:**
   ```bash
   docker compose -f /root/crane/docker-compose.dev.yml -p crane-dev restart backend
   ```

2. **Verify the sync:**
   - Check database connection
   - Verify tables exist
   - Test API endpoints

3. **If something went wrong, restore from backup:**
   ```bash
   # Find your backup file
   ls -lh /root/crane/backups/dev_db_before_sync_*.sql.gz
   
   # Restore it
   gunzip -c /root/crane/backups/dev_db_before_sync_YYYYMMDD_HHMMSS.sql.gz | \
     docker compose -f /root/crane/docker-compose.dev.yml -p crane-dev exec -T db \
       psql -U crane_dev_user -d crane_intelligence_dev
   ```

## Database Credentials

### Production
- Database: `crane_intelligence`
- User: `crane_user`
- Password: `crane_password`
- Port: `5434` (host) / `5432` (container)

### Dev
- Database: `crane_intelligence_dev`
- User: `crane_dev_user`
- Password: `crane_dev_password`
- Port: `5534` (host) / `5432` (container)

## Troubleshooting

### "Container is not running"
Start the required containers:
```bash
docker compose -f /root/crane/docker-compose.yml up -d db
docker compose -f /root/crane/docker-compose.dev.yml -p crane-dev up -d db
```

### "Permission denied"
Make scripts executable:
```bash
chmod +x /root/crane/scripts/database/*.sh
```

### "Connection refused"
Check if containers are running and ports are accessible:
```bash
docker compose -f /root/crane/docker-compose.yml ps
docker compose -f /root/crane/docker-compose.dev.yml -p crane-dev ps
```

### Sync failed mid-way
Restore from the backup that was created at the start:
```bash
gunzip -c /root/crane/backups/dev_db_before_sync_*.sql.gz | \
  docker compose -f /root/crane/docker-compose.dev.yml -p crane-dev exec -T db \
    psql -U crane_dev_user -d crane_intelligence_dev
```

## Related Scripts

- `backup-databases.sh` - Backup all environment databases
- `restore-database.sh` - Restore from a backup file
- `check_database_connection.sh` - Test database connectivity

