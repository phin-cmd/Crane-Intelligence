"""
Database Migration: Add target_audience column to email_templates table
Adds a column to specify which type of users the email is for: user, guest, admin, or all
"""
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Try to import, but handle if dependencies aren't available
try:
    from sqlalchemy import text
    from app.core.database import SessionLocal, engine
    SQLALCHEMY_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import SQLAlchemy: {e}")
    print("   This migration should be run from the backend environment")
    print("   or with proper Python dependencies installed.")
    SQLALCHEMY_AVAILABLE = False

def run_migration():
    """Add target_audience column to email_templates table"""
    if not SQLALCHEMY_AVAILABLE:
        print("❌ Cannot run migration: SQLAlchemy not available")
        print("   Please run this script from the backend environment")
        return
    
    db = SessionLocal()
    try:
        print("Starting migration: Add target_audience to email_templates")
        
        # Check if column already exists
        print("1. Checking if target_audience column exists...")
        try:
            result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='email_templates' AND column_name='target_audience'
            """))
            exists = result.fetchone() is not None
            
            if exists:
                print("   ⚠️  target_audience column already exists, skipping...")
                return
        except Exception as e:
            # For SQLite, use different query
            try:
                result = db.execute(text("PRAGMA table_info(email_templates)"))
                columns = [row[1] for row in result.fetchall()]
                if 'target_audience' in columns:
                    print("   ⚠️  target_audience column already exists, skipping...")
                    return
            except:
                pass
        
        # Add the column
        print("2. Adding target_audience column to email_templates table...")
        try:
            # For PostgreSQL
            if 'postgresql' in str(engine.url):
                db.execute(text("""
                    ALTER TABLE email_templates 
                    ADD COLUMN target_audience VARCHAR(20) DEFAULT 'all' 
                    CHECK (target_audience IN ('user', 'guest', 'admin', 'all'))
                """))
            else:
                # For SQLite
                db.execute(text("""
                    ALTER TABLE email_templates 
                    ADD COLUMN target_audience VARCHAR(20) DEFAULT 'all'
                """))
            db.commit()
            print("   ✓ target_audience column added successfully")
        except Exception as e:
            print(f"   ⚠️  Error adding target_audience column: {e}")
            db.rollback()
            # Try without CHECK constraint for SQLite
            try:
                db.execute(text("""
                    ALTER TABLE email_templates 
                    ADD COLUMN target_audience VARCHAR(20) DEFAULT 'all'
                """))
                db.commit()
                print("   ✓ target_audience column added successfully (without constraint)")
            except Exception as e2:
                print(f"   ❌ Failed to add column: {e2}")
                db.rollback()
                return
        
        # Set default value for existing rows
        print("3. Setting default values for existing templates...")
        try:
            db.execute(text("""
                UPDATE email_templates 
                SET target_audience = 'all' 
                WHERE target_audience IS NULL
            """))
            db.commit()
            print("   ✓ Default values set for existing templates")
        except Exception as e:
            print(f"   ⚠️  Error setting default values: {e}")
            db.rollback()
        
        print("\n✅ Migration completed successfully!")
        print("   Column 'target_audience' added with values: 'user', 'guest', 'admin', 'all'")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()

