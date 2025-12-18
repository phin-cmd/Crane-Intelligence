#!/usr/bin/env python3
"""
Script to fix all users who were created without verification tokens:
1. Find users with is_verified=False but no active tokens
2. Create verification tokens for them
3. Send verification emails
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

def fix_unverified_users():
    db = SessionLocal()
    try:
        # Find users who are unverified and have no active tokens
        users = db.query(User).filter(
            User.is_verified == False
        ).all()
        
        print(f"Found {len(users)} unverified users")
        
        fixed_count = 0
        for user in users:
            # Check if user has any unused tokens
            existing_token = db.query(EmailVerificationToken).filter(
                EmailVerificationToken.user_id == user.id,
                EmailVerificationToken.used == False,
                EmailVerificationToken.expires_at > datetime.utcnow()
            ).first()
            
            if existing_token:
                print(f"  User {user.email} already has an active token, skipping")
                continue
            
            print(f"\nFixing user: {user.email} (ID: {user.id})")
            
            # Create new verification token
            verification_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            verification_token_record = EmailVerificationToken(
                user_id=user.id,
                token=verification_token,
                expires_at=expires_at
            )
            db.add(verification_token_record)
            db.commit()
            
            # Send verification email
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
                print(f"  ✓ Verification email sent to {user.email}")
                fixed_count += 1
            else:
                print(f"  ✗ Failed to send email: {email_result.get('message')}")
                print(f"    Token: {verification_token}")
                print(f"    Link: {verification_link}")
        
        print(f"\n{'='*60}")
        print(f"Fixed {fixed_count} users")
        print(f"{'='*60}")
        
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_unverified_users()

