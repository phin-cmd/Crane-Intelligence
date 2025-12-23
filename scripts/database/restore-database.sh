#!/bin/bash
set -e

# Database Restore Script
# Usage: ./restore-database.sh <environment> <backup_file>
# Example: ./restore-database.sh prod /root/crane/backups/prod_db_20241218_120000.sql.gz

if [ $# -ne 2 ]; then
    echo "Usage: $0 <environment> <backup_file>"
    echo "Environments: dev, uat, prod"
    echo "Example: $0 prod /root/crane/backups/prod_db_20241218_120000.sql.gz"
    exit 1
fi

ENV=$1
BACKUP_FILE=$2

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "========================================="
echo "Database Restore Script"
echo "========================================="
echo "Environment: $ENV"
echo "Backup file: $BACKUP_FILE"
echo ""
read -p "⚠️  WARNING: This will overwrite the $ENV database. Continue? (yes/no) " -r
echo

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Restore cancelled."
    exit 1
fi

case $ENV in
    dev)
        echo "Restoring dev database..."
        gunzip -c "$BACKUP_FILE" | \
        docker compose -f /root/crane/docker-compose.dev.yml -p crane-dev exec -T db \
            psql -U crane_dev_user -d crane_intelligence_dev
        ;;
    uat)
        echo "Restoring UAT database..."
        gunzip -c "$BACKUP_FILE" | \
        docker compose -f /root/crane/docker-compose.uat.yml -p crane-uat exec -T db \
            psql -U crane_uat_user -d crane_intelligence_uat
        ;;
    prod)
        echo "Restoring production database..."
        echo "⚠️  EXTRA WARNING: You are restoring PRODUCTION database!"
        read -p "Type 'RESTORE PROD' to confirm: " -r
        echo
        if [[ ! $REPLY == "RESTORE PROD" ]]; then
            echo "Restore cancelled."
            exit 1
        fi
        gunzip -c "$BACKUP_FILE" | \
        docker compose -f /root/crane/docker-compose.yml exec -T db \
            psql -U crane_user -d crane_intelligence
        ;;
    *)
        echo "Error: Invalid environment. Use: dev, uat, or prod"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "Database restore complete!"
echo "========================================="

