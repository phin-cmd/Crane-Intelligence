#!/bin/bash

# Automated Database Backup Script for Crane Intelligence Platform
# This script creates automated backups of the PostgreSQL database

# Configuration
BACKUP_DIR="/root/Crane-Intelligence/backups"
DB_NAME="crane_db"
DB_USER="crane_user"
DB_HOST="localhost"
DB_PORT="5434"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/crane_db_backup_${DATE}.sql"
RETENTION_DAYS=7

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${BACKUP_DIR}/backup.log"
}

# Function to cleanup old backups
cleanup_old_backups() {
    log_message "Cleaning up backups older than $RETENTION_DAYS days..."
    find "$BACKUP_DIR" -name "crane_db_backup_*.sql" -type f -mtime +$RETENTION_DAYS -delete
    log_message "Old backup cleanup completed"
}

# Function to create backup
create_backup() {
    log_message "Starting database backup..."
    
    # Create backup using pg_dump
    PGPASSWORD="crane_password" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --no-password \
        --format=custom \
        --compress=9 \
        --file="$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        log_message "Database backup completed successfully: $BACKUP_FILE"
        
        # Get backup file size
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        log_message "Backup file size: $BACKUP_SIZE"
        
        # Verify backup integrity
        PGPASSWORD="crane_password" pg_restore --list "$BACKUP_FILE" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            log_message "Backup integrity verified successfully"
        else
            log_message "WARNING: Backup integrity check failed"
        fi
        
    else
        log_message "ERROR: Database backup failed"
        exit 1
    fi
}

# Function to test database connection
test_connection() {
    log_message "Testing database connection..."
    PGPASSWORD="crane_password" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "SELECT version();" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        log_message "Database connection successful"
        return 0
    else
        log_message "ERROR: Cannot connect to database"
        return 1
    fi
}

# Main execution
main() {
    log_message "=== Crane Intelligence Database Backup Started ==="
    
    # Test database connection
    if ! test_connection; then
        log_message "ERROR: Database connection failed. Backup aborted."
        exit 1
    fi
    
    # Create backup
    create_backup
    
    # Cleanup old backups
    cleanup_old_backups
    
    log_message "=== Database Backup Process Completed ==="
}

# Run main function
main "$@"
