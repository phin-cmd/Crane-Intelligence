"""
Two-Factor Authentication API endpoints for Admin Users
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ...core.database import get_db
from ...models.admin import AdminUser
from ...core.admin_auth import get_current_admin_user
from ...services.two_factor_service import TwoFactorService

router = APIRouter(prefix="/admin/2fa", tags=["admin-2fa"])


class Setup2FARequest(BaseModel):
    """Request to setup 2FA"""
    pass


class Setup2FAResponse(BaseModel):
    """Response for 2FA setup"""
    secret: str
    qr_code: str
    backup_codes: list[str]


class Verify2FARequest(BaseModel):
    """Request to verify 2FA token"""
    token: str


class Verify2FAResponse(BaseModel):
    """Response for 2FA verification"""
    success: bool
    message: str
    backup_codes: Optional[list[str]] = None


class Disable2FARequest(BaseModel):
    """Request to disable 2FA"""
    password: str  # Require password confirmation


class RegenerateBackupCodesResponse(BaseModel):
    """Response for regenerating backup codes"""
    backup_codes: list[str]


@router.get("/status")
async def get_2fa_status(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get 2FA status for current user"""
    return {
        "enabled": current_user.two_factor_enabled,
        "has_backup_codes": bool(current_user.two_factor_backup_codes),
        "backup_codes_count": len(current_user.two_factor_backup_codes) if current_user.two_factor_backup_codes else 0
    }


@router.post("/setup", response_model=Setup2FAResponse)
async def setup_2fa(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Setup 2FA for current admin user"""
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled"
        )
    
    # Generate secret
    secret = TwoFactorService.generate_secret(current_user.email)
    
    # Generate provisioning URI
    provisioning_uri = TwoFactorService.get_provisioning_uri(
        secret,
        current_user.email,
        issuer="Crane Intelligence Admin"
    )
    
    # Generate QR code
    qr_code = TwoFactorService.generate_qr_code(provisioning_uri)
    
    # Generate backup codes
    backup_codes = TwoFactorService.generate_backup_codes()
    
    # Store secret temporarily (will be saved after verification)
    # In production, you might want to store this in session/redis temporarily
    current_user.two_factor_secret = secret
    current_user.two_factor_backup_codes = backup_codes
    db.commit()
    
    return Setup2FAResponse(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes
    )


@router.post("/verify", response_model=Verify2FAResponse)
async def verify_2fa(
    request: Verify2FARequest,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Verify 2FA token to complete setup"""
    if not current_user.two_factor_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA setup not initiated. Please setup 2FA first."
        )
    
    # Verify token
    success, message = TwoFactorService.enable_2fa(
        db,
        current_user,
        current_user.two_factor_secret,
        request.token
    )
    
    if success:
        return Verify2FAResponse(
            success=True,
            message=message,
            backup_codes=current_user.two_factor_backup_codes
        )
    else:
        # Clear secret on failure
        current_user.two_factor_secret = None
        current_user.two_factor_backup_codes = None
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


@router.post("/disable")
async def disable_2fa(
    request: Disable2FARequest,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Disable 2FA for current admin user"""
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )
    
    # Verify password (you should verify against hashed password)
    from ...services.auth_service import auth_service
    if not auth_service.verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    TwoFactorService.disable_2fa(db, current_user)
    
    return {"message": "2FA disabled successfully"}


@router.post("/regenerate-backup-codes", response_model=RegenerateBackupCodesResponse)
async def regenerate_backup_codes(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Regenerate backup codes for 2FA"""
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )
    
    backup_codes = TwoFactorService.regenerate_backup_codes(db, current_user)
    
    return RegenerateBackupCodesResponse(backup_codes=backup_codes)


@router.get("/backup-codes")
async def get_backup_codes(
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get current backup codes (only shown once during setup)"""
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )
    
    if not current_user.two_factor_backup_codes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No backup codes available"
        )
    
    return {
        "backup_codes": current_user.two_factor_backup_codes,
        "count": len(current_user.two_factor_backup_codes)
    }

