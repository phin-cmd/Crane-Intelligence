#!/bin/bash
set -e

# Database Backup Script
# Backs up all three environment databases with enhanced features

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=${RETENTION_DAYS:-7}
LOG_FILE="$BACKUP_DIR/backup.log"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========================================="
log "Database Backup Script"
log "========================================="
log ""

# Function to backup a single database
backup_database() {
    local env=$1
    local compose_file=$2
    local project_name=$3
    local db_user=$4
    local db_name=$5
    
    log "Backing up $env database..."
    
    # Check if container is running
    if ! docker compose -f "$PROJECT_ROOT/$compose_file" -p "$project_name" ps db | grep -q "Up"; then
        log "⚠️  WARNING: $env database container is not running. Skipping backup."
        return 1
    fi
    
    local backup_file="$BACKUP_DIR/${env}_db_$DATE.sql.gz"
    
    # Perform backup
    if docker compose -f "$PROJECT_ROOT/$compose_file" -p "$project_name" exec -T db \
        pg_dump -U "$db_user" "$db_name" | gzip > "$backup_file"; then
        
        # Verify backup file was created and has content
        if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
            local size=$(du -h "$backup_file" | cut -f1)
            log "✅ $env database backed up successfully: $backup_file ($size)"
            
            # Create checksum for verification
            sha256sum "$backup_file" > "${backup_file}.sha256"
            log "   Checksum: $(cat "${backup_file}.sha256" | cut -d' ' -f1)"
            
            return 0
        else
            log "❌ ERROR: Backup file is empty or missing: $backup_file"
            return 1
        fi
    else
        log "❌ ERROR: Failed to backup $env database"
        return 1
    fi
}

# Backup Dev Database
backup_database "dev" \
    "docker-compose.dev.yml" \
    "crane-dev" \
    "crane_dev_user" \
    "crane_intelligence_dev"

# Backup UAT Database
backup_database "uat" \
    "docker-compose.uat.yml" \
    "crane-uat" \
    "crane_uat_user" \
    "crane_intelligence_uat"

# Backup Production Database
backup_database "prod" \
    "docker-compose.yml" \
    "crane" \
    "crane_user" \
    "crane_intelligence"

log ""
log "Backups created:"
ls -lh "$BACKUP_DIR"/*_${DATE}.sql.gz 2>/dev/null || log "   No backups created"

# Cleanup old backups
log ""
log "Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.sha256" -mtime +$RETENTION_DAYS -delete

# Count remaining backups
local_backup_count=$(find "$BACKUP_DIR" -name "*.sql.gz" | wc -l)
log "   Remaining backups: $local_backup_count"

log ""
log "========================================="
log "Backup complete!"
log "========================================="

