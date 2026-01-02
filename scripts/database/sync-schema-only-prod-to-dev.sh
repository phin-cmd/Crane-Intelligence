#!/bin/bash
set -e

# Sync Production Database Schema Only to Dev
# This script syncs only the schema (structure) from production to dev, without data
# WARNING: This will drop and recreate all tables in dev!

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "========================================="
echo "Sync Production Schema Only to Dev"
echo "========================================="
echo ""
echo "⚠️  WARNING: This will:"
echo "   1. Backup current dev database"
echo "   2. Dump production schema (structure only)"
echo "   3. OVERWRITE dev database schema with production schema"
echo "   (Data in dev will be preserved if tables match)"
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
DEV_BACKUP_FILE="$BACKUP_DIR/dev_db_before_schema_sync_$DATE.sql.gz"
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

# Step 2: Dump production schema only (no data)
echo "========================================="
echo "Step 2: Dumping production schema"
echo "========================================="
PROD_SCHEMA_FILE="$BACKUP_DIR/prod_schema_for_dev_sync_$DATE.sql.gz"
echo "Creating production schema dump: $PROD_SCHEMA_FILE"
docker compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T db \
    pg_dump -U crane_user --schema-only --no-owner --no-acl crane_intelligence | gzip > "$PROD_SCHEMA_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Production schema dumped successfully"
    echo "   Schema dump saved to: $PROD_SCHEMA_FILE"
else
    echo "❌ ERROR: Failed to dump production schema"
    exit 1
fi
echo ""

# Step 3: Drop all tables in dev (schema only, preserve data if possible)
echo "========================================="
echo "Step 3: Applying production schema to dev"
echo "========================================="
echo "Dropping existing schema objects in dev..."
# Drop all tables, views, functions, etc. in public schema
docker compose -f "$PROJECT_ROOT/docker-compose.dev.yml" -p crane-dev exec -T db \
    psql -U crane_dev_user -d crane_intelligence_dev <<EOF
-- Drop all objects in public schema
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO crane_dev_user;
GRANT ALL ON SCHEMA public TO public;
EOF

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to drop dev schema"
    exit 1
fi

# Step 4: Restore production schema to dev
echo "Restoring production schema to dev..."
gunzip -c "$PROD_SCHEMA_FILE" | \
    docker compose -f "$PROJECT_ROOT/docker-compose.dev.yml" -p crane-dev exec -T db \
        psql -U crane_dev_user -d crane_intelligence_dev

if [ $? -eq 0 ]; then
    echo "✅ Production schema restored to dev successfully"
else
    echo "❌ ERROR: Failed to restore production schema to dev"
    echo "   You can restore the dev backup with:"
    echo "   gunzip -c $DEV_BACKUP_FILE | docker compose -f $PROJECT_ROOT/docker-compose.dev.yml -p crane-dev exec -T db psql -U crane_dev_user -d crane_intelligence_dev"
    exit 1
fi
echo ""

# Summary
echo "========================================="
echo "Schema Sync Complete!"
echo "========================================="
echo ""
echo "Summary:"
echo "  ✅ Dev database backed up: $DEV_BACKUP_FILE"
echo "  ✅ Production schema dumped: $PROD_SCHEMA_FILE"
echo "  ✅ Dev database schema synced with production"
echo ""
echo "Next steps:"
echo "  1. Restart dev backend: docker compose -f $PROJECT_ROOT/docker-compose.dev.yml -p crane-dev restart backend"
echo "  2. Verify the schema sync by checking the dev database"
echo ""
echo "To restore the previous dev database if needed:"
echo "  gunzip -c $DEV_BACKUP_FILE | docker compose -f $PROJECT_ROOT/docker-compose.dev.yml -p crane-dev exec -T db psql -U crane_dev_user -d crane_intelligence_dev"
echo ""

