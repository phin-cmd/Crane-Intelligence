"""
User-Facing Payments and Subscription API
Provides endpoints for users to view their subscription info and billing history
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ...core.database import get_db
from ...services.auth_service import auth_service
from ...models.user import User
from ...models.fmv_report import FMVReport

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])
security = HTTPBearer()


# Subscription tier logic removed - pay-per-use model only


@router.get("/subscription-info")
async def get_subscription_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get subscription information for current user"""
    try:
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Pay-per-use model - no subscription tiers
        return {
            "success": True,
            "user_role": user.user_role.value if hasattr(user.user_role, 'value') else str(user.user_role),
            "total_payments": user.total_payments or 0,
            "payment_model": "pay_per_use"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscription info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription information"
        )


@router.get("/invoices")
async def get_user_invoices(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get billing history (invoices) for current user"""
    try:
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get all FMV reports with payments for this user
        reports = db.query(FMVReport).filter(
            FMVReport.user_id == user.id,
            FMVReport.amount_paid.isnot(None)
        ).order_by(FMVReport.paid_at.desc()).all()
        
        invoices = []
        for report in reports:
            # Create description from report type
            report_type = report.report_type.value if hasattr(report.report_type, 'value') else str(report.report_type)
            description = f"{report_type.replace('_', ' ').title()} Report"
            if report.crane_details and isinstance(report.crane_details, dict):
                manufacturer = report.crane_details.get('manufacturer', '')
                model = report.crane_details.get('model', '')
                if manufacturer or model:
                    description += f" - {manufacturer} {model}".strip()
            
            invoices.append({
                "id": report.id,
                "transaction_id": report.payment_intent_id or f"txn_{report.id}",
                "amount": float(report.amount_paid) if report.amount_paid else 0.0,
                "description": description,
                "status": report.payment_status or "succeeded",
                "report_type": report_type,
                "created_at": report.created_at.isoformat() if report.created_at else None,
                "paid_at": report.paid_at.isoformat() if report.paid_at else None
            })
        
        return {
            "success": True,
            "invoices": invoices,
            "total": len(invoices)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting invoices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve billing history"
        )

