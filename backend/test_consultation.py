#!/usr/bin/env python3
"""Test script to diagnose consultation API issues"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import get_db, engine, Base
from app.models.consultation import ConsultationRequest
from sqlalchemy import inspect

print("=== Testing Consultation API Setup ===")

# Check if table exists
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"\n1. Database tables: {tables}")
print(f"   consultation_requests table exists: {'consultation_requests' in tables}")

# Try to create table if it doesn't exist
if 'consultation_requests' not in tables:
    print("\n2. Creating consultation_requests table...")
    try:
        Base.metadata.create_all(bind=engine, tables=[ConsultationRequest.__table__])
        print("   ✓ Table created successfully")
    except Exception as e:
        print(f"   ✗ Error creating table: {e}")

# Test database connection
print("\n3. Testing database connection...")
try:
    db = next(get_db())
    print("   ✓ Database connection successful")
    
    # Try to query the table
    try:
        count = db.query(ConsultationRequest).count()
        print(f"   ✓ Can query consultation_requests table (count: {count})")
    except Exception as e:
        print(f"   ✗ Cannot query table: {e}")
        import traceback
        traceback.print_exc()
    
    db.close()
except Exception as e:
    print(f"   ✗ Database connection failed: {e}")
    import traceback
    traceback.print_exc()

# Test imports
print("\n4. Testing imports...")
try:
    from app.models.admin import AdminUser
    print("   ✓ AdminUser import successful")
    
    db = next(get_db())
    admin_count = db.query(AdminUser).count()
    print(f"   ✓ Can query AdminUser (count: {admin_count})")
    db.close()
except Exception as e:
    print(f"   ✗ AdminUser import/query failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")

