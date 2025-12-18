#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app')

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.services.auth_service import auth_service

db: Session = SessionLocal()
try:
    user = db.query(User).filter(User.email == 'kankanamitra01@gmail.com').first()
    if not user:
        print("User not found")
        sys.exit(1)
    
    print(f"User: {user.email}")
    print(f"Current hash: {user.hashed_password[:60]}...")
    
    new_hash = auth_service.get_password_hash('test123')
    print(f"New hash for test123: {new_hash[:60]}...")
    
    user.hashed_password = new_hash
    db.commit()
    print("Password updated to test123")
    
    # Verify it works
    result = auth_service.verify_password('test123', new_hash)
    print(f"Verification test: {result}")
finally:
    db.close()

