#!/usr/bin/env python3
"""
Initialize Equipment Database Tables
This script creates the equipment-related database tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, Base
from app.models.equipment import Equipment, MaintenanceRecord, InspectionRecord, ValuationRecord, Company
from app.models.user import User

def init_equipment_tables():
    """Initialize equipment-related database tables"""
    try:
        print("Creating equipment database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Equipment database tables created successfully!")
        print("Created tables:")
        print("  - equipment")
        print("  - maintenance_records")
        print("  - inspection_records")
        print("  - valuation_records")
        print("  - companies")
        
    except Exception as e:
        print(f"❌ Error creating equipment tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = init_equipment_tables()
    if success:
        print("\n🎉 Equipment database initialization completed!")
    else:
        print("\n💥 Equipment database initialization failed!")
        sys.exit(1)
