#!/bin/bash
set -e

# Database Migration Runner Script
# Applies pending migrations to the specified environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MIGRATIONS_DIR="$PROJECT_ROOT/backend/migrations"

ENVIRONMENT=${1:-dev}

echo "========================================="
echo "Database Migration Runner"
echo "Environment: $ENVIRONMENT"
echo "========================================="
echo ""

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|uat|production)$ ]]; then
    echo "❌ ERROR: Invalid environment. Must be: dev, uat, or production"
    exit 1
fi

# Safety check for production
if [ "$ENVIRONMENT" == "production" ]; then
    echo "⚠️  WARNING: You are about to run migrations on PRODUCTION!"
    echo ""
    read -p "Type 'yes' to continue: " -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "Migration cancelled."
        exit 1
    fi
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

echo "✅ Database container is running"
echo ""

# Check if migrations directory exists
if [ ! -d "$MIGRATIONS_DIR" ]; then
    echo "❌ ERROR: Migrations directory not found: $MIGRATIONS_DIR"
    exit 1
fi

# Run migrations using Python migration manager
echo "Running migrations..."
docker compose -f "$COMPOSE_FILE" -p "$COMPOSE_PROJECT" exec -T backend \
    python /app/migrations/migration_manager.py migrate --env "$ENVIRONMENT"

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✅ Migrations completed successfully!"
    echo "========================================="
else
    echo ""
    echo "========================================="
    echo "❌ Migration failed!"
    echo "========================================="
    exit 1
fi

