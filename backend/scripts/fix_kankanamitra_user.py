#!/usr/bin/env python3
"""
Script to fix kankanamitra01@gmail.com user:
1. Reset to unverified
2. Create verification token
3. Send verification email
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.models.user import User, EmailVerificationToken
from app.services.brevo_email_service import BrevoEmailService
from app.core.config import settings
from datetime import datetime, timedelta
import secrets

def fix_user():
    db = SessionLocal()
    try:
        # Find the user
        user = db.query(User).filter(User.email == "kankanamitra01@gmail.com").first()
        
        if not user:
            print("ERROR: User kankanamitra01@gmail.com not found")
            return
        
        print(f"Found user: {user.email} (ID: {user.id})")
        print(f"Current status: is_verified={user.is_verified}, is_active={user.is_active}")
        
        # Step 1: Reset to unverified
        user.is_verified = False
        print("✓ Reset user to unverified")
        
        # Step 2: Invalidate any existing tokens
        db.query(EmailVerificationToken).filter(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.used == False
        ).update({"used": True})
        print("✓ Invalidated existing tokens")
        
        # Step 3: Create new verification token
        verification_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        verification_token_record = EmailVerificationToken(
            user_id=user.id,
            token=verification_token,
            expires_at=expires_at
        )
        db.add(verification_token_record)
        print(f"✓ Created new verification token: {verification_token[:20]}...")
        
        db.commit()
        db.refresh(user)
        db.refresh(verification_token_record)
        
        # Step 4: Send verification email
        verification_link = f"{settings.frontend_url}/verify-email.html?token={verification_token}"
        first_name = user.full_name.split()[0] if user.full_name else user.username
        
        verification_email_context = {
            "username": user.username,
            "user_name": user.full_name,
            "first_name": first_name,
            "user_email": user.email,
            "verification_link": verification_link,
            "verification_token": verification_token,
            "expiry_days": 1,
            "platform_name": settings.app_name,
            "support_email": settings.mail_from_email
        }
        
        brevo_email_service = BrevoEmailService()
        email_result = brevo_email_service.send_template_email(
            to_emails=[user.email],
            template_name="email_verification.html",
            template_context=verification_email_context,
            subject=f"Verify Your Email Address - {settings.app_name}",
            tags=["email-verification", "manual-fix"]
        )
        
        if email_result.get("success"):
            print(f"✓ Verification email sent successfully to {user.email}")
            print(f"✓ Verification link: {verification_link}")
        else:
            print(f"✗ Failed to send email: {email_result.get('message')}")
            print(f"  Verification link: {verification_link}")
            print(f"  Token: {verification_token}")
        
        print("\n" + "="*60)
        print("User fix completed!")
        print(f"User: {user.email}")
        print(f"Status: is_verified={user.is_verified}")
        print(f"Verification link: {verification_link}")
        print("="*60)
        
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_user()

