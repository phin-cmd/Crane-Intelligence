# Database Migration Guide

This guide explains how to create, apply, and rollback database migrations safely.

## Overview

Migrations are managed through the `migration_manager.py` script, which:
- Tracks applied migrations in the `schema_migrations` table
- Ensures migrations are applied in order
- Supports rollback operations
- Includes safety checks for production

## Creating a Migration

### 1. Create Migration Files

```bash
cd backend/migrations
python migration_manager.py create --name add_user_preferences
```

This creates two files:
- `YYYYMMDD_HHMMSS_add_user_preferences.sql` - Migration script
- `YYYYMMDD_HHMMSS_add_user_preferences_rollback.sql` - Rollback script

### 2. Write Migration SQL

Edit the migration file:

```sql
-- Migration: add_user_preferences
-- Created: 2024-12-27
-- Description: Add user preferences table

BEGIN;

-- Step 1: Create table
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    preference_key VARCHAR(100) NOT NULL,
    preference_value TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, preference_key)
);

-- Step 2: Create indexes
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

COMMIT;
```

### 3. Write Rollback SQL

Edit the rollback file:

```sql
-- Rollback: add_user_preferences
-- Created: 2024-12-27

BEGIN;

-- Drop table
DROP TABLE IF EXISTS user_preferences;

COMMIT;
```

## Best Practices

### 1. Always Use Transactions

Wrap migrations in `BEGIN;` and `COMMIT;`:

```sql
BEGIN;
-- Your migration SQL
COMMIT;
```

### 2. Make Changes Backward Compatible

- Add columns as `NULL` first, then backfill, then make `NOT NULL`
- Add new tables before removing old ones
- Use `IF NOT EXISTS` and `IF EXISTS` clauses

### 3. Test in Dev First

Always test migrations in dev environment before applying to UAT/production:

```bash
# Test in dev
python migration_manager.py migrate --env dev

# Verify it works
python migration_manager.py status --env dev
```

### 4. Create Rollback Scripts

Always create rollback scripts for safety:

```sql
-- Rollback should undo exactly what the migration did
BEGIN;
ALTER TABLE users DROP COLUMN IF EXISTS new_field;
COMMIT;
```

## Applying Migrations

### Check Status

```bash
# Check migration status
python migration_manager.py status --env dev
```

### Apply Migrations

```bash
# Apply all pending migrations
python migration_manager.py migrate --env dev

# Dry run (see what would be applied)
python migration_manager.py migrate --env dev --dry-run
```

### Rollback Migration

```bash
# Rollback a specific migration
python migration_manager.py rollback --name YYYYMMDD_HHMMSS_migration_name --env dev
```

## Migration Workflow

### Development Environment

1. Create migration files
2. Write migration and rollback SQL
3. Test migration locally
4. Apply to dev: `python migration_manager.py migrate --env dev`
5. Verify application works
6. Commit migration files to git

### UAT Environment

1. Pull latest code (includes migration files)
2. Backup database: `./scripts/database/backup-databases.sh`
3. Apply migrations: `python migration_manager.py migrate --env uat`
4. Verify application works
5. Run UAT tests

### Production Environment

1. **CRITICAL**: Backup production database first!
   ```bash
   ./scripts/database/backup-databases.sh
   ```

2. Verify backup was created successfully

3. Apply migrations:
   ```bash
   python migration_manager.py migrate --env production
   ```

4. Monitor application for issues

5. If issues occur, rollback immediately:
   ```bash
   python migration_manager.py rollback --name <migration_name> --env production
   ```

## Safety Checks

The migration manager includes safety checks:

- **Production Warning**: Requires explicit confirmation before running on production
- **Transaction Support**: All migrations run in transactions (can be rolled back)
- **Migration Tracking**: Tracks which migrations have been applied
- **Checksum Verification**: Stores checksums to detect migration file changes

## Common Migration Patterns

### Adding a Column

```sql
BEGIN;

-- Step 1: Add column as nullable
ALTER TABLE users ADD COLUMN new_field VARCHAR(255) NULL;

-- Step 2: Backfill data
UPDATE users SET new_field = 'default_value' WHERE new_field IS NULL;

-- Step 3: Make NOT NULL (if required)
ALTER TABLE users ALTER COLUMN new_field SET NOT NULL;

COMMIT;
```

### Removing a Column

```sql
BEGIN;

-- Step 1: Remove constraints first
ALTER TABLE users DROP CONSTRAINT IF EXISTS constraint_name;

-- Step 2: Remove column
ALTER TABLE users DROP COLUMN IF EXISTS old_field;

COMMIT;
```

### Creating a Table

```sql
BEGIN;

CREATE TABLE IF NOT EXISTS new_table (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    -- other columns
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_new_table_user_id ON new_table(user_id);

COMMIT;
```

### Modifying Column Type

```sql
BEGIN;

-- Step 1: Add new column
ALTER TABLE users ADD COLUMN new_field_new_type VARCHAR(255);

-- Step 2: Migrate data
UPDATE users SET new_field_new_type = CAST(old_field AS VARCHAR(255));

-- Step 3: Drop old column
ALTER TABLE users DROP COLUMN old_field;

-- Step 4: Rename new column
ALTER TABLE users RENAME COLUMN new_field_new_type TO field_name;

COMMIT;
```

## Troubleshooting

### Migration Fails

1. Check error message
2. Fix migration SQL
3. If already partially applied, manually fix database
4. Re-run migration

### Need to Rollback

1. Use rollback script: `python migration_manager.py rollback --name <migration>`
2. If rollback script doesn't exist, manually restore from backup
3. Update migration tracking table if needed

### Migration Already Applied

If a migration shows as applied but shouldn't be:

```sql
-- Remove from tracking (use with caution!)
DELETE FROM schema_migrations WHERE migration_name = 'migration_name';
```

## CI/CD Integration

Migrations are automatically applied during deployment:

- **Dev**: Migrations run automatically on deploy
- **UAT**: Migrations run after backup, before deploy
- **Production**: Migrations run after backup, with extra safety checks

See `.github/workflows/*.yml` for details.

