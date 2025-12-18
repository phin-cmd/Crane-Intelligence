"""
Two-Factor Authentication Service for Admin Users
"""
import pyotp
import qrcode
import io
import base64
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from ..models.admin import AdminUser
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)


class TwoFactorService:
    """Service for managing two-factor authentication"""
    
    @staticmethod
    def generate_secret(email: str) -> str:
        """Generate a TOTP secret for a user"""
        return pyotp.random_base32()
    
    @staticmethod
    def get_provisioning_uri(secret: str, email: str, issuer: str = "Crane Intelligence") -> str:
        """Get the provisioning URI for QR code generation"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=email,
            issuer_name=issuer
        )
    
    @staticmethod
    def generate_qr_code(provisioning_uri: str) -> str:
        """Generate QR code image as base64 string"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """Verify a TOTP token"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=1)  # Allow 1 time step window
        except Exception as e:
            logger.error(f"Error verifying 2FA token: {e}")
            return False
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """Generate backup codes for 2FA"""
        return [secrets.token_hex(4).upper() for _ in range(count)]
    
    @staticmethod
    def verify_backup_code(backup_codes: List[str], code: str) -> bool:
        """Verify a backup code and remove it if valid"""
        if not backup_codes:
            return False
        
        code_upper = code.upper().strip()
        if code_upper in backup_codes:
            backup_codes.remove(code_upper)
            return True
        return False
    
    @staticmethod
    def enable_2fa(
        db: Session,
        admin_user: AdminUser,
        secret: str,
        verification_token: str
    ) -> Tuple[bool, str]:
        """Enable 2FA for an admin user after verification"""
        # Verify the token first
        if not TwoFactorService.verify_token(secret, verification_token):
            return False, "Invalid verification code"
        
        # Generate backup codes
        backup_codes = TwoFactorService.generate_backup_codes()
        
        # Update user
        admin_user.two_factor_enabled = True
        admin_user.two_factor_secret = secret  # In production, encrypt this
        admin_user.two_factor_backup_codes = backup_codes
        
        db.commit()
        db.refresh(admin_user)
        
        return True, "2FA enabled successfully"
    
    @staticmethod
    def disable_2fa(db: Session, admin_user: AdminUser) -> bool:
        """Disable 2FA for an admin user"""
        admin_user.two_factor_enabled = False
        admin_user.two_factor_secret = None
        admin_user.two_factor_backup_codes = None
        
        db.commit()
        return True
    
    @staticmethod
    def verify_2fa_login(
        db: Session,
        admin_user: AdminUser,
        token: str
    ) -> Tuple[bool, Optional[str]]:
        """Verify 2FA token during login"""
        if not admin_user.two_factor_enabled:
            return True, None  # 2FA not enabled, skip verification
        
        if not admin_user.two_factor_secret:
            return False, "2FA is enabled but no secret found"
        
        # Try TOTP token first
        if TwoFactorService.verify_token(admin_user.two_factor_secret, token):
            return True, None
        
        # Try backup codes
        if admin_user.two_factor_backup_codes:
            if TwoFactorService.verify_backup_code(
                admin_user.two_factor_backup_codes.copy(),
                token
            ):
                # Update backup codes in database
                admin_user.two_factor_backup_codes = admin_user.two_factor_backup_codes
                db.commit()
                return True, None
        
        return False, "Invalid 2FA code"
    
    @staticmethod
    def regenerate_backup_codes(db: Session, admin_user: AdminUser) -> List[str]:
        """Regenerate backup codes for a user"""
        if not admin_user.two_factor_enabled:
            raise ValueError("2FA is not enabled for this user")
        
        backup_codes = TwoFactorService.generate_backup_codes()
        admin_user.two_factor_backup_codes = backup_codes
        db.commit()
        
        return backup_codes
    
    @staticmethod
    def check_account_lockout(admin_user: AdminUser) -> Tuple[bool, Optional[str]]:
        """Check if account is locked due to failed login attempts"""
        if admin_user.account_locked_until:
            if datetime.utcnow() < admin_user.account_locked_until:
                remaining = (admin_user.account_locked_until - datetime.utcnow()).seconds
                return False, f"Account locked. Try again in {remaining // 60} minutes"
            else:
                # Lockout expired, reset
                admin_user.account_locked_until = None
                admin_user.failed_login_attempts = 0
        
        return True, None
    
    @staticmethod
    def record_failed_login(db: Session, admin_user: AdminUser, max_attempts: int = 5, lockout_minutes: int = 30):
        """Record a failed login attempt and lock account if threshold reached"""
        admin_user.failed_login_attempts += 1
        
        if admin_user.failed_login_attempts >= max_attempts:
            admin_user.account_locked_until = datetime.utcnow() + timedelta(minutes=lockout_minutes)
            logger.warning(f"Account locked for admin user {admin_user.email} due to {admin_user.failed_login_attempts} failed attempts")
        
        db.commit()
    
    @staticmethod
    def reset_failed_attempts(db: Session, admin_user: AdminUser):
        """Reset failed login attempts on successful login"""
        admin_user.failed_login_attempts = 0
        admin_user.account_locked_until = None
        db.commit()

