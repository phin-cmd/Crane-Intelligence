#!/bin/bash
# Comprehensive Deployment and Database Sync Script
# Syncs code and database from Production to UAT and DEV environments
# WARNING: This will overwrite UAT and DEV databases with production data!

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRANE_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$CRANE_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Deploy & Sync: Production → UAT & DEV"
echo "=========================================="
echo ""
echo -e "${RED}⚠️  CRITICAL WARNING:${NC}"
echo -e "${RED}   This script will:${NC}"
echo -e "${RED}   1. Deploy production code to UAT and DEV${NC}"
echo -e "${RED}   2. OVERWRITE UAT and DEV databases with production data${NC}"
echo -e "${RED}   3. Restart all backend services${NC}"
echo ""
echo -e "${YELLOW}This is a DESTRUCTIVE operation!${NC}"
echo ""
read -p "Are you absolutely sure you want to continue? (type 'yes' to confirm): " -r
echo

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Operation cancelled."
    exit 1
fi

# Safety check: Verify we're not accidentally running on production
echo "Performing safety checks..."
HOSTNAME=$(hostname)
if [[ "$HOSTNAME" == *"prod"* ]] || [[ "$HOSTNAME" == *"production"* ]]; then
    echo -e "${RED}❌ ERROR: This script cannot run on production servers!${NC}"
    exit 1
fi

# Check if docker compose files exist
if [ ! -f "$CRANE_DIR/docker-compose.yml" ]; then
    echo -e "${RED}❌ ERROR: Production docker-compose.yml not found!${NC}"
    exit 1
fi

if [ ! -f "$CRANE_DIR/docker-compose.dev.yml" ]; then
    echo -e "${RED}❌ ERROR: Dev docker-compose.dev.yml not found!${NC}"
    exit 1
fi

if [ ! -f "$CRANE_DIR/docker-compose.uat.yml" ]; then
    echo -e "${RED}❌ ERROR: UAT docker-compose.uat.yml not found!${NC}"
    exit 1
fi

# Check if containers are running
echo "Checking if production database container is running..."
if ! docker compose -f "$CRANE_DIR/docker-compose.yml" ps db | grep -q "Up"; then
    echo -e "${RED}❌ ERROR: Production database container is not running!${NC}"
    echo "   Start it with: docker compose -f $CRANE_DIR/docker-compose.yml up -d db"
    exit 1
fi

echo "Checking if dev database container is running..."
if ! docker compose -f "$CRANE_DIR/docker-compose.dev.yml" -p crane-dev ps db | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Dev database container is not running. Starting it...${NC}"
    docker compose -f "$CRANE_DIR/docker-compose.dev.yml" -p crane-dev up -d db
    sleep 5
fi

echo "Checking if uat database container is running..."
if ! docker compose -f "$CRANE_DIR/docker-compose.uat.yml" -p crane-uat ps db | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  UAT database container is not running. Starting it...${NC}"
    docker compose -f "$CRANE_DIR/docker-compose.uat.yml" -p crane-uat up -d db
    sleep 5
fi

echo -e "${GREEN}✅ Safety checks passed${NC}"
echo ""

# Create backup directory
BACKUP_DIR="$CRANE_DIR/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

# Function to sync database from production to target environment
sync_database() {
    local target_env=$1
    local compose_file=$2
    local project_name=$3
    local db_user=$4
    local db_name=$5
    
    echo "=========================================="
    echo -e "${CYAN}Syncing Database: Production → ${target_env^^}${NC}"
    echo "=========================================="
    echo ""
    
    # Step 1: Backup target database
    echo -e "${BLUE}Step 1: Backing up ${target_env^^} database${NC}"
    TARGET_BACKUP_FILE="$BACKUP_DIR/${target_env}_db_before_sync_$DATE.sql.gz"
    echo "Creating backup: $TARGET_BACKUP_FILE"
    docker compose -f "$compose_file" -p "$project_name" exec -T db \
        pg_dump -U "$db_user" "$db_name" | gzip > "$TARGET_BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ ${target_env^^} database backed up successfully${NC}"
        echo "   Backup saved to: $TARGET_BACKUP_FILE"
    else
        echo -e "${RED}❌ ERROR: Failed to backup ${target_env^^} database${NC}"
        return 1
    fi
    echo ""
    
    # Step 2: Dump production database
    echo -e "${BLUE}Step 2: Dumping production database${NC}"
    PROD_DUMP_FILE="$BACKUP_DIR/prod_dump_for_${target_env}_sync_$DATE.sql.gz"
    echo "Creating production dump: $PROD_DUMP_FILE"
    docker compose -f "$CRANE_DIR/docker-compose.yml" exec -T db \
        pg_dump -U crane_user crane_intelligence | gzip > "$PROD_DUMP_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Production database dumped successfully${NC}"
        echo "   Dump saved to: $PROD_DUMP_FILE"
    else
        echo -e "${RED}❌ ERROR: Failed to dump production database${NC}"
        return 1
    fi
    echo ""
    
    # Step 3: Drop and recreate target database
    echo -e "${BLUE}Step 3: Preparing ${target_env^^} database${NC}"
    echo "Dropping existing connections..."
    docker compose -f "$compose_file" -p "$project_name" exec -T db \
        psql -U "$db_user" -d postgres -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '$db_name' AND pid <> pg_backend_pid();" || true
    
    echo "Dropping ${target_env^^} database..."
    docker compose -f "$compose_file" -p "$project_name" exec -T db \
        psql -U "$db_user" -d postgres -c "DROP DATABASE IF EXISTS $db_name;" || true
    
    echo "Creating new ${target_env^^} database..."
    docker compose -f "$compose_file" -p "$project_name" exec -T db \
        psql -U "$db_user" -d postgres -c "CREATE DATABASE $db_name;"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ ${target_env^^} database recreated successfully${NC}"
    else
        echo -e "${RED}❌ ERROR: Failed to recreate ${target_env^^} database${NC}"
        return 1
    fi
    echo ""
    
    # Step 4: Restore production data to target
    echo -e "${BLUE}Step 4: Restoring production data to ${target_env^^}${NC}"
    echo "This may take a few minutes..."
    gunzip -c "$PROD_DUMP_FILE" | \
        docker compose -f "$compose_file" -p "$project_name" exec -T db \
            psql -U "$db_user" -d "$db_name"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Production data restored to ${target_env^^} successfully${NC}"
    else
        echo -e "${RED}❌ ERROR: Failed to restore production data to ${target_env^^}${NC}"
        echo "   You can restore the backup with:"
        echo "   gunzip -c $TARGET_BACKUP_FILE | docker compose -f $compose_file -p $project_name exec -T db psql -U $db_user -d $db_name"
        return 1
    fi
    echo ""
    
    # Step 5: Update sequences
    echo -e "${BLUE}Step 5: Updating database sequences${NC}"
    docker compose -f "$compose_file" -p "$project_name" exec -T db \
        psql -U "$db_user" -d "$db_name" <<EOF
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
            EXECUTE format('SELECT COALESCE(MAX(id), 0) FROM %I', r.table_name) INTO max_id;
            seq_name := r.table_name || '_id_seq';
            IF EXISTS (SELECT 1 FROM pg_class WHERE relname = seq_name) THEN
                EXECUTE format('SELECT setval(%L, %s, true)', seq_name, max_id + 1);
            END IF;
        EXCEPTION WHEN OTHERS THEN
            CONTINUE;
        END;
    END LOOP;
END \$\$;
EOF
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Sequences updated successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  WARNING: Failed to update some sequences (this may be normal)${NC}"
    fi
    echo ""
    
    return 0
}

# Function to deploy code to target environment
deploy_code() {
    local target_env=$1
    local compose_file=$2
    local project_name=$3
    
    echo "=========================================="
    echo -e "${CYAN}Deploying Code to ${target_env^^}${NC}"
    echo "=========================================="
    echo ""
    
    # Check if docker compose is available
    if command -v docker compose &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        echo -e "${RED}ERROR: docker compose not found${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Step 1: Stopping ${target_env^^} backend container...${NC}"
    CONTAINER_NAME=$(docker ps -a --format "{{.Names}}" | grep -E "^${project_name}-backend-1$" | head -1)
    if [ -n "$CONTAINER_NAME" ]; then
        docker stop "$CONTAINER_NAME" 2>/dev/null || true
        docker rm "$CONTAINER_NAME" 2>/dev/null || true
        echo -e "${GREEN}✓ ${target_env^^} backend container stopped${NC}"
    else
        echo -e "${YELLOW}⚠ ${target_env^^} backend container not found (may not be running)${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}Step 2: Rebuilding ${target_env^^} backend image...${NC}"
    $DOCKER_COMPOSE -f "$compose_file" -p "$project_name" build --no-cache backend
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ ERROR: Failed to rebuild ${target_env^^} backend${NC}"
        return 1
    fi
    
    echo ""
    echo -e "${BLUE}Step 3: Starting ${target_env^^} backend container...${NC}"
    $DOCKER_COMPOSE -f "$compose_file" -p "$project_name" up -d --no-deps backend
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ ERROR: Failed to start ${target_env^^} backend${NC}"
        return 1
    fi
    
    echo ""
    echo -e "${BLUE}Step 4: Waiting for ${target_env^^} backend to be ready...${NC}"
    sleep 5
    
    echo ""
    echo -e "${BLUE}Step 5: Verifying ${target_env^^} backend...${NC}"
    CONTAINER_NAME=$(docker ps --filter "name=${project_name}-backend" --format "{{.Names}}" | head -1)
    if [ -z "$CONTAINER_NAME" ]; then
        echo -e "${RED}✗ ${target_env^^} backend container not found${NC}"
        return 1
    fi
    
    # Verify environment
    if docker exec "$CONTAINER_NAME" env 2>/dev/null | grep -q "ENVIRONMENT=${target_env}"; then
        echo -e "${GREEN}✓ ${target_env^^} backend is running with correct environment${NC}"
    else
        echo -e "${RED}✗ ${target_env^^} backend environment verification failed${NC}"
        return 1
    fi
    echo ""
    
    return 0
}

# Main execution
echo "=========================================="
echo "Starting Deployment and Sync Process"
echo "=========================================="
echo ""

# Sync DEV
echo -e "${CYAN}=== Processing DEV Environment ===${NC}"
echo ""
sync_database "dev" "docker-compose.dev.yml" "crane-dev" "crane_dev_user" "crane_intelligence_dev"
if [ $? -eq 0 ]; then
    deploy_code "dev" "docker-compose.dev.yml" "crane-dev"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ DEV environment sync and deployment complete!${NC}"
    else
        echo -e "${RED}❌ DEV deployment failed (database was synced)${NC}"
    fi
else
    echo -e "${RED}❌ DEV database sync failed${NC}"
fi
echo ""

# Sync UAT
echo -e "${CYAN}=== Processing UAT Environment ===${NC}"
echo ""
sync_database "uat" "docker-compose.uat.yml" "crane-uat" "crane_uat_user" "crane_intelligence_uat"
if [ $? -eq 0 ]; then
    deploy_code "uat" "docker-compose.uat.yml" "crane-uat"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ UAT environment sync and deployment complete!${NC}"
    else
        echo -e "${RED}❌ UAT deployment failed (database was synced)${NC}"
    fi
else
    echo -e "${RED}❌ UAT database sync failed${NC}"
fi
echo ""

# Final Summary
echo "=========================================="
echo "Deployment and Sync Summary"
echo "=========================================="
echo ""
echo "Backups created:"
ls -lh "$BACKUP_DIR"/*${DATE}* 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}' || echo "  No backups found"
echo ""
echo "Next steps:"
echo "  1. Verify deployments:"
echo "     - DEV: http://localhost:8104/api/v1/config/public"
echo "     - UAT: http://localhost:8204/api/v1/config/public"
echo ""
echo "  2. Test payment flow:"
echo "     ./scripts/test-complete-payment-flow.sh dev"
echo "     ./scripts/test-complete-payment-flow.sh uat"
echo ""
echo "  3. Monitor logs:"
echo "     docker logs crane-dev-backend-1 -f"
echo "     docker logs crane-uat-backend-1 -f"
echo ""
echo -e "${GREEN}✅ Deployment and sync process complete!${NC}"
echo ""

