#!/usr/bin/env python3
"""
Database Migration Manager
Manages database migrations with rollback support and safety checks
"""

import os
import sys
import argparse
import subprocess
import psycopg2
from psycopg2 import sql
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_db, engine

class MigrationManager:
    def __init__(self, environment='dev'):
        self.environment = environment
        self.migrations_dir = Path(__file__).parent
        self.migrations_table = 'schema_migrations'
        
        # Set database connection based on environment
        if environment == 'dev':
            self.db_url = os.getenv('DATABASE_URL', 'postgresql://crane_dev_user:crane_dev_password@localhost:5534/crane_intelligence_dev')
        elif environment == 'uat':
            self.db_url = os.getenv('DATABASE_URL', 'postgresql://crane_uat_user:crane_uat_password@localhost:5634/crane_intelligence_uat')
        else:  # production
            self.db_url = os.getenv('DATABASE_URL', 'postgresql://crane_user:crane_password@localhost:5434/crane_intelligence')
        
        # Safety check for production
        if environment == 'production':
            print("⚠️  WARNING: You are about to run migrations on PRODUCTION!")
            response = input("Type 'yes' to continue: ")
            if response.lower() != 'yes':
                print("Migration cancelled.")
                sys.exit(1)
    
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url)
    
    def ensure_migrations_table(self):
        """Create migrations tracking table if it doesn't exist"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.migrations_table} (
                        id SERIAL PRIMARY KEY,
                        migration_name VARCHAR(255) UNIQUE NOT NULL,
                        applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        rolled_back_at TIMESTAMP WITH TIME ZONE,
                        checksum VARCHAR(64)
                    );
                """)
                conn.commit()
        finally:
            conn.close()
    
    def get_applied_migrations(self):
        """Get list of applied migrations"""
        self.ensure_migrations_table()
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT migration_name, applied_at, rolled_back_at
                    FROM {self.migrations_table}
                    WHERE rolled_back_at IS NULL
                    ORDER BY applied_at;
                """)
                return [row[0] for row in cur.fetchall()]
        finally:
            conn.close()
    
    def get_pending_migrations(self):
        """Get list of pending migrations"""
        applied = set(self.get_applied_migrations())
        migrations = sorted([f.stem for f in self.migrations_dir.glob('*.sql') if f.stem != 'latest'])
        return [m for m in migrations if m not in applied]
    
    def apply_migration(self, migration_name):
        """Apply a single migration"""
        migration_file = self.migrations_dir / f"{migration_name}.sql"
        
        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            return False
        
        print(f"📝 Applying migration: {migration_name}")
        
        # Read migration file
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Start transaction
                cur.execute("BEGIN;")
                
                # Apply migration
                cur.execute(migration_sql)
                
                # Record migration
                cur.execute(f"""
                    INSERT INTO {self.migrations_table} (migration_name, checksum)
                    VALUES (%s, %s)
                    ON CONFLICT (migration_name) DO NOTHING;
                """, (migration_name, self._calculate_checksum(migration_sql)))
                
                # Commit transaction
                conn.commit()
                print(f"✅ Migration applied successfully: {migration_name}")
                return True
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Migration failed: {migration_name}")
            print(f"   Error: {str(e)}")
            return False
        finally:
            conn.close()
    
    def rollback_migration(self, migration_name):
        """Rollback a migration (requires rollback script)"""
        rollback_file = self.migrations_dir / f"{migration_name}_rollback.sql"
        
        if not rollback_file.exists():
            print(f"❌ Rollback file not found: {rollback_file}")
            print("   Cannot rollback without rollback script!")
            return False
        
        print(f"🔄 Rolling back migration: {migration_name}")
        
        # Read rollback file
        with open(rollback_file, 'r') as f:
            rollback_sql = f.read()
        
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Start transaction
                cur.execute("BEGIN;")
                
                # Apply rollback
                cur.execute(rollback_sql)
                
                # Mark migration as rolled back
                cur.execute(f"""
                    UPDATE {self.migrations_table}
                    SET rolled_back_at = CURRENT_TIMESTAMP
                    WHERE migration_name = %s;
                """, (migration_name,))
                
                # Commit transaction
                conn.commit()
                print(f"✅ Migration rolled back successfully: {migration_name}")
                return True
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Rollback failed: {migration_name}")
            print(f"   Error: {str(e)}")
            return False
        finally:
            conn.close()
    
    def _calculate_checksum(self, content):
        """Calculate checksum for migration content"""
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def status(self):
        """Show migration status"""
        print(f"\n📊 Migration Status ({self.environment.upper()})")
        print("=" * 60)
        
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()
        
        print(f"\n✅ Applied migrations ({len(applied)}):")
        for migration in applied:
            print(f"   - {migration}")
        
        print(f"\n⏳ Pending migrations ({len(pending)}):")
        for migration in pending:
            print(f"   - {migration}")
        
        print()
    
    def migrate(self, dry_run=False):
        """Apply all pending migrations"""
        pending = self.get_pending_migrations()
        
        if not pending:
            print("✅ No pending migrations")
            return True
        
        print(f"\n🚀 Applying {len(pending)} pending migration(s)...")
        
        if dry_run:
            print("🔍 DRY RUN - No changes will be made")
            for migration in pending:
                print(f"   Would apply: {migration}")
            return True
        
        success = True
        for migration in pending:
            if not self.apply_migration(migration):
                success = False
                print(f"\n❌ Migration failed. Stopping.")
                break
        
        return success


def main():
    parser = argparse.ArgumentParser(description='Database Migration Manager')
    parser.add_argument('command', choices=['status', 'migrate', 'rollback', 'create'],
                       help='Command to execute')
    parser.add_argument('--env', choices=['dev', 'uat', 'production'],
                       default='dev', help='Environment (default: dev)')
    parser.add_argument('--name', help='Migration name (for create/rollback)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run (show what would be done)')
    
    args = parser.parse_args()
    
    manager = MigrationManager(environment=args.env)
    
    if args.command == 'status':
        manager.status()
    
    elif args.command == 'migrate':
        success = manager.migrate(dry_run=args.dry_run)
        sys.exit(0 if success else 1)
    
    elif args.command == 'rollback':
        if not args.name:
            print("❌ Migration name required for rollback")
            print("   Usage: python migration_manager.py rollback --name <migration_name>")
            sys.exit(1)
        success = manager.rollback_migration(args.name)
        sys.exit(0 if success else 1)
    
    elif args.command == 'create':
        if not args.name:
            print("❌ Migration name required")
            print("   Usage: python migration_manager.py create --name <migration_name>")
            sys.exit(1)
        
        # Create migration template
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        migration_file = manager.migrations_dir / f"{timestamp}_{args.name}.sql"
        rollback_file = manager.migrations_dir / f"{timestamp}_{args.name}_rollback.sql"
        
        migration_template = f"""-- Migration: {args.name}
-- Created: {datetime.now().isoformat()}
-- Description: [Describe what this migration does]

BEGIN;

-- Your migration SQL here
-- Example:
-- ALTER TABLE users ADD COLUMN new_field VARCHAR(255);

COMMIT;
"""
        
        rollback_template = f"""-- Rollback: {args.name}
-- Created: {datetime.now().isoformat()}

BEGIN;

-- Your rollback SQL here
-- Example:
-- ALTER TABLE users DROP COLUMN new_field;

COMMIT;
"""
        
        with open(migration_file, 'w') as f:
            f.write(migration_template)
        
        with open(rollback_file, 'w') as f:
            f.write(rollback_template)
        
        print(f"✅ Created migration files:")
        print(f"   - {migration_file}")
        print(f"   - {rollback_file}")


if __name__ == '__main__':
    main()

