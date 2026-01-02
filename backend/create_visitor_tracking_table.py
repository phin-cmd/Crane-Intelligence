#!/usr/bin/env python3
"""
Script to create visitor_tracking table in all environments
Run this script to ensure the table exists in dev, UAT, and production
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, init_db
from app.models.visitor_tracking import VisitorTracking
from sqlalchemy import inspect, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_table_exists():
    """Check if visitor_tracking table exists"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return 'visitor_tracking' in tables
    except Exception as e:
        logger.error(f"Error checking tables: {e}")
        return False

def create_table():
    """Create the visitor_tracking table"""
    try:
        logger.info("Creating visitor_tracking table...")
        
        # Import the model to ensure it's registered
        from app.models.visitor_tracking import VisitorTracking
        from app.core.database import Base
        
        # Create the table
        VisitorTracking.__table__.create(bind=engine, checkfirst=True)
        
        logger.info("✅ visitor_tracking table created successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating table: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_table_structure():
    """Verify the table structure"""
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns('visitor_tracking')
        
        logger.info(f"\n✅ Table 'visitor_tracking' has {len(columns)} columns:")
        for col in columns:
            logger.info(f"   - {col['name']}: {col['type']}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error verifying table: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Visitor Tracking Table Creation Script")
    print("=" * 60)
    print()
    
    # Check if table exists
    if check_table_exists():
        print("✅ visitor_tracking table already exists!")
        verify_table_structure()
    else:
        print("❌ visitor_tracking table does not exist. Creating...")
        if create_table():
            verify_table_structure()
            print("\n✅ Migration completed successfully!")
        else:
            print("\n❌ Migration failed. Please check the error messages above.")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Script Complete")
    print("=" * 60)

