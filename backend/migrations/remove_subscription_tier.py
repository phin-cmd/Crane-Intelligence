"""
Database Migration: Remove Subscription Tier Logic
Removes subscription_tier columns and related subscription management fields
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
    """Remove subscription tier columns and tables"""
    if not SQLALCHEMY_AVAILABLE:
        print("❌ Cannot run migration: SQLAlchemy not available")
        print("   Please run this script from the backend environment")
        return
    
    db = SessionLocal()
    try:
        print("Starting migration: Remove Subscription Tier Logic")
        
        # 1. Drop subscription_tier from users table
        print("1. Dropping subscription_tier from users table...")
        try:
            db.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS subscription_tier"))
            db.commit()
            print("   ✓ subscription_tier column removed from users")
        except Exception as e:
            print(f"   ⚠️  Error removing subscription_tier from users: {e}")
            db.rollback()
        
        # 2. Drop subscription_start_date from users table
        print("2. Dropping subscription_start_date from users table...")
        try:
            db.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS subscription_start_date"))
            db.commit()
            print("   ✓ subscription_start_date column removed from users")
        except Exception as e:
            print(f"   ⚠️  Error removing subscription_start_date: {e}")
            db.rollback()
        
        # 3. Drop subscription_end_date from users table
        print("3. Dropping subscription_end_date from users table...")
        try:
            db.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS subscription_end_date"))
            db.commit()
            print("   ✓ subscription_end_date column removed from users")
        except Exception as e:
            print(f"   ⚠️  Error removing subscription_end_date: {e}")
            db.rollback()
        
        # 4. Drop monthly_valuations_used from users table
        print("4. Dropping monthly_valuations_used from users table...")
        try:
            db.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS monthly_valuations_used"))
            db.commit()
            print("   ✓ monthly_valuations_used column removed from users")
        except Exception as e:
            print(f"   ⚠️  Error removing monthly_valuations_used: {e}")
            db.rollback()
        
        # 5. Drop monthly_api_calls_used from users table
        print("5. Dropping monthly_api_calls_used from users table...")
        try:
            db.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS monthly_api_calls_used"))
            db.commit()
            print("   ✓ monthly_api_calls_used column removed from users")
        except Exception as e:
            print(f"   ⚠️  Error removing monthly_api_calls_used: {e}")
            db.rollback()
        
        # 6. Drop subscription_tier from fmv_reports table
        print("6. Dropping subscription_tier from fmv_reports table...")
        try:
            db.execute(text("ALTER TABLE fmv_reports DROP COLUMN IF EXISTS subscription_tier"))
            db.commit()
            print("   ✓ subscription_tier column removed from fmv_reports")
        except Exception as e:
            print(f"   ⚠️  Error removing subscription_tier from fmv_reports: {e}")
            db.rollback()
        
        # 7. Drop subscription_plans table if it exists
        print("7. Dropping subscription_plans table...")
        try:
            db.execute(text("DROP TABLE IF EXISTS subscription_plans CASCADE"))
            db.commit()
            print("   ✓ subscription_plans table removed")
        except Exception as e:
            print(f"   ⚠️  Error removing subscription_plans table: {e}")
            db.rollback()
        
        print("\n✅ Migration completed successfully!")
        print("   Note: total_payments column kept for payment history tracking")
        print("   Note: user_role column kept for user role display")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()

