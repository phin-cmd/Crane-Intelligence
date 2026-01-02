#!/bin/bash
set -e

# Sync Production Database to Dev
# This script syncs the production database schema and data to the dev environment
# WARNING: This will overwrite the dev database!

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "========================================="
echo "Sync Production Database to Dev"
echo "========================================="
echo ""
echo "⚠️  WARNING: This will:"
echo "   1. Backup current dev database"
echo "   2. Dump production database"
echo "   3. OVERWRITE dev database with production data"
echo ""
read -p "Are you sure you want to continue? (yes/no) " -r
echo

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Sync cancelled."
    exit 1
fi

# Safety check: Verify we're not accidentally running on production
echo "Performing safety checks..."
HOSTNAME=$(hostname)
if [[ "$HOSTNAME" == *"prod"* ]] || [[ "$HOSTNAME" == *"production"* ]]; then
    echo "❌ ERROR: This script cannot run on production servers!"
    exit 1
fi

# Check if docker compose files exist
if [ ! -f "$PROJECT_ROOT/docker-compose.yml" ]; then
    echo "❌ ERROR: Production docker-compose.yml not found!"
    exit 1
fi

if [ ! -f "$PROJECT_ROOT/docker-compose.dev.yml" ]; then
    echo "❌ ERROR: Dev docker-compose.dev.yml not found!"
    exit 1
fi

# Check if containers are running
echo "Checking if production database container is running..."
if ! docker compose -f "$PROJECT_ROOT/docker-compose.yml" ps db | grep -q "Up"; then
    echo "❌ ERROR: Production database container is not running!"
    echo "   Start it with: docker compose -f $PROJECT_ROOT/docker-compose.yml up -d db"
    exit 1
fi

echo "Checking if dev database container is running..."
if ! docker compose -f "$PROJECT_ROOT/docker-compose.dev.yml" -p crane-dev ps db | grep -q "Up"; then
    echo "❌ ERROR: Dev database container is not running!"
    echo "   Start it with: docker compose -f $PROJECT_ROOT/docker-compose.dev.yml -p crane-dev up -d db"
    exit 1
fi

echo "✅ Safety checks passed"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Step 1: Backup current dev database
echo "========================================="
echo "Step 1: Backing up current dev database"
echo "========================================="
DEV_BACKUP_FILE="$BACKUP_DIR/dev_db_before_sync_$DATE.sql.gz"
echo "Creating backup: $DEV_BACKUP_FILE"
docker compose -f "$PROJECT_ROOT/docker-compose.dev.yml" -p crane-dev exec -T db \
    pg_dump -U crane_dev_user crane_intelligence_dev | gzip > "$DEV_BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Dev database backed up successfully"
    echo "   Backup saved to: $DEV_BACKUP_FILE"
else
    echo "❌ ERROR: Failed to backup dev database"
    exit 1
fi
echo ""

# Step 2: Dump production database
echo "========================================="
echo "Step 2: Dumping production database"
echo "========================================="
PROD_DUMP_FILE="$BACKUP_DIR/prod_dump_for_dev_sync_$DATE.sql.gz"
echo "Creating production dump: $PROD_DUMP_FILE"
docker compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T db \
    pg_dump -U crane_user crane_intelligence | gzip > "$PROD_DUMP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Production database dumped successfully"
    echo "   Dump saved to: $PROD_DUMP_FILE"
else
    echo "❌ ERROR: Failed to dump production database"
    exit 1
fi
echo ""

# Step 3: Drop and recreate dev database
echo "========================================="
echo "Step 3: Preparing dev database"
echo "========================================="
echo "Dropping existing connections to dev database..."
docker compose -f "$PROJECT_ROOT/docker-compose.dev.yml" -p crane-dev exec -T db \
    psql -U crane_dev_user -d postgres -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'crane_intelligence_dev' AND pid <> pg_backend_pid();" || true

echo "Dropping dev database..."
docker compose -f "$PROJECT_ROOT/docker-compose.dev.yml" -p crane-dev exec -T db \
    psql -U crane_dev_user -d postgres -c "DROP DATABASE IF EXISTS crane_intelligence_dev;" || true

echo "Creating new dev database..."
docker compose -f "$PROJECT_ROOT/docker-compose.dev.yml" -p crane-dev exec -T db \
    psql -U crane_dev_user -d postgres -c "CREATE DATABASE crane_intelligence_dev;"

if [ $? -eq 0 ]; then
    echo "✅ Dev database recreated successfully"
else
    echo "❌ ERROR: Failed to recreate dev database"
    exit 1
fi
echo ""

# Step 4: Restore production data to dev
echo "========================================="
echo "Step 4: Restoring production data to dev"
echo "========================================="
echo "This may take a few minutes..."
gunzip -c "$PROD_DUMP_FILE" | \
    docker compose -f "$PROJECT_ROOT/docker-compose.dev.yml" -p crane-dev exec -T db \
        psql -U crane_dev_user -d crane_intelligence_dev

if [ $? -eq 0 ]; then
    echo "✅ Production data restored to dev successfully"
else
    echo "❌ ERROR: Failed to restore production data to dev"
    echo "   You can restore the dev backup with:"
    echo "   gunzip -c $DEV_BACKUP_FILE | docker compose -f $PROJECT_ROOT/docker-compose.dev.yml -p crane-dev exec -T db psql -U crane_dev_user -d crane_intelligence_dev"
    exit 1
fi
echo ""

# Step 5: Update sequences and reset any dev-specific data if needed
echo "========================================="
echo "Step 5: Updating database sequences"
echo "========================================="
echo "Updating sequences to prevent ID conflicts..."
docker compose -f "$PROJECT_ROOT/docker-compose.dev.yml" -p crane-dev exec -T db \
    psql -U crane_dev_user -d crane_intelligence_dev <<EOF
-- Update sequences to max ID + 1 for all tables with id columns
DO \$\$
DECLARE
    r RECORD;
    max_id INTEGER;
    seq_name TEXT;
BEGIN
    FOR r IN 
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
    LOOP
        BEGIN
            -- Try to get max id
            EXECUTE format('SELECT COALESCE(MAX(id), 0) FROM %I', r.table_name) INTO max_id;
            
            -- Try to reset sequence
            seq_name := r.table_name || '_id_seq';
            IF EXISTS (SELECT 1 FROM pg_class WHERE relname = seq_name) THEN
                EXECUTE format('SELECT setval(%L, %s, true)', seq_name, max_id + 1);
            END IF;
        EXCEPTION WHEN OTHERS THEN
            -- Skip tables without id column or sequence
            CONTINUE;
        END;
    END LOOP;
END \$\$;
EOF

if [ $? -eq 0 ]; then
    echo "✅ Sequences updated successfully"
else
    echo "⚠️  WARNING: Failed to update some sequences (this may be normal)"
fi
echo ""

# Summary
echo "========================================="
echo "Sync Complete!"
echo "========================================="
echo ""
echo "Summary:"
echo "  ✅ Dev database backed up: $DEV_BACKUP_FILE"
echo "  ✅ Production database dumped: $PROD_DUMP_FILE"
echo "  ✅ Dev database synced with production data"
echo ""
echo "Next steps:"
echo "  1. Restart dev backend: docker compose -f $PROJECT_ROOT/docker-compose.dev.yml -p crane-dev restart backend"
echo "  2. Verify the sync by checking the dev database"
echo ""
echo "To restore the previous dev database if needed:"
echo "  gunzip -c $DEV_BACKUP_FILE | docker compose -f $PROJECT_ROOT/docker-compose.dev.yml -p crane-dev exec -T db psql -U crane_dev_user -d crane_intelligence_dev"
echo ""

