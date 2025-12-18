"""
GDPR Compliance API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

from ...core.database import get_db
from ...models.admin import AdminUser
from ...models.user import User
from ...core.admin_auth import require_admin_or_super_admin
from ...services.audit_service import AuditService

router = APIRouter(prefix="/admin/gdpr", tags=["admin-gdpr"])


class GDPRRequestResponse(BaseModel):
    """GDPR request response"""
    id: int
    user_id: int
    user_email: str
    request_type: str  # export, deletion
    status: str  # pending, processing, completed, failed
    created_at: datetime
    completed_at: Optional[datetime]


class GDPRExportResponse(BaseModel):
    """GDPR data export response"""
    user_id: int
    user_data: Dict[str, Any]
    created_at: datetime


@router.post("/export/{user_id}", response_model=GDPRExportResponse)
async def export_user_data(
    user_id: int,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Export all user data for GDPR compliance"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Collect all user data
    from ...models.fmv_report import FMVReport
    from ...models.payment import Payment, Refund
    
    user_data = {
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "company_name": user.company_name,
            "user_role": user.user_role.value if hasattr(user.user_role, 'value') else str(user.user_role),
            "subscription_tier": user.subscription_tier.value if hasattr(user.subscription_tier, 'value') else str(user.subscription_tier),
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None
        },
        "fmv_reports": [],
        "payments": [],
        "refunds": []
    }
    
    # Get FMV reports
    reports = db.query(FMVReport).filter(FMVReport.user_id == user_id).all()
    for report in reports:
        user_data["fmv_reports"].append({
            "id": report.id,
            "report_type": report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type),
            "status": report.status.value if hasattr(report.status, 'value') else str(report.status),
            "amount_paid": float(report.amount_paid) if report.amount_paid else None,
            "created_at": report.created_at.isoformat()
        })
    
    # Get payments
    payments = db.query(Payment).filter(Payment.user_id == user_id).all()
    for payment in payments:
        user_data["payments"].append({
            "id": payment.id,
            "amount": payment.amount,
            "status": payment.status,
            "created_at": payment.created_at.isoformat()
        })
    
    # Get refunds
    refunds = db.query(Refund).filter(Refund.user_id == user_id).all()
    for refund in refunds:
        user_data["refunds"].append({
            "id": refund.id,
            "amount": refund.amount,
            "status": refund.status,
            "created_at": refund.created_at.isoformat()
        })
    
    # Log audit action
    AuditService.log_view(
        db=db,
        admin_user_id=current_user.id,
        resource_type="user",
        resource_id=str(user_id),
        description=f"Exported GDPR data for user: {user.email}"
    )
    
    return GDPRExportResponse(
        user_id=user_id,
        user_data=user_data,
        created_at=datetime.utcnow()
    )


@router.post("/delete/{user_id}")
async def delete_user_data(
    user_id: int,
    confirm: bool = False,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Delete all user data for GDPR compliance"""
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must confirm deletion by setting confirm=true"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_email = user.email
    
    # Delete related data
    from ...models.fmv_report import FMVReport
    from ...models.payment import Payment, Refund
    
    # Delete FMV reports
    db.query(FMVReport).filter(FMVReport.user_id == user_id).delete()
    
    # Delete refunds
    db.query(Refund).filter(Refund.user_id == user_id).delete()
    
    # Note: Payments might need to be kept for accounting - anonymize instead
    # For GDPR, we'll anonymize the user data
    user.email = f"deleted_{user_id}@deleted.local"
    user.username = f"deleted_{user_id}"
    user.full_name = "Deleted User"
    user.company_name = "Deleted"
    user.is_active = False
    
    # Log audit action
    AuditService.log_delete(
        db=db,
        admin_user_id=current_user.id,
        resource_type="user",
        resource_id=str(user_id),
        old_values={"email": user_email},
        description=f"Deleted GDPR data for user: {user_email}"
    )
    
    db.commit()
    
    return {"message": f"User data deleted successfully (anonymized)"}


@router.get("/requests", response_model=List[GDPRRequestResponse])
async def list_gdpr_requests(
    status: Optional[str] = None,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """List GDPR requests"""
    # In a real implementation, you'd have a GDPRRequest model
    # This is a placeholder
    return []


@router.get("/export/{user_id}/download")
async def download_user_data(
    user_id: int,
    current_user: AdminUser = Depends(require_admin_or_super_admin),
    db: Session = Depends(get_db)
):
    """Download user data export as JSON file"""
    from fastapi.responses import Response
    
    export_data = await export_user_data(user_id, current_user, db)
    
    return Response(
        content=json.dumps(export_data.user_data, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=user_{user_id}_data_export.json"}
    )

