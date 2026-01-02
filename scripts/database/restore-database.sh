#!/bin/bash
set -e

# Database Restore Script
# Restores a database from backup

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/backups"

ENVIRONMENT=${1:-}
BACKUP_FILE=${2:-}

if [ -z "$ENVIRONMENT" ] || [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <environment> <backup_file>"
    echo ""
    echo "Environments: dev, uat, production"
    echo ""
    echo "Available backups:"
    ls -lh "$BACKUP_DIR"/*.sql.gz 2>/dev/null | awk '{print $9, "(" $5 ")"}'
    exit 1
fi

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|uat|production)$ ]]; then
    echo "❌ ERROR: Invalid environment. Must be: dev, uat, or production"
    exit 1
fi

# Safety check for production
if [ "$ENVIRONMENT" == "production" ]; then
    echo "⚠️  WARNING: You are about to RESTORE PRODUCTION DATABASE!"
    echo "   This will OVERWRITE all production data!"
    echo ""
    read -p "Type 'RESTORE PRODUCTION' to continue: " -r
    echo
    if [[ ! $REPLY == "RESTORE PRODUCTION" ]]; then
        echo "Restore cancelled."
        exit 1
    fi
fi

# Resolve backup file path
if [ ! -f "$BACKUP_FILE" ]; then
    # Try relative to backup directory
    if [ -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
        BACKUP_FILE="$BACKUP_DIR/$BACKUP_FILE"
    else
        echo "❌ ERROR: Backup file not found: $BACKUP_FILE"
        exit 1
    fi
fi

# Verify backup file exists and has content
if [ ! -f "$BACKUP_FILE" ] || [ ! -s "$BACKUP_FILE" ]; then
    echo "❌ ERROR: Backup file is missing or empty: $BACKUP_FILE"
    exit 1
fi

# Verify checksum if available
CHECKSUM_FILE="${BACKUP_FILE}.sha256"
if [ -f "$CHECKSUM_FILE" ]; then
    echo "Verifying backup checksum..."
    if sha256sum -c "$CHECKSUM_FILE" > /dev/null 2>&1; then
        echo "✅ Backup checksum verified"
    else
        echo "❌ ERROR: Backup checksum verification failed!"
        echo "   Backup file may be corrupted. Do not proceed."
        exit 1
    fi
else
    echo "⚠️  WARNING: No checksum file found. Cannot verify backup integrity."
fi

# Set docker compose file based on environment
if [ "$ENVIRONMENT" == "dev" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
    COMPOSE_PROJECT="crane-dev"
    DB_USER="crane_dev_user"
    DB_NAME="crane_intelligence_dev"
elif [ "$ENVIRONMENT" == "uat" ]; then
    COMPOSE_FILE="docker-compose.uat.yml"
    COMPOSE_PROJECT="crane-uat"
    DB_USER="crane_uat_user"
    DB_NAME="crane_intelligence_uat"
else
    COMPOSE_FILE="docker-compose.yml"
    COMPOSE_PROJECT="crane"
    DB_USER="crane_user"
    DB_NAME="crane_intelligence"
fi

cd "$PROJECT_ROOT"

# Check if containers are running
echo "Checking if database container is running..."
if ! docker compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" ps db | grep -q "Up"; then
    echo "❌ ERROR: Database container is not running!"
    echo "   Start it with: docker compose -f $COMPOSE_FILE -p $COMPOSE_PROJECT up -d db"
    exit 1
fi

echo ""
echo "========================================="
echo "Database Restore"
echo "Environment: $ENVIRONMENT"
echo "Backup file: $BACKUP_FILE"
echo "========================================="
echo ""

# Create a backup before restore (safety measure)
echo "Creating safety backup before restore..."
SAFETY_BACKUP="$BACKUP_DIR/${ENVIRONMENT}_db_before_restore_$(date +%Y%m%d_%H%M%S).sql.gz"
docker compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" exec -T db \
    pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$SAFETY_BACKUP"

if [ $? -eq 0 ] && [ -s "$SAFETY_BACKUP" ]; then
    echo "✅ Safety backup created: $SAFETY_BACKUP"
else
    echo "❌ ERROR: Failed to create safety backup. Aborting restore."
    exit 1
fi

# Drop existing database connections
echo "Dropping existing database connections..."
docker compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" exec -T db \
    psql -U "$DB_USER" -d postgres -c "
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '$DB_NAME'
        AND pid <> pg_backend_pid();
    " || true

# Restore database
echo "Restoring database from backup..."
gunzip -c "$BACKUP_FILE" | \
    docker compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" exec -T db \
        psql -U "$DB_USER" -d "$DB_NAME"

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✅ Database restored successfully!"
    echo "========================================="
    echo ""
    echo "Safety backup saved at: $SAFETY_BACKUP"
    echo ""
    echo "Next steps:"
    echo "  1. Restart backend: docker compose -f $COMPOSE_FILE -p $COMPOSE_PROJECT restart backend"
    echo "  2. Verify application works correctly"
    echo "  3. Check data integrity"
else
    echo ""
    echo "========================================="
    echo "❌ Restore failed!"
    echo "========================================="
    echo ""
    echo "You can restore the safety backup with:"
    echo "  $0 $ENVIRONMENT $SAFETY_BACKUP"
    exit 1
fi
