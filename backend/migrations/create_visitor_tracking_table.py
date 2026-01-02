"""
Migration script to create visitor_tracking table
Run this script to create the visitor tracking table in the database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine, get_db
from app.models.visitor_tracking import VisitorTracking, Base

def create_visitor_tracking_table():
    """Create the visitor_tracking table"""
    try:
        print("Creating visitor_tracking table...")
        
        # Create all tables defined in Base (including VisitorTracking)
        Base.metadata.create_all(bind=engine, tables=[VisitorTracking.__table__])
        
        print("✅ visitor_tracking table created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating visitor_tracking table: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Visitor Tracking Table Migration")
    print("=" * 60)
    
    success = create_visitor_tracking_table()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("The visitor_tracking table is now available for use.")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)

