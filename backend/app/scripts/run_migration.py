#!/usr/bin/env python3
"""
Run database migration for FMV report status updates
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import Settings

def run_migration():
    """Run the migration script"""
    settings = Settings()
    engine = create_engine(settings.database_url)
    
    # Read migration file
    migration_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'migrations',
        'add_need_more_info_fields.sql'
    )
    
    print(f"Reading migration from: {migration_path}")
    with open(migration_path, 'r') as f:
        migration_sql = f.read()
    
    print("\nRunning migration...")
    print("="*70)
    
    with engine.connect() as conn:
        # Execute each statement
        statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for statement in statements:
            if statement:
                try:
                    print(f"Executing: {statement[:60]}...")
                    conn.execute(text(statement))
                    conn.commit()
                    print("✅ Success")
                except Exception as e:
                    # Check if it's a "already exists" error (which is OK with IF NOT EXISTS)
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        print(f"⚠️ Already exists (OK): {str(e)[:60]}")
                    else:
                        print(f"❌ Error: {str(e)}")
                        raise
    
    print("\n" + "="*70)
    print("✅ Migration completed!")
    print("="*70)
    
    # Verify the migration
    print("\nVerifying migration...")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'fmv_reports' 
            AND column_name IN ('need_more_info_at', 'need_more_info_reason')
            ORDER BY column_name;
        """))
        
        columns = [row[0] for row in result]
        if 'need_more_info_at' in columns and 'need_more_info_reason' in columns:
            print("✅ Both columns exist: need_more_info_at, need_more_info_reason")
        else:
            print(f"⚠️ Missing columns. Found: {columns}")

if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        sys.exit(1)

